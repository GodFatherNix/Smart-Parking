from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


def _reset_floor_state(app_module, floor_id: int, *, total_slots: int, current_vehicles: int):
    from app.core.database import SessionLocal
    from app.models.floor import Floor

    session = SessionLocal()
    try:
        floor = session.query(Floor).filter(Floor.id == floor_id).first()
        floor.total_slots = total_slots
        floor.current_vehicles = current_vehicles
        floor.is_active = True
        session.commit()
    finally:
        session.close()


def test_record_event_updates_vehicle_counts_atomically(app_module):
    from app.core.database_ops import EventOperations

    _reset_floor_state(app_module, 1, total_slots=20, current_vehicles=5)

    entry_event, entry_floor, entry_duplicate = EventOperations.record_event(
        camera_id="cam_db_001",
        floor_id=1,
        track_id="track_db_001",
        vehicle_type="car",
        direction="entry",
        confidence=0.95,
    )

    exit_event, exit_floor, exit_duplicate = EventOperations.record_event(
        camera_id="cam_db_001",
        floor_id=1,
        track_id="track_db_002",
        vehicle_type="car",
        direction="exit",
        confidence=0.95,
    )

    assert entry_event.id > 0
    assert exit_event.id > 0
    assert entry_duplicate is False
    assert exit_duplicate is False
    assert entry_floor.current_vehicles == 6
    assert exit_floor.current_vehicles == 5


def test_duplicate_event_detection_logic(app_module):
    from app.core.database_ops import EventOperations

    _reset_floor_state(app_module, 1, total_slots=50, current_vehicles=3)
    fixed_ts = datetime.utcnow()

    first_event, first_floor, first_duplicate = EventOperations.record_event(
        camera_id="cam_dup_001",
        floor_id=1,
        track_id="track_dup_001",
        vehicle_type="car",
        direction="entry",
        confidence=0.88,
        timestamp=fixed_ts,
    )

    second_event, second_floor, second_duplicate = EventOperations.record_event(
        camera_id="cam_dup_001",
        floor_id=1,
        track_id="track_dup_001",
        vehicle_type="car",
        direction="entry",
        confidence=0.88,
        timestamp=fixed_ts,
    )

    assert first_duplicate is False
    assert second_duplicate is True
    assert first_event.id == second_event.id
    assert first_floor.current_vehicles == 4
    assert second_floor.current_vehicles == 4


def test_concurrent_duplicate_record_event_is_thread_safe(app_module):
    from app.core.database import SessionLocal
    from app.core.database_ops import EventOperations
    from app.models.event import Event

    _reset_floor_state(app_module, 1, total_slots=100, current_vehicles=0)
    fixed_ts = datetime.utcnow()

    def submit():
        _, floor, is_duplicate = EventOperations.record_event(
            camera_id="cam_conc_001",
            floor_id=1,
            track_id="track_conc_dup_001",
            vehicle_type="car",
            direction="entry",
            confidence=0.91,
            timestamp=fixed_ts,
        )
        return floor.current_vehicles, is_duplicate

    futures = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        for _ in range(20):
            futures.append(executor.submit(submit))

    results = [future.result() for future in as_completed(futures)]
    duplicate_count = sum(1 for _, is_duplicate in results if is_duplicate)

    session = SessionLocal()
    try:
        event_count = session.query(Event).filter(Event.track_id == "track_conc_dup_001").count()
    finally:
        session.close()

    assert duplicate_count >= 19
    assert event_count == 1
