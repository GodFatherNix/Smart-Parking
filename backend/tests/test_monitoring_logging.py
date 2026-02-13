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


def test_monitoring_metrics_endpoint_exposes_system_metrics(client, auth_headers):
    # Generate traffic for metrics aggregation.
    client.get("/floors", headers=auth_headers)
    client.get("/events?hours=24&limit=10", headers=auth_headers)

    response = client.get("/monitoring/metrics", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()

    assert "recent_request_count" in payload
    assert "recent_avg_latency_ms" in payload
    assert "status_counts" in payload
    assert isinstance(payload["top_routes"], list)


def test_monitoring_alerts_include_error_rate_and_low_availability(client, app_module, auth_headers, monkeypatch):
    _set_floor_state(1, total_slots=20, current_vehicles=18)

    def forced_error(*_args, **_kwargs):
        raise RuntimeError("forced failure for monitoring alert test")

    monkeypatch.setattr(app_module.FloorOperations, "get_all_active_floors", forced_error)
    # Produce 5xx responses to trigger high error rate alert.
    client.get("/floors", headers=auth_headers)
    client.get("/floors", headers=auth_headers)

    # Restore original operation for low availability evaluation.
    monkeypatch.undo()

    response = client.get("/monitoring/alerts", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()

    alert_codes = {item["code"] for item in payload["alerts"]}
    assert "HIGH_ERROR_RATE" in alert_codes
    assert "LOW_PARKING_AVAILABILITY" in alert_codes
