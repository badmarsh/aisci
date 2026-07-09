import requests
BASE_URL = "http://localhost:3000"
r = requests.post(
    f"{BASE_URL}/api/auth/register",
    json={
        "email": "admin@example.com",
        "password": "password123!"
    }
)
print(r.status_code)
print(r.text)
