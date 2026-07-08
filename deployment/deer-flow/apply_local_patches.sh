#!/usr/bin/env bash
# Re-apply all AiSci-local patches to the vendored DeerFlow checkout.
# Run after any clean checkout, container rebuild, or vendor sync.
# See README-local-patches.md for rationale behind each patch.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$SCRIPT_DIR/config.yaml"
UPLOADS="$SCRIPT_DIR/backend/app/gateway/routers/uploads.py"

red()   { printf '\033[0;31m%s\033[0m\n' "$*"; }
green() { printf '\033[0;32m%s\033[0m\n' "$*"; }
warn()  { printf '\033[0;33m%s\033[0m\n' "$*"; }

echo "=== DeerFlow local patch applicator ==="
echo "Working dir: $SCRIPT_DIR"
echo ""

FAILURES=0

# ── Patch 1 & 2 & 4: config.yaml checks ──────────────────────────────────────
echo "-- config.yaml checks"

if [[ ! -f "$CONFIG" ]]; then
    red "  MISSING  $CONFIG — cannot apply config patches"
    FAILURES=$((FAILURES + 1))
else
    # Patch 1: run_events.backend must be db
    if grep -q "backend: db" "$CONFIG" && grep -q "run_events:" "$CONFIG"; then
        green "  OK       run_events.backend = db"
    else
        warn "  NEEDS FIX  run_events.backend is not 'db' — edit $CONFIG"
        warn "             Set run_events.backend: db and remove any checkpointer: block"
        FAILURES=$((FAILURES + 1))
    fi

    # Patch 2: summarization nesting — trim_tokens_to_summarize must NOT be indented under keep:
    # Check that trim_tokens_to_summarize appears at 2-space indent (sibling of keep:), not 4+
    if grep -qP "^  trim_tokens_to_summarize:" "$CONFIG"; then
        green "  OK       summarization nesting correct"
    elif grep -q "trim_tokens_to_summarize:" "$CONFIG"; then
        warn "  NEEDS FIX  trim_tokens_to_summarize is nested inside keep: — fix indentation in $CONFIG"
        FAILURES=$((FAILURES + 1))
    else
        warn "  MISSING  trim_tokens_to_summarize not found in $CONFIG — may need manual review"
    fi

    # Patch 4: NVIDIA models must use NVIDIA_API_BASE
    if grep -A5 "nvidia-qwen3-5-122b" "$CONFIG" 2>/dev/null | grep -q "NVIDIA_API_BASE"; then
        green "  OK       nvidia-qwen3-5-122b uses NVIDIA_API_BASE"
    else
        warn "  NEEDS FIX  nvidia-qwen3-5-122b may be using wrong base_url — check $CONFIG"
        FAILURES=$((FAILURES + 1))
    fi
fi

echo ""

# ── Patch 3: uploads.py permissions ──────────────────────────────────────────
echo "-- uploads.py sandbox permissions"

if [[ ! -f "$UPLOADS" ]]; then
    red "  MISSING  $UPLOADS — cannot verify upload patch"
    FAILURES=$((FAILURES + 1))
else
    # Check that _make_file_sandbox_writable is called unconditionally
    # (i.e., not only inside an `if sync_to_sandbox:` block)
    if grep -q "S_IROTH" "$UPLOADS" && grep -q "S_IWOTH" "$UPLOADS"; then
        green "  OK       _make_file_sandbox_writable sets S_IROTH | S_IWOTH"
    else
        warn "  NEEDS FIX  uploads.py does not set world-readable/writable permissions"
        warn "             Apply patch from README-local-patches.md Patch 3"
        warn "             File: $UPLOADS"
        FAILURES=$((FAILURES + 1))
    fi
fi

echo ""

# ── Summary ───────────────────────────────────────────────────────────────────
if [[ "$FAILURES" -eq 0 ]]; then
    green "=== All patches verified — no action needed ==="
    exit 0
else
    red "=== $FAILURES patch(es) need manual attention ==="
    echo ""
    echo "See deployment/deer-flow/README-local-patches.md for fix instructions."
    echo "See docs/ops/troubleshooting.md for root cause details."
    exit 1
fi
