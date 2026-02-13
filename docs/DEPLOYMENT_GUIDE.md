# SmartPark Deployment Guide

## Platform

- Selected: **Render**
- CI/CD: GitHub Actions (`.github/workflows/ci-cd.yml`)

## Production Deployment Steps

1. Configure environment files:
   - `.env.production` (from `.env.production.example`)
2. Set GitHub repository secrets:
   - `RENDER_STAGING_DEPLOY_HOOK`
   - `RENDER_PROD_BACKEND_DEPLOY_HOOK`
   - `RENDER_PROD_FRONTEND_DEPLOY_HOOK`
   - `RENDER_PROD_VISION_DEPLOY_HOOK`
3. Deploy stack:
```powershell
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```
4. Verify:
   - Backend ready: `GET /health/ready`
   - Frontend loads dashboard
   - Logs present in collector output

## Branch-Based Flow

- `develop` push -> staging deploy hook.
- `main` push -> production deploy hooks.

## Database Backups

- Automatic backup service included in `docker-compose.prod.yml`.
- Manual scripts:
  - `ops/backup/postgres_backup.sh`
  - `ops/backup/postgres_restore.sh`
  - `ops/backup/postgres_backup.ps1`
  - `ops/backup/postgres_restore.ps1`
