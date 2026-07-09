import requests
BASE_URL = "http://localhost:3000"
session = requests.Session()
r = session.post(
    f"{BASE_URL}/api/auth/login",
    data={"username": "admin@example.com", "password": "password123!"}
)
CONNECTOR_ID = 1
r2 = session.put(
    f"{BASE_URL}/api/manage/connector/{CONNECTOR_ID}/credential/0",
    json={"name": "Docs CC Pair", "is_public": True, "access_type": "public"}
)
print("Link CC Pair:", r2.status_code, r2.text)
