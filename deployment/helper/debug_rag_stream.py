#!/usr/bin/env python3
from __future__ import annotations
"""Debug RAG - dumps full raw stream and parses correctly."""
import os
import requests
import json

BASE_URL = "http://localhost:3000"
api_key = "on_hLxHEO432IFLuDN3psKyxgLH3g35yvvZqOx21yP1Iw__GrPullG5YR0h4ZfJpkTZAvPPqhQ28mXd8cHYNWzThjWOCPGBaYO6vnC8G13FcNf3FAt-PDveEyj6slAKrWLZaBeTu-9inqY-Ty-sc0C5MBMSPPD2_z6DG-n8QCn9tjdmabNNFESJhQ9IH0CeoQZ9VycfU3-HyPUL8YO71LIrRFqs1DWh5vAH6tJsTpq6ybdZFY026gSkRsoRFAX3VJTA"
HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

persona_id = 2

# 1. Create session
sess_resp = requests.post(f"{BASE_URL}/api/chat/create-chat-session",
                          headers=HEADERS, json={"persona_id": persona_id, "description": "Debug"})
print(f"Session status: {sess_resp.status_code}")
if sess_resp.status_code != 200:
    print(sess_resp.text)
    exit(1)
session_id = sess_resp.json()["chat_session_id"]
print(f"Session ID: {session_id}")

# 2. Send message
question = "What are the typical transverse velocity and freeze-out temperature parameters used in Blast-Wave fits for 13 TeV pp collisions?"
msg_payload = {
    "chat_session_id": session_id,
    "message": question,
    "parent_message_id": None,
    "file_descriptors": [],
    "prompt_id": None,
    "search_doc_ids": [],
    "query_override": None,
}
print(f"\nSending question: {question[:80]}...")
msg_resp = requests.post(f"{BASE_URL}/api/chat/send-chat-message",
                         headers=HEADERS, json=msg_payload)
print(f"Response status: {msg_resp.status_code}")
print(f"\n=== RAW STREAM (first 3000 chars) ===")
raw = msg_resp.text
print(raw[:3000])

print(f"\n=== PARSED PACKETS ===")
for line in raw.strip().split('\n'):
    line = line.strip()
    if not line:
        continue
    # SSE format: data: {...}
    if line.startswith("data:"):
        line = line[5:].strip()
    try:
        data = json.loads(line)
        ptype = data.get("type") or (data.get("obj") or {}).get("type", "?")
        if ptype in ("top_documents", "search_response", "relevant_documents"):
            print(f"[{ptype}] docs found: {data}")
        elif ptype == "message_delta":
            content = data.get("content", "") or (data.get("obj") or {}).get("content", "")
            print(f"[message_delta] {content[:100]}")
        elif ptype == "message":
            print(f"[message] {str(data)[:200]}")
        else:
            print(f"[{ptype}] ...")
    except json.JSONDecodeError:
        if line:
            print(f"[raw] {line[:120]}")
