from app.services.event_handler import EventHandler


def _tracked_obj(track_id: str, x: int, y: int, width: int = 50, height: int = 40):
    return {
        "track_id": track_id,
        "centroid": {"x": x, "y": y},
        "class_name": "car",
        "confidence": 0.9,
        "bbox": {"width": width, "height": height},
    }


def test_short_occlusion_keeps_crossing_continuity():
    handler = EventHandler(
        line_points=[(0, 360), (1280, 360)],
        direction_mapping={"up": "entry", "down": "exit"},
        occlusion_tolerance_frames=5,
    )

    assert handler.process_frame([_tracked_obj("t1", 100, 350)], frame_id=1) == []
    assert handler.process_frame([], frame_id=2) == []
    events = handler.process_frame([_tracked_obj("t1", 100, 372)], frame_id=3)
    assert len(events) == 1
    assert events[0]["direction"] == "exit"


def test_long_occlusion_does_not_emit_stale_crossing():
    handler = EventHandler(
        line_points=[(0, 360), (1280, 360)],
        occlusion_tolerance_frames=3,
    )

    assert handler.process_frame([_tracked_obj("t2", 120, 350)], frame_id=1) == []
    events = handler.process_frame([_tracked_obj("t2", 120, 380)], frame_id=10)
    assert events == []


def test_reversal_is_suppressed_within_reversal_window():
    handler = EventHandler(
        line_points=[(0, 360), (1280, 360)],
        direction_mapping={"up": "entry", "down": "exit"},
        duplicate_cooldown_frames=1,
        reversal_suppression_frames=10,
    )

    handler.process_frame([_tracked_obj("t3", 140, 350)], frame_id=1)
    first_cross = handler.process_frame([_tracked_obj("t3", 140, 372)], frame_id=2)
    assert len(first_cross) == 1
    assert first_cross[0]["direction"] == "exit"

    # Rapid backward movement would normally be "entry", but should be suppressed.
    backward = handler.process_frame([_tracked_obj("t3", 140, 340)], frame_id=3)
    assert backward == []


def test_various_vehicle_sizes_and_speeds_are_handled():
    handler = EventHandler(
        line_points=[(0, 360), (1280, 360)],
        area_threshold=100,
        direction_mapping={"up": "entry", "down": "exit"},
    )

    # Small vehicle at threshold area and large vehicle with fast movement.
    handler.process_frame([_tracked_obj("small", 200, 350, width=10, height=10)], frame_id=1)
    small_events = handler.process_frame([_tracked_obj("small", 200, 365, width=10, height=10)], frame_id=2)

    handler.process_frame([_tracked_obj("large", 300, 280, width=160, height=120)], frame_id=3)
    large_events = handler.process_frame([_tracked_obj("large", 300, 420, width=160, height=120)], frame_id=4)

    assert len(small_events) == 1
    assert len(large_events) == 1
