import requests
import json

try:
    res = requests.post("http://localhost:8082/api/v1/authentication/sign-up", json={
        "firstName": "Admin",
        "lastName": "User",
        "email": "admin@multica.ai",
        "password": "password123",
        "trackEvents": False,
        "newsLetter": False
    })
    print(res.status_code)
    print(res.text)
except Exception as e:
    print(e)
