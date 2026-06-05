import requests
import json

BASE_URL = "http://localhost:3000"
api_key = "on_hLxHEO432IFLuDN3psKyxgLH3g35yvvZqOx21yP1Iw__GrPullG5YR0h4ZfJpkTZAvPPqhQ28mXd8cHYNWzThjWOCPGBaYO6vnC8G13FcNf3FAt-PDveEyj6slAKrWLZaBeTu-9inqY-Ty-sc0C5MBMSPPD2_z6DG-n8QCn9tjdmabNNFESJhQ9IH0CeoQZ9VycfU3-HyPUL8YO71LIrRFqs1DWh5vAH6tJsTpq6ybdZFY026gSkRsoRFAX3VJTA"

HEADERS = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "query": "What are the typical transverse velocity and freeze-out temperature parameters?",
    "search_type": "semantic",
    "human_selected_filters": None,
    "enable_auto_detect_filters": False,
    "offset": 0,
    "limit": 3
}

for path in ["/api/chat/search", "/api/search", "/api/query/standard-answer"]:
    print(f"\n--- Testing Path: {path} ---")
    resp = requests.post(f"{BASE_URL}{path}", headers=HEADERS, json=payload)
    print(f"Status: {resp.status_code}")
    try:
        data = resp.json()
        print(f"Response (truncated): {str(data)[:500]}")
    except:
        print(resp.text[:500])
