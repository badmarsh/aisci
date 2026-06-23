#!/usr/bin/env python3
"""Fix search_settings regression: restore id=10 (Alibaba 1536-dim) as PRESENT.

The Onyx stack was recently restarted and created a new search_settings row (id=26)
for BAAI/bge-m3 (1024-dim). The canonical model is Alibaba-NLP/gte-Qwen2-1.5B-instruct
(1536-dim) with the existing active OpenSearch index danswer_chunk_alibaba_nlp_gte_qwen2_1_5b_instruct.

This script:
1. Confirms the current state
2. Sets id=26 -> PAST and id=10 -> PRESENT
3. Verifies the fix
"""
import subprocess
import json
import sys

def psql(query):
    r = subprocess.run(
        ["docker", "exec", "onyx-db", "psql", "-U", "postgres", "-d", "postgres", "-c", query],
        capture_output=True, text=True
    )
    print("STDOUT:", r.stdout)
    if r.stderr:
        print("STDERR:", r.stderr)
    return r.returncode

print("=== BEFORE: Search settings state ===")
psql("SELECT id, model_name, model_dim, status FROM search_settings ORDER BY id;")

print("\n=== CHECKING: Active OpenSearch indices ===")
r = subprocess.run(
    ["docker", "exec", "onyx-opensearch", "curl", "-s", "http://localhost:9200/_cat/indices?v&h=index,docs.count,store.size"],
    capture_output=True, text=True
)
print(r.stdout)

print("\n=== FIXING: Restore Alibaba model (id=10) as PRESENT, set BAAI (id=26) to PAST ===")
rc = psql("UPDATE search_settings SET status = 'PAST' WHERE id = 26;")
if rc != 0:
    print("ERROR: Could not set id=26 to PAST")
    sys.exit(1)

rc = psql("UPDATE search_settings SET status = 'PRESENT' WHERE id = 10;")
if rc != 0:
    print("ERROR: Could not set id=10 to PRESENT")
    sys.exit(1)

print("\n=== AFTER: Search settings state ===")
psql("SELECT id, model_name, model_dim, status FROM search_settings ORDER BY id;")

print("\n=== NOTE: Onyx API server must be restarted to pick up new search_settings ===")
print("Run: docker compose -f deployment/onyx/docker-compose.yml restart api_server background")
