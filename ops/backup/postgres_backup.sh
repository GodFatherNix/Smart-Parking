#!/usr/bin/env bash
set -euo pipefail

: "${POSTGRES_HOST:=localhost}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_DB:=smartpark}"
: "${POSTGRES_USER:=smartpark}"
: "${POSTGRES_PASSWORD:=}"
: "${BACKUP_DIR:=./backups}"

mkdir -p "${BACKUP_DIR}"
timestamp="$(date -u +%Y%m%d_%H%M%S)"
outfile="${BACKUP_DIR}/${POSTGRES_DB}_${timestamp}.sql.gz"

export PGPASSWORD="${POSTGRES_PASSWORD}"
pg_dump \
  --host="${POSTGRES_HOST}" \
  --port="${POSTGRES_PORT}" \
  --username="${POSTGRES_USER}" \
  --dbname="${POSTGRES_DB}" \
  --format=plain \
  --no-owner \
  --no-privileges | gzip > "${outfile}"

echo "Backup created: ${outfile}"
