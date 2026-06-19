#!/usr/bin/env python3
"""Trigger reindex of all active connector_credential_pairs for new search_settings."""
import subprocess

def psql(q):
    r = subprocess.run(
        ["docker", "exec", "onyx-db", "psql", "-U", "postgres", "-d", "postgres", "-c", q],
        capture_output=True, text=True
    )
    return r.stdout.strip()

# Show active cc_pairs
print("=== Active connector_credential_pairs ===")
print(psql("""
    SELECT ccp.id, c.name, ccp.status
    FROM connector_credential_pair ccp
    JOIN connector c ON ccp.connector_id = c.id
    WHERE ccp.status = 'ACTIVE'
    ORDER BY ccp.id;
"""))

# Check if background has picked up the new search_settings and queued attempts
print("\n=== All index_attempts (last 10) ===")
print(psql("""
    SELECT ia.id, ia.connector_id, ia.search_settings_id, ia.status, ia.time_created
    FROM index_attempt ia
    ORDER BY ia.id DESC LIMIT 10;
"""))

# Check if there's a "new index" switchover attempt queued
print("\n=== search_settings switchover status ===")
print(psql("""
    SELECT id, model_name, status, switchover_type FROM search_settings ORDER BY id DESC LIMIT 5;
"""))
