from app.services.event_handler import EventHandler


def _obj(track_id: str, x: int, y: int):
    return {
        "track_id": track_id,
        "centroid": {"x": x, "y": y},
        "class_name": "car",
        "confidence": 0.91,
        "bbox": {"width": 50, "height": 40},
    }


def test_multi_camera_simultaneous_processing_independent_state():
    cam_a = EventHandler(camera_id="cam_001", floor_id=1, line_points=[(0, 360), (1280, 360)])
    cam_b = EventHandler(camera_id="cam_002", floor_id=2, line_points=[(0, 300), (1280, 300)])

    events = []

    # Simulate simultaneous frame progression for 2 cameras.
    for frame_id in range(1, 6):
        # cam_a crossing around y=360
        y_a = 350 if frame_id < 3 else 370
        events.extend(cam_a.process_frame([_obj("a_track", 200, y_a)], frame_id))

        # cam_b crossing around y=300
        y_b = 290 if frame_id < 3 else 320
        events.extend(cam_b.process_frame([_obj("b_track", 300, y_b)], frame_id))

    cam_a_events = [e for e in events if e["camera_id"] == "cam_001"]
    cam_b_events = [e for e in events if e["camera_id"] == "cam_002"]

    assert len(cam_a_events) == 1
    assert len(cam_b_events) == 1
    assert cam_a_events[0]["floor_id"] == 1
    assert cam_b_events[0]["floor_id"] == 2
