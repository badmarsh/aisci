#!/usr/bin/env python3
"""
Full migration to optimal local RAG stack:
- Embedding: Alibaba-NLP/gte-Qwen2-1.5B-instruct (1536-dim, local model-server)
- Contextual RAG: gemma2:27b via Ollama (local, best quality)
- Multipass indexing: enabled
- Reranking: handled via env var RERANK_MODEL_NAME in compose (separate step)

This script:
1. Creates a model_configuration row for gemma2:27b via Ollama
2. Creates a new search_settings row (FUTURE) with Alibaba 1536-dim + contextual RAG + gemma2
3. Sets the new row as the migration target (PRESENT current row goes PAST on next restart)
"""
import subprocess
import sys

def psql(q):
    r = subprocess.run(
        ["docker", "exec", "onyx-db", "psql", "-U", "postgres", "-d", "postgres", "-c", q],
        capture_output=True, text=True
    )
    print("OUT:", r.stdout.strip()[:500] if r.stdout.strip() else "(no output)")
    if r.returncode != 0:
        print("ERR:", r.stderr[:300])
    return r.stdout, r.returncode

def psql_val(q):
    r = subprocess.run(
        ["docker", "exec", "onyx-db", "psql", "-U", "postgres", "-d", "postgres", "-tAc", q],
        capture_output=True, text=True
    )
    return r.stdout.strip()

print("=== STEP 1: Create model_configuration for gemma2:27b via ollama_chat (provider id=6) ===")
# Check if it already exists
existing = psql_val("SELECT id FROM model_configuration WHERE name='gemma2-27b-contextual' LIMIT 1;")
if existing:
    gemma_config_id = existing
    print(f"Already exists: model_configuration id={gemma_config_id}")
else:
    out, rc = psql("""
        INSERT INTO model_configuration 
            (llm_provider_id, name, is_visible, max_input_tokens, supports_image_input, display_name, model_name)
        VALUES 
            (6, 'gemma2-27b-contextual', false, 8192, false, 'Local Gemma2:27b (Contextual RAG)', 'gemma2:27b')
        RETURNING id;
    """)
    gemma_config_id = psql_val("SELECT id FROM model_configuration WHERE name='gemma2-27b-contextual' LIMIT 1;")
    print(f"Created model_configuration id={gemma_config_id}")

print(f"\n=== STEP 2: Create new search_settings FUTURE row for Alibaba 1536-dim ===")
# Check if it already exists (to be idempotent)
existing_ss = psql_val("SELECT id FROM search_settings WHERE model_name='Alibaba-NLP/gte-Qwen2-1.5B-instruct' AND status='FUTURE' LIMIT 1;")
if existing_ss:
    new_ss_id = existing_ss
    print(f"Already exists FUTURE row: id={new_ss_id}")
else:
    out, rc = psql(f"""
        INSERT INTO search_settings 
            (model_name, model_dim, normalize, query_prefix, passage_prefix, index_name, 
             status, multipass_indexing, embedding_precision, enable_contextual_rag, 
             switchover_type, contextual_rag_model_configuration_id)
        VALUES 
            ('Alibaba-NLP/gte-Qwen2-1.5B-instruct', 1536, true,
             'Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery: ',
             '',
             'danswer_chunk_alibaba_nlp_gte_qwen2_1_5b_instruct',
             'FUTURE', true, 'FLOAT', true,
             'reindex', {gemma_config_id})
        RETURNING id;
    """)
    new_ss_id = psql_val("SELECT id FROM search_settings WHERE model_name='Alibaba-NLP/gte-Qwen2-1.5B-instruct' AND status='FUTURE' LIMIT 1;")
    print(f"Created FUTURE search_settings id={new_ss_id}")

print(f"\n=== STEP 3: Set FUTURE as PRESENT (trigger reindex) ===")
print("Setting current PRESENT (id=26) -> PAST")
psql("UPDATE search_settings SET status='PAST' WHERE status='PRESENT';")

print(f"Setting new row (id={new_ss_id}) -> PRESENT")
psql(f"UPDATE search_settings SET status='PRESENT' WHERE id={new_ss_id};")

print("\n=== Final state ===")
psql("SELECT id, model_name, model_dim, status, enable_contextual_rag, multipass_indexing, contextual_rag_model_configuration_id FROM search_settings ORDER BY id;")

print("\n=== DONE ===")
print("Next steps:")
print("1. Restart API server + background worker to pick up new search_settings")
print("2. Add RERANK_MODEL_NAME=BAAI/bge-reranker-v2-m3 to compose + env")
print("3. Trigger connector runs to reindex all documents")
