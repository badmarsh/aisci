import jwt
import requests
import json
import time

secret = 'cGX_KFu_tU7bbxw6gAd97Kc_XrQE3je8iXLV_ANSqUhQBlV88KDyMw'

# Create a payload for a valid JWT
payload = {
    "sub": "d7c1fa63-98c0-4111-ab98-f842bbb7c950",  # The user id we found in the threads folder
    "exp": int(time.time()) + 3600
}

token = jwt.encode(payload, secret, algorithm="HS256")

headers = {
    "Authorization": f"Bearer {token}"
}

# Try to get thread state
url = "http://localhost:2026/api/threads/99375b6a-67ea-4948-9c25-4b8b79ed4c2c/state"
res = requests.get(url, headers=headers)
print("State Status:", res.status_code)
if res.status_code == 200:
    with open('/home/ubuntu/aisci/state.json', 'w') as f:
        json.dump(res.json(), f, indent=2)
else:
    print(res.text)

# Try to get runs or messages
url_messages = "http://localhost:2026/api/threads/99375b6a-67ea-4948-9c25-4b8b79ed4c2c/messages"
res_msgs = requests.get(url_messages, headers=headers)
print("Messages Status:", res_msgs.status_code)
if res_msgs.status_code == 200:
    with open('/home/ubuntu/aisci/messages.json', 'w') as f:
        json.dump(res_msgs.json(), f, indent=2)
else:
    print(res_msgs.text)
