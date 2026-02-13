from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum,
    UniqueConstraint, Index, Float, CheckConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.core.database import Base


class VehicleType(str, Enum):
    car = "car"
    motorcycle = "motorcycle"
    bus = "bus"
    truck = "truck"


class Direction(str, Enum):
    entry = "entry"
    exit = "exit"


class Event(Base):
    __tablename__ = "events"
    
    # Constraints for idempotency and data integrity
    __table_args__ = (
        UniqueConstraint(
            'camera_id', 'track_id', 'direction', 'timestamp',
            name='uq_event_idempotency'
        ),
        Index('ix_event_camera_floor_timestamp', 'camera_id', 'floor_id', 'timestamp'),
        Index('ix_event_track_direction', 'track_id', 'direction'),
        Index('ix_event_timestamp', 'timestamp'),
        CheckConstraint('confidence >= 0 AND confidence <= 1', name='ck_confidence_range'),
    )

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String(100), nullable=False, index=True)
    floor_id = Column(Integer, ForeignKey("floors.id"), nullable=False, index=True)
    track_id = Column(String(100), nullable=False, index=True)
    vehicle_type = Column(SQLEnum(VehicleType), nullable=False)
    direction = Column(SQLEnum(Direction), nullable=False)
    confidence = Column(Float, default=0.8, nullable=False)  # Detection confidence (0-1)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    floor = relationship("Floor", back_populates="events")

    def __repr__(self):
        return f"<Event(id={self.id}, camera_id={self.camera_id}, track_id={self.track_id}, direction={self.direction}, timestamp={self.timestamp})>"
