#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../onyx"

echo "=== Sample OpenSearch chunk (access_control_list + document_sets) ==="
docker compose exec onyx-opensearch curl -s \
  "http://localhost:9200/danswer_chunk_alibaba_nlp_gte_qwen2_1_5b_instruct/_search?size=2&pretty" \
  -H "Content-Type: application/json" \
  -d '{"query":{"match_all":{}},"_source":["document_id","access_control_list","document_sets","source_type","semantic_id"]}' \
  2>/dev/null | head -80

echo ""
echo "=== API key user ==="
docker compose exec onyx-db psql -U postgres -d postgres -c \
  "SELECT u.id, u.email, u.role, ak.api_key_display FROM \"user\" u LEFT JOIN api_key ak ON ak.user_id = u.id WHERE ak.api_key_display IS NOT NULL;"

echo ""
echo "=== Document set 6 sync status ==="
docker compose exec onyx-db psql -U postgres -d postgres -c \
  "SELECT id, name, is_up_to_date FROM document_set WHERE id=6;"

echo ""
echo "=== User access to connector ==="
docker compose exec onyx-db psql -U postgres -d postgres -c \
  "SELECT * FROM user__external_permission WHERE user_email IS NOT NULL LIMIT 10;" 2>/dev/null || \
docker compose exec onyx-db psql -U postgres -d postgres -c \
  "SELECT * FROM document__user_public_permissions LIMIT 5;" 2>/dev/null || echo "(no external permissions table)"
