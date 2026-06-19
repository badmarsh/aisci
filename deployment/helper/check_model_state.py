#!/usr/bin/env python3
"""Check encoder model info and what the model-server is actually running."""
import subprocess
import json

# First check the actual loaded model from the indexing model server logs
r = subprocess.run(
    ["docker", "logs", "onyx-indexing-model-server", "--tail", "50"],
    capture_output=True, text=True
)
print("=== INDEXING MODEL SERVER LAST 50 LINES ===")
print(r.stdout[-3000:] if r.stdout else r.stderr[-1000:])

# Check background worker for the model info
r2 = subprocess.run(
    ["docker", "logs", "onyx-background", "--since", "5m"],
    capture_output=True, text=True
)
print("\n=== BACKGROUND WORKER MODEL REFERENCES (last 5m) ===")
lines = r2.stdout.split('\n')
model_lines = [l for l in lines if 'model' in l.lower() and ('baai' in l.lower() or 'alibaba' in l.lower() or 'embed' in l.lower())]
print('\n'.join(model_lines[:20]) if model_lines else "(none)")

# Check the env in the model server container
r3 = subprocess.run(
    ["docker", "exec", "onyx-indexing-model-server", "env"],
    capture_output=True, text=True
)
env_lines = [l for l in r3.stdout.split('\n') if 'MODEL' in l or 'EMBED' in l or 'ENCODER' in l]
print("\n=== MODEL SERVER ENV VARS ===")
print('\n'.join(env_lines))

# Run the cutover check again now that id=26 is restored
print("\n=== CUTOVER CHECK (current state) ===")
r4 = subprocess.run(
    ["python3", "/home/ubuntu/aisci/deployment/helper/onyx_opensearch_cutover.py", "--json"],
    capture_output=True, text=True, cwd="/home/ubuntu/aisci"
)
try:
    data = json.loads(r4.stdout)
    ss = data.get("search_settings", {})
    print(f"active_index: {ss.get('active_index_name')}")
    print(f"model: {ss.get('model_name')}, dim: {ss.get('model_dim')}")
    print(f"status: {ss.get('status')}")
    chk = data.get("checks", {})
    print(f"missing_chunks: {chk.get('missing_count', 'N/A')}")
    print(f"ready_for_cutover: {data.get('ready_for_cutover')}")
except Exception as e:
    print(f"Parse error: {e}")
    print(r4.stdout[:1000])
