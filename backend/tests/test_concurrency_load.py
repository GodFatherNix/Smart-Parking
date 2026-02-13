import asyncio

import pytest
from httpx import ASGITransport, AsyncClient


def _prepare_floor_capacity(floor_id: int, *, total_slots: int, current_vehicles: int):
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


@pytest.mark.asyncio
async def test_concurrent_event_requests_duplicate_payload(app_module, auth_headers):
    _prepare_floor_capacity(1, total_slots=300, current_vehicles=0)

    payload = {
        "camera_id": "cam_async_dup_001",
        "floor_id": 1,
        "track_id": "track_async_dup_001",
        "vehicle_type": "car",
        "direction": "entry",
        "confidence": 0.97,
    }

    transport = ASGITransport(app=app_module.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        tasks = [ac.post("/event", json=payload, headers=auth_headers) for _ in range(30)]
        responses = await asyncio.gather(*tasks)
        floor_response = await ac.get("/floors/1", headers=auth_headers)

    assert all(resp.status_code == 200 for resp in responses)
    duplicate_messages = [
        resp.json()["message"] for resp in responses if resp.json()["message"].lower().startswith("duplicate")
    ]
    assert len(duplicate_messages) >= 29
    assert floor_response.status_code == 200
    assert floor_response.json()["current_vehicles"] == 1


@pytest.mark.asyncio
async def test_load_concurrent_camera_events(app_module, auth_headers):
    _prepare_floor_capacity(1, total_slots=1000, current_vehicles=0)

    payloads = []
    for idx in range(200):
        payloads.append(
            {
                "camera_id": f"cam_load_{idx % 8}",
                "floor_id": 1,
                "track_id": f"track_load_{idx}",
                "vehicle_type": "car",
                "direction": "entry",
                "confidence": 0.9,
            }
        )

    transport = ASGITransport(app=app_module.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        tasks = [ac.post("/event", json=payload, headers=auth_headers) for payload in payloads]
        responses = await asyncio.gather(*tasks)
        floor_response = await ac.get("/floors/1", headers=auth_headers)
        events_response = await ac.get("/events?hours=24&limit=500", headers=auth_headers)

    success_count = sum(1 for response in responses if response.status_code == 200)
    assert success_count == 200
    assert floor_response.status_code == 200
    assert floor_response.json()["current_vehicles"] == 200
    assert events_response.status_code == 200
    assert events_response.json()["filtered_count"] >= 200
