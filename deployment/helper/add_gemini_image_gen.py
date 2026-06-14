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
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Image Generation Config
# Using OpenAI provider type pointing to our bridge
config_payload = {
    "image_provider_id": "gemini-openrouter",
    "model_name": "google/gemini-3-pro-image-preview",
    "provider": "openai",
    "api_key": "dummy", # Bridge handles real keys
    "api_base": "http://onyx-image-bridge:8090/v1",
    "is_default": True
}

print("Configuring Gemini Image Generation via Bridge...")
resp = requests.post(f"{BASE_URL}/api/admin/image-generation/config", headers=HEADERS, json=config_payload)

if resp.status_code in [200, 201]:
    print("SUCCESS: Image generation configured.")
    print(json.dumps(resp.json(), indent=2))
else:
    print(f"FAILED: {resp.status_code} {resp.text}")

