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

payload = {
    "name": "Integrated-Corpus",
    "description": "Integration of literature and system docs.",
    "cc_pair_ids": [1, 4, 6],
    "is_public": True
}
resp = requests.post(f"{BASE_URL}/api/manage/admin/document-set", headers=HEADERS, json=payload)
print(f"Doc Set Status: {resp.status_code}")
if resp.status_code in [200, 201]:
    ds_id = resp.json()["id"]
    print(f"New Doc Set ID: {ds_id}")
