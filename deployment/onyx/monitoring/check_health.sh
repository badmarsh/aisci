#!/usr/bin/env bash
# Onyx runtime health check — alembic drift, indexing failures, Redis queue depth.
# Exit 0 = all green. Exit 1 = one or more checks failed.
# Run manually or from cron; output is human-readable and CI-parseable.

set -euo pipefail

COMPOSE_DIR="$(cd "$(dirname "$0")/../.." && pwd)/onyx"
EXPECTED_ALEMBIC_HEAD="ea418a384b9d"
FAILURES=0

red()   { printf '\033[0;31m%s\033[0m\n' "$*"; }
green() { printf '\033[0;32m%s\033[0m\n' "$*"; }
warn()  { printf '\033[0;33m%s\033[0m\n' "$*"; }

check() {
    local label="$1"; shift
    if "$@" 2>/dev/null; then
        green "  PASS  $label"
    else
        red   "  FAIL  $label"
        FAILURES=$((FAILURES + 1))
    fi
}

echo "=== Onyx Health Check $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

# ── 1. Alembic version drift ──────────────────────────────────────────────────
echo ""
echo "-- Alembic version"
ACTUAL=$(docker exec onyx-db psql -U postgres -d postgres -tAc \
    "SELECT version_num FROM alembic_version LIMIT 1;" 2>/dev/null || echo "ERROR")
if [[ "$ACTUAL" == "$EXPECTED_ALEMBIC_HEAD" ]]; then
    green "  PASS  alembic_version = $ACTUAL"
else
    red   "  FAIL  alembic_version = $ACTUAL (expected $EXPECTED_ALEMBIC_HEAD)"
    FAILURES=$((FAILURES + 1))
fi

# ── 2. Index attempt failures in last 24h ─────────────────────────────────────
echo ""
echo "-- Index attempt failures (last 24h)"
FAIL_COUNT=$(docker exec onyx-db psql -U postgres -d postgres -tAc \
    "SELECT COUNT(*) FROM index_attempt
     WHERE status = 'failed'
       AND time_started > NOW() - INTERVAL '24 hours';" 2>/dev/null || echo "ERROR")
if [[ "$FAIL_COUNT" == "0" ]]; then
    green "  PASS  0 failed index attempts in last 24h"
else
    red   "  FAIL  $FAIL_COUNT failed index attempt(s) in last 24h"
    docker exec onyx-db psql -U postgres -d postgres -c \
        "SELECT id, connector_id, error_msg, time_started
         FROM index_attempt
         WHERE status = 'failed' AND time_started > NOW() - INTERVAL '24 hours'
         ORDER BY time_started DESC LIMIT 5;" 2>/dev/null || true
    FAILURES=$((FAILURES + 1))
fi

# ── 3. Redis queue depth ──────────────────────────────────────────────────────
echo ""
echo "-- Redis queue depth"
QUEUE_LEN=$(docker exec onyx-redis redis-cli LLEN celery 2>/dev/null || echo "ERROR")
if [[ "$QUEUE_LEN" =~ ^[0-9]+$ ]] && [[ "$QUEUE_LEN" -lt 100 ]]; then
    green "  PASS  celery queue depth = $QUEUE_LEN"
elif [[ "$QUEUE_LEN" =~ ^[0-9]+$ ]]; then
    warn  "  WARN  celery queue depth = $QUEUE_LEN (>= 100, may be backed up)"
else
    red   "  FAIL  could not read Redis queue depth"
    FAILURES=$((FAILURES + 1))
fi

# ── 4. OpenSearch cluster health ──────────────────────────────────────────────
echo ""
echo "-- OpenSearch cluster health"
OS_STATUS=$(docker exec onyx-opensearch curl -s -u "admin:${OPENSEARCH_ADMIN_PASSWORD:-admin}" \
    "http://localhost:9200/_cluster/health" 2>/dev/null \
    | python3 -c "import json,sys; print(json.load(sys.stdin).get('status','ERROR'))" 2>/dev/null \
    || echo "ERROR")
if [[ "$OS_STATUS" == "green" ]]; then
    green "  PASS  OpenSearch cluster status = green"
elif [[ "$OS_STATUS" == "yellow" ]]; then
    warn  "  WARN  OpenSearch cluster status = yellow (replica shards unassigned — normal for single-node)"
else
    red   "  FAIL  OpenSearch cluster status = $OS_STATUS"
    FAILURES=$((FAILURES + 1))
fi

# ── 5. LiteLLM probe ─────────────────────────────────────────────────────────
echo ""
echo "-- LiteLLM health"
LITELLM_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:4001/health/liveliness 2>/dev/null || echo "000")
if [[ "$LITELLM_STATUS" == "200" ]]; then
    green "  PASS  LiteLLM /health/liveliness = 200"
else
    red   "  FAIL  LiteLLM /health/liveliness = $LITELLM_STATUS"
    FAILURES=$((FAILURES + 1))
fi

# ── 6. MCP liveness (Scite + Consensus) ───────────────────────────────────────
# Soft check: missing/expired OAuth tokens are reported but do not fail the
# overall health check, since extracting tokens is a manual operator step.
# Hard failures (proxy unreachable, upstream error) DO bump $FAILURES.
echo ""
echo "-- MCP liveness (Scite + Consensus)"
MCP_REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
if command -v python3 >/dev/null 2>&1 && [[ -f "$MCP_REPO_ROOT/deployment/helper/check_mcp_liveness.py" ]]; then
    if python3 "$MCP_REPO_ROOT/deployment/helper/check_mcp_liveness.py"; then
        : # exit 0 — no hard failures (some probes may still be WARN; that is
          # expected when tokens have not been provisioned)
    else
        red "  FAIL  MCP liveness reported a hard failure (proxy or upstream)"
        FAILURES=$((FAILURES + 1))
    fi
else
    warn "  SKIP  check_mcp_liveness.py not available"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
if [[ "$FAILURES" -eq 0 ]]; then
    green "=== All checks passed ==="
    exit 0
else
    red "=== $FAILURES check(s) failed ==="
    exit 1
fi
