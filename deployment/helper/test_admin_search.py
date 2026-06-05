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

def search(query):
    payload = {
        "query": query,
        "filters": {
            "source_types": None,
            "document_set_names": ["Robert Corpus"],
            "time_cutoff": None,
            "tags": None
        }
    }
    resp = requests.post(f"{BASE_URL}/api/admin/search", headers=HEADERS, json=payload)
    print(json.dumps(resp.json(), indent=2))

search("OpenSearch parity")
