from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum


class VehicleTypeEnum(str, Enum):
    car = "car"
    motorcycle = "motorcycle"
    bus = "bus"
    truck = "truck"


class DirectionEnum(str, Enum):
    entry = "entry"
    exit = "exit"


class EventSchema(BaseModel):
    camera_id: str
    floor_id: int
    track_id: str
    vehicle_type: VehicleTypeEnum
    direction: DirectionEnum


class EventResponseSchema(BaseModel):
    id: int
    camera_id: str
    floor_id: int
    track_id: str
    vehicle_type: VehicleTypeEnum
    direction: DirectionEnum
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
