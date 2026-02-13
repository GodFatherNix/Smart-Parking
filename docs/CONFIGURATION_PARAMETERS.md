# SmartPark Configuration Parameters

## Backend (`backend/.env*`)

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | DB connection string (SQLite or PostgreSQL) |
| `DATABASE_ECHO` | SQLAlchemy SQL logging toggle |
| `API_KEYS` | Allowed API keys (comma-separated) |
| `API_KEY_HEADER` | Header name for API key |
| `API_RATE_LIMIT` | Per-client request budget in window |
| `API_RATE_LIMIT_WINDOW_SECONDS` | Rate limit window size |
| `CORS_ALLOW_ORIGINS` | Allowed frontend origins |
| `LOG_LEVEL` | Backend log level |
| `LOG_FORMAT` | `standard` or `json` logs |
| `LOG_FILE` | Backend log file path |
| `SENTRY_DSN` | Sentry DSN for error tracking |
| `SENTRY_ENVIRONMENT` | Sentry environment tag |
| `SENTRY_TRACES_SAMPLE_RATE` | Sentry traces sampling rate |
| `MONITORING_HISTORY_SIZE` | In-memory request history size |
| `MONITORING_ERROR_RATE_THRESHOLD` | Alert threshold for 5xx rate |
| `MONITORING_LATENCY_MS_THRESHOLD` | Alert threshold for latency |
| `MONITORING_LOW_AVAILABILITY_THRESHOLD` | Alert threshold for floor slots |

## Frontend (`frontend/.env*`)

| Variable | Purpose |
|---|---|
| `VITE_API_URL` | Backend base URL/proxy path |
| `VITE_API_KEY` | API key sent from frontend |
| `VITE_API_KEY_HEADER` | API key header name |
| `VITE_API_TIMEOUT_MS` | Request timeout |
| `VITE_API_RETRY_ATTEMPTS` | Retry attempts for retryable requests |
| `VITE_API_RETRY_DELAY_MS` | Base retry backoff delay |

## Vision (`vision/.env*`)

| Variable | Purpose |
|---|---|
| `BACKEND_API_URL` | Backend base URL |
| `BACKEND_EVENT_ENDPOINT` | Event ingestion endpoint |
| `MODEL_NAME` | YOLO model name |
| `MODEL_CONFIDENCE_THRESHOLD` | Detection confidence threshold |
| `MODEL_IOU_THRESHOLD` | IoU threshold |
| `VIDEO_INPUT_TYPE` | `file` or `rtsp` |
| `VIDEO_INPUT_PATH` | File path or RTSP URL |
| `VIDEO_FPS` | Frame processing FPS target |
| `CAMERA_CONFIG_PATH` | Camera config JSON file path |
| `AREA_THRESHOLD` | Minimum bbox area for crossing logic |
| `EVENT_DUPLICATE_COOLDOWN_FRAMES` | Crossing duplicate suppression frames |
| `EVENT_OCCLUSION_TOLERANCE_FRAMES` | Max frame gap for continuity |
| `EVENT_REVERSAL_SUPPRESSION_FRAMES` | Reverse crossing suppression window |
| `LOG_LEVEL` | Vision log level |
| `LOG_FORMAT` | Vision log format |
| `LOG_FILE` | Vision log file path |
| `SENTRY_DSN` | Vision Sentry DSN |
| `SENTRY_ENVIRONMENT` | Vision Sentry environment |
| `SENTRY_TRACES_SAMPLE_RATE` | Vision Sentry traces sample rate |
