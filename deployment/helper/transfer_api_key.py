from __future__ import annotations
import subprocess
out = subprocess.check_output([
    "docker", "exec", "-i", "onyx-db", "psql", "-U", "postgres", "-d", "postgres"
], input=b"UPDATE api_key SET user_id = '24120fa3-ae77-410c-b4db-86b0f7b885f4' WHERE id = 1;")
print(out.decode('utf-8'))
