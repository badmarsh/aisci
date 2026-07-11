from __future__ import annotations
import subprocess
out = subprocess.check_output([
    "docker", "exec", "-i", "onyx-db", "psql", "-U", "postgres", "-d", "postgres"
], input=b"\\d api_key; SELECT * FROM api_key;")
print(out.decode('utf-8'))
