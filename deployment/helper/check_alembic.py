#!/usr/bin/env python3
"""Check alembic version and model state."""
import subprocess

# Check the actual alembic head from the running container
r = subprocess.run(
    ["docker", "exec", "onyx-api-server", "python3", "-c",
     "import subprocess; r=subprocess.run(['alembic', 'heads'], capture_output=True, text=True, cwd='/app'); print(r.stdout); print(r.stderr)"],
    capture_output=True, text=True
)
print("=== Alembic heads (container) ===")
print(r.stdout[:2000], r.stderr[:500])

# Check the DB version
r2 = subprocess.run(
    ["docker", "exec", "onyx-db", "psql", "-U", "postgres", "-d", "postgres",
     "-c", "SELECT version_num FROM alembic_version;"],
    capture_output=True, text=True
)
print("=== DB alembic version ===")
print(r2.stdout)

# Check API server logs for migration messages
r3 = subprocess.run(
    ["docker", "logs", "onyx-api-server", "--tail", "100"],
    capture_output=True, text=True
)
migration_lines = [l for l in r3.stdout.split('\n') if 'alembic' in l.lower() or 'migration' in l.lower() or 'upgrade' in l.lower()]
print("=== API server migration log lines ===")
print('\n'.join(migration_lines[:20]) if migration_lines else "(none)")

# Check what the preflight script expected
r4 = subprocess.run(
    ["grep", "-n", "alembic\|ea418a\|01c63", "/home/ubuntu/aisci/deployment/onyx/preflight_check.sh"],
    capture_output=True, text=True
)
print("\n=== Preflight alembic checks ===")
print(r4.stdout[:1000])
