#!/usr/bin/env bash
# ------------------------------------------------------------
# setup_onyx_mcp.sh  –  One‑click installation for the Onyx MCP service
# ------------------------------------------------------------

set -euo pipefail

# ---------- 1️⃣  Secrets (replace if you need different values) ----------
if [ -z "${ONYX_API_KEY:-}" ]; then
  echo "Set ONYX_API_KEY in the environment before running this setup helper." >&2
  exit 1
fi
MCP_PROXY_AUTH_TOKEN="8339e2a295755e9988ff392e4430914a"

# ---------- 2️⃣  Paths ----------
HOME_DIR="$HOME"
OPENFANG_DIR="${HOME_DIR}/.openfang"
ENV_FILE="${OPENFANG_DIR}/env.sh"
BIN_DIR="${OPENFANG_DIR}/bin"
SERVICE_DIR="${OPENFANG_DIR}/services"
REGISTRY_FILE="${OPENFANG_DIR}/registry.json"

# ---------- 3️⃣  Ensure directories exist ----------
mkdir -p "$OPENFANG_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$SERVICE_DIR"

# ---------- 4️⃣  Write environment variables ----------
{
  echo "export ONYX_API_KEY=\"$ONYX_API_KEY\""
  echo "export MCP_PROXY_AUTH_TOKEN=\"$MCP_PROXY_AUTH_TOKEN\""
} > "$ENV_FILE"
chmod 600 "$ENV_FILE"

# Load them for the current session
source "$ENV_FILE"

# ---------- 5️⃣  Bash wrapper (onyx-mcp.sh) ----------
WRAPPER="${BIN_DIR}/onyx-mcp.sh"
cat > "$WRAPPER" <<'EOF'
#!/usr/bin/env bash
# Wrapper for the Onyx MCP SSE endpoint – uses ONYX_API_KEY from the environment
# Usage: onyx-mcp.sh "your prompt"
set -euo pipefail

PROMPT="${1:-}"
if [ -z "$PROMPT" ]; then
  echo "Usage: $0 \"your prompt\""
  exit 1
fi

REQ=$(jq -nc --arg q "$PROMPT" '{"messages":[{"role":"user","content":$q}]}')

curl -N -s "http://127.0.0.1:8095/onyx/sse" \
  -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ONYX_API_KEY}" \
  -d "$REQ" | awk '/^data:/ {print substr($0,7)}' | jq -r '.content'
EOF
chmod +x "$WRAPPER"

# ---------- 6️⃣  Service descriptor ----------
SERVICE_JSON="${SERVICE_DIR}/onyx-mcp.json"
cat > "$SERVICE_JSON" <<'EOF'
{
  "name": "onyx",
  "description": "Onyx knowledge-base MCP (SSE transport) behind the local proxy",
  "base_url": "http://127.0.0.1:8095/onyx/sse",
  "auth_type": "Bearer",
  "env_var": "ONYX_API_KEY",
  "default_payload": {
    "messages": [{"role":"user","content":""}]
  }
}
EOF

# ---------- 7️⃣  Register the service ----------
if [ ! -f "$REGISTRY_FILE" ]; then
  echo "{}" > "$REGISTRY_FILE"
fi
jq '.onyx = {path: "'"$SERVICE_JSON"'"}' "$REGISTRY_FILE" > "${REGISTRY_FILE}.tmp" && mv "${REGISTRY_FILE}.tmp" "$REGISTRY_FILE"

# ---------- 8️⃣  Quick verification ----------
echo "=== Health check (expect 200) ==="
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8095/onyx/

echo "=== Registry entry ==="
jq .onyx "$REGISTRY_FILE"

echo "=== Test wrapper ==="
onyx-mcp.sh "What is the purpose of the Onyx knowledge base?"
echo
echo "✅ Setup finished."
