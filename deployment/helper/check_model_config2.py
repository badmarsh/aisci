#!/usr/bin/env python3
"""Get full details on model_configuration and llm_provider for contextual RAG."""
import subprocess

def psql(q):
    r = subprocess.run(
        ["docker", "exec", "onyx-db", "psql", "-U", "postgres", "-d", "postgres", "-c", q],
        capture_output=True, text=True
    )
    return r.stdout

print("=== model_configuration id=278 full ===")
print(psql("SELECT * FROM model_configuration WHERE id=278;"))

print("=== model_configuration id=262 full ===")
print(psql("SELECT * FROM model_configuration WHERE id=262;"))

print("=== model_configuration id=126 full ===")
print(psql("SELECT * FROM model_configuration WHERE id=126;"))

print("=== model_configuration id=132 full ===")
print(psql("SELECT * FROM model_configuration WHERE id=132;"))

print("=== all llm_providers (name, provider, model, api_base) ===")
print(psql("SELECT id, name, provider, default_model_name, api_base FROM llm_provider;"))

print("=== search_settings id=19 (old Alibaba+contextual) full ===")
print(psql("SELECT * FROM search_settings WHERE id=19;"))

# Also check reranking — it's in search_settings or elsewhere?
print("=== search_settings columns with 'rerank' in name ===")
print(psql("SELECT column_name FROM information_schema.columns WHERE table_name='search_settings' AND column_name ILIKE '%rerank%';"))
