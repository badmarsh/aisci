#!/usr/bin/env python3
"""Platform health check script - session 2026-06-19"""
import subprocess
import json
import sys
import time

def run(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return "(timeout)"
    except Exception as e:
        return f"(error: {e})"

print("=== Waiting 20s for services to stabilize ===")
time.sleep(20)

print("\n=== OPENSEARCH HEALTH ===")
out = run("docker exec onyx-opensearch curl -s http://localhost:9200/_cluster/health")
print(out)
try:
    d = json.loads(out.strip())
    print("Status:", d.get("status"), "| unassigned_shards:", d.get("unassigned_shards"))
except:
    print("Could not parse JSON")

print("\n=== OPENSEARCH CLUSTER SETTINGS ===")
out = run("docker exec onyx-opensearch curl -s http://localhost:9200/_cluster/settings")
try:
    d = json.loads(out.strip())
    cluster = d.get("persistent", {}).get("cluster", {})
    print(json.dumps(cluster, indent=2))
except:
    print(out[:500])

print("\n=== LITELLM HEALTH ===")
out = run("curl -s http://localhost:4001/health")
try:
    d = json.loads(out.strip())
    print("healthy:", d.get("healthy_count"), "| unhealthy:", d.get("unhealthy_count"))
    for m in d.get("unhealthy_endpoints", []):
        err = str(m.get("error", ""))[:80]
        print("  UNHEALTHY:", m.get("model"), "|", err)
except:
    print("Could not parse LiteLLM response:", out[:200])

print("\n=== OLLAMA MODELS ===")
print(run("docker exec onyx-ollama ollama list"))

print("\n=== ONYX API HEALTH ===")
print(run("curl -s http://localhost:3000/api/health"))

print("\n=== BACKGROUND LOGS: vision ===")
out = run("docker logs onyx-background --since 15m 2>&1 | grep -i 'vision-capable\\|no vision' | tail -10")
print(out if out.strip() else "(no vision warnings)")

print("\n=== BACKGROUND LOGS: recent errors ===")
print(run("docker logs onyx-background --since 5m 2>&1 | grep -i 'error\\|fail\\|warn' | tail -20"))

print("\n=== SEARCH SETTINGS (DB) ===")
print(run("docker exec onyx-db psql -U postgres -d postgres -c 'SELECT id, model_name, model_dim, status FROM search_settings ORDER BY id;'"))

print("\n=== DISK SPACE ===")
print(run("df -h /"))

print("\n=== CHECK_HEALTH SCRIPT ===")
print(run("bash /home/ubuntu/aisci/deployment/onyx/monitoring/check_health.sh 2>&1", timeout=60))
