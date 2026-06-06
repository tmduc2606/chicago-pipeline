#!/bin/bash
set -e

HOST="${API_POSTGRES_HOST:-postgres}"
PORT="${API_POSTGRES_PORT:-5432}"
DB="${API_POSTGRES_DB:-chicago}"
USER="${API_POSTGRES_USER:-chicago}"
PASS="${API_POSTGRES_PASSWORD:-change_me_local}"

echo "Waiting for warehouse tables on ${HOST}:${PORT}/${DB}..."

until PGPASSWORD="$PASS" psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DB" -c \
  "SELECT 1 FROM warehouse.fact_crime LIMIT 1;" > /dev/null 2>&1; do
  echo "  Tables not ready yet, retrying in 3s..."
  sleep 3
done

echo "Warehouse tables ready. Starting API..."
exec "$@"
