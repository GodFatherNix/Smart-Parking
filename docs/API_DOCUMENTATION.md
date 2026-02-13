# SmartPark API Documentation

## OpenAPI/Swagger

- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Authentication

- Header: `X-API-Key: <your-key>`
- Public endpoints:
  - `GET /`
  - `GET /health`
  - `GET /health/live`
  - `GET /health/ready`
  - `GET /docs`
  - `GET /openapi.json`
  - `GET /redoc`

## Core Endpoints

### `POST /event`
- Purpose: ingest entry/exit vehicle event.
- Request body:
```json
{
  "camera_id": "cam_001",
  "floor_id": 1,
  "track_id": "track_123",
  "vehicle_type": "car",
  "direction": "entry",
  "confidence": 0.95
}
```
- Notes:
  - Idempotency enforced for duplicates.
  - Floor counts update atomically.

### `GET /floors`
- Purpose: list all active floors with occupancy.

### `GET /floors/{floor_id}`
- Purpose: get occupancy for one floor.

### `GET /recommend`
- Purpose: return best available floor and alternatives.

### `GET /events`
- Purpose: paginated event log retrieval.
- Query params:
  - `hours` (default `24`)
  - `limit` (default `100`)
  - `offset` (default `0`)
  - `floor_id` (optional)
  - `vehicle_type` (optional)
  - `direction` (optional)

## Monitoring/Health Endpoints

### `GET /health`
- General app+database status snapshot.

### `GET /health/live`
- Liveness probe endpoint.

### `GET /health/ready`
- Readiness probe with DB connectivity check.

### `GET /monitoring/metrics`
- Runtime request/error/latency metrics.

### `GET /monitoring/alerts`
- Active anomaly alerts:
  - `HIGH_ERROR_RATE`
  - `HIGH_LATENCY`
  - `LOW_PARKING_AVAILABILITY`

## Error Model

Typical error response:
```json
{
  "success": false,
  "error": "Validation Error",
  "detail": "...",
  "status_code": 422
}
```
