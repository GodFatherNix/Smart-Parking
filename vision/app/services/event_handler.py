"""Line crossing detection and event generation service."""

import logging
from datetime import UTC, datetime
from typing import Dict, List, Optional, Tuple
import math

logger = logging.getLogger(__name__)


class EventHandler:
    """Detect line crossings and generate parking entry/exit events."""

    def __init__(
        self,
        line_points: Optional[List[Tuple[int, int]]] = None,
        area_threshold: int = 100,
        camera_id: str = "cam_001",
        floor_id: int = 1,
        direction_mapping: Optional[Dict[str, str]] = None,
        duplicate_cooldown_frames: int = 12,
        occlusion_tolerance_frames: int = 20,
        min_crossing_distance_px: int = 5,
        reversal_suppression_frames: int = 20,
    ):
        self.line_points = line_points or [(0, 360), (1280, 360)]
        self.area_threshold = area_threshold
        self.camera_id = camera_id
        self.floor_id = floor_id
        self.direction_mapping = direction_mapping or {
            "up": "entry",
            "down": "exit",
            "left": "entry",
            "right": "exit",
            "positive": "entry",
            "negative": "exit",
        }
        self.duplicate_cooldown_frames = max(1, duplicate_cooldown_frames)
        self.occlusion_tolerance_frames = max(1, occlusion_tolerance_frames)
        self.min_crossing_distance_px = max(0, min_crossing_distance_px)
        self.reversal_suppression_frames = max(1, reversal_suppression_frames)

        self.track_history: Dict[str, Dict[str, object]] = {}
        self.last_crossing: Dict[str, Dict[str, object]] = {}
        logger.info(
            f"EventHandler initialized for camera={camera_id} floor={floor_id} "
            f"line={self.line_points}"
        )

    def process_frame(
        self,
        tracked_objects: List[dict],
        frame_id: int,
        timestamp: Optional[datetime] = None,
    ) -> List[dict]:
        """Process tracked objects and return crossing events."""
        now = timestamp or datetime.now(UTC)
        events: List[dict] = []

        for obj in tracked_objects:
            bbox = obj.get("bbox", {})
            area = int(bbox.get("width", 0)) * int(bbox.get("height", 0))
            if area < self.area_threshold:
                continue

            track_id = str(obj.get("track_id", ""))
            centroid = obj.get("centroid")
            if not track_id or centroid is None:
                continue

            event = self._detect_line_crossing(track_id, centroid, frame_id, now)
            if event:
                event.update(
                    {
                        "camera_id": self.camera_id,
                        "floor_id": self.floor_id,
                        "vehicle_type": obj.get("class_name", "unknown"),
                        "confidence": float(obj.get("confidence", 0.0)),
                        "frame_id": frame_id,
                    }
                )
                events.append(event)

        return events

    def _detect_line_crossing(
        self,
        track_id: str,
        centroid: Dict[str, int],
        frame_id: int,
        timestamp: datetime,
    ) -> Optional[dict]:
        current_pos = (int(centroid["x"]), int(centroid["y"]))
        prev_state = self.track_history.get(track_id)
        self.track_history[track_id] = {"position": current_pos, "frame_id": frame_id}

        if prev_state is None:
            return None

        frame_gap = frame_id - int(prev_state["frame_id"])
        if frame_gap > self.occlusion_tolerance_frames:
            return None

        prev_pos = prev_state["position"]
        if self._movement_distance(prev_pos, current_pos) < self.min_crossing_distance_px:
            return None

        crossing = self._check_line_crossing(prev_pos, current_pos)
        if crossing is None:
            return None

        mapped_direction = self._map_direction(prev_pos, current_pos, crossing["sign"])
        if self._is_reversal_suppressed(track_id, mapped_direction, frame_id):
            return None
        if not self._is_unique_crossing(track_id, mapped_direction, frame_id):
            return None

        self.last_crossing[track_id] = {
            "direction": mapped_direction,
            "frame_id": frame_id,
        }

        return {
            "track_id": track_id,
            "direction": mapped_direction,
            "timestamp": timestamp.isoformat(),
            "crossing_point": {
                "x": crossing["point"][0],
                "y": crossing["point"][1],
            },
        }

    def _check_line_crossing(
        self,
        prev_pos: Tuple[int, int],
        curr_pos: Tuple[int, int],
    ) -> Optional[dict]:
        line_start = tuple(self.line_points[0])
        line_end = tuple(self.line_points[1])

        def cross_product_sign(point):
            return (line_end[0] - line_start[0]) * (point[1] - line_start[1]) - (
                line_end[1] - line_start[1]
            ) * (point[0] - line_start[0])

        prev_side = cross_product_sign(prev_pos)
        curr_side = cross_product_sign(curr_pos)

        # Strict crossing when sides differ.
        if prev_side * curr_side < 0:
            crossing_point = (
                int((prev_pos[0] + curr_pos[0]) / 2),
                int((prev_pos[1] + curr_pos[1]) / 2),
            )
            return {
                "point": crossing_point,
                "sign": "positive" if curr_side > 0 else "negative",
            }

        return None

    def _map_direction(self, prev_pos: Tuple[int, int], curr_pos: Tuple[int, int], sign: str) -> str:
        # Use dominant motion axis relative to line orientation.
        line_start = tuple(self.line_points[0])
        line_end = tuple(self.line_points[1])
        line_dx = abs(line_end[0] - line_start[0])
        line_dy = abs(line_end[1] - line_start[1])

        movement_x = curr_pos[0] - prev_pos[0]
        movement_y = curr_pos[1] - prev_pos[1]

        if line_dx >= line_dy:
            primary = "down" if movement_y > 0 else "up"
        else:
            primary = "right" if movement_x > 0 else "left"

        return self.direction_mapping.get(primary) or self.direction_mapping.get(sign) or "entry"

    def _is_unique_crossing(self, track_id: str, direction: str, frame_id: int) -> bool:
        """Single-event-per-crossing guarantee with cooldown against jitter duplicates."""
        prev_cross = self.last_crossing.get(track_id)
        if prev_cross is None:
            return True

        within_cooldown = (frame_id - int(prev_cross["frame_id"])) <= self.duplicate_cooldown_frames
        # Block all repeated crossings in cooldown window to suppress oscillation jitter.
        if within_cooldown:
            return False

        return True

    @staticmethod
    def _movement_distance(prev_pos: Tuple[int, int], curr_pos: Tuple[int, int]) -> float:
        return math.hypot(curr_pos[0] - prev_pos[0], curr_pos[1] - prev_pos[1])

    def _is_reversal_suppressed(self, track_id: str, direction: str, frame_id: int) -> bool:
        """Suppress immediate opposite-direction recrossing caused by backing up/reversal jitter."""
        previous = self.last_crossing.get(track_id)
        if previous is None:
            return False

        prev_dir = str(previous.get("direction", ""))
        if not prev_dir:
            return False

        is_opposite = (prev_dir, direction) in {("entry", "exit"), ("exit", "entry")}
        if not is_opposite:
            return False

        return (frame_id - int(previous["frame_id"])) <= self.reversal_suppression_frames

    def clear_old_tracks(self, max_age: int = 100, current_frame: int = 0):
        """Clear stale track history to avoid unbounded memory growth."""
        stale_history = []
        for track_id, state in self.track_history.items():
            last_seen = int(state.get("frame_id", 0))
            if current_frame - last_seen > max_age:
                stale_history.append(track_id)

        for track_id in stale_history:
            self.track_history.pop(track_id, None)
            self.last_crossing.pop(track_id, None)
