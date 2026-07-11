#!/usr/bin/env python3
from __future__ import annotations
import requests
import json

BASE_URL = "http://localhost:3000"
API_KEY = (
    "on_hLxHEO432IFLuDN3psKyxgLH3g35yvvZqOx21yP1Iw__GrPullG5YR0h4ZfJpk"
    "TZAvPPqhQ28mXd8cHYNWzThjWOCPGBaYO6vnC8G13FcNf3FAt-PDveEyj6slAKrWLZ"
    "aBeTu-9inqY-Ty-sc0C5MBMSPPD2_z6DG-n8QCn9tjdmabNNFESJhQ9IH0CeoQZ9Vy"
    "cfU3-HyPUL8YO71LIrRFqs1DWh5vAH6tJsTpq6ybdZFY026gSkRsoRFAX3VJTA"
)
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

print("Creating session...")
sess = requests.post(
    f"{BASE_URL}/api/chat/create-chat-session",
    headers=HEADERS,
    json={"persona_id": 2, "description": "test-model-error"},
)
if sess.status_code == 200:
    session_id = sess.json()["chat_session_id"]
    print(f"Session created: {session_id}")
    
    print("Sending message...")
    msg = requests.post(
        f"{BASE_URL}/api/chat/send-chat-message",
        headers=HEADERS,
        json={
            "chat_session_id": session_id,
            "message": "Hello",
            "prompt_id": None,
            "search_doc_ids": [],
            "file_descriptors": [],
            "parent_message_id": None,
            "stream": False,
        },
    )
    print(f"Send status: {msg.status_code}")
    print(f"Response: {msg.text[:500]}")
else:
    print(f"Failed to create session: {sess.status_code} {sess.text}")
