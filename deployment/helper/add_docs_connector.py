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
            api_key = line.strip().split("=", 1)[1].strip('"\'')
            break

HEADERS = {"Content-Type": "application/json"}
if api_key:
    HEADERS["Authorization"] = f"Bearer {api_key}"

def main():
    # 1. Create Connector
    connector_payload = {
        "name": "AiSci-Docs",
        "source": "FILE",
        "input_type": "LOAD_STATE",
        "connector_specific_config": {
            "file_locations": ["/home/ubuntu/aisci/docs/"],
            "file_names": [], # Empty means all? Or maybe I need to list them.
            # Actually File connector usually takes a folder in some versions or needs files listed.
            # In Onyx v4, "file" source often means uploaded files.
            # Let's check existing connectors.
        }
    }
    # Wait, existing connector 3 has source FILE. Let's see its config.
    # SELECT * FROM connector WHERE id = 3;
