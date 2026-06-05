#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../onyx"

echo "=== All schemas in onyx DB ==="
docker compose exec onyx-db psql -U postgres -d onyx -c \
  "SELECT nspname FROM pg_namespace WHERE nspname NOT IN ('pg_catalog','information_schema','pg_toast') ORDER BY nspname;"

echo ""
echo "=== Tables in 'public' schema ==="
docker compose exec onyx-db psql -U postgres -d onyx -c \
  "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename LIMIT 20;"

echo ""
echo "=== All non-system schemas with table counts ==="
docker compose exec onyx-db psql -U postgres -d onyx -c \
  "SELECT schemaname, count(*) as tables FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema') GROUP BY schemaname ORDER BY tables DESC;"
