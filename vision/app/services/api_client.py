"""API client for transmitting events to backend with offline buffering."""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class BackendClient:
    """HTTP client for backend communication with persistent offline queue."""

    def __init__(
        self,
        api_url: str,
        timeout: int = 5,
        retry_attempts: int = 3,
        retry_delay: int = 1,
        local_log_path: str = "./logs/events_local.jsonl",
        queue_path: str = "./logs/events_queue.jsonl",
    ):
        self.api_url = api_url
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self.is_online = True

        self.local_log_path = Path(local_log_path)
        self.queue_path = Path(queue_path)
        self.local_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)

        self._queue: List[dict] = self._load_queue_from_disk()
        logger.info(
            f"BackendClient initialized for {api_url} | queued events loaded: {len(self._queue)}"
        )

    @staticmethod
    def normalize_event_payload(event: Dict) -> Dict:
        """Convert internal event object to backend API payload schema."""
        payload = {
            "camera_id": event.get("camera_id"),
            "floor_id": int(event.get("floor_id", 0)),
            "track_id": str(event.get("track_id", "")),
            "vehicle_type": str(event.get("vehicle_type", "car")),
            "direction": str(event.get("direction", "entry")),
            "confidence": float(event.get("confidence", 0.8)),
        }
        return payload

    def _append_jsonl(self, file_path: Path, payload: Dict) -> None:
        with file_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=True) + "\n")

    def _rewrite_queue_file(self) -> None:
        with self.queue_path.open("w", encoding="utf-8") as f:
            for event in self._queue:
                f.write(json.dumps(event, ensure_ascii=True) + "\n")

    def _load_queue_from_disk(self) -> List[dict]:
        if not self.queue_path.exists():
            return []

        queue: List[dict] = []
        with self.queue_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    queue.append(json.loads(line))
                except json.JSONDecodeError:
                    logger.warning("Skipping malformed queued event line")
        return queue

    def queue_size(self) -> int:
        return len(self._queue)

    def log_event_locally(self, event: Dict) -> None:
        """Persist raw event to local log before network submission."""
        envelope = {
            "logged_at": time.time(),
            "event": event,
        }
        self._append_jsonl(self.local_log_path, envelope)

    def _queue_event(self, payload: Dict) -> None:
        self._queue.append(payload)
        self._append_jsonl(self.queue_path, payload)
        logger.warning(f"Event queued for retry. queue_size={len(self._queue)}")

    def submit_event(self, payload: Dict, queue_on_failure: bool = True) -> bool:
        """Submit normalized event payload to backend with retries."""
        for attempt in range(self.retry_attempts):
            try:
                logger.debug(f"Submitting event (attempt {attempt + 1}): {payload}")
                response = self.session.post(
                    self.api_url,
                    json=payload,
                    timeout=self.timeout,
                )
                if response.status_code in (200, 201):
                    self.is_online = True
                    return True

                logger.warning(
                    f"Backend returned status {response.status_code}: {response.text}"
                )
            except requests.exceptions.Timeout:
                logger.warning(f"Event submission timeout (attempt {attempt + 1})")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Event submission connection error (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Error submitting event: {e}")

            if attempt < self.retry_attempts - 1:
                time.sleep(self.retry_delay)

        self.is_online = False
        if queue_on_failure:
            self._queue_event(payload)
        return False

    def process_event(self, event: Dict) -> bool:
        """Log event locally, normalize payload, submit or queue."""
        self.log_event_locally(event)
        payload = self.normalize_event_payload(event)
        return self.submit_event(payload, queue_on_failure=True)

    def flush_queued_events(self, max_events: int = 100) -> Dict[str, int]:
        """Retry queued events when network is available."""
        if not self._queue:
            return {"flushed": 0, "failed": 0}

        flushed = 0
        failed = 0
        remaining: List[dict] = []

        for idx, payload in enumerate(self._queue):
            if idx >= max_events:
                remaining.extend(self._queue[idx:])
                break

            if self.submit_event(payload, queue_on_failure=False):
                flushed += 1
            else:
                failed += 1
                remaining.append(payload)

        self._queue = remaining
        self._rewrite_queue_file()
        if flushed > 0 or failed > 0:
            logger.info(
                f"Queue flush result: flushed={flushed}, failed={failed}, remaining={len(self._queue)}"
            )
        return {"flushed": flushed, "failed": failed}

    def health_check(self) -> bool:
        """Check backend health endpoint."""
        try:
            base_url = self.api_url.rsplit("/", 1)[0] if "/" in self.api_url else self.api_url
            health_url = f"{base_url}/health"
            response = self.session.get(health_url, timeout=self.timeout)
            healthy = response.status_code == 200
            self.is_online = healthy
            if healthy:
                logger.info("Backend health check passed")
            else:
                logger.warning(f"Backend health check failed: {response.status_code}")
            return healthy
        except Exception as e:
            logger.error(f"Backend health check error: {e}")
            self.is_online = False
            return False
