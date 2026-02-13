from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum


# ============= ENUMERATIONS =============

class VehicleType(str, Enum):
    """Vehicle type enumeration"""
    car = "car"
    motorcycle = "motorcycle"
    truck = "truck"
    bus = "bus"


class Direction(str, Enum):
    """Direction enumeration"""
    entry = "entry"
    exit = "exit"


# ============= REQUEST SCHEMAS =============

class EventCreateRequest(BaseModel):
    """Schema for POST /event - Record a parking event"""
    camera_id: str = Field(..., min_length=1, max_length=50, description="Camera identifier")
    floor_id: int = Field(..., gt=0, description="Floor ID")
    track_id: str = Field(..., min_length=1, max_length=100, description="Vehicle tracking ID")
    vehicle_type: VehicleType = Field(..., description="Type of vehicle")
    direction: Direction = Field(..., description="Entry or exit")
    confidence: float = Field(default=0.95, ge=0, le=1, description="Detection confidence (0-1)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "camera_id": "cam_001",
                "floor_id": 1,
                "track_id": "track_12345",
                "vehicle_type": "car",
                "direction": "entry",
                "confidence": 0.95
            }
        }
    )

class EventFilterRequest(BaseModel):
    """Schema for GET /events - Filter parameters"""
    floor_id: Optional[int] = Field(None, description="Filter by floor ID")
    vehicle_type: Optional[VehicleType] = Field(None, description="Filter by vehicle type")
    direction: Optional[Direction] = Field(None, description="Filter by direction (entry/exit)")
    hours: int = Field(default=24, ge=1, le=365*24, description="Events from last N hours")
    limit: int = Field(default=100, ge=1, le=1000, description="Max results")
    offset: int = Field(default=0, ge=0, description="Pagination offset")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "floor_id": 1,
                "vehicle_type": "car",
                "direction": "entry",
                "hours": 24,
                "limit": 100,
                "offset": 0
            }
        }
    )


# ============= RESPONSE SCHEMAS =============

class FloorResponse(BaseModel):
    """Schema for floor data in responses"""
    id: int
    name: str
    description: Optional[str] = None
    total_slots: int
    current_vehicles: int
    available_slots: int
    occupancy_percentage: float
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Ground Floor",
                "description": "Main parking area",
                "total_slots": 50,
                "current_vehicles": 35,
                "available_slots": 15,
                "occupancy_percentage": 70.0,
                "is_active": True,
                "created_at": "2026-02-12T10:00:00",
                "updated_at": "2026-02-12T12:30:00"
            }
        }
    )


class EventResponse(BaseModel):
    """Schema for event data in responses"""
    id: int
    camera_id: str
    floor_id: int
    track_id: str
    vehicle_type: VehicleType
    direction: Direction
    confidence: float
    timestamp: datetime
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "camera_id": "cam_001",
                "floor_id": 1,
                "track_id": "track_12345",
                "vehicle_type": "car",
                "direction": "entry",
                "confidence": 0.95,
                "timestamp": "2026-02-12T12:30:00",
                "created_at": "2026-02-12T12:30:01"
            }
        }
    )


class EventCreateResponse(BaseModel):
    """Schema for POST /event response"""
    success: bool
    message: str
    event_id: int
    floor_id: int
    current_vehicles: int
    available_slots: int
    occupancy_percentage: float
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Vehicle entry recorded successfully",
                "event_id": 1,
                "floor_id": 1,
                "current_vehicles": 36,
                "available_slots": 14,
                "occupancy_percentage": 72.0
            }
        }
    )


class FloorsListResponse(BaseModel):
    """Schema for GET /floors response"""
    success: bool
    total_floors: int
    total_capacity: int
    total_vehicles: int
    total_available: int
    average_occupancy: float
    floors: List[FloorResponse]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "total_floors": 4,
                "total_capacity": 200,
                "total_vehicles": 145,
                "total_available": 55,
                "average_occupancy": 72.5,
                "floors": []
            }
        }
    )


class RecommendationResponse(BaseModel):
    """Schema for GET /recommend response"""
    success: bool
    recommended_floor: FloorResponse
    reason: str
    available_alternatives: List[FloorResponse]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "recommended_floor": {},
                "reason": "Lowest occupancy rate (40%)",
                "available_alternatives": []
            }
        }
    )


class EventsListResponse(BaseModel):
    """Schema for GET /events response"""
    success: bool
    total_count: int
    filtered_count: int
    limit: int
    offset: int
    events: List[EventResponse]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "total_count": 150,
                "filtered_count": 50,
                "limit": 100,
                "offset": 0,
                "events": []
            }
        }
    )


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    status_code: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": "Invalid floor ID",
                "detail": "Floor with ID 999 not found",
                "status_code": 404
            }
        }
    )


class HealthCheckResponse(BaseModel):
    """Schema for health check"""
    status: str
    timestamp: datetime
    project: str
    database: dict
    error: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2026-02-12T12:30:00",
                "project": "SmartPark API",
                "database": {
                    "total_floors": 4,
                    "total_events": 150,
                    "tables_exist": True
                }
            }
        }
    )


class RootResponse(BaseModel):
    """Schema for root endpoint"""
    message: str
    docs: str
    openapi: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Welcome to SmartPark API",
                "docs": "/docs",
                "openapi": "/openapi.json",
            }
        }
    )


# Legacy schemas (keeping for compatibility)
from app.schemas.floor import FloorSchema, FloorResponseSchema
from app.schemas.event import EventSchema, EventResponseSchema

__all__ = [
    "VehicleType", "Direction",
    "EventCreateRequest", "EventFilterRequest",
    "FloorResponse", "EventResponse", "EventCreateResponse",
    "FloorsListResponse", "RecommendationResponse", "EventsListResponse",
    "ErrorResponse", "HealthCheckResponse", "RootResponse",
    "FloorSchema", "FloorResponseSchema", "EventSchema", "EventResponseSchema"
]
