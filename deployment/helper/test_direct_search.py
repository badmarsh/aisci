#!/usr/bin/env python3
"""Test direct search API to isolate RAG retrieval issue."""

import requests
import json

BASE_URL = "http://localhost:3000"
API_KEY = "on_hLxHEO432IFLuDN3psKyxgLH3g35yvvZqOx21yP1Iw__GrPullG5YR0h4ZfJpkTZAvPPqhQ28mXd8cHYNWzThjWOCPGBaYO6vnC8G13FcNf3FAt-PDveEyj6slAKrWLZaBeTu-9inqY-Ty-sc0C5MBMSPPD2_z6DG-n8QCn9tjdmabNNFESJhQ9IH0CeoQZ9VycfU3-HyPUL8YO71LIrRFqs1DWh5vAH6tJsTpq6ybdZFY026gSkRsoRFAX3VJTA"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Test 1: Direct document search
print("=== Test 1: Direct document search ===")
search_payload = {
    "query": "OpenSearch parity check command",
    "collection": "danswer_chunk_alibaba_nlp_gte_qwen2_1_5b_instruct",
    "filters": {},
    "offset": 0
}

try:
    resp = requests.post(f"{BASE_URL}/api/query/document-search", headers=headers, json=search_payload, timeout=10)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Documents returned: {len(data.get('documents', []))}")
        if data.get('documents'):
            print(f"Top result: {data['documents'][0].get('semantic_identifier', 'N/A')}")
    else:
        print(f"Error: {resp.text}")
except Exception as e:
    print(f"Exception: {e}")

print("\n=== Test 2: Query with persona 2 ===")
# Create chat session with persona 2
sess_payload = {"persona_id": 2, "description": "Direct search test"}
sess_resp = requests.post(f"{BASE_URL}/api/chat/create-chat-session", headers=headers, json=sess_payload)
if sess_resp.status_code == 200:
    session_id = sess_resp.json().get("chat_session_id")
    print(f"Session created: {session_id}")

    # Send test message
    msg_payload = {
        "chat_session_id": session_id,
        "message": "What is the OpenSearch parity check command?",
        "parent_message_id": None,
        "file_descriptors": [],
        "prompt_id": None,
        "search_doc_ids": [],
        "query_override": None
    }
    msg_resp = requests.post(f"{BASE_URL}/api/chat/send-chat-message", headers=headers, json=msg_payload, stream=True)

    chunks_retrieved = 0
    for line in msg_resp.iter_lines():
        if line:
            try:
                data = json.loads(line)
                if "top_documents" in data:
                    chunks_retrieved = len(data.get("top_documents", []))
                    print(f"Chunks retrieved: {chunks_retrieved}")
                    if chunks_retrieved > 0:
                        print(f"Top doc: {data['top_documents'][0].get('semantic_identifier', 'N/A')}")
            except:
                pass

    if chunks_retrieved == 0:
        print("WARNING: No chunks retrieved in persona query")
else:
    print(f"Failed to create session: {sess_resp.text}")
