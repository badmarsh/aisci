import os
#!/usr/bin/env python3
import requests

API_KEY = os.environ["DASHSCOPE_API_KEY"]  # set in deployment/onyx/.env — never hardcode
API_BASE = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"

models = [
    "qwen3-coder-30b-a3b-instruct",
    "qwen3-coder-next",
    "qwen3-coder-plus"
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
                "messages": [{"role": "user", "content": "Write a python function to print hello"}],
                "max_tokens": 50
            },
            timeout=10
        )
        print(f"{model}: {res.status_code} - {res.text[:150]}")
    except Exception as e:
        print(f"Error {model}: {e}")
