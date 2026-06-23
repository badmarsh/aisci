from __future__ import annotations
import requests
import json
import os

BASE_URL = "http://localhost:3000"
env_path = "deployment/onyx/.env"
api_key = None
with open(env_path, "r") as f:
    for line in f:
        if line.startswith("ONYX_API_KEY="):
            api_key = line.strip().split("=", 1)[1].strip("\"\'")
            break

HEADERS = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

def search(query):
    sess = requests.post(f"{BASE_URL}/api/chat/create-chat-session", headers=HEADERS, json={"persona_id": 1}).json()
    sid = sess["chat_session_id"]
    msg = requests.post(f"{BASE_URL}/api/chat/send-chat-message", headers=HEADERS, json={
        "chat_session_id": sid, "message": query, "parent_message_id": None, "file_descriptors": [], "stream": True
    })
    
    answer = ""
    for line in msg.text.strip().split('\n'):
        if line:
            try:
                data = json.loads(line)
                if "obj" in data and data["obj"].get("type") == "message_delta":
                    answer += data["obj"].get("content", "")
            except:
                pass
    return answer

print("Searching Rath 2020 for parameters...")
print(search("In Rath_2020_1908.04208.pdf, find and quote any numerical values for Tkin and beta for 13 TeV."))
