#!/usr/bin/env bash
# ============================================================
# OpenFang dezinfo project -- setup.sh
# Installs 5 agents, 4 workflows, and required skills.
# DOES NOT overwrite your existing config.toml -- instead
# merges only the dezinfo-specific config sections.
#
# Usage:
#   export DASHSCOPE_API_KEY="sk-..."   # DashScope direct endpoint
#   export BRAVE_API_KEY="BSA..."       # optional but recommended
#   bash setup.sh
#
# If you route via OpenRouter instead:
#   export OPENROUTER_API_KEY="sk-or-..."
#   bash setup.sh
#
# Optional env overrides:
#   OPENFANG_BASE_URL   (default: https://dashscope-intl.aliyuncs.com/compatible-mode/v1)
# ============================================================
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "${GREEN}[ok]${NC}  $*"; }
info() { echo -e "${CYAN}[--]${NC}  $*"; }
warn() { echo -e "${YELLOW}[!!]${NC}  $*"; }
die()  { echo -e "${RED}[ERR]${NC} $*" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENFANG_DIR="${HOME}/.openfang"
TMP_DIR="/tmp/openfang"
BASE_URL="${OPENFANG_BASE_URL:-https://dashscope-intl.aliyuncs.com/compatible-mode/v1}"

# ── 0. preflight ──────────────────────────────────────────────
echo ""
echo -e "${BOLD}OpenFang dezinfo project -- setup${NC}"
echo "========================================"

# Accept either DashScope or OpenRouter key
if [[ -n "${DASHSCOPE_API_KEY:-}" ]]; then
  API_KEY="${DASHSCOPE_API_KEY}"
  API_KEY_ENV="DASHSCOPE_API_KEY"
elif [[ -n "${OPENROUTER_API_KEY:-}" ]]; then
  API_KEY="${OPENROUTER_API_KEY}"
  API_KEY_ENV="OPENROUTER_API_KEY"
  BASE_URL="${OPENFANG_BASE_URL:-https://openrouter.ai/api/v1}"
  warn "Using OpenRouter. Models in agent .toml files use DashScope names -- verify they are available on your OpenRouter account."
else
  die "No API key found. Export DASHSCOPE_API_KEY or OPENROUTER_API_KEY first."
fi

[[ -z "${BRAVE_API_KEY:-}" ]] && warn "BRAVE_API_KEY not set. Web search will be limited."

# ── 1. check openfang binary ──────────────────────────────────
info "Checking for openfang binary..."
if ! command -v openfang &>/dev/null; then
  info "Installing OpenFang..."
  curl -fsSL https://get.openfang.ai | sh
  export PATH="${HOME}/.local/bin:${HOME}/bin:${PATH}"
  command -v openfang &>/dev/null || die "openfang binary not found after install. Add it to PATH manually."
  ok "OpenFang installed: $(openfang --version)"
else
  ok "OpenFang already installed: $(openfang --version)"
fi

# ── 2. ensure workspace exists ────────────────────────────────
info "Checking workspace..."
if [[ ! -d "${OPENFANG_DIR}" ]]; then
  openfang init --quick
  ok "Workspace created at ${OPENFANG_DIR}"
else
  ok "Workspace exists at ${OPENFANG_DIR} -- keeping your existing config"
fi
mkdir -p "${TMP_DIR}"

# ── 3. merge dezinfo config sections (no overwrite) ───────────
info "Merging dezinfo config sections into ${OPENFANG_DIR}/config.toml..."
CFG="${OPENFANG_DIR}/config.toml"

# Helper: append a TOML section block only if the header isn't already present
append_section_if_missing() {
  local header="$1"   # e.g. "[knowledge_graph]"
  local block="$2"    # full multi-line block to append
  if grep -qF "${header}" "${CFG}" 2>/dev/null; then
    ok "  ${header} already present -- skipping"
  else
    printf "\n%s\n" "${block}" >> "${CFG}"
    ok "  ${header} added"
  fi
}

append_section_if_missing "[knowledge_graph]" "[knowledge_graph]
enabled = true
backend = \"sqlite\"
path    = \"~/.openfang/knowledge-graph.db\""

append_section_if_missing "[output]" "[output]
dir = \"/tmp/openfang\""

append_section_if_missing "[monitoring]" "[monitoring]
prometheus_port  = 9100
healthcheck_path = \"/health\""

if [[ -n "${BRAVE_API_KEY:-}" ]]; then
  append_section_if_missing "[skills]" "[skills]
search_engine = \"brave\"
brave_api_key = \"${BRAVE_API_KEY}\""
else
  append_section_if_missing "[skills]" "[skills]
search_engine = \"duckduckgo\""
fi

ok "Config merge done"

# ── 4. write API key to .env (additive) ───────────────────────
info "Updating ~/.openfang/.env..."
ENV_FILE="${OPENFANG_DIR}/.env"
touch "${ENV_FILE}"
chmod 600 "${ENV_FILE}"

set_env_key() {
  local key="$1" val="$2"
  if grep -q "^${key}=" "${ENV_FILE}" 2>/dev/null; then
    sed -i "s|^${key}=.*|${key}=${val}|" "${ENV_FILE}"
  else
    echo "${key}=${val}" >> "${ENV_FILE}"
  fi
}

set_env_key "${API_KEY_ENV}" "${API_KEY}"
[[ -n "${BRAVE_API_KEY:-}" ]] && set_env_key "BRAVE_API_KEY" "${BRAVE_API_KEY}"
ok ".env updated (existing keys preserved)"

# ── 5. install skills ─────────────────────────────────────────
info "Installing required skills..."
SKILLS=(
  "humanizer"
  "browser-use"
  "automation-workflows"
  "ontology"
  "youtube-watcher"
  "eric-deep-research-agent"
  "filesystem"
  "news-summary"
  "multi-search-engine"
  "knowledge-digest"
  "self-improvement"
)
for skill in "${SKILLS[@]}"; do
  if openfang skill list 2>/dev/null | grep -q "^${skill}"; then
    ok "  already installed: ${skill}"
  else
    info "  installing: ${skill}"
    openfang skill install "${skill}" \
      && ok "  installed: ${skill}" \
      || warn "  could not install ${skill} -- install manually later"
  fi
done

# ── 6. start / verify daemon ──────────────────────────────────
info "Checking daemon..."
if openfang status &>/dev/null; then
  ok "Daemon already running"
else
  info "Starting daemon..."
  openfang start --detach || warn "Could not auto-start daemon. Run: openfang start"
fi

# ── 7. register agents ────────────────────────────────────────
info "Registering agents..."
AGENTS=("watchdog" "inquisitor" "visual-analyst" "impact-comms" "archivist")
for agent in "${AGENTS[@]}"; do
  TOML="${SCRIPT_DIR}/agents/${agent}.toml"
  [[ ! -f "${TOML}" ]] && warn "  ${TOML} not found -- skipping" && continue
  if openfang agent list 2>/dev/null | grep -q "^${agent}"; then
    ok "  agent already exists: ${agent}"
  else
    openfang agent create --file "${TOML}" \
      && ok "  registered: ${agent}" \
      || warn "  failed to register ${agent}"
  fi
done

# ── 8. register workflows ─────────────────────────────────────
info "Registering workflows..."
WORKFLOWS=(
  "osint-dezinformacia-monitor"
  "coordinated-debunk-engine"
  "meme-deepfake-triage"
  "social-impact-accountability"
)
for wf in "${WORKFLOWS[@]}"; do
  JSON="${SCRIPT_DIR}/workflows/${wf}.json"
  [[ ! -f "${JSON}" ]] && warn "  ${JSON} not found -- skipping" && continue
  if openfang workflow list 2>/dev/null | grep -q "^${wf}"; then
    ok "  workflow already exists: ${wf}"
  else
    openfang workflow register --file "${JSON}" \
      && ok "  registered: ${wf}" \
      || warn "  failed to register ${wf}"
  fi
done

# ── 9. attach cron trigger for watchdog ───────────────────────
info "Attaching cron trigger to watchdog (every 15 min)..."
openfang trigger set watchdog --cron "*/15 * * * *" 2>/dev/null \
  && ok "Cron trigger set" \
  || warn "Could not set cron trigger -- set manually: openfang trigger set watchdog --cron '*/15 * * * *'"

# ── done ──────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}Setup complete!${NC}"
echo "----------------------------------------"
echo -e "  API key env : ${API_KEY_ENV}"
echo -e "  Base URL    : ${BASE_URL}"
echo -e "  Workspace   : ${OPENFANG_DIR}"
echo -e "  Tmp output  : ${TMP_DIR}"
echo ""
echo -e "  Run a monitoring cycle:"
echo -e "    ${CYAN}openfang workflow run osint-dezinformacia-monitor${NC}"
echo -e "  Investigate a claim:"
echo -e "    ${CYAN}openfang workflow run coordinated-debunk-engine \"Claim: ...\"${NC}"
echo -e "  Dashboard:"
echo -e "    ${CYAN}openfang dashboard  # http://127.0.0.1:4200/${NC}"
echo ""
