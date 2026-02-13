# Phase 6 Monitoring and Logging

This phase adds centralized logging, live monitoring metrics, anomaly alerts, and error tracking.

## Centralized Logging

Production compose uses a dedicated collector:
- Service: `log-collector` (`fluent/fluent-bit`)
- Config: `ops/logging/fluent-bit.conf`
- Inputs: backend and vision log volumes
- Output: `aggregated_logs` volume in JSON lines format

Backend and vision are configured for JSON log output in production.

## Monitoring Dashboard Metrics

Backend exposes operational monitoring endpoints:
- `GET /monitoring/metrics`
- `GET /monitoring/alerts`

Example metrics returned:
- recent request count
- recent average latency
- status code distribution
- top routes

This payload can be consumed by Grafana/BI dashboards.

## Alerts for System Anomalies

`/monitoring/alerts` evaluates active anomalies:
- `HIGH_ERROR_RATE`
- `HIGH_LATENCY`
- `LOW_PARKING_AVAILABILITY`

Thresholds are configurable via backend environment variables:
- `MONITORING_ERROR_RATE_THRESHOLD`
- `MONITORING_LATENCY_MS_THRESHOLD`
- `MONITORING_LOW_AVAILABILITY_THRESHOLD`

## Error Tracking (Sentry)

Optional Sentry integration is enabled for backend and vision:
- Backend env:
  - `SENTRY_DSN`
  - `SENTRY_ENVIRONMENT`
  - `SENTRY_TRACES_SAMPLE_RATE`
- Vision env:
  - `SENTRY_DSN`
  - `SENTRY_ENVIRONMENT`
  - `SENTRY_TRACES_SAMPLE_RATE`

If DSN is empty, Sentry is skipped automatically.
