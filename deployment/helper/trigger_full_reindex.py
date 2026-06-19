#!/usr/bin/env python3
"""Trigger reindex for all active cc_pairs via Onyx API."""
import subprocess, json, time

def psql_val(q):
    r = subprocess.run(
        ["docker", "exec", "onyx-db", "psql", "-U", "postgres", "-d", "postgres", "-tAc", q],
        capture_output=True, text=True
    )
    return r.stdout.strip()

def psql(q):
    r = subprocess.run(
        ["docker", "exec", "onyx-db", "psql", "-U", "postgres", "-d", "postgres", "-c", q],
        capture_output=True, text=True
    )
    return r.stdout.strip()

# Get ONYX_API_KEY from env file
api_key = None
with open("/home/ubuntu/aisci/deployment/onyx/.env") as f:
    for line in f:
        if line.startswith("ONYX_API_KEY="):
            api_key = line.strip().split("=", 1)[1]
            break

print(f"API key: {'found' if api_key else 'MISSING'}")

# Get active cc_pair IDs
cc_pairs = psql_val("""
    SELECT string_agg(id::text, ',') FROM connector_credential_pair WHERE status='ACTIVE';
""")
print(f"Active cc_pairs: {cc_pairs}")

# Trigger run via API for each cc_pair
for cc_id in cc_pairs.split(","):
    cc_id = cc_id.strip()
    if not cc_id:
        continue
    
    result = subprocess.run([
        "docker", "exec", "onyx-api-server",
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "-X", "POST",
        f"http://localhost:8080/api/manage/admin/connector/{cc_id}/run_once",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", '{"from_beginning": true}'
    ], capture_output=True, text=True)
    print(f"  cc_pair {cc_id}: HTTP {result.stdout.strip()}")
    time.sleep(0.5)

# Wait 5s then check attempts
time.sleep(5)
print("\n=== Index attempts after trigger ===")
print(psql("""
    SELECT ia.id, ia.connector_id, ia.search_settings_id, ia.status, ia.time_created
    FROM index_attempt ia
    ORDER BY ia.id DESC LIMIT 8;
"""))
