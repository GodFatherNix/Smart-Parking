# Phase 2 Database Architecture Overview

## Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              (Settings management)
│   │   ├── database.py            (SQLAlchemy setup)
│   │   ├── logging.py             (Logging framework)
│   │   ├── migrations.py      ✨ NEW (Table creation)
│   │   ├── seed.py           ✨ NEW (Data seeding)
│   │   └── database_ops.py   ✨ NEW (Query operations)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── floor.py               (Floor model - ENHANCED)
│   │   └── event.py               (Event model - ENHANCED)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── floor.py               (Floor schemas)
│   │   └── event.py               (Event schemas)
│   └── __init__.py
├── main.py                        (Entry point - UPDATED)
├── requirements.txt
├── .env
└── smartpark.db                   (SQLite database)
```

## Data Flow

### Application Startup

```
1. main.py starts
   ↓
2. Import migration functions
   ↓
3. Check if tables exist
   ├─→ YES: Skip creation
   │
   └─→ NO: Create tables with constraints
       ├─ Floors table
       │  └─ Constraints: UNIQUE(name), CHECK constraints
       │  └─ Indexes: name, updated_at, is_active
       │
       └─ Events table
          └─ Constraints: UNIQUE(camera_id, track_id, direction, timestamp)
          └─ Indexes: camera_id, floor_id, track_id, timestamp
   ↓
4. Seed initial data if needed
   ├─ seed_floors()
   │  └─ Create: Ground, First, Second floors
   │
   └─ seed_sample_events()
      └─ Create: 15 sample events
   ↓
5. Log database statistics
   └─ "Floors: 4, Events: 15"
   ↓
6. Application ready
```

### Recording a Parking Event

```
Vision Service
    ↓ POST /events
    ↓ {camera_id, floor_id, track_id, vehicle_type, direction, confidence, timestamp}
    ↓
EventOperations.record_event()
    ↓
Check for duplicate (UNIQUE constraint)
    ├─ FOUND: Return existing event
    │
    └─ NOT FOUND: Insert new event
       ↓
       FloorOperations.update_vehicle_count()
       ├─ If entry: current_vehicles++
       └─ If exit: current_vehicles--
       ↓
       Validate constraints (current_vehicles ≤ total_slots)
       ↓
       Commit to database
```

### Querying Floor Data

```
Frontend / API Client
    ↓ GET /floors
    ↓
FloorOperations.get_all_active_floors()
    ↓
SQLAlchemy Query with index lookup
    ├─ WHERE is_active = true
    └─ ORDER BY (total_slots - current_vehicles) DESC
    ↓
Return Floor objects with calculated properties
    ├─ available_slots = total_slots - current_vehicles
    └─ occupancy_percentage = (current_vehicles / total_slots) * 100
    ↓
Serialize to JSON response
```

## Database Operations Cheat Sheet

### Floor Operations

```python
from app.core.database_ops import FloorOperations

# Get all active floors
floors = FloorOperations.get_all_active_floors()

# Get specific floor
floor = FloorOperations.get_floor_by_id(1)
floor = FloorOperations.get_floor_by_name("Ground Floor")

# Get best floor (most available)
best = FloorOperations.get_recommended_floor()

# Update vehicle count
FloorOperations.update_vehicle_count(floor_id=1, direction=Direction.entry)
```

### Event Operations

```python
from app.core.database_ops import EventOperations
from app.models.event import VehicleType, Direction

# Record a parking event
event = EventOperations.record_event(
    camera_id="cam_001",
    floor_id=1,
    track_id="track_12345",
    vehicle_type=VehicleType.car,
    direction=Direction.entry,
    confidence=0.92
)

# Get recent events for floor
events = EventOperations.get_events_by_floor(floor_id=1, limit=100)

# Get events in time range
events = EventOperations.get_events_by_time_range(
    start_time=datetime.utcnow() - timedelta(hours=24),
    end_time=datetime.utcnow(),
    floor_id=1
)

# Get statistics
stats = EventOperations.get_event_statistics(hours=24)

# Clean up old events
deleted = EventOperations.cleanup_old_events(days=30)
```

## Database Schema Visualization

```
┌─────────────────────────────────────────────────┐
│            FLOORS TABLE                         │
├─────────────────────────────────────────────────┤
│ id (PK)              │                          │
│ name (UNIQUE)        │ Ground Floor            │
│ description          │ Main entry/exit point  │
│ total_slots          │ 50                      │
│ current_vehicles     │ 12                      │
│ is_active            │ true                    │
│ created_at           │ 2026-02-12 10:00:00    │
│ updated_at           │ 2026-02-12 10:30:45    │
└─────────────────────────────────────────────────┘
         │  1                          M  ↓
         └──────────────────────────────→ 
┌─────────────────────────────────────────────────┐
│            EVENTS TABLE                         │
├─────────────────────────────────────────────────┤
│ id (PK)              │ 1001                    │
│ camera_id            │ cam_001 (INDEX)        │
│ floor_id (FK)        │ 1                       │
│ track_id (INDEX)     │ track_a1b2c3            │
│ vehicle_type         │ car                     │
│ direction            │ entry                   │
│ confidence           │ 0.92                    │
│ timestamp (INDEX)    │ 2026-02-12 10:30:45    │
│ created_at           │ 2026-02-12 10:30:45    │
│                                                │
│ UNIQUE (camera_id, track_id, direction, ts)  │
└─────────────────────────────────────────────────┘
```

## Constraints & Indexes

### Floors Table

**Constraints**:
```sql
PRIMARY KEY (id)
UNIQUE (name)
CHECK (total_slots >= 0)
CHECK (current_vehicles >= 0)
CHECK (current_vehicles <= total_slots)
```

**Indexes**:
```sql
INDEX ix_floor_name (name)
INDEX ix_floor_updated_at (updated_at)
INDEX ix_floor_is_active (is_active)
```

### Events Table

**Constraints**:
```sql
PRIMARY KEY (id)
FOREIGN KEY (floor_id) REFERENCES floors(id)
UNIQUE (camera_id, track_id, direction, timestamp)
CHECK (confidence >= 0 AND confidence <= 1)
```

**Indexes**:
```sql
INDEX ix_event_camera_id (camera_id)
INDEX ix_event_floor_id (floor_id)
INDEX ix_event_track_id (track_id)
INDEX ix_event_timestamp (timestamp)
INDEX ix_event_camera_floor_timestamp (camera_id, floor_id, timestamp)
INDEX ix_event_track_direction (track_id, direction)
```

## Migration & Seeding Flow

### initialization on Startup

```
Check database.db exists?
    ├─→ YES: Check if tables exist
    │        ├─→ YES: Load existing data
    │        └─→ NO:  Create tables & seed
    │
    └─→ NO:  Create database
            ├─ Create tables with constraints
            ├─ Seed 4 floors
            └─ Seed 15 sample events
```

### Manual Operations

```
# Create fresh database
from app.core.migrations import create_tables
create_tables()

# Seed data
from app.core.seed import seed_floors, seed_sample_events
seed_floors()
seed_sample_events()

# Reset everything
from app.core.seed import reset_database_seed
reset_database_seed()

# View statistics
from app.core.migrations import get_table_info, get_database_stats
info = get_table_info()
stats = get_database_stats()
```

## Query Examples

### Get Recommended Floor

```python
# Returns floor with most available slots
floor = FloorOperations.get_recommended_floor()

# SQL equivalent:
SELECT * FROM floors
WHERE is_active = true
ORDER BY (total_slots - current_vehicles) DESC
LIMIT 1
```

### Record Parking Entry

```python
EventOperations.record_event(
    camera_id="cam_001",
    floor_id=1,
    track_id="track_abc123",
    vehicle_type=VehicleType.car,
    direction=Direction.entry,
    confidence=0.95
)

# SQL operations:
# 1. Check for duplicate
SELECT * FROM events
WHERE camera_id = 'cam_001'
  AND track_id = 'track_abc123'
  AND direction = 'entry'
  AND timestamp = '2026-02-12 10:30:45'

# 2. If not found, insert
INSERT INTO events (camera_id, floor_id, track_id, vehicle_type, direction, confidence, timestamp)
VALUES ('cam_001', 1, 'track_abc123', 'car', 'entry', 0.95, '2026-02-12 10:30:45')

# 3. Update floor counts
UPDATE floors SET current_vehicles = 13 WHERE id = 1
```

### Get Event Statistics

```python
stats = EventOperations.get_event_statistics(hours=24)

# Returns:
{
    "total_events": 127,
    "entries": 65,
    "exits": 62,
    "by_vehicle_type": {
        "car": 80,
        "motorcycle": 25,
        "bus": 15,
        "truck": 7
    },
    "by_floor": {
        "Ground Floor": 45,
        "First Floor": 42,
        "Second Floor": 40
    }
}
```

## Files Summary

| File | Purpose | Lines | Key Functions |
|------|---------|-------|---|
| migrations.py | Schema management | 120 | create_tables(), check_tables_exist(), get_table_info() |
| seed.py | Data population | 180 | seed_floors(), seed_sample_events(), reset_database_seed() |
| database_ops.py | Query interface | 280 | FloorOperations, EventOperations classes |
| floor.py | Floor model | 45 | Floor ORM model with constraints |
| event.py | Event model | 50 | Event ORM model with idempotency |
| main.py | Integration | 100 | Startup hooks, health check |

---

**Database Architecture Complete ✅**

Ready for Phase 3: API Endpoint Implementation
