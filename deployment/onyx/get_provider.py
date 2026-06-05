import requests
import json
import os

env_path = "/home/ubuntu/aisci/deployment/onyx/.env"
api_key = None
with open(env_path, "r") as f:
    for line in f:
        if line.startswith("ONYX_API_KEY="):
            api_key = line.strip().split("=", 1)[1].strip('"\'')
            break

headers = {"Authorization": f"Bearer {api_key}"}
resp = requests.get("http://localhost:3000/api/admin/llm/provider", headers=headers)
print(json.dumps(resp.json(), indent=2))
