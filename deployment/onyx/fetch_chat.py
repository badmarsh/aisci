import subprocess

cmd = "docker exec onyx-db psql -U postgres -x -c \"SELECT message_type, message FROM chat_message WHERE chat_session_id = 'bbe787c0-af55-4022-a3f2-1f0a08d25b41' ORDER BY id ASC;\""
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
with open("chat_output.txt", "w") as f:
    f.write(result.stdout)
