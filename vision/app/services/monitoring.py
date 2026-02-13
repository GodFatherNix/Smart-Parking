"""Runtime monitoring and dashboard metrics writer."""

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


@dataclass
class CameraStatus:
    camera_id: str
    source: str
    status: str = "initializing"  # initializing|running|degraded|offline
    last_frame_at: float = 0.0
    consecutive_read_failures: int = 0


@dataclass
class PerformanceMonitor:
    dashboard_path: str
    started_at: float = field(default_factory=time.time)
    totals: Dict[str, int] = field(
        default_factory=lambda: {
            "frames": 0,
            "detections": 0,
            "tracked_objects": 0,
            "events_generated": 0,
            "events_transmitted": 0,
            "events_queued": 0,
        }
    )
    stage_latency_ms_sum: Dict[str, float] = field(
        default_factory=lambda: {"detect": 0.0, "track": 0.0, "event": 0.0, "transmit": 0.0}
    )

    def __post_init__(self):
        path = Path(self.dashboard_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._path = path

    def record_stage_latency(self, stage: str, latency_ms: float):
        if stage in self.stage_latency_ms_sum:
            self.stage_latency_ms_sum[stage] += max(0.0, latency_ms)

    def write_dashboard(self, frame_count: int, camera: CameraStatus, backend_online: bool, queue_size: int):
        uptime = max(time.time() - self.started_at, 1e-6)
        avg_fps = frame_count / uptime
        avg_latency = {
            stage: (total / frame_count if frame_count > 0 else 0.0)
            for stage, total in self.stage_latency_ms_sum.items()
        }

        payload = {
            "timestamp": time.time(),
            "uptime_seconds": uptime,
            "average_fps": avg_fps,
            "camera": {
                "camera_id": camera.camera_id,
                "source": camera.source,
                "status": camera.status,
                "last_frame_at": camera.last_frame_at,
                "consecutive_read_failures": camera.consecutive_read_failures,
            },
            "backend_online": backend_online,
            "queue_size": queue_size,
            "totals": self.totals,
            "average_stage_latency_ms": avg_latency,
        }

        self._path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
        logger.debug(f"Monitoring dashboard updated at {self._path}")
