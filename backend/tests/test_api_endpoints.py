def test_public_endpoints_are_accessible(client):
    root = client.get("/")
    health = client.get("/health")
    live = client.get("/health/live")
    ready = client.get("/health/ready")

    assert root.status_code == 200
    assert health.status_code == 200
    assert live.status_code == 200
    assert ready.status_code == 200
    assert root.json()["docs"] == "/docs"
    assert "status" in health.json()
    assert live.json()["status"] == "alive"
    assert ready.json()["status"] == "ready"


def test_protected_endpoint_requires_api_key(client):
    response = client.get("/floors")
    assert response.status_code == 401
    assert response.json()["error"] == "Authentication Error"


def test_get_floors_with_auth(client, auth_headers):
    response = client.get("/floors", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["total_floors"] >= 1
    assert isinstance(payload["floors"], list)


def test_get_floor_by_id_with_auth(client, auth_headers):
    floors_response = client.get("/floors", headers=auth_headers)
    floor_id = floors_response.json()["floors"][0]["id"]

    response = client.get(f"/floors/{floor_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == floor_id


def test_get_recommendation_with_auth(client, auth_headers):
    response = client.get("/recommend", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert "recommended_floor" in payload


def test_get_events_with_filters_and_validation(client, auth_headers):
    response = client.get("/events?hours=24&limit=20&offset=0", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

    invalid = client.get("/events?hours=0", headers=auth_headers)
    assert invalid.status_code == 422
    assert invalid.json()["error"] == "Validation Error"


def test_latest_camera_frame_endpoint_requires_auth_and_handles_empty_directory(client, auth_headers):
    unauth = client.get("/camera/latest-frame")
    assert unauth.status_code == 401

    response = client.get("/camera/latest-frame", headers=auth_headers)
    # In test environment frames are not generated, endpoint should be graceful.
    assert response.status_code in (404, 200)


def test_post_event_and_duplicate_idempotency(client, auth_headers):
    payload = {
        "camera_id": "cam_api_test_001",
        "floor_id": 1,
        "track_id": "track_api_idempotent_001",
        "vehicle_type": "car",
        "direction": "entry",
        "confidence": 0.99,
    }

    first = client.post("/event", json=payload, headers=auth_headers)
    second = client.post("/event", json=payload, headers=auth_headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["success"] is True
    assert second.json()["success"] is True
    assert second.json()["message"].lower().startswith("duplicate")
