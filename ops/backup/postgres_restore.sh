#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <backup-file.sql.gz>"
  exit 1
fi

backup_file="$1"
if [[ ! -f "${backup_file}" ]]; then
  echo "Backup file not found: ${backup_file}"
  exit 1
fi

: "${POSTGRES_HOST:=localhost}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_DB:=smartpark}"
: "${POSTGRES_USER:=smartpark}"
: "${POSTGRES_PASSWORD:=}"

export PGPASSWORD="${POSTGRES_PASSWORD}"
gunzip -c "${backup_file}" | psql \
  --host="${POSTGRES_HOST}" \
  --port="${POSTGRES_PORT}" \
  --username="${POSTGRES_USER}" \
  --dbname="${POSTGRES_DB}"

echo "Restore completed from: ${backup_file}"
