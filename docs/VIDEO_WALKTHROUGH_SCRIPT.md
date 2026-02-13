# SmartPark Video Walkthrough Script

## Goal
Record a 5-8 minute walkthrough demonstrating end-to-end SmartPark functionality.

## Recording Outline

1. Intro (30s)
- Show project folders (`backend`, `frontend`, `vision`, `docs`).
- Briefly explain parking flow.

2. Backend API (1.5 min)
- Open Swagger UI at `/docs`.
- Show `POST /event`, `GET /floors`, `GET /recommend`, `GET /events`.
- Show health and monitoring endpoints.

3. Frontend Dashboard (1.5 min)
- Open dashboard.
- Explain floor occupancy, recommendation panel, event log filters.
- Trigger refresh and show data update.

4. Vision Service (1.5 min)
- Show camera configuration file.
- Start vision service.
- Explain detection -> tracking -> crossing -> event transmission flow.

5. Monitoring and Operations (1 min)
- Show `/monitoring/metrics` and `/monitoring/alerts`.
- Show production compose files and backup scripts.

6. CI/CD and Deployment (1 min)
- Show GitHub Actions workflow file.
- Explain staging (`develop`) and production (`main`) auto-deploy hooks.

## Demo Checklist Before Recording

- Backend running on `:8000`
- Frontend running on `:3000`
- API key configured
- Sample events available
- Vision service runnable with sample source
- Monitoring endpoints returning data

## Suggested Closing
- Summarize architecture, reliability features, and next roadmap items.
