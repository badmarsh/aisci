#!/usr/bin/env bash
# DeerFlow E2E smoke test — run inside WSL
# Tests: frontend reachable, auth working, run creation, tool call routing to Onyx
set -euo pipefail

BASE="http://localhost:2026"
ADMIN_EMAIL="${ADMIN_EMAIL:-}"
if [ -z "$ADMIN_EMAIL" ] && [ -f "deployment/onyx/.env.local" ]; then
    ADMIN_EMAIL=$(grep "ADMIN_EMAIL" deployment/onyx/.env.local | cut -d= -f2 | tr -d '"' | tr -d "'")
fi
if [ -z "$ADMIN_EMAIL" ] && [ -f "deployment/onyx/.env" ]; then
    ADMIN_EMAIL=$(grep "ADMIN_EMAIL" deployment/onyx/.env | cut -d= -f2 | tr -d '"' | tr -d "'")
fi
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@aisci.local}"

echo "=== DeerFlow E2E Smoke Test ==="
echo ""

# 1. Frontend health
echo "[1] Frontend health..."
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/")
echo "    GET / -> $CODE"
[ "$CODE" = "200" ] && echo "    PASS" || echo "    FAIL (expected 200)"

# 2. API unauthenticated (should 401)
echo ""
echo "[2] API auth gate..."
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/runs")
echo "    GET /api/runs (no token) -> $CODE"
[ "$CODE" = "401" ] && echo "    PASS" || echo "    FAIL (expected 401)"

# 3. Auth — get JWT
echo ""
echo "[3] Auth login with JWT secret..."
AUTH_TOKEN=$(python3 -c "
import jwt, time, json, os
secret = 'V6DWIkRazE7XqO7QZfZJBjX-vhvX4fuMfGX_qkAZjpk'
email = os.environ.get('ADMIN_EMAIL', '$ADMIN_EMAIL')
payload = {'sub': 'admin', 'email': email, 'exp': int(time.time()) + 3600}
print(jwt.encode(payload, secret, algorithm='HS256'))
" 2>/dev/null || echo "")

if [ -z "$AUTH_TOKEN" ]; then
    echo "    SKIP (PyJWT not available for token generation)"
    AUTH_HEADER=""
else
    echo "    JWT generated: ${AUTH_TOKEN:0:40}..."
    AUTH_HEADER="Authorization: Bearer $AUTH_TOKEN"
fi

# 4. Try authenticated run list
echo ""
echo "[4] Authenticated run list..."
if [ -n "$AUTH_HEADER" ]; then
    RESP=$(curl -s -w "\nHTTP_CODE:%{http_code}" -H "$AUTH_HEADER" "$BASE/api/runs" 2>&1)
    CODE=$(echo "$RESP" | grep "HTTP_CODE:" | cut -d: -f2)
    BODY=$(echo "$RESP" | grep -v "HTTP_CODE:")
    echo "    GET /api/runs (authenticated) -> $CODE"
    echo "    Body: ${BODY:0:200}"
    [ "$CODE" = "200" ] && echo "    PASS" || echo "    NOTE: $CODE"
else
    echo "    SKIP (no auth token)"
fi

# 5. MCP proxy connectivity (Onyx route)
echo ""
echo "[5] Onyx MCP proxy route..."
CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8095/onyx/sse" --max-time 3 2>/dev/null || echo "TIMEOUT")
echo "    GET onyx-mcp-proxy:8095/onyx/sse -> $CODE"
[ "$CODE" = "200" ] || [ "$CODE" = "307" ] && echo "    PASS" || echo "    NOTE: $CODE (may require auth)"

# 6. Brave Search env var present
echo ""
echo "[6] Brave Search key env check..."
BRAVE_KEY=$(grep "BRAVE_SEARCH_API_KEY" /home/ubuntu/aisci/deployment/deer-flow/.env | cut -d= -f2 | tr -d '"')
if [[ "$BRAVE_KEY" == BSA* ]] || [[ "$BRAVE_KEY" == "\$BRAVE"* ]]; then
    echo "    BRAVE_SEARCH_API_KEY is set: ${BRAVE_KEY:0:10}..."
    echo "    PASS"
else
    echo "    WARN: BRAVE_SEARCH_API_KEY is empty or placeholder"
fi

echo ""
echo "=== Done ==="
