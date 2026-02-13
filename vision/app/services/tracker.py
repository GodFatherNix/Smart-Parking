"""Vehicle tracking service using ByteTrack."""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class TrackState:
    """Track metadata and lifecycle state."""

    track_id: str
    class_name: str
    last_centroid: Dict[str, int]
    last_seen_frame: int
    hit_count: int = 1
    miss_count: int = 0
    history: List[Dict[str, int]] = field(default_factory=list)


class VehicleTracker:
    """ByteTrack wrapper with explicit track state management."""

    def __init__(self, track_buffer: int = 30, conf_threshold: float = 0.5):
        self.track_buffer = track_buffer
        self.conf_threshold = conf_threshold
        self.tracker = None
        self.active_tracks: Dict[str, TrackState] = {}
        self._initialize_tracker()

    def _initialize_tracker(self):
        """Initialize ByteTrack tracker."""
        try:
            from supervision import ByteTrack  # pylint: disable=import-outside-toplevel

            logger.info("Initializing ByteTrack tracker")
            self.tracker = ByteTrack(
                track_buffer=self.track_buffer,
                frame_rate=15,
            )
            logger.info("ByteTrack tracker initialized successfully")
        except ImportError:
            logger.error("supervision package not installed. Run: pip install supervision")
            raise

    def _create_detections(self, detections: List[dict]):
        """Convert detection payloads to supervision Detections."""
        try:
            from supervision import Detections  # pylint: disable=import-outside-toplevel
        except ImportError:
            logger.error("supervision package not available")
            return None

        if not detections:
            return Detections.empty()

        xyxy = []
        confidence = []
        class_id = []

        for det in detections:
            xyxy.append([det["bbox"]["x1"], det["bbox"]["y1"], det["bbox"]["x2"], det["bbox"]["y2"]])
            confidence.append(float(det["confidence"]))
            class_id.append(int(det["class_id"]))

        return Detections(
            xyxy=np.array(xyxy, dtype=np.float32),
            confidence=np.array(confidence, dtype=np.float32),
            class_id=np.array(class_id, dtype=np.int32),
        )

    def _run_tracker(self, sv_detections):
        """Run ByteTrack while tolerating minor API differences across versions."""
        if self.tracker is None:
            self._initialize_tracker()

        try:
            return self.tracker.update_with_detections(sv_detections)
        except TypeError:
            # Older versions may require keyword name.
            return self.tracker.update_with_detections(detections=sv_detections)

    def _to_tracked_objects(self, tracked_detections, raw_detections: List[dict], frame_id: int) -> List[dict]:
        """Merge tracker IDs back into detection payloads."""
        tracked_objects: List[dict] = []

        if tracked_detections is None or len(tracked_detections) == 0:
            return tracked_objects

        tracker_ids = getattr(tracked_detections, "tracker_id", None)
        xyxy = tracked_detections.xyxy
        conf = tracked_detections.confidence
        class_ids = tracked_detections.class_id

        for idx in range(len(tracked_detections)):
            x1, y1, x2, y2 = xyxy[idx].tolist()
            confidence = float(conf[idx]) if conf is not None else 0.0
            class_id = int(class_ids[idx]) if class_ids is not None else -1
            class_name = next(
                (det["class_name"] for det in raw_detections if int(det["class_id"]) == class_id),
                "unknown",
            )

            tracker_id_value = None
            if tracker_ids is not None and idx < len(tracker_ids):
                tracker_id_value = tracker_ids[idx]

            if tracker_id_value is None:
                track_id = f"track_{frame_id}_{idx}"
            else:
                track_id = str(int(tracker_id_value))

            centroid = {"x": int((x1 + x2) / 2), "y": int((y1 + y2) / 2)}
            tracked_objects.append(
                {
                    "track_id": track_id,
                    "frame_id": frame_id,
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": confidence,
                    "bbox": {
                        "x1": int(x1),
                        "y1": int(y1),
                        "x2": int(x2),
                        "y2": int(y2),
                        "width": int(x2 - x1),
                        "height": int(y2 - y1),
                    },
                    "centroid": centroid,
                }
            )

        return tracked_objects

    def _update_track_state(self, tracked_objects: List[dict], frame_id: int):
        """Update active track lifecycle and remove stale tracks."""
        seen_ids = set()

        for obj in tracked_objects:
            track_id = obj["track_id"]
            seen_ids.add(track_id)

            if track_id in self.active_tracks:
                state = self.active_tracks[track_id]
                state.last_centroid = obj["centroid"]
                state.last_seen_frame = frame_id
                state.hit_count += 1
                state.miss_count = 0
                state.history.append(obj["centroid"])
                if len(state.history) > self.track_buffer:
                    state.history = state.history[-self.track_buffer :]
            else:
                self.active_tracks[track_id] = TrackState(
                    track_id=track_id,
                    class_name=obj["class_name"],
                    last_centroid=obj["centroid"],
                    last_seen_frame=frame_id,
                    history=[obj["centroid"]],
                )

        # Increment miss count and remove stale tracks.
        stale_ids: List[str] = []
        for track_id, state in self.active_tracks.items():
            if track_id not in seen_ids:
                state.miss_count += 1
                if state.miss_count > self.track_buffer:
                    stale_ids.append(track_id)

        for track_id in stale_ids:
            self.active_tracks.pop(track_id, None)

    def update(self, detections: List[dict], frame_id: int) -> List[dict]:
        """Update tracker with detections and return tracked objects."""
        try:
            sv_detections = self._create_detections(detections)
            tracked_detections = self._run_tracker(sv_detections)
            tracked_objects = self._to_tracked_objects(tracked_detections, detections, frame_id)
            self._update_track_state(tracked_objects, frame_id)

            logger.debug(
                f"Frame {frame_id}: detections={len(detections)} tracked={len(tracked_objects)} "
                f"active_tracks={len(self.active_tracks)}"
            )
            return tracked_objects
        except Exception as e:
            logger.error(f"Error during tracking: {e}")
            return []

    def get_tracking_metrics(self) -> Dict[str, int]:
        """Basic consistency metrics for operational monitoring."""
        return {
            "active_tracks": len(self.active_tracks),
            "total_track_hits": sum(track.hit_count for track in self.active_tracks.values()),
        }

    def reset(self):
        """Reset tracker state."""
        if self.tracker:
            self.tracker.reset()
        self.active_tracks.clear()
        logger.info("Tracker reset")
