#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------------
# 1️⃣  Path to the MCP configuration file
# ------------------------------------------------------------------
MCP_CFG="$HOME/.openfang/mcp_config.yaml"

# ------------------------------------------------------------------
# 2️⃣  Ensure the directory exists
# ------------------------------------------------------------------
mkdir -p "$(dirname "$MCP_CFG")"

# ------------------------------------------------------------------
# 3️⃣  Write (or overwrite) the filesystem server block
# ------------------------------------------------------------------
cat > "$MCP_CFG" <<'EOF'
[mcp_servers]
  [[mcp_servers]]
  name = "filesystem"
  timeout_secs = 30

  [mcp_servers.transport]
  type = "stdio"
  command = "npx"
  args = ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
EOF

echo "✅  Updated $MCP_CFG with the filesystem MCP server."
