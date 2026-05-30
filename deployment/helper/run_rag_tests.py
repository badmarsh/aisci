import os
import requests
import json
import sys

BASE_URL = "http://localhost:3000"

api_key = "on_hLxHEO432IFLuDN3psKyxgLH3g35yvvZqOx21yP1Iw__GrPullG5YR0h4ZfJpkTZAvPPqhQ28mXd8cHYNWzThjWOCPGBaYO6vnC8G13FcNf3FAt-PDveEyj6slAKrWLZaBeTu-9inqY-Ty-sc0C5MBMSPPD2_z6DG-n8QCn9tjdmabNNFESJhQ9IH0CeoQZ9VycfU3-HyPUL8YO71LIrRFqs1DWh5vAH6tJsTpq6ybdZFY026gSkRsoRFAX3VJTA"

HEADERS = {"Content-Type": "application/json"}
if api_key:
    HEADERS["Authorization"] = f"Bearer {api_key}"

def run_test(question, persona_id):
    # 1. Create session
    sess_payload = {"persona_id": persona_id, "description": "RAG Evaluation"}
    sess_resp = requests.post(f"{BASE_URL}/api/chat/create-chat-session", headers=HEADERS, json=sess_payload)
    if sess_resp.status_code != 200:
        print(f"Failed to create session: {sess_resp.text}")
        return
    session_id = sess_resp.json().get("chat_session_id")
    
    # 2. Send message
    msg_payload = {
        "chat_session_id": session_id,
        "message": question,
        "parent_message_id": None,
        "file_descriptors": [],
        "prompt_id": None,
        "search_doc_ids": [],
        "query_override": None
    }
    msg_resp = requests.post(f"{BASE_URL}/api/chat/send-chat-message", headers=HEADERS, json=msg_payload)
    
    print(f"\nQ: {question}")
    answer_text = ""
    for line in msg_resp.text.strip().split('\n'):
        if line:
            try:
                data = json.loads(line)
                if "obj" in data and data["obj"].get("type") == "message_delta":
                    answer_text += data["obj"].get("content", "")
                elif "error" in data:
                    print(f"Stream error: {data['error']}")
            except:
                pass
    print(f"A: {answer_text}")
    print("---------------------------------")

questions = [
    "What are the typical transverse velocity and freeze-out temperature parameters used in Blast-Wave fits for 13 TeV pp collisions?",
    "How does the Tsallis-Pareto distribution handle high-pT tails compared to standard Boltzmann-Juttner?",
    "What is the command to run the OpenSearch parity regression check?",
    "Does the manuscript compare the boson probability distribution model against a Tsallis or Blast-Wave baseline? If so, what is the stated motivation?",
    "Why shouldn't I use internal_search to check the status of the evidence ledger?"
]


persona_id = 2 # physics-validator

print("Starting RAG tests...")
for q in questions:
    run_test(q, persona_id)
print("\nDone.")
