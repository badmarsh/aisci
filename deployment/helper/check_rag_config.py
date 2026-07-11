#!/usr/bin/env python3
"""Investigate Onyx search_settings and contextual RAG configuration."""
import subprocess

def psql(q):
    r = subprocess.run(
        ["docker", "exec", "onyx-db", "psql", "-U", "postgres", "-d", "postgres", "-c", q],
        capture_output=True, text=True
    )
    return r.stdout

# Search settings columns — what's available
print("=== search_settings columns ===")
print(psql(r"\d search_settings"))

# Current PRESENT row full detail
print("=== PRESENT search_settings (full) ===")
print(psql("SELECT * FROM search_settings WHERE status='PRESENT';"))

# LLM providers
print("=== LLM providers ===")
print(psql("SELECT id, name, provider, model, fast_default_model_name, default_model_name FROM llm_provider LIMIT 10;"))

# Check if connector_credential_pair has contextual RAG flags
print("=== connector contextual rag ===")
print(psql("SELECT column_name FROM information_schema.columns WHERE table_name='connector_credential_pair' AND column_name ILIKE '%context%';"))

# Global settings
print("=== key global settings ===")
print(psql("SELECT name, value FROM user_global_setting LIMIT 30;"))
