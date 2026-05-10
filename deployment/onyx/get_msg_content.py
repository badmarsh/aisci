import subprocess
import json

cmd = "docker exec onyx-db psql -U postgres -c \"SELECT id, message FROM chat_message WHERE id IN (614, 617);\""
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(result.stdout)
