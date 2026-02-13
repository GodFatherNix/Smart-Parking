"""Database seeding script - Initial data population"""

import logging
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.models.floor import Floor
from app.models.event import Event, VehicleType, Direction

logger = logging.getLogger(__name__)


def seed_floors():
    """Seed initial floor data"""
    session = SessionLocal()
    
    try:
        # Check if floors already exist
        existing_floors = session.query(Floor).count()
        if existing_floors > 0:
            logger.info(f"Database already contains {existing_floors} floors, skipping seed")
            return
        
        floors_data = [
            {
                "name": "Ground Floor",
                "description": "Main parking level at ground floor - Main entry/exit point",
                "total_slots": 50,
                "is_active": True,
            },
            {
                "name": "First Floor",
                "description": "First level above ground - Accessible via ramp",
                "total_slots": 45,
                "is_active": True,
            },
            {
                "name": "Second Floor",
                "description": "Second level above ground - Premium spot area",
                "total_slots": 40,
                "is_active": True,
            },
            {
                "name": "Basement Level 1",
                "description": "Underground level 1 - Cool storage area",
                "total_slots": 60,
                "is_active": False,  # Inactive for now
            },
        ]
        
        for floor_data in floors_data:
            floor = Floor(**floor_data)
            session.add(floor)
            logger.info(f"Created floor: {floor.name} ({floor.total_slots} slots)")
        
        session.commit()
        logger.info(f"Successfully seeded {len(floors_data)} floors")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error seeding floors: {e}")
        raise
    finally:
        session.close()


def seed_sample_events():
    """Seed sample event data for testing"""
    session = SessionLocal()
    
    try:
        # Check if events already exist
        existing_events = session.query(Event).count()
        if existing_events > 0:
            logger.info(f"Database already contains {existing_events} events, skipping seed")
            return
        
        # Get floors
        floors = session.query(Floor).filter(Floor.is_active == True).all()
        if not floors:
            logger.warning("No active floors found, cannot seed events")
            return
        
        # Create sample events
        base_time = datetime.utcnow() - timedelta(hours=2)
        events_data = []
        
        for i in range(15):
            floor = floors[i % len(floors)]
            vehicle_types = [VehicleType.car, VehicleType.motorcycle, VehicleType.bus, VehicleType.truck]
            
            event = Event(
                camera_id=f"cam_00{(i % 3) + 1}",
                floor_id=floor.id,
                track_id=f"track_{i:05d}",
                vehicle_type=vehicle_types[i % len(vehicle_types)],
                direction=Direction.entry if i % 2 == 0 else Direction.exit,
                confidence=0.85 + (i % 10) * 0.01,
                timestamp=base_time + timedelta(minutes=i * 10),
            )
            session.add(event)
            events_data.append(event)
            logger.debug(f"Created event: {event.track_id} ({event.direction})")
        
        session.commit()
        logger.info(f"Successfully seeded {len(events_data)} sample events")
        
        # Update floor vehicle counts
        for floor in floors:
            floor_events = session.query(Event).filter(Event.floor_id == floor.id).all()
            entries = sum(1 for e in floor_events if e.direction == Direction.entry)
            exits = sum(1 for e in floor_events if e.direction == Direction.exit)
            current_vehicles = max(0, entries - exits)
            floor.current_vehicles = min(current_vehicles, floor.total_slots)
            logger.info(f"Updated {floor.name}: {entries} entries, {exits} exits, {current_vehicles} current vehicles")
        
        session.commit()
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error seeding events: {e}")
        raise
    finally:
        session.close()


def reset_database_seed():
    """Reset database and reseed with fresh data"""
    try:
        from app.core.migrations import reinitialize_database
        logger.warning("RESETTING DATABASE AND RESEEDING...")
        reinitialize_database()
        
        seed_floors()
        seed_sample_events()
        
        logger.info("Database reset and reseeded successfully")
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise


def display_seed_summary():
    """Display summary of seeded data"""
    session = SessionLocal()
    
    try:
        print("\n=== Database Seed Summary ===")
        
        floors = session.query(Floor).all()
        print(f"\nFloors: {len(floors)}")
        for floor in floors:
            print(f"  - {floor.name}: {floor.current_vehicles}/{floor.total_slots} vehicles "
                  f"({floor.occupancy_percentage:.1f}% occupied)")
        
        events = session.query(Event).all()
        print(f"\nTotal Events: {len(events)}")
        
        # Stats by direction
        entries = len([e for e in events if e.direction == Direction.entry])
        exits = len([e for e in events if e.direction == Direction.exit])
        print(f"  - Entries: {entries}")
        print(f"  - Exits: {exits}")
        
        # Stats by vehicle type
        print(f"\nVehicles by type:")
        for vtype in VehicleType:
            count = len([e for e in events if e.vehicle_type == vtype])
            print(f"  - {vtype.value}: {count}")
        
        print()
        
    finally:
        session.close()


if __name__ == "__main__":
    # Initialize logging for standalone execution
    import sys
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )
    
    # Seed database
    seed_floors()
    seed_sample_events()
    display_seed_summary()
