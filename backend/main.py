from time import perf_counter

from fastapi import FastAPI, HTTPException, Path, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import get_settings
from app.core.logging import logger
from app.core.security import (
    InMemoryRateLimiter,
    get_client_identifier,
    is_public_path,
    require_api_key,
)
from app.core.monitoring import MonitoringState, MonitoringThresholds
from datetime import datetime
from sqlalchemy import text
from pathlib import Path as FilePath

# Import database components with error handling for SQLAlchemy compatibility
get_database_stats = None
seed_floors = None
seed_sample_events = None
FloorOperations = None
EventOperations = None
create_tables = None
check_tables_exist = None
engine = None

try:
    from app.core.database import Base, engine
    from app.core.migrations import create_tables, check_tables_exist, get_database_stats
    from app.core.seed import seed_floors, seed_sample_events
    from app.core.database_ops import FloorOperations, EventOperations
    
    # Initialize database
    if check_tables_exist and not check_tables_exist():
        logger.info("Creating database tables...")
        create_tables()
        logger.info("Database tables created")
    elif check_tables_exist:
        logger.info("Database tables already exist")
except (ImportError, AssertionError) as e:
    logger.warning(f"Database initialization warning: {type(e).__name__}: {e}")
except Exception as e:
    logger.warning(f"Database initialization error: {e}")

# Import schemas
from app.schemas import (
    EventCreateRequest, EventCreateResponse, FloorsListResponse,
    RecommendationResponse, EventsListResponse, FloorResponse, EventResponse,
    VehicleType, Direction, ErrorResponse, HealthCheckResponse, RootResponse
)

settings = get_settings()
if settings.sentry_dsn:
    try:
        import sentry_sdk  # pylint: disable=import-outside-toplevel
        from sentry_sdk.integrations.fastapi import FastApiIntegration  # pylint: disable=import-outside-toplevel

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.sentry_environment,
            traces_sample_rate=settings.sentry_traces_sample_rate,
            integrations=[FastApiIntegration()],
        )
        logger.info("Sentry error tracking initialized")
    except Exception as exc:
        logger.warning(f"Sentry initialization skipped: {exc}")

rate_limiter = InMemoryRateLimiter(
    max_requests=settings.api_rate_limit,
    window_seconds=settings.api_rate_limit_window_seconds,
)
monitoring = MonitoringState(
    history_size=settings.monitoring_history_size,
    thresholds=MonitoringThresholds(
        error_rate_threshold=settings.monitoring_error_rate_threshold,
        latency_ms_threshold=settings.monitoring_latency_ms_threshold,
        low_availability_threshold=settings.monitoring_low_availability_threshold,
    ),
)
cors_origins = settings.parse_csv_setting(settings.cors_allow_origins)
cors_methods = settings.parse_csv_setting(settings.cors_allow_methods)
cors_headers = settings.parse_csv_setting(settings.cors_allow_headers)
allow_all_origins = cors_origins == ["*"]


def _serialize_floor(floor_obj):
    """Pydantic v2-compatible ORM serialization helper."""
    return FloorResponse.model_validate(floor_obj)


def _serialize_event(event_obj):
    """Pydantic v2-compatible ORM serialization helper."""
    return EventResponse.model_validate(event_obj)

# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    description="Real-time parking management system",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else ["*"],
    allow_credentials=not allow_all_origins,
    allow_methods=cors_methods if cors_methods else ["*"],
    allow_headers=cors_headers if cors_headers else ["*"],
)


@app.middleware("http")
async def request_security_and_logging_middleware(request: Request, call_next):
    start = perf_counter()
    request_id = request.headers.get("X-Request-ID", "n/a")
    path = request.url.path
    method = request.method
    client = get_client_identifier(request)
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    try:
        if method != "OPTIONS":
            try:
                require_api_key(request)
            except HTTPException as exc:
                status_code = exc.status_code
                return JSONResponse(
                    status_code=exc.status_code,
                    content=ErrorResponse(
                        error="Authentication Error",
                        detail=str(exc.detail),
                        status_code=exc.status_code,
                    ).model_dump(),
                )

            if not is_public_path(path):
                allowed, retry_after = rate_limiter.check(client)
                if not allowed:
                    status_code = status.HTTP_429_TOO_MANY_REQUESTS
                    logger.warning(
                        f"Rate limit exceeded: client={client} path={path} retry_after={retry_after}s"
                    )
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content=ErrorResponse(
                            error="Too Many Requests",
                            detail="Rate limit exceeded",
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        ).model_dump(),
                        headers={"Retry-After": str(retry_after)},
                    )

        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        duration_ms = (perf_counter() - start) * 1000
        monitoring.record_request(
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
        )
        logger.info(
            f"{method} {path} status={status_code} duration_ms={duration_ms:.2f} "
            f"client={client} request_id={request_id}"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP Exception",
            detail=detail,
            status_code=exc.status_code,
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Validation Error",
            detail=str(exc),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ).model_dump(),
    )


@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.project_name}")
    try:
        # Seed initial data if functions are available
        if seed_floors and seed_sample_events:
            seed_floors()
            seed_sample_events()
        
        # Log database stats if available
        if get_database_stats:
            stats = get_database_stats()
            logger.info(f"Database stats - Floors: {stats.get('floors_count', 0)}, Events: {stats.get('events_count', 0)}")
    except Exception as e:
        logger.warning(f"Database seeding warning: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.project_name}")


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint with database statistics"""
    try:
        response = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "project": settings.project_name,
            "database": {
                "floors": 0,
                "events": 0,
                "tables_exist": False
            }
        }
        
        if get_database_stats:
            stats = get_database_stats()
            response["database"]["floors"] = stats.get('floors_count', 0)
            response["database"]["events"] = stats.get('events_count', 0)
            response["database"]["tables_exist"] = True
        
        return response
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "project": settings.project_name,
            "database": {
                "floors": 0,
                "events": 0,
                "tables_exist": False
            },
            "error": str(e)
        }


@app.get("/health/live")
async def liveness_check():
    """Kubernetes/container liveness probe endpoint."""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "project": settings.project_name,
    }


@app.get("/health/ready")
async def readiness_check():
    """Readiness probe endpoint that validates database connectivity."""
    if engine is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "timestamp": datetime.now().isoformat(),
                "project": settings.project_name,
                "database_ready": False,
                "detail": "Database engine is not initialized",
            },
        )

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "project": settings.project_name,
            "database_ready": True,
        }
    except Exception as exc:
        logger.error(f"Readiness check failed: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "timestamp": datetime.now().isoformat(),
                "project": settings.project_name,
                "database_ready": False,
                "detail": "Database connection failed",
            },
        )


@app.get("/monitoring/metrics")
async def monitoring_metrics():
    """Operational metrics snapshot for dashboards."""
    payload = monitoring.snapshot()
    payload["timestamp"] = datetime.now().isoformat()
    return payload


@app.get("/monitoring/alerts")
async def monitoring_alerts():
    """Evaluate live alert conditions for anomalies."""
    low_availability_floors = []
    if FloorOperations:
        try:
            floors = FloorOperations.get_all_active_floors()
            low_availability_floors = [
                {"id": floor.id, "name": floor.name, "available_slots": floor.available_slots}
                for floor in floors
                if floor.available_slots <= settings.monitoring_low_availability_threshold
            ]
        except Exception as exc:
            logger.warning(f"Unable to evaluate floor availability alert state: {exc}")

    alerts = monitoring.evaluate_alerts(low_availability_floors=low_availability_floors)
    return {
        "timestamp": datetime.now().isoformat(),
        "active_alert_count": len(alerts),
        "alerts": alerts,
    }


@app.get("/camera/latest-frame")
async def latest_camera_frame():
    """
    Return the latest annotated frame generated by vision service.
    Expected path defaults to ../vision/frames relative to backend.
    """
    frame_dir = FilePath(settings.vision_frame_dir)
    if not frame_dir.exists() or not frame_dir.is_dir():
        raise HTTPException(status_code=404, detail="Frame directory not found")

    candidates = sorted(
        [path for ext in ("*.jpg", "*.jpeg", "*.png") for path in frame_dir.glob(ext)],
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise HTTPException(status_code=404, detail="No camera frame available yet")

    latest = candidates[0]
    media_type = "image/jpeg" if latest.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
    return FileResponse(path=str(latest), media_type=media_type, filename=latest.name)


@app.get("/", response_model=RootResponse)
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to SmartPark API",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


# ============= CORE API ENDPOINTS =============

@app.post("/event", response_model=EventCreateResponse)
async def record_event(event: EventCreateRequest):
    """
    Record a parking event (vehicle entry or exit)
    
    Returns updated floor occupancy and event details.
    Idempotency is guaranteed through unique constraint on (camera_id, track_id, direction, timestamp window).
    """
    if not (EventOperations and FloorOperations):
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        # Record the event with idempotency and atomic floor count update.
        db_event, floor, is_duplicate = EventOperations.record_event(
            camera_id=event.camera_id,
            floor_id=event.floor_id,
            track_id=event.track_id,
            vehicle_type=event.vehicle_type.value,
            direction=event.direction.value,
            confidence=event.confidence
        )

        logger.info(
            f"Event {'deduplicated' if is_duplicate else 'recorded'}: "
            f"{event.direction.value} - {event.vehicle_type.value} on floor {event.floor_id}"
        )
        
        return EventCreateResponse(
            success=True,
            message=(
                f"Duplicate vehicle {event.direction.value} ignored"
                if is_duplicate
                else f"Vehicle {event.direction.value} recorded successfully"
            ),
            event_id=db_event.id,
            floor_id=floor.id,
            current_vehicles=floor.current_vehicles,
            available_slots=floor.available_slots,
            occupancy_percentage=floor.occupancy_percentage
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Event validation error: {e}")
        status_code = 409 if ("full" in str(e).lower() or "empty" in str(e).lower()) else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error recording event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/floors", response_model=FloorsListResponse)
async def get_floors():
    """
    Get all active floors with current occupancy information
    
    Returns list of all floors with capacity, occupancy, and availability data.
    """
    if not FloorOperations:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        floors = FloorOperations.get_all_active_floors()
        
        if not floors:
            logger.warning("No active floors found")
            raise HTTPException(status_code=404, detail="No active floors found")
        
        # Calculate aggregate statistics
        total_capacity = sum(f.total_slots for f in floors)
        total_vehicles = sum(f.current_vehicles for f in floors)
        total_available = sum(f.available_slots for f in floors)
        average_occupancy = (total_vehicles / total_capacity * 100) if total_capacity > 0 else 0
        
        logger.info(f"Retrieved {len(floors)} active floors")
        
        return FloorsListResponse(
            success=True,
            total_floors=len(floors),
            total_capacity=total_capacity,
            total_vehicles=total_vehicles,
            total_available=total_available,
            average_occupancy=round(average_occupancy, 2),
            floors=[_serialize_floor(floor) for floor in floors]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving floors: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/floors/{floor_id}", response_model=FloorResponse)
async def get_floor(floor_id: int = Path(..., gt=0, description="Floor ID")):
    """
    Get specific floor by ID with current occupancy
    """
    if not FloorOperations:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        floor = FloorOperations.get_floor_by_id(floor_id)
        
        if not floor:
            logger.warning(f"Floor {floor_id} not found")
            raise HTTPException(status_code=404, detail=f"Floor {floor_id} not found")
        
        return _serialize_floor(floor)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving floor {floor_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/recommend", response_model=RecommendationResponse)
async def get_recommendation():
    """
    Get recommended floor for parking based on occupancy rates
    
    Returns the floor with the lowest occupancy percentage, along with alternatives.
    """
    if not FloorOperations:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        recommended = FloorOperations.get_recommended_floor()
        if not recommended:
            raise HTTPException(status_code=404, detail="No suitable floor found")
        
        all_floors = FloorOperations.get_all_active_floors()
        
        # Get alternatives (other floors sorted by occupancy)
        alternatives = [f for f in sorted(all_floors, key=lambda x: x.occupancy_percentage) 
                       if f.id != recommended.id][:3]
        
        occupancy = recommended.occupancy_percentage
        if occupancy < 30:
            reason = "Very low occupancy rate (< 30%)"
        elif occupancy < 50:
            reason = "Low occupancy rate (< 50%)"
        elif occupancy < 70:
            reason = "Moderate occupancy rate (< 70%)"
        else:
            reason = "Best available option"
        
        logger.info(f"Recommendation returned: Floor {recommended.id} ({occupancy}% occupancy)")
        
        return RecommendationResponse(
            success=True,
            recommended_floor=_serialize_floor(recommended),
            reason=reason,
            available_alternatives=[_serialize_floor(floor) for floor in alternatives]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/events", response_model=EventsListResponse)
async def get_events(
    floor_id: int | None = Query(default=None, gt=0, description="Filter by floor ID"),
    vehicle_type: VehicleType | None = Query(default=None, description="Filter by vehicle type"),
    direction: Direction | None = Query(default=None, description="Filter by direction (entry/exit)"),
    hours: int = Query(24, ge=1, le=365*24, description="Events from last N hours"),
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """
    Get event logs with optional filtering
    
    Supports filtering by floor, vehicle type, direction, and time range.
    """
    if not EventOperations:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        paginated_events, total_count, filtered_count = EventOperations.get_filtered_events(
            hours=hours,
            floor_id=floor_id,
            vehicle_type=vehicle_type.value if vehicle_type else None,
            direction=direction.value if direction else None,
            limit=limit,
            offset=offset,
        )

        logger.info(f"Retrieved {len(paginated_events)} events (total after filters: {filtered_count})")
        
        return EventsListResponse(
            success=True,
            total_count=total_count,
            filtered_count=filtered_count,
            limit=limit,
            offset=offset,
            events=[_serialize_event(event) for event in paginated_events]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving events: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
