import asyncio
import importlib
import os
import sys
from datetime import datetime
from time import perf_counter

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient


def _set_floor_state(floor_id: int, *, total_slots: int, current_vehicles: int):
    from app.core.database import SessionLocal
    from app.models.floor import Floor

    session = SessionLocal()
    try:
        floor = session.query(Floor).filter(Floor.id == floor_id).first()
        floor.total_slots = total_slots
        floor.current_vehicles = current_vehicles
        floor.is_active = True
        session.commit()
    finally:
        session.close()


def _find_event_by_track(events: list[dict], track_id: str) -> dict | None:
    for event in events:
        if event.get("track_id") == track_id:
            return event
    return None


def _clear_backend_modules() -> None:
    for module_name in list(sys.modules):
        if module_name == "main" or module_name.startswith("app."):
            sys.modules.pop(module_name, None)


def test_full_flow_vision_to_backend_to_frontend_display_contract(client, auth_headers):
    _set_floor_state(1, total_slots=200, current_vehicles=10)
    track_id = "track_phase5_e2e_001"
    payload = {
        "camera_id": "cam_phase5_001",
        "floor_id": 1,
        "track_id": track_id,
        "vehicle_type": "car",
        "direction": "entry",
        "confidence": 0.98,
    }

    event_res = client.post("/event", json=payload, headers=auth_headers)
    floors_res = client.get("/floors", headers=auth_headers)
    recommend_res = client.get("/recommend", headers=auth_headers)
    events_res = client.get("/events?hours=24&limit=500", headers=auth_headers)

    assert event_res.status_code == 200
    assert floors_res.status_code == 200
    assert recommend_res.status_code == 200
    assert events_res.status_code == 200

    floors_payload = floors_res.json()
    events_payload = events_res.json()
    recommend_payload = recommend_res.json()

    floor_1 = next(item for item in floors_payload["floors"] if item["id"] == 1)
    assert floor_1["current_vehicles"] == 11
    assert floor_1["available_slots"] == floor_1["total_slots"] - floor_1["current_vehicles"]
    assert "recommended_floor" in recommend_payload
    assert "available_alternatives" in recommend_payload

    recorded = _find_event_by_track(events_payload["events"], track_id)
    assert recorded is not None
    assert recorded["camera_id"] == "cam_phase5_001"
    assert recorded["direction"] == "entry"


@pytest.mark.asyncio
async def test_8_plus_simultaneous_camera_streams(app_module, auth_headers):
    _set_floor_state(1, total_slots=5000, current_vehicles=0)
    transport = ASGITransport(app=app_module.app)
    payloads = []
    per_camera_events = 25
    camera_count = 8

    for camera_idx in range(camera_count):
        for event_idx in range(per_camera_events):
            payloads.append(
                {
                    "camera_id": f"cam_phase5_{camera_idx}",
                    "floor_id": 1,
                    "track_id": f"track_phase5_cam{camera_idx}_{event_idx}",
                    "vehicle_type": "car",
                    "direction": "entry",
                    "confidence": 0.91,
                }
            )

    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        responses = await asyncio.gather(
            *[ac.post("/event", json=payload, headers=auth_headers) for payload in payloads]
        )
        floor_res = await ac.get("/floors/1", headers=auth_headers)

    assert all(response.status_code == 200 for response in responses)
    assert floor_res.status_code == 200
    assert floor_res.json()["current_vehicles"] == camera_count * per_camera_events


def test_duplicate_event_prevention_system_level(client, auth_headers):
    _set_floor_state(1, total_slots=100, current_vehicles=0)
    payload = {
        "camera_id": "cam_phase5_dup_001",
        "floor_id": 1,
        "track_id": "track_phase5_dup_001",
        "vehicle_type": "car",
        "direction": "entry",
        "confidence": 0.93,
    }

    responses = [client.post("/event", json=payload, headers=auth_headers) for _ in range(10)]
    floor_res = client.get("/floors/1", headers=auth_headers)

    assert all(response.status_code == 200 for response in responses)
    duplicate_count = sum(
        1 for response in responses if response.json()["message"].lower().startswith("duplicate")
    )
    assert duplicate_count >= 9
    assert floor_res.json()["current_vehicles"] == 1


def test_end_to_end_latency_under_one_second(client, auth_headers):
    _set_floor_state(1, total_slots=500, current_vehicles=0)
    payload = {
        "camera_id": "cam_phase5_latency_001",
        "floor_id": 1,
        "track_id": "track_phase5_latency_001",
        "vehicle_type": "car",
        "direction": "entry",
        "confidence": 0.9,
    }

    start = perf_counter()
    response = client.post("/event", json=payload, headers=auth_headers)
    elapsed_seconds = perf_counter() - start

    assert response.status_code == 200
    assert elapsed_seconds < 1.0


def test_sustained_stream_load_reliability(client, auth_headers):
    _set_floor_state(1, total_slots=8000, current_vehicles=0)
    total_events = 400
    ok = 0

    for idx in range(total_events):
        payload = {
            "camera_id": f"cam_phase5_load_{idx % 8}",
            "floor_id": 1,
            "track_id": f"track_phase5_load_{idx}",
            "vehicle_type": "car",
            "direction": "entry",
            "confidence": 0.89,
        }
        response = client.post("/event", json=payload, headers=auth_headers)
        if response.status_code == 200:
            ok += 1

    success_ratio = ok / float(total_events)
    assert success_ratio >= 0.99


def test_system_uptime_target_99_percent_via_healthchecks(client):
    total_checks = 200
    healthy = 0

    for _ in range(total_checks):
        response = client.get("/health")
        if response.status_code == 200 and response.json()["status"] == "healthy":
            healthy += 1

    uptime_ratio = healthy / float(total_checks)
    assert uptime_ratio >= 0.99


def test_graceful_recovery_after_transient_failure(client, auth_headers, monkeypatch):
    from app.core import database_ops

    _set_floor_state(1, total_slots=200, current_vehicles=0)
    original = database_ops.EventOperations.record_event
    state = {"failed_once": False}

    def flaky_once(*args, **kwargs):
        if not state["failed_once"]:
            state["failed_once"] = True
            raise RuntimeError("transient failure")
        return original(*args, **kwargs)

    monkeypatch.setattr(database_ops.EventOperations, "record_event", flaky_once)

    payload = {
        "camera_id": "cam_phase5_recovery_001",
        "floor_id": 1,
        "track_id": "track_phase5_recovery_001",
        "vehicle_type": "car",
        "direction": "entry",
        "confidence": 0.9,
    }

    failed = client.post("/event", json=payload, headers=auth_headers)
    recovered = client.post("/event", json=payload, headers=auth_headers)

    assert failed.status_code == 500
    assert recovered.status_code == 200


def test_database_state_restoration_after_backend_restart(client, app_module, auth_headers, monkeypatch):
    _set_floor_state(1, total_slots=200, current_vehicles=0)
    payload = {
        "camera_id": "cam_phase5_restore_001",
        "floor_id": 1,
        "track_id": "track_phase5_restore_001",
        "vehicle_type": "car",
        "direction": "entry",
        "confidence": 0.92,
    }

    create_res = client.post("/event", json=payload, headers=auth_headers)
    assert create_res.status_code == 200

    db_url = os.environ["DATABASE_URL"]
    api_keys = os.environ.get("API_KEYS", "test-api-key")
    _clear_backend_modules()
    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("API_KEYS", api_keys)
    reloaded_main = importlib.import_module("main")

    with TestClient(reloaded_main.app, raise_server_exceptions=False) as reloaded_client:
        events_res = reloaded_client.get("/events?hours=24&limit=500", headers=auth_headers)

    assert events_res.status_code == 200
    restored = _find_event_by_track(events_res.json()["events"], "track_phase5_restore_001")
    assert restored is not None


def test_data_accuracy_counts_and_floor_availability(client, auth_headers):
    _set_floor_state(1, total_slots=100, current_vehicles=0)
    entries = 12
    exits = 5
    track_idx = 0

    for _ in range(entries):
        response = client.post(
            "/event",
            json={
                "camera_id": "cam_phase5_accuracy_001",
                "floor_id": 1,
                "track_id": f"track_phase5_acc_in_{track_idx}",
                "vehicle_type": "car",
                "direction": "entry",
                "confidence": 0.95,
            },
            headers=auth_headers,
        )
        track_idx += 1
        assert response.status_code == 200

    for _ in range(exits):
        response = client.post(
            "/event",
            json={
                "camera_id": "cam_phase5_accuracy_001",
                "floor_id": 1,
                "track_id": f"track_phase5_acc_out_{track_idx}",
                "vehicle_type": "car",
                "direction": "exit",
                "confidence": 0.95,
            },
            headers=auth_headers,
        )
        track_idx += 1
        assert response.status_code == 200

    floor_res = client.get("/floors/1", headers=auth_headers)
    assert floor_res.status_code == 200
    payload = floor_res.json()
    expected_current = entries - exits
    assert payload["current_vehicles"] == expected_current
    assert payload["available_slots"] == payload["total_slots"] - expected_current


def test_event_timestamp_validity(client, auth_headers):
    _set_floor_state(1, total_slots=100, current_vehicles=0)
    track_id = "track_phase5_ts_001"
    payload = {
        "camera_id": "cam_phase5_ts_001",
        "floor_id": 1,
        "track_id": track_id,
        "vehicle_type": "car",
        "direction": "entry",
        "confidence": 0.96,
    }

    before = datetime.utcnow()
    create_res = client.post("/event", json=payload, headers=auth_headers)
    after = datetime.utcnow()
    assert create_res.status_code == 200

    events_res = client.get("/events?hours=24&limit=500", headers=auth_headers)
    assert events_res.status_code == 200
    event = _find_event_by_track(events_res.json()["events"], track_id)
    assert event is not None

    parsed = datetime.fromisoformat(event["timestamp"])
    assert before <= parsed <= after
