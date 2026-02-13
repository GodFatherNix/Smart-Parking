from pathlib import Path
from unittest.mock import Mock

import requests

from app.services.api_client import BackendClient


def test_event_transmission_retries_and_queues_on_failure(tmp_path):
    local_log = tmp_path / "events_local.jsonl"
    queue_log = tmp_path / "events_queue.jsonl"

    client = BackendClient(
        api_url="http://localhost:8000/event",
        retry_attempts=2,
        retry_delay=0,
        local_log_path=str(local_log),
        queue_path=str(queue_log),
    )

    client.session.post = Mock(side_effect=requests.exceptions.ConnectionError("offline"))

    ok = client.process_event(
        {
            "camera_id": "cam_001",
            "floor_id": 1,
            "track_id": "t1",
            "vehicle_type": "car",
            "direction": "entry",
            "confidence": 0.9,
        }
    )
    assert ok is False
    assert client.queue_size() == 1
    assert local_log.exists()
    assert queue_log.exists()


def test_queued_events_flush_successfully(tmp_path):
    local_log = tmp_path / "events_local.jsonl"
    queue_log = tmp_path / "events_queue.jsonl"

    client = BackendClient(
        api_url="http://localhost:8000/event",
        retry_attempts=1,
        retry_delay=0,
        local_log_path=str(local_log),
        queue_path=str(queue_log),
    )

    # Queue one event manually via failure path
    client.session.post = Mock(side_effect=requests.exceptions.ConnectionError("offline"))
    client.process_event(
        {
            "camera_id": "cam_001",
            "floor_id": 1,
            "track_id": "t2",
            "vehicle_type": "car",
            "direction": "entry",
            "confidence": 0.9,
        }
    )
    assert client.queue_size() == 1

    # Then simulate backend recovery
    success_response = Mock()
    success_response.status_code = 200
    success_response.text = "ok"
    client.session.post = Mock(return_value=success_response)

    result = client.flush_queued_events(max_events=10)
    assert result["flushed"] == 1
    assert client.queue_size() == 0
    assert Path(queue_log).read_text(encoding="utf-8").strip() == ""
