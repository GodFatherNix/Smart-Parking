"""Vehicle detection service using YOLOv8."""

import logging
from typing import Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class VehicleDetector:
    """Vehicle detection with explicit pre-process -> infer -> post-process flow."""

    # COCO class IDs
    CLASS_NAME_BY_ID: Dict[int, str] = {
        2: "car",
        3: "motorcycle",
        5: "bus",
        7: "truck",
    }

    def __init__(
        self,
        model_path: str,
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        device: str = "cpu",
        target_classes: Optional[List[str]] = None,
        dark_frame_brightness_threshold: float = 60.0,
        low_light_confidence_factor: float = 0.8,
        low_light_min_confidence: float = 0.25,
        low_light_enhance_frame: bool = False,
    ):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        self.model = None
        self.target_classes = set(item.lower() for item in (target_classes or self.CLASS_NAME_BY_ID.values()))
        self.dark_frame_brightness_threshold = dark_frame_brightness_threshold
        self.low_light_confidence_factor = low_light_confidence_factor
        self.low_light_min_confidence = low_light_min_confidence
        self.low_light_enhance_frame = low_light_enhance_frame
        self._initialize_model()

    def _initialize_model(self):
        """Load YOLO model."""
        try:
            from ultralytics import YOLO  # pylint: disable=import-outside-toplevel

            logger.info(f"Loading YOLOv8 model from {self.model_path}")
            self.model = YOLO(self.model_path)
            self.model.to(self.device)
            logger.info(f"Model loaded successfully on device: {self.device}")
            logger.info(f"Target detection classes: {sorted(self.target_classes)}")
        except ImportError:
            logger.error("ultralytics package not installed. Run: pip install ultralytics")
            raise
        except FileNotFoundError:
            logger.error(f"Model file not found: {self.model_path}")
            raise

    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """Pre-process input frame before inference."""
        if frame is None:
            raise ValueError("Input frame is None")
        if len(frame.shape) != 3:
            raise ValueError("Input frame must have shape [H, W, C]")
        if self.low_light_enhance_frame and self._estimate_brightness(frame) < self.dark_frame_brightness_threshold:
            frame = self._enhance_low_light(frame)
        return frame

    def infer(self, frame: np.ndarray, confidence_threshold: Optional[float] = None):
        """Run model inference."""
        if self.model is None:
            self._initialize_model()
        effective_conf = confidence_threshold if confidence_threshold is not None else self.confidence_threshold
        return self.model(
            frame,
            conf=effective_conf,
            iou=self.iou_threshold,
            verbose=False,
        )

    def postprocess(self, result, min_confidence: Optional[float] = None) -> List[dict]:
        """Convert model output into normalized detection payloads."""
        detections: List[dict] = []
        if result.boxes is None:
            return detections
        conf_threshold = min_confidence if min_confidence is not None else self.confidence_threshold

        for box in result.boxes:
            class_id = int(box.cls[0])
            class_name = self.CLASS_NAME_BY_ID.get(class_id)
            if class_name is None or class_name.lower() not in self.target_classes:
                continue

            confidence = float(box.conf[0])
            if confidence < conf_threshold:
                continue

            x1, y1, x2, y2 = box.xyxy[0].tolist()
            detections.append(
                {
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
                    "centroid": {
                        "x": int((x1 + x2) / 2),
                        "y": int((y1 + y2) / 2),
                    },
                }
            )

        return detections

    def detect(self, frame: np.ndarray) -> List[dict]:
        """Full detection pipeline: pre-process, infer, post-process."""
        try:
            processed = self.preprocess(frame)
            effective_conf = self._effective_confidence_threshold(processed)
            results = self.infer(processed, confidence_threshold=effective_conf)
            detections = self.postprocess(results[0], min_confidence=effective_conf)
            logger.debug(f"Detected {len(detections)} vehicles in frame")
            return detections
        except Exception as e:
            logger.error(f"Error during detection: {e}")
            return []

    def _effective_confidence_threshold(self, frame: np.ndarray) -> float:
        brightness = self._estimate_brightness(frame)
        if brightness < self.dark_frame_brightness_threshold:
            return max(
                self.low_light_min_confidence,
                self.confidence_threshold * self.low_light_confidence_factor,
            )
        return self.confidence_threshold

    @staticmethod
    def _estimate_brightness(frame: np.ndarray) -> float:
        return float(np.mean(frame))

    @staticmethod
    def _enhance_low_light(frame: np.ndarray) -> np.ndarray:
        """Best-effort low-light enhancement; no-op if OpenCV is unavailable."""
        try:
            import cv2  # pylint: disable=import-outside-toplevel
        except ImportError:
            return frame

        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        y_channel, cr_channel, cb_channel = cv2.split(ycrcb)
        equalized_y = cv2.equalizeHist(y_channel)
        merged = cv2.merge((equalized_y, cr_channel, cb_channel))
        return cv2.cvtColor(merged, cv2.COLOR_YCrCb2BGR)

    def visualize_detections(self, frame: np.ndarray, detections: List[dict]) -> np.ndarray:
        """Draw bounding boxes and labels on frame for debugging/monitoring."""
        try:
            import cv2  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise RuntimeError("opencv-python is required for visualization") from exc

        annotated = frame.copy()
        for det in detections:
            x1 = det["bbox"]["x1"]
            y1 = det["bbox"]["y1"]
            x2 = det["bbox"]["x2"]
            y2 = det["bbox"]["y2"]
            label = f"{det['class_name']} {det['confidence']:.2f}"

            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 220, 0), 2)
            cv2.putText(
                annotated,
                label,
                (x1, max(20, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 220, 0),
                2,
                cv2.LINE_AA,
            )

        return annotated

    def warm_up(self, frame_width: int = 1280, frame_height: int = 720):
        """Warm up model with dummy inference."""
        try:
            if self.model is None:
                self._initialize_model()
            dummy_frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
            _ = self.infer(dummy_frame)
            logger.info("Model warm-up completed")
        except Exception as e:
            logger.warning(f"Model warm-up failed: {e}")
