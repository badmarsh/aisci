import os
#!/usr/bin/env python3
import requests
import json

API_KEY = os.environ["NVIDIA_API_KEY"]  # set in deployment/onyx/.env — never hardcode
API_BASE = "https://integrate.api.nvidia.com/v1/chat/completions"

models = [
    "nvidia/llama-3.1-nemotron-70b-instruct",
    "nvidia/llama-3.1-nemotron-nano-8b-v1"
]

for model in models:
    try:
        res = requests.post(
            API_BASE,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Say OK in 2 words"}],
                "max_tokens": 50
            },
            timeout=10
        )
        print(f"=== {model} ===")
        print(res.status_code)
        print(json.dumps(res.json(), indent=2))
    except Exception as e:
        print(f"Error {model}: {e}")
