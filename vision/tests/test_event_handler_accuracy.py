from datetime import UTC, datetime

from app.services.event_handler import EventHandler


def _tracked_obj(track_id: str, x: int, y: int, class_name: str = "car"):
    return {
        "track_id": track_id,
        "centroid": {"x": x, "y": y},
        "class_name": class_name,
        "confidence": 0.95,
        "bbox": {"width": 50, "height": 40},
    }


def test_counting_accuracy_target_95_percent():
    handler = EventHandler(
        line_points=[(0, 360), (1280, 360)],
        direction_mapping={"up": "entry", "down": "exit"},
        duplicate_cooldown_frames=5,
    )

    # 20 vehicles, each crosses line once from y=350 -> y=370 (down => exit by mapping)
    expected_events = 20
    generated_events = []
    frame_id = 0

    for vehicle_idx in range(expected_events):
        track_id = f"v_{vehicle_idx}"
        frame_id += 1
        generated_events.extend(handler.process_frame([_tracked_obj(track_id, 100 + vehicle_idx, 350)], frame_id))
        frame_id += 1
        generated_events.extend(handler.process_frame([_tracked_obj(track_id, 100 + vehicle_idx, 370)], frame_id))

    accuracy = len(generated_events) / float(expected_events)
    assert accuracy >= 0.95


def test_single_event_per_crossing_guarantee():
    handler = EventHandler(
        line_points=[(0, 360), (1280, 360)],
        duplicate_cooldown_frames=10,
    )
    track_id = "track_1"

    # First movement crosses the line.
    events_1 = handler.process_frame([_tracked_obj(track_id, 200, 350)], frame_id=1, timestamp=datetime.now(UTC))
    events_2 = handler.process_frame([_tracked_obj(track_id, 200, 370)], frame_id=2, timestamp=datetime.now(UTC))

    # Immediate jitter around line should not create duplicate event in cooldown window.
    events_3 = handler.process_frame([_tracked_obj(track_id, 200, 355)], frame_id=3, timestamp=datetime.now(UTC))
    events_4 = handler.process_frame([_tracked_obj(track_id, 200, 365)], frame_id=4, timestamp=datetime.now(UTC))

    total_events = events_1 + events_2 + events_3 + events_4
    assert len(total_events) == 1
