#!/bin/bash
set -e

echo "=== SEARCH SETTINGS ==="
docker exec onyx-db psql -U postgres -d postgres -c "SELECT id, model_name, model_dim, status FROM search_settings ORDER BY id;"

echo ""
echo "=== INDEX ATTEMPTS IN_PROGRESS ==="
docker exec onyx-db psql -U postgres -d postgres -c "SELECT id, status, connector_credential_pair_id, time_started FROM index_attempt WHERE status='IN_PROGRESS' ORDER BY id DESC LIMIT 5;"

echo ""
echo "=== LITELLM HEALTH ==="
curl -s http://localhost:4001/health > /tmp/litellm_health.json 2>&1 || echo "LiteLLM curl failed"
python3 << 'EOF'
import json
try:
    with open('/tmp/litellm_health.json') as f:
        d = json.load(f)
    print('healthy:', d.get('healthy_count', 'N/A'), '| unhealthy:', d.get('unhealthy_count', 'N/A'))
    for m in d.get('unhealthy_endpoints', []):
        err = str(m.get('error', ''))[:80]
        print('  UNHEALTHY:', m.get('model'), '|', err)
except Exception as e:
    print('Error:', e)
EOF

echo ""
echo "=== DISK SPACE ==="
df -h /

echo ""
echo "=== OPENSEARCH CLUSTER STATE ==="
docker exec onyx-opensearch curl -s http://localhost:9200/_cluster/settings > /tmp/os_settings.json 2>&1 || echo "OS settings curl failed"
python3 << 'EOF'
import json
try:
    with open('/tmp/os_settings.json') as f:
        d = json.load(f)
    print(json.dumps(d.get('persistent', {}).get('cluster', {}), indent=2))
except Exception as e:
    print('Error:', e)
EOF

echo ""
echo "=== OPENSEARCH CLUSTER HEALTH ==="
docker exec onyx-opensearch curl -s http://localhost:9200/_cluster/health

echo ""
echo "=== OLLAMA MODELS ==="
docker exec onyx-ollama ollama list

echo ""
echo "=== ONYX API HEALTH ==="
curl -s http://localhost:3000/api/health

echo ""
echo "=== BACKGROUND LOGS: vision (last 10m) ==="
docker logs onyx-background --since 10m 2>&1 | grep -i 'vision-capable\|no vision' | tail -10 || echo "(no matches)"
