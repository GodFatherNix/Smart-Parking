"""Database operations and queries"""

import logging
from collections import defaultdict
from threading import Lock
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from app.core.database import SessionLocal
from app.models.floor import Floor
from app.models.event import Event, Direction, VehicleType

logger = logging.getLogger(__name__)


class FloorOperations:
    """Operations on Floor model"""
    
    @staticmethod
    def get_all_active_floors() -> List[Floor]:
        """Get all active floors"""
        session = SessionLocal()
        try:
            return session.query(Floor).filter(Floor.is_active == True).all()
        finally:
            session.close()
    
    @staticmethod
    def get_floor_by_id(floor_id: int) -> Optional[Floor]:
        """Get floor by ID"""
        session = SessionLocal()
        try:
            return session.query(Floor).filter(Floor.id == floor_id).first()
        finally:
            session.close()
    
    @staticmethod
    def get_floor_by_name(name: str) -> Optional[Floor]:
        """Get floor by name"""
        session = SessionLocal()
        try:
            return session.query(Floor).filter(Floor.name == name).first()
        finally:
            session.close()
    
    @staticmethod
    def get_recommended_floor() -> Optional[Floor]:
        """Get floor with most available slots"""
        session = SessionLocal()
        try:
            floor = session.query(Floor).filter(
                Floor.is_active == True
            ).order_by(
                (Floor.total_slots - Floor.current_vehicles).desc()
            ).first()
            
            if floor:
                logger.info(f"Recommended floor: {floor.name} with {floor.available_slots} available slots")
            
            return floor
        finally:
            session.close()
    
    @staticmethod
    def update_vehicle_count(floor_id: int, direction: Direction):
        """Update vehicle count on floor"""
        session = SessionLocal()
        try:
            floor = session.query(Floor).filter(Floor.id == floor_id).first()
            
            if not floor:
                logger.warning(f"Floor {floor_id} not found")
                return None
            
            if direction == Direction.entry:
                if floor.current_vehicles < floor.total_slots:
                    floor.current_vehicles += 1
                    logger.info(f"Vehicle entry at {floor.name}: {floor.current_vehicles}/{floor.total_slots}")
                else:
                    logger.warning(f"Floor {floor.name} is full, cannot add vehicle")
            
            elif direction == Direction.exit:
                if floor.current_vehicles > 0:
                    floor.current_vehicles -= 1
                    logger.info(f"Vehicle exit at {floor.name}: {floor.current_vehicles}/{floor.total_slots}")
                else:
                    logger.warning(f"Floor {floor.name} is empty, cannot remove vehicle")
            
            session.commit()
            return floor
        
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating vehicle count: {e}")
            raise
        finally:
            session.close()


class EventOperations:
    """Operations on Event model"""

    _lock_registry_guard = Lock()
    _event_locks = defaultdict(Lock)

    @classmethod
    def _get_event_lock(cls, key: tuple[str, str, int, str]) -> Lock:
        with cls._lock_registry_guard:
            return cls._event_locks[key]
    
    @staticmethod
    def record_event(
        camera_id: str,
        floor_id: int,
        track_id: str,
        vehicle_type: VehicleType | str,
        direction: Direction | str,
        confidence: float = 0.8,
        timestamp: Optional[datetime] = None,
        idempotency_window_seconds: int = 5,
    ) -> Tuple[Event, Floor, bool]:
        """
        Record a parking event with atomic floor count update.

        Returns (event, floor, is_duplicate).
        """
        session = SessionLocal()
        try:
            event_timestamp = timestamp or datetime.utcnow()
            event_direction = Direction(direction) if isinstance(direction, str) else direction
            event_vehicle_type = VehicleType(vehicle_type) if isinstance(vehicle_type, str) else vehicle_type
            lock_key = (camera_id, track_id, floor_id, event_direction.value)
            operation_lock = EventOperations._get_event_lock(lock_key)

            with operation_lock:
                with session.begin():
                    floor = session.query(Floor).filter(Floor.id == floor_id).first()
                    if not floor:
                        raise ValueError(f"Floor {floor_id} not found")

                    window_delta = timedelta(seconds=max(0, idempotency_window_seconds))
                    window_start = event_timestamp - window_delta
                    window_end = event_timestamp + window_delta

                    # Idempotency check within a small timestamp window to tolerate retry drift.
                    existing = session.query(Event).filter(
                        and_(
                            Event.camera_id == camera_id,
                            Event.track_id == track_id,
                            Event.floor_id == floor_id,
                            Event.direction == event_direction,
                            Event.timestamp >= window_start,
                            Event.timestamp <= window_end,
                        )
                    ).order_by(Event.timestamp.desc()).first()

                    if existing:
                        logger.warning(
                            f"Duplicate event detected: {track_id} ({event_direction.value}) "
                            f"between {window_start.isoformat()} and {window_end.isoformat()}"
                        )
                        session.refresh(floor)
                        return existing, floor, True

                    # Atomic update protects count accuracy under concurrent requests.
                    if event_direction == Direction.entry:
                        updated = session.query(Floor).filter(
                            Floor.id == floor_id,
                            Floor.current_vehicles < Floor.total_slots
                        ).update(
                            {Floor.current_vehicles: Floor.current_vehicles + 1},
                            synchronize_session=False,
                        )
                        if updated == 0:
                            raise ValueError(f"Floor {floor_id} is full")
                    elif event_direction == Direction.exit:
                        updated = session.query(Floor).filter(
                            Floor.id == floor_id,
                            Floor.current_vehicles > 0
                        ).update(
                            {Floor.current_vehicles: Floor.current_vehicles - 1},
                            synchronize_session=False,
                        )
                        if updated == 0:
                            raise ValueError(f"Floor {floor_id} is empty")

                    event = Event(
                        camera_id=camera_id,
                        floor_id=floor_id,
                        track_id=track_id,
                        vehicle_type=event_vehicle_type,
                        direction=event_direction,
                        confidence=confidence,
                        timestamp=event_timestamp,
                    )

                    session.add(event)
                    session.flush()

                    floor = session.query(Floor).filter(Floor.id == floor_id).first()
                    session.refresh(event)
                    session.refresh(floor)

            logger.info(f"Event recorded: {track_id} ({event_direction.value}) at {camera_id}")
            return event, floor, False

        except IntegrityError:
            session.rollback()
            end_time = event_timestamp + timedelta(seconds=max(0, idempotency_window_seconds))
            start_time = event_timestamp - timedelta(seconds=max(0, idempotency_window_seconds))
            existing = session.query(Event).filter(
                and_(
                    Event.camera_id == camera_id,
                    Event.track_id == track_id,
                    Event.floor_id == floor_id,
                    Event.direction == event_direction,
                    Event.timestamp >= start_time,
                    Event.timestamp <= end_time,
                )
            ).order_by(Event.timestamp.desc()).first()
            floor = session.query(Floor).filter(Floor.id == floor_id).first()
            if existing and floor:
                logger.warning(f"Duplicate event detected by integrity constraint: {track_id}")
                return existing, floor, True
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error recording event: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_events_by_floor(floor_id: int, limit: int = 100) -> List[Event]:
        """Get recent events for a floor"""
        session = SessionLocal()
        try:
            return session.query(Event).filter(
                Event.floor_id == floor_id
            ).order_by(
                Event.timestamp.desc()
            ).limit(limit).all()
        finally:
            session.close()
    
    @staticmethod
    def get_events_by_time_range(
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        floor_id: Optional[int] = None
    ) -> List[Event]:
        """Get events within time range"""
        session = SessionLocal()
        try:
            if end_time is None:
                end_time = datetime.utcnow()
            if start_time is None:
                start_time = end_time - timedelta(hours=24)

            query = session.query(Event).filter(
                and_(
                    Event.timestamp >= start_time,
                    Event.timestamp <= end_time,
                )
            )
            
            if floor_id:
                query = query.filter(Event.floor_id == floor_id)
            
            return query.order_by(Event.timestamp.desc()).all()
        finally:
            session.close()

    @staticmethod
    def get_filtered_events(
        hours: int = 24,
        floor_id: Optional[int] = None,
        vehicle_type: Optional[VehicleType | str] = None,
        direction: Optional[Direction | str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[Event], int, int]:
        """Get filtered and paginated events from the last N hours."""
        session = SessionLocal()
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)

            base_query = session.query(Event).filter(
                and_(
                    Event.timestamp >= start_time,
                    Event.timestamp <= end_time,
                )
            )
            total_count = base_query.count()

            filtered_query = base_query

            if floor_id is not None:
                filtered_query = filtered_query.filter(Event.floor_id == floor_id)
            if vehicle_type is not None:
                normalized_vehicle_type = (
                    VehicleType(vehicle_type) if isinstance(vehicle_type, str) else vehicle_type
                )
                filtered_query = filtered_query.filter(Event.vehicle_type == normalized_vehicle_type)
            if direction is not None:
                normalized_direction = Direction(direction) if isinstance(direction, str) else direction
                filtered_query = filtered_query.filter(Event.direction == normalized_direction)

            filtered_count = filtered_query.count()
            events = filtered_query.order_by(Event.timestamp.desc()).offset(offset).limit(limit).all()

            return events, total_count, filtered_count
        finally:
            session.close()
    
    @staticmethod
    def get_event_statistics(hours: int = 24) -> dict:
        """Get event statistics for last N hours"""
        session = SessionLocal()
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            events = session.query(Event).filter(
                Event.timestamp >= start_time
            ).all()
            
            stats = {
                "total_events": len(events),
                "entries": len([e for e in events if e.direction == Direction.entry]),
                "exits": len([e for e in events if e.direction == Direction.exit]),
                "by_vehicle_type": {},
                "by_floor": {},
            }
            
            # Group by vehicle type
            for vtype in VehicleType:
                count = len([e for e in events if e.vehicle_type == vtype])
                stats["by_vehicle_type"][vtype.value] = count
            
            # Group by floor
            floors = session.query(Floor).all()
            for floor in floors:
                count = len([e for e in events if e.floor_id == floor.id])
                stats["by_floor"][floor.name] = count
            
            return stats
        
        finally:
            session.close()
    
    @staticmethod
    def cleanup_old_events(days: int = 30):
        """Delete events older than N days"""
        session = SessionLocal()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            deleted = session.query(Event).filter(
                Event.timestamp < cutoff_date
            ).delete()
            
            session.commit()
            logger.info(f"Deleted {deleted} events older than {days} days")
            
            return deleted
        
        except Exception as e:
            session.rollback()
            logger.error(f"Error cleaning up events: {e}")
            raise
        finally:
            session.close()


if __name__ == "__main__":
    # Initialize logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Test operations
    print("\n=== Testing Database Operations ===")
    
    floors = FloorOperations.get_all_active_floors()
    print(f"\nActive Floors: {len(floors)}")
    for floor in floors:
        print(f"  - {floor.name}: {floor.available_slots} available")
    
    recommended = FloorOperations.get_recommended_floor()
    print(f"\nRecommended Floor: {recommended.name if recommended else 'None'}")
    
    stats = EventOperations.get_event_statistics(hours=24)
    print(f"\nEvent Statistics (last 24 hours):")
    print(f"  Total: {stats['total_events']}")
    print(f"  Entries: {stats['entries']}")
    print(f"  Exits: {stats['exits']}")
