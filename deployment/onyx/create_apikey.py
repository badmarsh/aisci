import requests
BASE_URL = "http://localhost:3000"
session = requests.Session()
session.post(
    f"{BASE_URL}/api/auth/login",
    data={"username": "admin@example.com", "password": "password123!"}
)
r = session.post(f"{BASE_URL}/api/manage/api-key", json={"name": "test_key", "role": "admin"})
print(r.status_code, r.text)
if r.status_code == 200:
    print("KEY:", r.json()["api_key"])
