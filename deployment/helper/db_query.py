from __future__ import annotations
import subprocess
out = subprocess.check_output([
    "docker", "exec", "-i", "onyx-db", "psql", "-U", "postgres", "-d", "postgres"
], input=b'SELECT id, email, role FROM "user"; SELECT id, api_key_display, api_key, user_id FROM api_key;')
print(out.decode('utf-8'))
