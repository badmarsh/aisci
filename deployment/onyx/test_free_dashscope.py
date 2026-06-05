import os
#!/usr/bin/env python3
import requests

API_KEY = os.environ["DASHSCOPE_API_KEY"]  # set in deployment/onyx/.env — never hardcode
API_BASE = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"

models = [
    "qwen3.5-flash",
    "qwen3.5-flash-2026-02-23",
    "qwen3.6-flash",
    "qwen-plus-latest",
    "qwen-plus-2025-09-11",
    "qwen-plus-2025-07-28",
    "qwen3.5-plus-2026-02-15",
    "qwen-turbo",
    "qwen3-max",
    "qwen-max",
    "qwen3.7-max-2026-05-20",
    "qwen3-coder-plus",
    "qwen3-coder-plus-2025-09-23",
    "deepseek-v3.2",
    "glm-5.1"
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
                "messages": [{"role": "user", "content": "Say OK"}],
                "max_tokens": 10
            },
            timeout=10
        )
        if res.status_code == 200:
            print(f"✅ {model}: SUCCESS - {res.json()['choices'][0]['message']['content'].strip()}")
        else:
            print(f"❌ {model}: Failed with HTTP {res.status_code} - {res.text}")
    except Exception as e:
        print(f"⚠️ {model}: Error {e}")
