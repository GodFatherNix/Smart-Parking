from pathlib import Path

import pytest

from app.services.video_source import FrameRateRegulator, VideoSource, VideoSourceConfig


def test_sample_mp4_smoke_read():
    try:
        import cv2  # noqa: F401
    except ImportError:
        pytest.skip("opencv-python not installed in environment")

    sample = Path("data/sample_video.mp4")
    if not sample.exists():
        pytest.skip("Sample MP4 not found at vision/data/sample_video.mp4")

    source = VideoSource(
        VideoSourceConfig(
            source=str(sample),
            source_type="file",
            target_fps=10,
        )
    )
    regulator = FrameRateRegulator(target_fps=10)

    assert source.open() is True
    read_count = 0
    for _ in range(10):
        regulator.tick()
        ok, _frame = source.read_frame()
        if not ok:
            break
        read_count += 1

    source.close()
    assert read_count > 0
