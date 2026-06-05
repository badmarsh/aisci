import os
import requests
import json
import sys

BASE_URL = "http://localhost:3000"

api_key = "on_hLxHEO432IFLuDN3psKyxgLH3g35yvvZqOx21yP1Iw__GrPullG5YR0h4ZfJpkTZAvPPqhQ28mXd8cHYNWzThjWOCPGBaYO6vnC8G13FcNf3FAt-PDveEyj6slAKrWLZaBeTu-9inqY-Ty-sc0C5MBMSPPD2_z6DG-n8QCn9tjdmabNNFESJhQ9IH0CeoQZ9VycfU3-HyPUL8YO71LIrRFqs1DWh5vAH6tJsTpq6ybdZFY026gSkRsoRFAX3VJTA"

HEADERS = {"Content-Type": "application/json"}
if api_key:
    HEADERS["Authorization"] = f"Bearer {api_key}"

payload = {
  "id": 5,
  "name": "LiteLLM",
  "provider": "litellm",
  "api_key": "dummy",
  "api_base": "http://onyx-litellm:4001/v1",
  "default_model_name": "qwen-max",
  "fast_default_model_name": "qwen-rag-fast",
  "custom_config": {
    "api_base": "http://onyx-litellm:4001/v1",
    "api_key": "dummy"
  },
  "model_configurations": [
    {
      "name": "qwen-max",
      "display_name": "Qwen Max",
      "is_default": True,
      "is_visible": True
    },
    {
      "name": "qwen-rag-fast",
      "display_name": "Qwen Fast",
      "is_visible": True
    }
  ]
}

resp = requests.put(f"{BASE_URL}/api/admin/llm/provider?is_creation=false", headers=HEADERS, json=payload)
print(resp.status_code)
print(resp.text)
