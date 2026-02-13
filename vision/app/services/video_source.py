"""Video frame acquisition service for RTSP and file sources."""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class VideoSourceConfig:
    """Video input source configuration."""

    source: str
    source_type: str  # "rtsp" or "file"
    width: Optional[int] = None
    height: Optional[int] = None
    target_fps: int = 15
    reconnect_delay_seconds: float = 1.0


class FrameRateRegulator:
    """Regulate processing loop to target FPS."""

    def __init__(self, target_fps: int):
        self.target_fps = max(1, target_fps)
        self.frame_interval_seconds = 1.0 / float(self.target_fps)
        self._last_tick = None

    def tick(self) -> None:
        now = time.perf_counter()
        if self._last_tick is None:
            self._last_tick = now
            return

        elapsed = now - self._last_tick
        sleep_for = self.frame_interval_seconds - elapsed
        if sleep_for > 0:
            time.sleep(sleep_for)

        self._last_tick = time.perf_counter()


class VideoSource:
    """Open and read frames from RTSP stream or local file."""

    def __init__(self, config: VideoSourceConfig):
        self.config = config
        self.capture = None
        self._is_open = False
        self._cv2 = None

    @staticmethod
    def infer_source_type(source: str) -> str:
        source_lower = source.lower()
        if source_lower.startswith("rtsp://"):
            return "rtsp"
        return "file"

    def open(self) -> bool:
        if self._cv2 is None:
            try:
                import cv2  # pylint: disable=import-outside-toplevel
                self._cv2 = cv2
            except ImportError as exc:
                logger.error("OpenCV is required for video acquisition. Install: pip install opencv-python")
                raise RuntimeError("opencv-python is not installed") from exc

        if self._is_open and self.capture is not None and self.capture.isOpened():
            return True

        if self.config.source_type == "file":
            file_path = Path(self.config.source)
            if not file_path.exists():
                logger.error(f"Video file not found: {self.config.source}")
                return False

        logger.info(f"Opening video source: {self.config.source} ({self.config.source_type})")
        self.capture = self._cv2.VideoCapture(self.config.source)

        if self.config.width:
            self.capture.set(self._cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
        if self.config.height:
            self.capture.set(self._cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)

        self._is_open = bool(self.capture and self.capture.isOpened())
        if not self._is_open:
            logger.error(f"Failed to open video source: {self.config.source}")
        return self._is_open

    def close(self) -> None:
        if self.capture is not None:
            self.capture.release()
        self.capture = None
        self._is_open = False

    def read_frame(self):
        if not self._is_open or self.capture is None:
            if not self.open():
                return False, None

        ok, frame = self.capture.read()
        if ok:
            return True, frame

        # For RTSP sources, try reconnecting.
        if self.config.source_type == "rtsp":
            logger.warning("RTSP frame read failed, attempting reconnect...")
            self.close()
            time.sleep(self.config.reconnect_delay_seconds)
            if self.open():
                return self.capture.read()

        return False, None
