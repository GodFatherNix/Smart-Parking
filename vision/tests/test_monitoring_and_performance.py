import json
import time
from pathlib import Path
from unittest.mock import patch

from app.services.monitoring import CameraStatus, PerformanceMonitor
from app.services.video_source import FrameRateRegulator


def test_monitoring_dashboard_written_with_fps_and_latency(tmp_path):
    dashboard = tmp_path / "monitor.json"
    monitor = PerformanceMonitor(str(dashboard))

    cam = CameraStatus(camera_id="cam_001", source="rtsp://example")
    cam.status = "running"
    cam.last_frame_at = time.time()

    monitor.totals["frames"] = 30
    monitor.totals["detections"] = 60
    monitor.record_stage_latency("detect", 100.0)
    monitor.record_stage_latency("track", 80.0)
    monitor.record_stage_latency("event", 20.0)
    monitor.record_stage_latency("transmit", 50.0)

    monitor.write_dashboard(frame_count=30, camera=cam, backend_online=True, queue_size=2)

    payload = json.loads(Path(dashboard).read_text(encoding="utf-8"))
    assert payload["average_fps"] > 0
    assert payload["camera"]["status"] == "running"
    assert payload["queue_size"] == 2
    assert "average_stage_latency_ms" in payload


def test_frame_rate_regulation_target_range():
    regulator = FrameRateRegulator(target_fps=10)

    with patch("time.sleep") as sleep_mock, patch(
        "time.perf_counter", side_effect=[0.0, 0.05, 0.051]
    ):
        regulator.tick()  # first tick initializes timer
        regulator.tick()  # second tick may sleep to regulate

        # For 10 FPS interval(0.1s) and 0.05 elapsed, expected sleep is approx 0.05s.
        assert sleep_mock.call_count == 1
        assert abs(sleep_mock.call_args[0][0] - 0.05) < 0.02
