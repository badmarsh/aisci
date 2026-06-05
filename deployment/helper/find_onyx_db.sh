#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../onyx"

for DB in postgres onyx recovery_april30; do
  echo "=== DB: $DB ==="
  docker compose exec onyx-db psql -U postgres -d "$DB" -c \
    "SELECT schemaname, count(*) as tables FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema') GROUP BY schemaname ORDER BY tables DESC;" 2>/dev/null || echo "  (could not connect)"
  echo ""
done
