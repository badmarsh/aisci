from __future__ import annotations
import subprocess
import json

def run_sql(query):
    try:
        out = subprocess.check_output([
            "docker", "exec", "-i", "onyx-db", "psql", "-U", "postgres", "-d", "postgres", "-c", query
        ])
        return out.decode('utf-8')
    except Exception as e:
        return str(e)

print("=== Documents in DB ===")
print(run_sql("SELECT id, semantic_id, chunk_count FROM document;"))

print("=== Index Attempts for settings 19 ===")
print(run_sql("SELECT id, status, total_docs_indexed, new_docs_indexed, error_msg, time_started, time_updated FROM index_attempt WHERE search_settings_id=19 ORDER BY id DESC;"))
