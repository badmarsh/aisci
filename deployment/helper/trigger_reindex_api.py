from __future__ import annotations
import requests
import os

BASE_URL = "http://localhost:3000"
api_key = os.environ.get("ONYX_API_KEY") or "on_hLxHEO432IFLuDN3psKyxgLH3g35yvvZqOx21yP1Iw__GrPullG5YR0h4ZfJpkTZAvPPqhQ28mXd8cHYNWzThjWOCPGBaYO6vnC8G13FcNf3FAt-PDveEyj6slAKrWLZaBeTu-9inqY-Ty-sc0C5MBMSPPD2_z6DG-n8QCn9tjdmabNNFESJhQ9IH0CeoQZ9VycfU3-HyPUL8YO71LIrRFqs1DWh5vAH6tJsTpq6ybdZFY026gSkRsoRFAX3VJTA"

HEADERS = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def main():
    connector_id = 4
    credential_ids = [0]
    
    payload = {
        "connector_id": connector_id,
        "credential_ids": credential_ids,
        "from_beginning": True
    }
    
    print(f"Triggering Onyx re-indexing via API for connector_id={connector_id}...")
    resp = requests.post(f"{BASE_URL}/api/manage/admin/connector/run-once", headers=HEADERS, json=payload)
    print(f"Response status: {resp.status_code}")
    print(f"Response body: {resp.text}")

if __name__ == "__main__":
    main()
