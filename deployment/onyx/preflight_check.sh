#!/usr/bin/env bash
# Pre-reindex preflight check for the Onyx stack.
# Run BEFORE and AFTER any reindex, backend image rebuild, or embedding model change.
# Exit 0 = safe to proceed. Exit 1 = do not reindex until issues are resolved.
#
# Usage:
#   bash deployment/onyx/preflight_check.sh
#
# What it checks:
#   1. OpenSearch parity (Postgres doc count vs index chunk count) via cutover helper
#   2. Embedding model alignment (DB setting vs .env vs model-server)
#   3. Minimal /api/search probe via Onyx API

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CUTOVER_SCRIPT="$REPO_ROOT/deployment/helper/onyx_opensearch_cutover.py"
ENV_FILE="$REPO_ROOT/deployment/onyx/.env"

red()   { printf '\033[0;31m%s\033[0m\n' "$*"; }
green() { printf '\033[0;32m%s\033[0m\n' "$*"; }
warn()  { printf '\033[0;33m%s\033[0m\n' "$*"; }

FAILURES=0

echo "=== Onyx Pre-Reindex Preflight $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo ""

# ── 1. OpenSearch parity via cutover helper ───────────────────────────────────
echo "-- OpenSearch parity check"
if [[ ! -f "$CUTOVER_SCRIPT" ]]; then
    red "  FAIL  cutover script not found: $CUTOVER_SCRIPT"
    FAILURES=$((FAILURES + 1))
else
    PARITY_OUT=$(python3 "$CUTOVER_SCRIPT" --json 2>&1 || true)
    MISSING=$(echo "$PARITY_OUT" | python3 -c \
        "import json,sys; d=json.load(sys.stdin); print(d.get('indexes', {}).get('primary', {}).get('missing_document_count', 0))" 2>/dev/null || echo "ERROR")
    MISMATCHED=$(echo "$PARITY_OUT" | python3 -c \
        "import json,sys; d=json.load(sys.stdin); print(d.get('indexes', {}).get('primary', {}).get('mismatched_document_count', 0))" 2>/dev/null || echo "ERROR")
    RETRIEVAL=$(echo "$PARITY_OUT" | python3 -c \
        "import json,sys; d=json.load(sys.stdin); print(d.get('tenant_record', {}).get('rows', [{}])[0].get('enable_opensearch_retrieval', '?'))" 2>/dev/null || echo "ERROR")

    if [[ "$MISSING" == "0" && "$MISMATCHED" == "0" && "$RETRIEVAL" == "True" ]]; then
        green "  PASS  parity green — missing=$MISSING mismatched=$MISMATCHED retrieval=$RETRIEVAL"
    else
        red   "  FAIL  parity check — missing=$MISSING mismatched=$MISMATCHED retrieval=$RETRIEVAL"
        echo "$PARITY_OUT" | head -20
        FAILURES=$((FAILURES + 1))
    fi
fi

echo ""

# ── 2. Embedding model alignment ─────────────────────────────────────────────
echo "-- Embedding model alignment"
EXPECTED_MODEL="Alibaba-NLP/gte-Qwen2-1.5B-instruct"
EXPECTED_DIM="1536"

ENV_MODEL=$(grep "^DOCUMENT_ENCODER_MODEL=" "$ENV_FILE" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '"' || echo "NOT_SET")
ENV_DIM=$(grep "^DOC_EMBEDDING_DIM=\|^EMBEDDING_DIM=" "$ENV_FILE" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '"' || echo "NOT_SET")

DB_MODEL=$(docker exec onyx-db psql -U postgres -d postgres -tAc \
    "SELECT model_name FROM search_settings ORDER BY id DESC LIMIT 1;" 2>/dev/null | tr -d ' ' || echo "ERROR")
DB_DIM=$(docker exec onyx-db psql -U postgres -d postgres -tAc \
    "SELECT model_dim FROM search_settings ORDER BY id DESC LIMIT 1;" 2>/dev/null | tr -d ' ' || echo "ERROR")

if [[ "$ENV_MODEL" == "$EXPECTED_MODEL" ]]; then
    green "  PASS  .env DOCUMENT_ENCODER_MODEL = $ENV_MODEL"
else
    red   "  FAIL  .env DOCUMENT_ENCODER_MODEL = $ENV_MODEL (expected $EXPECTED_MODEL)"
    FAILURES=$((FAILURES + 1))
fi

if [[ "$ENV_DIM" == "$EXPECTED_DIM" ]]; then
    green "  PASS  .env embedding dim = $ENV_DIM"
else
    red   "  FAIL  .env embedding dim = $ENV_DIM (expected $EXPECTED_DIM)"
    FAILURES=$((FAILURES + 1))
fi

if [[ "$DB_MODEL" == "$EXPECTED_MODEL" ]]; then
    green "  PASS  DB search_settings model = $DB_MODEL"
else
    red   "  FAIL  DB search_settings model = $DB_MODEL (expected $EXPECTED_MODEL)"
    FAILURES=$((FAILURES + 1))
fi

if [[ "$DB_DIM" == "$EXPECTED_DIM" ]]; then
    green "  PASS  DB search_settings dim = $DB_DIM"
else
    red   "  FAIL  DB search_settings dim = $DB_DIM (expected $EXPECTED_DIM)"
    FAILURES=$((FAILURES + 1))
fi

echo ""

# ── 3. Minimal search probe ───────────────────────────────────────────────────
echo "-- Onyx search API probe"
ONYX_API_KEY=$(grep "^ONYX_API_KEY=" "$ENV_FILE" 2>/dev/null | cut -d= -f2- | tr -d '"' || echo "")

if [[ -z "$ONYX_API_KEY" ]]; then
    warn "  SKIP  ONYX_API_KEY not set in $ENV_FILE — skipping search probe"
else
    SEARCH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST http://localhost:3000/api/search/send-search-message \
        -H "Authorization: Bearer $ONYX_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"search_query":"test","num_hits":1,"include_content":false,"stream":false}' \
        2>/dev/null || echo "000")
    if [[ "$SEARCH_STATUS" == "200" ]]; then
        green "  PASS  /api/search/send-search-message = 200"
    else
        red   "  FAIL  /api/search/send-search-message = $SEARCH_STATUS"
        FAILURES=$((FAILURES + 1))
    fi
fi

echo ""

# ── Summary ───────────────────────────────────────────────────────────────────
if [[ "$FAILURES" -eq 0 ]]; then
    green "=== Preflight PASSED — safe to reindex ==="
    exit 0
else
    red "=== Preflight FAILED ($FAILURES issue(s)) — resolve before reindexing ==="
    echo ""
    echo "See docs/ops/deployment-reference.md for the pre-reindex checklist."
    exit 1
fi
