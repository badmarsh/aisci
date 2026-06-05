import os
#!/usr/bin/env python3
import requests
import json

API_KEY = os.environ["NVIDIA_API_KEY"]  # set in deployment/onyx/.env — never hardcode
API_BASE = "https://integrate.api.nvidia.com/v1/chat/completions"

models = [
    "nvidia/llama-3.3-nemotron-super-49b-v1.5",
    "meta/llama-4-maverick-17b-128e-instruct",
    "nvidia/llama-nemotron-embed-1b-v2"
]

# Test Chat
for model in models[:2]:
    try:
        res = requests.post(
            API_BASE,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Say OK"}],
                "max_tokens": 50
            },
            timeout=30
        )
        print(f"=== {model} ===")
        print(f"Status: {res.status_code}")
        print(json.dumps(res.json(), indent=2))
    except Exception as e:
        print(f"Error {model}: {e}")

# Test Embedding
try:
    res = requests.post(
        API_BASE.replace("chat/completions", "embeddings"),
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "nvidia/llama-nemotron-embed-1b-v2",
            "input": "test text",
            "input_type": "query"
        },
        timeout=10
    )
    print("=== Embedding ===")
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        print("Success! Dim:", len(res.json()["data"][0]["embedding"]))
    else:
        print(res.text)
except Exception as e:
    print(f"Error embedding: {e}")
