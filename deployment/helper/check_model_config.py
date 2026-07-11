#!/usr/bin/env python3
"""Get reranking and contextual RAG model configuration details."""
import subprocess

def psql(q):
    r = subprocess.run(
        ["docker", "exec", "onyx-db", "psql", "-U", "postgres", "-d", "postgres", "-c", q],
        capture_output=True, text=True
    )
    return r.stdout

# model_configuration table
print("=== model_configuration table schema ===")
print(psql(r"\d model_configuration"))

print("=== model_configuration id=278 ===")
print(psql("SELECT * FROM model_configuration WHERE id=278;"))

print("=== all model_configurations ===")
print(psql("SELECT * FROM model_configuration LIMIT 20;"))

# Check llm_provider table more thoroughly
print("=== llm_provider table schema ===")
print(psql(r"\d llm_provider"))

print("=== all llm_providers ===")
print(psql("SELECT id, name, provider, model, api_base, api_key IS NOT NULL as has_key FROM llm_provider;"))

# Check search_settings reranking-related fields
print("=== search_settings with reranking ===")
print(psql("SELECT id, model_name, status, enable_contextual_rag, multipass_indexing, contextual_rag_model_configuration_id FROM search_settings ORDER BY id;"))
