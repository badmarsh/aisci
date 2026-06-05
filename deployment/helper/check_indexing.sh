#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../onyx"

echo "=== Tables matching 'index' ==="
docker compose exec onyx-db psql -U postgres -d onyx -c \
  "SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename ILIKE '%index%' ORDER BY tablename;"

echo ""
echo "=== Latest index attempts (connector_id=3) ==="
docker compose exec onyx-db psql -U postgres -d onyx -c \
  "SELECT id, status, total_docs_indexed, new_docs_indexed, chunk_count, error_count,
          to_char(time_started,'HH24:MI:SS') as started,
          to_char(time_updated,'HH24:MI:SS') as updated
   FROM indexingattempt WHERE connector_id=3 ORDER BY id DESC LIMIT 5;" 2>/dev/null || \
docker compose exec onyx-db psql -U postgres -d onyx -c \
  "SELECT id, status, total_docs_indexed, new_docs_indexed, chunk_count, error_count,
          to_char(time_started,'HH24:MI:SS') as started,
          to_char(time_updated,'HH24:MI:SS') as updated
   FROM index_attempt WHERE connector_id=3 ORDER BY id DESC LIMIT 5;" 2>/dev/null || \
echo "Could not find index attempt table — checking all tables..."

echo ""
echo "=== All public tables ==="
docker compose exec onyx-db psql -U postgres -d onyx -c \
  "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;"
