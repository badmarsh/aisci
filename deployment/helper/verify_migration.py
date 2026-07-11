#!/usr/bin/env python3
"""Verify final RAG stack state post-migration."""
import subprocess

def psql(q):
    r = subprocess.run(
        ["docker", "exec", "onyx-db", "psql", "-U", "postgres", "-d", "postgres", "-c", q],
        capture_output=True, text=True
    )
    return r.stdout.strip()

print("=== PRESENT search_settings ===")
print(psql("SELECT id, model_name, model_dim, status, enable_contextual_rag, multipass_indexing, contextual_rag_model_configuration_id FROM search_settings WHERE status='PRESENT';"))

print("\n=== model_configuration id=784 (gemma2 contextual) ===")
print(psql("SELECT id, llm_provider_id, name, display_name, model_name FROM model_configuration WHERE id=784;"))

print("\n=== Recent index_attempts ===")
print(psql("SELECT id, connector_id, search_settings_id, status, error_msg, time_started, time_updated FROM index_attempt ORDER BY id DESC LIMIT 5;"))

print("\n=== model server env ===")
import subprocess
r = subprocess.run(["docker", "exec", "onyx-indexing-model-server", "env"], capture_output=True, text=True)
for line in r.stdout.splitlines():
    if any(k in line for k in ["ENCODER", "EMBEDDING", "RERANK", "NORMALIZE"]):
        print(line)
