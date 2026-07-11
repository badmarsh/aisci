from __future__ import annotations
import subprocess
out = subprocess.check_output([
    "docker", "exec", "-i", "onyx-db", "psql", "-U", "postgres", "-d", "postgres"
], input=b'UPDATE "user" SET role = \'ADMIN\' WHERE id = \'980fd80c-a607-4f03-915d-f0f439b8d144\'; SELECT id, email, role FROM "user";')
print(out.decode('utf-8'))
