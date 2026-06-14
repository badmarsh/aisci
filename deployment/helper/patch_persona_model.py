from __future__ import annotations
import os
import requests
import sys

BASE_URL = "http://localhost:3000"
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def load_api_key():
    key = os.environ.get("ONYX_API_KEY", "").strip()
    if key: return key
    env_path = os.path.join(REPO_ROOT, "deployment", "onyx", ".env")
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("ONYX_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"\'')
    raise SystemExit("No ONYX_API_KEY found")

API_KEY = load_api_key()
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# 1. Fetch persona 2
r = requests.get(f"{BASE_URL}/api/persona/2", headers=HEADERS)
if r.status_code != 200:
    raise SystemExit(f"GET persona failed: {r.text}")
persona = r.json()

# 2. Patch only the model override and num_chunks
payload = {
    "name": persona["name"],
    "description": persona.get("description", ""),
    "system_prompt": persona.get("system_prompt", ""),
    "task_prompt": persona.get("task_prompt", ""),
    "document_set_ids": [ds["id"] for ds in persona.get("document_sets", [])],
    "tool_ids": [t["id"] for t in persona.get("tools", [])],
    "is_public": persona.get("is_public", True),
    "display_priority": persona.get("display_priority"),
    "num_chunks": 10, # RESTORED TO 10
    "llm_model_version_override": persona.get("llm_model_version_override", "qwen-rag-balanced"),
    "llm_relevance_filter": persona.get("llm_relevance_filter", False),
    "datetime_aware": persona.get("datetime_aware", False),
    "starter_messages": persona.get("starter_messages", []),
}

patch_r = requests.patch(f"{BASE_URL}/api/persona/2", headers=HEADERS, json=payload)
if patch_r.status_code != 200:
    raise SystemExit(f"PATCH persona failed: {patch_r.text}")

print("Successfully updated physics-validator (id=2) to num_chunks=5.")
