# Phase 6 Deployment Pipeline

## Deployment Platform Choice

Selected platform: **Render**.

Reason:
- Supports containerized web services and workers.
- Provides deploy hooks for simple GitHub-triggered releases.
- Works well for separate backend/frontend/vision services.

## CI/CD Workflow

Workflow file:
- `.github/workflows/ci-cd.yml`

Pipeline behavior:
- Trigger on pull requests to `main` and `develop`.
- Trigger on pushes to `main` and `develop`.
- Run automated test gates:
  - Backend: `pytest`
  - Frontend: `npm run test` and `npm run build`
  - Vision: `pytest`
- Auto-deploy after all tests pass:
  - `develop` -> staging via one Render staging deploy hook
  - `main` -> production via separate backend/frontend/vision hooks

## Required GitHub Secrets

Set these in repository secrets:
- `RENDER_STAGING_DEPLOY_HOOK`
- `RENDER_PROD_BACKEND_DEPLOY_HOOK`
- `RENDER_PROD_FRONTEND_DEPLOY_HOOK`
- `RENDER_PROD_VISION_DEPLOY_HOOK`

## Environment-Specific Configurations

Templates available:
- `.env.staging.example`
- `.env.production.example`
- `backend/.env.production.example`
- `frontend/.env.production.example`
- `vision/.env.production.example`

Recommended mapping:
- `develop` branch uses staging values.
- `main` branch uses production values.

## Deployment Flow

1. Open PR to `develop` or `main`.
2. CI runs all tests and frontend build.
3. Merge PR.
4. Push to `develop` triggers staging deployment hook.
5. Push to `main` triggers production deployment hooks.
