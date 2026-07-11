from __future__ import annotations
import subprocess
out = subprocess.check_output([
    "docker", "exec", "-i", "onyx-db", "psql", "-U", "postgres", "-d", "postgres"
], input=b"\\d llm_provider; SELECT id, name, provider FROM llm_provider;")
print(out.decode('utf-8'))
