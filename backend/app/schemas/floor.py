from pydantic import BaseModel, ConfigDict
from datetime import datetime


class FloorSchema(BaseModel):
    name: str
    total_slots: int


class FloorResponseSchema(BaseModel):
    id: int
    name: str
    total_slots: int
    current_vehicles: int
    available_slots: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
