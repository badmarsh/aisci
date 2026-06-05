#!/usr/bin/env bash
# Quick RAG test via Onyx API
set -euo pipefail

API_BASE="http://localhost"
# Get the first admin user's API key or use basic auth token
# Try the search endpoint with a test query

echo "=== Testing Onyx search (semantic RAG) ==="
curl -s -X POST "$API_BASE/api/query/search" \
  -H "Content-Type: application/json" \
  -b "fastapiusersauth=$(cat /tmp/onyx_cookie 2>/dev/null || echo '')" \
  -d '{
    "query": "What is the main topic of the PhD thesis?",
    "search_type": "semantic",
    "human_selected_filters": null,
    "enable_auto_detect_filters": false,
    "offset": 0,
    "limit": 3
  }' 2>&1 | python3 -m json.tool 2>/dev/null | head -80 || \
curl -s -X POST "$API_BASE/api/query/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic of the PhD thesis?",
    "search_type": "semantic",
    "human_selected_filters": null,
    "enable_auto_detect_filters": false,
    "offset": 0,
    "limit": 3
  }' 2>&1 | head -80

echo ""
echo "=== Testing LiteLLM health ==="
curl -s http://localhost/litellm/health 2>&1 | python3 -m json.tool 2>/dev/null | head -40 || \
curl -s http://localhost:4001/health 2>&1 | head -20

echo ""
echo "=== Testing LiteLLM models list ==="
curl -s http://localhost/litellm/v1/models \
  -H "Authorization: Bearer any-key" 2>&1 | python3 -m json.tool 2>/dev/null | grep '"id"' | head -20 || \
curl -s http://localhost:4001/v1/models \
  -H "Authorization: Bearer any-key" 2>&1 | python3 -m json.tool 2>/dev/null | grep '"id"' | head -20
