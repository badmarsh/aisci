from __future__ import annotations
import requests
import os
import json

BASE_URL = "http://localhost:3000"
env_path = "deployment/onyx/.env"
api_key = None
with open(env_path, "r") as f:
    for line in f:
        if line.startswith("ONYX_API_KEY="):
            api_key = line.strip().split("=", 1)[1].strip("\"\'")
            break

HEADERS = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

def main():
    valid_ids = [1, 4, 6]
    print(f"Mapping CC Pair IDs: {valid_ids}")

    # Try PUT for Document Set
    payload = {
        "name": "Robert Corpus",
        "description": "Robert's manuscript, Tsallis baselines, and all papers listed in research/robert/evidence-ledger.md.",
        "cc_pair_ids": valid_ids,
        "is_public": True
    }
    resp = requests.put(f"{BASE_URL}/api/manage/admin/document-set/2", headers=HEADERS, json=payload)
    if resp.status_code == 405:
         # Maybe PATCH with id suffix?
         resp = requests.patch(f"{BASE_URL}/api/manage/admin/document-set", headers=HEADERS, json=payload)
    print(f"Robert Corpus update: {resp.status_code}")

    # Fix Persona
    persona = requests.get(f"{BASE_URL}/api/persona/2", headers=HEADERS).json()
    persona["num_chunks"] = 20
    persona["document_set_ids"] = [2]
    persona["tool_ids"] = [1]
    persona["datetime_aware"] = True
    persona["llm_relevance_filter"] = False
    
    allowed = ["name", "description", "system_prompt", "task_prompt", "document_set_ids", "num_chunks", "is_public", "display_priority", "starter_messages", "tool_ids", "datetime_aware", "llm_relevance_filter"]
    patch_payload = {k: v for k, v in persona.items() if k in allowed}
    
    resp = requests.patch(f"{BASE_URL}/api/persona/2", headers=HEADERS, json=patch_payload)
    print(f"Physics Validator update: {resp.status_code}")

if __name__ == "__main__":
    main()
