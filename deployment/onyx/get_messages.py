import subprocess
import json

cmd = "docker exec onyx-db psql -U postgres -c \"SELECT id, message_type, substring(message from 1 for 100) as msg_preview, citations, error FROM chat_message WHERE chat_session_id = 'bbe787c0-af55-4022-a3f2-1f0a08d25b41' ORDER BY id;\""
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(result.stdout)
