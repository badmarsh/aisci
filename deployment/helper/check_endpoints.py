from __future__ import annotations
import os
import requests
import json

BASE_URL = "http://localhost:3000"
env_path = "deployment/onyx/.env"
api_key = None
with open(env_path, "r") as f:
    for line in f:
        if line.startswith("ONYX_API_KEY="):
            api_key = line.strip().split("=", 1)[1].strip('"\'')
            break

HEADERS = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

endpoints = [
    "/api/admin/document-set",
    "/api/manage/admin/document-set"
]

test_ds = {
    "name": "Test Set With Connector",
    "description": "test",
    "cc_pair_ids": [2],
    "is_public": True,
    "is_up_to_date": True
}

r = requests.post(f"{BASE_URL}/api/manage/admin/document-set", headers=HEADERS, json=test_ds)
print(f"POST status: {r.status_code}")
if r.status_code in [200, 201]:
    print(r.json())
else:
    print(r.text)
