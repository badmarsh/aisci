from __future__ import annotations
import os
import requests
import json
import sys

BASE_URL = "http://localhost:3000"

# Load API key from env file
env_path = "deployment/onyx/.env"
api_key = None
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("ONYX_API_KEY="):
                api_key = line.strip().split("=", 1)[1].strip('"\'')
                break

if not api_key:
    print("Could not find ONYX_API_KEY in .env")
    sys.exit(1)

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
  "id": 5,
  "name": "LiteLLM",
  "provider": "litellm",
  "api_key": "dummy",
  "api_base": "http://onyx-litellm:4001/v1",
  "default_model_name": "qwen-balanced",
  "fast_default_model_name": "qwen-fast",
  "custom_config": {
    "api_base": "http://onyx-litellm:4001/v1",
    "api_key": "dummy"
  },
  "model_configurations": [
    {
      "name": "qwen-fast",
      "display_name": "Qwen Fast (Flash)",
      "is_visible": True
    },
    {
      "name": "qwen-balanced",
      "display_name": "Qwen Balanced (Plus)",
      "is_default": True,
      "is_visible": True
    },
    {
      "name": "qwen-max",
      "display_name": "Qwen Max (3.7)",
      "is_visible": True
    },
    {
      "name": "qwen-coder",
      "display_name": "Qwen Coder (30B)",
      "is_visible": True
    },
    {
      "name": "nvidia-balanced",
      "display_name": "NVIDIA Llama 3.3 70B",
      "is_visible": True
    },
    {
      "name": "nvidia-fast",
      "display_name": "NVIDIA Nemotron 8B",
      "is_visible": True
    },
    {
      "name": "nvidia-reasoning",
      "display_name": "NVIDIA Nemotron 49B (Reasoning)",
      "is_visible": True
    }
  ]
}

resp = requests.put(f"{BASE_URL}/api/admin/llm/provider?is_creation=false", headers=HEADERS, json=payload)
print("Status:", resp.status_code)
print(resp.text)
