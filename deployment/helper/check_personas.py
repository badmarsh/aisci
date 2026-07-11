from __future__ import annotations
import subprocess
out = subprocess.check_output([
    "docker", "exec", "-i", "onyx-db", "psql", "-U", "postgres", "-d", "postgres"
], input=b"SELECT id, name FROM persona;")
print(out.decode('utf-8'))
