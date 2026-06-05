import requests
import json
import os

BASE_URL = "http://localhost:3000"
env_path = "deployment/onyx/.env"
api_key = None
with open(env_path, "r") as f:
    for line in f:
        if line.startswith("ONYX_API_KEY="):
            api_key = line.strip().split("=", 1)[1].strip("\"\'")
            break

HEADERS = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

resp = requests.get(f"{BASE_URL}/api/manage/document-set", headers=HEADERS)
doc_sets = resp.json()
print(json.dumps([ds for ds in doc_sets if ds["id"] == 2], indent=2))
