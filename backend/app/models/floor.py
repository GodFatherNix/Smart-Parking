from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, UniqueConstraint, Index, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Floor(Base):
    __tablename__ = "floors"
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('name', name='uq_floor_name'),
        CheckConstraint('total_slots >= 0', name='ck_total_slots_positive'),
        CheckConstraint('current_vehicles >= 0', name='ck_current_vehicles_positive'),
        CheckConstraint('current_vehicles <= total_slots', name='ck_vehicles_not_exceed_slots'),
        Index('ix_floor_updated_at', 'updated_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    total_slots = Column(Integer, nullable=False)
    current_vehicles = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    events = relationship("Event", back_populates="floor", cascade="all, delete-orphan")

    @property
    def available_slots(self) -> int:
        """Calculate available slots"""
        return max(0, self.total_slots - self.current_vehicles)
    
    @property
    def occupancy_percentage(self) -> float:
        """Calculate occupancy percentage"""
        if self.total_slots == 0:
            return 0.0
        return (self.current_vehicles / self.total_slots) * 100

    def __repr__(self):
        return f"<Floor(id={self.id}, name={self.name}, current_vehicles={self.current_vehicles}/{self.total_slots}, occupancy={self.occupancy_percentage:.1f}%)>"
