#!/usr/bin/env python3
"""Investigation and fix for search_settings."""
import subprocess
import json

def psql(query):
    r = subprocess.run(
        ["docker", "exec", "onyx-db", "psql", "-U", "postgres", "-d", "postgres", "-c", query],
        capture_output=True, text=True
    )
    return r.stdout

def docker_exec(container, cmd):
    r = subprocess.run(
        ["docker", "exec", container] + cmd,
        capture_output=True, text=True
    )
    return r.stdout + r.stderr

print("=== All Alibaba rows in search_settings ===")
print(psql("SELECT id, model_name, model_dim, status FROM search_settings WHERE model_name LIKE '%Alibaba%' ORDER BY id;"))

print("=== OpenSearch indices ===")
r = subprocess.run(["docker", "exec", "onyx-opensearch", "curl", "-s", "http://localhost:9200/_cat/indices"],
    capture_output=True, text=True)
print(r.stdout or r.stderr)

print("=== tenant_migration table (enable_opensearch_retrieval) ===")
print(psql("SELECT id, enable_opensearch_retrieval, total_chunks_migrated FROM tenant_migration_record LIMIT 5;"))

# Try to find the correct Alibaba row that matches the OpenSearch index
# The active OpenSearch index should be danswer_chunk_alibaba_nlp_gte_qwen2_1_5b_instruct
# This would correspond to one of the 1536-dim Alibaba rows

# Fix: The row with status PRESENT now should be id=19 (most recent Alibaba) or id=1
# Let's check the opensearch cutover output
print("=== Running cutover check ===")
r = subprocess.run(
    ["python3", "/home/ubuntu/aisci/deployment/helper/onyx_opensearch_cutover.py", "--json"],
    capture_output=True, text=True, cwd="/home/ubuntu/aisci"
)
try:
    data = json.loads(r.stdout)
    print("active_index_name:", data.get("search_settings", {}).get("active_index_name"))
    print("model_name:", data.get("search_settings", {}).get("model_name"))
    print("id:", data.get("search_settings", {}).get("id"))
    print("status:", data.get("search_settings", {}).get("status"))
    print("missing chunks:", data.get("checks", {}).get("missing_count", "N/A"))
except:
    print("stdout:", r.stdout[:500])
    print("stderr:", r.stderr[:200])

# Now look at what alembic version is loaded to understand the mismatch
print("=== Alembic version in DB ===")
print(psql("SELECT version_num FROM alembic_version;"))
