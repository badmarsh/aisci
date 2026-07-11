from __future__ import annotations
import subprocess

def run_sql(query):
    try:
        out = subprocess.check_output([
            "docker", "exec", "-i", "onyx-db", "psql", "-U", "postgres", "-d", "postgres", "-c", query
        ])
        return out.decode('utf-8')
    except Exception as e:
        return str(e)

print("=== Persona 2 ===")
print(run_sql("SELECT * FROM persona WHERE id=2;"))

print("=== Persona 2 Associated Connector Pairs ===")
print(run_sql("SELECT * FROM persona__connector_credential_pair WHERE persona_id=2;"))

print("=== All Personas ===")
print(run_sql("SELECT id, name, description FROM persona;"))
