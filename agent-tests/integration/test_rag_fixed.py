#!/usr/bin/env python3
"""Test if RAG retrieval issues are fixed for the two original queries."""
import requests
import json

BASE_URL = "http://localhost:3000"
api_key = "on_hLxHEO432IFLuDN3psKyxgLH3g35yvvZqOx21yP1Iw__GrPullG5YR0h4ZfJpkTZAvPPqhQ28mXd8cHYNWzThjWOCPGBaYO6vnC8G13FcNf3FAt-PDveEyj6slAKrWLZaBeTu-9inqY-Ty-sc0C5MBMSPPD2_z6DG-n8QCn9tjdmabNNFESJhQ9IH0CeoQZ9VycfU3-HyPUL8YO71LIrRFqs1DWh5vAH6tJsTpq6ybdZFY026gSkRsoRFAX3VJTA"
HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

persona_id = 2

# Original test queries
queries = [
    "Why shouldn't I use internal_search to check the status of the evidence ledger?",
    "What is the command to run the OpenSearch parity regression check?"
]

def test_query(question, query_num):
    print(f"\n{'='*80}")
    print(f"Query {query_num}: {question}")
    print('='*80)

    # Create session
    sess_resp = requests.post(f"{BASE_URL}/api/chat/create-chat-session",
                              headers=HEADERS, json={"persona_id": persona_id, "description": f"RAG Test Q{query_num}"})

    if sess_resp.status_code != 200:
        print(f"❌ Failed to create session: {sess_resp.status_code}")
        print(sess_resp.text)
        return

    session_id = sess_resp.json()["chat_session_id"]
    print(f"✓ Session created: {session_id}")

    # Send message
    msg_payload = {
        "chat_session_id": session_id,
        "message": question,
        "parent_message_id": None,
        "file_descriptors": [],
        "prompt_id": None,
        "search_doc_ids": [],
        "query_override": None,
    }

    msg_resp = requests.post(f"{BASE_URL}/api/chat/send-chat-message",
                             headers=HEADERS, json=msg_payload)

    if msg_resp.status_code != 200:
        print(f"❌ Failed to send message: {msg_resp.status_code}")
        print(msg_resp.text)
        return

    print(f"✓ Message sent, processing response...\n")

    # Parse response
    docs_found = 0
    answer_text = []

    for line in msg_resp.text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue

        if line.startswith("data:"):
            line = line[5:].strip()

        try:
            data = json.loads(line)
            ptype = data.get("type") or (data.get("obj") or {}).get("type", "?")

            if ptype in ("top_documents", "search_response", "relevant_documents"):
                docs = data.get("top_documents") or data.get("documents") or []
                docs_found = len(docs)
                print(f"📄 Documents retrieved: {docs_found}")
                if docs_found > 0:
                    for i, doc in enumerate(docs[:3], 1):
                        title = doc.get("semantic_identifier", "Unknown")
                        print(f"   {i}. {title}")

            elif ptype == "message_delta":
                content = data.get("content", "") or (data.get("obj") or {}).get("content", "")
                if content:
                    answer_text.append(content)

        except json.JSONDecodeError:
            pass

    # Print answer
    full_answer = "".join(answer_text)
    print(f"\n💬 Answer:")
    print(full_answer[:500])
    if len(full_answer) > 500:
        print(f"... (truncated, total length: {len(full_answer)} chars)")

    # Check if it's the same failure
    if "NOT FOUND IN CORPUS" in full_answer:
        print(f"\n❌ STILL FAILING - Same 'NOT FOUND IN CORPUS' error")
    elif docs_found == 0:
        print(f"\n⚠️  No documents retrieved, but different response")
    else:
        print(f"\n✅ SUCCESS - Retrieved {docs_found} documents and provided answer")

    return session_id

if __name__ == "__main__":
    session_ids = []
    for i, query in enumerate(queries, 1):
        sid = test_query(query, i)
        if sid:
            session_ids.append(sid)

    print(f"\n{'='*80}")
    print("Test session IDs:")
    for sid in session_ids:
        print(f"  http://localhost:3000/app?chatId={sid}")
