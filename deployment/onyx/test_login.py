import requests
BASE_URL = "http://localhost:3000"
session = requests.Session()
r = session.post(
    f"{BASE_URL}/api/auth/login",
    data={
        "username": "admin@example.com",
        "password": "password123!"
    }
)
print("Login status:", r.status_code)
r2 = session.get(f"{BASE_URL}/api/manage/admin/connector")
print("Connectors:", r2.status_code, r2.text)
