#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../onyx"

echo "=== Find files with litellm.completion ==="
docker compose exec onyx-background find /app/onyx -name "*.py" -exec grep -l "litellm.completion" {} \;

echo ""
echo "=== LitellmLLM class location ==="
docker compose exec onyx-background find /app/onyx -name "*.py" -exec grep -l "class LitellmLLM" {} \;

echo ""
echo "=== LLMProviderView from_model method ==="
docker compose exec onyx-background find /app/onyx -name "*.py" -exec grep -l "LLMProviderView" {} \; | head -5
