#!/usr/bin/env python3
"""Test RAG queries to check if retrieval issues are fixed."""

import requests
import json
import sys

# Test queries from the original sessions
queries = [
    "Why shouldn't I use internal_search to check the status of the evidence ledger?",
    "What is the command to run the OpenSearch parity regression check?"
]

base_url = "http://localhost:3000"
api_url = f"{base_url}/api/chat/send-message"

# Get session/auth info - we'll need to check how auth works
session = requests.Session()

def test_query(query, query_num):
    print(f"\n{'='*80}")
    print(f"Testing Query {query_num}: {query}")
    print('='*80)

    # Try to send message - may need auth token
    payload = {
        "message": query,
        "chat_session_id": None,  # Create new session
        "persona_id": 2,  # Same persona as original tests
        "prompt_id": None,
        "search_doc_ids": None,
        "retrieval_options": {
            "run_search": "always"
        }
    }

    try:
        response = session.post(api_url, json=payload)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            # Stream response
            for line in response.iter_lines():
                if line:
                    print(line.decode('utf-8'))
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    for i, query in enumerate(queries, 1):
        test_query(query, i)
