# Phase 7 Code Review Report

## Scope

Reviewed backend, frontend, and vision modules for:
- deprecated patterns
- naming/style consistency
- debug leftovers
- maintainability risks

## Findings and Actions

1. Deprecated Pydantic usage in backend response conversion
- Issue: `from_orm()` usage generated v2 deprecation warnings.
- Action: migrated to `model_validate(...)` helper serialization in `backend/main.py`.

2. Deprecated class-based schema config
- Issue: legacy `class Config` in compatibility schemas.
- Action: migrated to `ConfigDict(from_attributes=True)` in:
  - `backend/app/schemas/floor.py`
  - `backend/app/schemas/event.py`

3. Debug console output in frontend runtime paths
- Issue: console logging in API and hooks introduced noisy client logs.
- Action: removed console logging from:
  - `frontend/src/services/api.js`
  - `frontend/src/hooks/useFetch.js`

4. Readability improvements
- Action: added explicit serializer helpers in `backend/main.py`:
  - `_serialize_floor(...)`
  - `_serialize_event(...)`

## Residual Risks

- Some datetime deprecation warnings remain (`utcnow`) in legacy model/ops paths.
- FastAPI `@app.on_event(...)` deprecations remain; migrate to lifespan handlers in future cleanup.

## Validation

- Backend tests pass.
- Frontend tests pass.
- Vision tests pass.
