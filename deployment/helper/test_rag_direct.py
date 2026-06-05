import requests
import json

BASE_URL = "http://localhost:3000"
api_key = "on_hLxHEO432IFLuDN3psKyxgLH3g35yvvZqOx21yP1Iw__GrPullG5YR0h4ZfJpkTZAvPPqhQ28mXd8cHYNWzThjWOCPGBaYO6vnC8G13FcNf3FAt-PDveEyj6slAKrWLZaBeTu-9inqY-Ty-sc0C5MBMSPPD2_z6DG-n8QCn9tjdmabNNFESJhQ9IH0CeoQZ9VycfU3-HyPUL8YO71LIrRFqs1DWh5vAH6tJsTpq6ybdZFY026gSkRsoRFAX3VJTA"

HEADERS = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 1. Create session
sess_payload = {"persona_id": 2, "description": "Diagnostic Run"}
sess_resp = requests.post(f"{BASE_URL}/api/chat/create-chat-session", headers=HEADERS, json=sess_payload)
print(f"Session Status: {sess_resp.status_code}")
session_id = sess_resp.json().get("chat_session_id")
print(f"Session ID: {session_id}")

# 2. Send message
msg_payload = {
    "chat_session_id": session_id,
    "message": "What is the main topic of the PhD thesis?",
    "parent_message_id": None,
    "file_descriptors": [],
    "prompt_id": None,
    "search_doc_ids": [],
    "query_override": None
}
msg_resp = requests.post(f"{BASE_URL}/api/chat/send-chat-message", headers=HEADERS, json=msg_payload)
print(f"Message Status: {msg_resp.status_code}")

for line in msg_resp.text.strip().split('\n'):
    if line:
        try:
            data = json.loads(line)
            # Print any event info to see what's being returned
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Raw line (unparseable): {line[:100]} | Error: {e}")
