#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../onyx"
DB=postgres

echo "=== connector_credential_pair columns ==="
docker compose exec onyx-db psql -U postgres -d "$DB" -c \
  "SELECT column_name FROM information_schema.columns WHERE table_name='connector_credential_pair' ORDER BY ordinal_position;"

echo ""
echo "=== connector_credential_pair data ==="
docker compose exec onyx-db psql -U postgres -d "$DB" -c \
  "SELECT * FROM connector_credential_pair ORDER BY id;"

echo ""
echo "=== index_attempt #44 full row ==="
docker compose exec onyx-db psql -U postgres -d "$DB" -c \
  "SELECT id, status, total_docs_indexed, new_docs_indexed, total_chunks,
          total_failures_batch_level, total_batches, completed_batches,
          left(coalesce(error_msg,''),300) as error_msg,
          left(coalesce(full_exception_trace,''),500) as trace
   FROM index_attempt WHERE id=44;"

echo ""
echo "=== Recent background logs (onyx-background last 50) ==="
docker compose logs onyx-background --tail 50 2>&1 | grep -iE "error|fail|contextual|chunk|multipass|index_attempt.*44" || true
