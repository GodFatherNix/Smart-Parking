from unittest.mock import patch

import numpy as np

from app.services.detector import VehicleDetector


def test_dark_frame_uses_relaxed_confidence_threshold():
    with patch.object(VehicleDetector, "_initialize_model", lambda self: None):
        detector = VehicleDetector(
            model_path="dummy.pt",
            confidence_threshold=0.5,
            dark_frame_brightness_threshold=60,
            low_light_confidence_factor=0.8,
            low_light_min_confidence=0.25,
        )

    dark_frame = np.zeros((32, 32, 3), dtype=np.uint8)
    effective = detector._effective_confidence_threshold(dark_frame)
    assert effective == 0.4


def test_bright_frame_keeps_base_confidence_threshold():
    with patch.object(VehicleDetector, "_initialize_model", lambda self: None):
        detector = VehicleDetector(
            model_path="dummy.pt",
            confidence_threshold=0.5,
            dark_frame_brightness_threshold=60,
            low_light_confidence_factor=0.8,
            low_light_min_confidence=0.25,
        )

    bright_frame = np.full((32, 32, 3), 220, dtype=np.uint8)
    effective = detector._effective_confidence_threshold(bright_frame)
    assert effective == 0.5
