"""Runtime monitoring and simple alerting for backend API."""

from collections import Counter, deque
from dataclasses import dataclass
from threading import Lock
from typing import Deque
from datetime import datetime


@dataclass
class MonitoringThresholds:
    error_rate_threshold: float
    latency_ms_threshold: float
    low_availability_threshold: int


class MonitoringState:
    """In-memory metrics aggregator for operational observability."""

    def __init__(self, history_size: int, thresholds: MonitoringThresholds):
        self.history_size = max(50, history_size)
        self.thresholds = thresholds
        self._lock = Lock()
        self.request_history: Deque[dict] = deque(maxlen=self.history_size)
        self.route_counts: Counter = Counter()
        self.status_counts: Counter = Counter()
        self.error_counts: Counter = Counter()
        self.started_at = datetime.utcnow().isoformat()

    def record_request(self, *, method: str, path: str, status_code: int, duration_ms: float) -> None:
        with self._lock:
            self.request_history.append(
                {
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                }
            )
            self.route_counts[f"{method} {path}"] += 1
            self.status_counts[str(status_code)] += 1
            if status_code >= 500:
                self.error_counts["5xx"] += 1
            elif status_code >= 400:
                self.error_counts["4xx"] += 1

    def snapshot(self) -> dict:
        with self._lock:
            recent = list(self.request_history)

        total_requests = len(recent)
        total_errors = sum(1 for item in recent if int(item["status_code"]) >= 500)
        avg_latency = (
            sum(float(item["duration_ms"]) for item in recent) / total_requests
            if total_requests
            else 0.0
        )
        error_rate = (total_errors / total_requests) if total_requests else 0.0

        return {
            "started_at": self.started_at,
            "history_window_size": self.history_size,
            "recent_request_count": total_requests,
            "recent_5xx_count": total_errors,
            "recent_error_rate": round(error_rate, 4),
            "recent_avg_latency_ms": round(avg_latency, 2),
            "status_counts": dict(self.status_counts),
            "top_routes": self.route_counts.most_common(10),
        }

    def evaluate_alerts(self, *, low_availability_floors: list[dict] | None = None) -> list[dict]:
        snapshot = self.snapshot()
        alerts: list[dict] = []

        if snapshot["recent_error_rate"] >= self.thresholds.error_rate_threshold:
            alerts.append(
                {
                    "code": "HIGH_ERROR_RATE",
                    "severity": "high",
                    "message": (
                        f"Recent 5xx error rate {snapshot['recent_error_rate']:.2%} "
                        f"exceeds threshold {self.thresholds.error_rate_threshold:.2%}"
                    ),
                }
            )

        if snapshot["recent_avg_latency_ms"] >= self.thresholds.latency_ms_threshold:
            alerts.append(
                {
                    "code": "HIGH_LATENCY",
                    "severity": "medium",
                    "message": (
                        f"Recent average latency {snapshot['recent_avg_latency_ms']:.2f}ms "
                        f"exceeds threshold {self.thresholds.latency_ms_threshold:.2f}ms"
                    ),
                }
            )

        if low_availability_floors:
            floor_names = ", ".join(item["name"] for item in low_availability_floors[:5])
            alerts.append(
                {
                    "code": "LOW_PARKING_AVAILABILITY",
                    "severity": "medium",
                    "message": (
                        f"Floors below {self.thresholds.low_availability_threshold} slots: {floor_names}"
                    ),
                }
            )

        return alerts
