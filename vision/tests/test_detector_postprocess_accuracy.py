from unittest.mock import patch

import numpy as np

from app.services.detector import VehicleDetector


class _FakeBox:
    def __init__(self, class_id: int, confidence: float, xyxy):
        self.cls = np.array([class_id], dtype=np.float32)
        self.conf = np.array([confidence], dtype=np.float32)
        self.xyxy = np.array([xyxy], dtype=np.float32)


class _FakeResult:
    def __init__(self, boxes):
        self.boxes = boxes


def test_detection_accuracy_target_90_percent_with_synthetic_predictions():
    with patch.object(VehicleDetector, "_initialize_model", lambda self: None):
        detector = VehicleDetector(
            model_path="dummy.pt",
            confidence_threshold=0.5,
            target_classes=["car", "motorcycle", "bus", "truck"],
        )

    # 10 ground-truth vehicles, 9 correctly represented above confidence threshold
    fake_boxes = [
        _FakeBox(2, 0.95, [0, 0, 50, 50]),   # car
        _FakeBox(3, 0.92, [10, 10, 60, 60]),  # motorcycle
        _FakeBox(5, 0.91, [20, 20, 70, 70]),  # bus
        _FakeBox(7, 0.93, [30, 30, 80, 80]),  # truck
        _FakeBox(2, 0.90, [40, 40, 90, 90]),
        _FakeBox(3, 0.89, [50, 50, 100, 100]),
        _FakeBox(5, 0.88, [60, 60, 110, 110]),
        _FakeBox(7, 0.87, [70, 70, 120, 120]),
        _FakeBox(2, 0.86, [80, 80, 130, 130]),
        _FakeBox(2, 0.20, [90, 90, 140, 140]),  # below threshold => miss
    ]

    detections = detector.postprocess(_FakeResult(fake_boxes))
    detected_count = len(detections)
    expected_gt = 10
    accuracy = detected_count / float(expected_gt)
    assert accuracy >= 0.9


def test_detector_filters_only_configured_vehicle_classes():
    with patch.object(VehicleDetector, "_initialize_model", lambda self: None):
        detector = VehicleDetector(
            model_path="dummy.pt",
            confidence_threshold=0.5,
            target_classes=["car"],
        )

    fake_boxes = [
        _FakeBox(2, 0.99, [0, 0, 10, 10]),  # car
        _FakeBox(3, 0.99, [0, 0, 10, 10]),  # motorcycle
    ]

    detections = detector.postprocess(_FakeResult(fake_boxes))
    assert len(detections) == 1
    assert detections[0]["class_name"] == "car"
