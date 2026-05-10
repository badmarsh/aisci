import subprocess
cmd = "docker exec onyx-db psql -U postgres -c \"SELECT id, semantic_id FROM document WHERE id IN (2132, 2136, 2137, 2139, 2135);\""
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(result.stdout)
print("STDERR:")
print(result.stderr)
