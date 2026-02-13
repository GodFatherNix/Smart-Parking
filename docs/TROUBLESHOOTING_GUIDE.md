# SmartPark Troubleshooting Guide

## Backend Issues

### API fails to start
- Check Python version: `python --version`
- Reinstall deps: `pip install -r backend/requirements.txt`
- Verify DB URL in `backend/.env`

### Auth failures (`401`)
- Ensure API key header exists: `X-API-Key`
- Confirm key in `API_KEYS` env setting

### Rate limit errors (`429`)
- Increase `API_RATE_LIMIT` for high traffic environments
- Verify client retries/backoff behavior

## Frontend Issues

### API errors in UI
- Confirm `VITE_API_URL` and `VITE_API_KEY`
- Check browser network tab for status codes

### Build failures
- Use Node 18+ and run:
```powershell
cd frontend
npm ci
npm run build
```

## Vision Service Issues

### No detections
- Confirm model exists: `vision/models/yolov8n.pt`
- Check confidence threshold settings
- Verify video input path/RTSP URL

### Events not reaching backend
- Check `BACKEND_API_URL` and API key setup
- Inspect queue file: `vision/logs/events_queue.jsonl`
- Run backend health checks (`/health`, `/health/ready`)

## Docker/Deployment Issues

### Containers up but app unavailable
- Check backend health endpoint in container logs
- Validate port mappings in compose files

### PostgreSQL connection errors
- Verify `POSTGRES_*` env values and credentials
- Ensure backend `DATABASE_URL` matches postgres service

## Logging and Monitoring

- Backend metrics: `GET /monitoring/metrics`
- Alerts: `GET /monitoring/alerts`
- Aggregated logs from fluent-bit output volume
