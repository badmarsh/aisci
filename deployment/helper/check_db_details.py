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

print("=== Search Settings ===")
print(run_sql("SELECT id, model_name, status, provider_type, multipass_indexing, enable_contextual_rag FROM search_settings;"))

print("=== Document Count ===")
print(run_sql("SELECT count(*) FROM document;"))

print("=== Index Attempt Counts ===")
print(run_sql("SELECT search_settings_id, status, count(*), sum(total_docs_indexed), sum(new_docs_indexed) FROM index_attempt GROUP BY search_settings_id, status ORDER BY search_settings_id;"))

print("=== Connector Status ===")
print(run_sql("SELECT id, name, source, status FROM connector;"))
print(run_sql("SELECT * FROM connector_credential_pair;"))
