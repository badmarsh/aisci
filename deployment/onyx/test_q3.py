import requests
BASE_URL = "http://localhost:3000"
session = requests.Session()
session.post(
    f"{BASE_URL}/api/auth/login",
    data={"username": "admin@example.com", "password": "password123!"}
)
headers = {"Content-Type": "application/json"}
sess_resp = session.post(
    f"{BASE_URL}/api/chat/create-chat-session",
    headers=headers,
    json={"persona_id": 0, "description": "test q3"},
)
session_id = sess_resp.json().get("chat_session_id")
print("Session ID:", session_id)

msg_resp = session.post(
    f"{BASE_URL}/api/chat/send-chat-message",
    headers=headers,
    json={
        "chat_session_id": session_id,
        "message": "What is the command to run the OpenSearch parity regression check?",
        "parent_message_id": None,
        "file_descriptors": [],
        "prompt_id": None,
        "search_doc_ids": [],
        "query_override": None,
    },
)
print("Response code:", msg_resp.status_code)
print("Response text:", msg_resp.text[:500])
