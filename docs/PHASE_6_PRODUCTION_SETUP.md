# Phase 6 Production Setup

This document covers production-ready setup for PostgreSQL, environment variables, backups, health checks, and log aggregation.

## 1. PostgreSQL Production Stack

Use `docker-compose.prod.yml` with root `.env.production`:

```bash
cp .env.production.example .env.production
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

Core production services:
- `postgres`: primary production database
- `postgres-backup`: scheduled backup container
- `backend`: FastAPI connected to PostgreSQL
- `frontend`: built static app on Nginx
- `log-collector`: Fluent Bit log aggregation
- `vision`: optional profile (`--profile vision`)

## 2. Environment Variables

Production templates:
- `.env.production.example`
- `backend/.env.production.example`
- `frontend/.env.production.example`
- `vision/.env.production.example`

Set strong values before deployment:
- `POSTGRES_PASSWORD`
- `API_KEYS`
- `CORS_ALLOW_ORIGINS`

## 3. Database Backups

Automatic backups:
- `postgres-backup` service in `docker-compose.prod.yml`

Manual backups:
- Linux/macOS: `ops/backup/postgres_backup.sh`
- Windows: `ops/backup/postgres_backup.ps1`

Manual restore:
- Linux/macOS: `ops/backup/postgres_restore.sh <backup-file.sql.gz>`
- Windows: `ops/backup/postgres_restore.ps1 -BackupFile <backup-file.sql.gz>`

## 4. Health Endpoints

Available backend health endpoints:
- `GET /health` (overall health + stats)
- `GET /health/live` (liveness)
- `GET /health/ready` (readiness with DB check)

Production compose healthcheck uses `/health/ready`.

## 5. Logging Aggregation

Backend and vision services write JSON logs to mounted volumes:
- `/var/log/smartpark/backend/backend.log`
- `/var/log/smartpark/vision/vision.log`

Fluent Bit config:
- `ops/logging/fluent-bit.conf`

Aggregated output volume:
- `aggregated_logs` (JSON lines from all service logs)
