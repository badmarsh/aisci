from __future__ import annotations
import requests
import json
import os
import sys

BASE_URL = "http://localhost:3000"
env_path = "deployment/onyx/.env"
api_key = None
with open(env_path, "r") as f:
    for line in f:
        if line.startswith("ONYX_API_KEY="):
            api_key = line.strip().split("=", 1)[1].strip("\"\'")
            break

HEADERS = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

def ask(question):
    sess_resp = requests.post(f"{BASE_URL}/api/chat/create-chat-session", headers=HEADERS, json={"persona_id": 2})
    sid = sess_resp.json()["chat_session_id"]
    msg_resp = requests.post(f"{BASE_URL}/api/chat/send-chat-message", headers=HEADERS, json={
        "chat_session_id": sid, "message": question, "parent_message_id": None, "file_descriptors": [], "stream": True
    })
    
    answer = ""
    doc_count = 0
    for line in msg_resp.text.strip().split('\n'):
        if line:
            try:
                data = json.loads(line)
                if "obj" in data:
                    obj = data["obj"]
                    if obj.get("type") == "message_delta":
                        answer += obj.get("content", "")
                    elif obj.get("type") == "search_docs":
                        doc_count = len(obj.get("top_documents", []))
            except:
                pass
    return answer, doc_count

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "Test"
    ans, count = ask(q)
    print(f"DOC COUNT: {count}")
    print(ans)
