#!/usr/bin/env python3
"""Restore correct search_settings: id=26 (BAAI/bge-m3) is the actual active index.

Investigation shows danswer_chunk_baai_bge_m3 has 670 docs in OpenSearch.
The Alibaba index (danswer_chunk_alibaba_nlp_gte_qwen2_1_5b_instruct) does NOT exist.
So we must restore id=26 to PRESENT.
"""
import subprocess

def psql(query):
    r = subprocess.run(
        ["docker", "exec", "onyx-db", "psql", "-U", "postgres", "-d", "postgres", "-c", query],
        capture_output=True, text=True
    )
    print("STDOUT:", r.stdout)
    if r.stderr:
        print("STDERR:", r.stderr)
    return r.returncode

print("=== Restoring id=26 (BAAI/bge-m3) to PRESENT ===")
psql("UPDATE search_settings SET status = 'PRESENT' WHERE id = 26;")

print("\n=== Final state ===")
psql("SELECT id, model_name, model_dim, status FROM search_settings ORDER BY id;")
