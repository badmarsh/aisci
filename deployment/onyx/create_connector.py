import requests
BASE_URL = "http://localhost:3000"
session = requests.Session()
r = session.post(
    f"{BASE_URL}/api/auth/login",
    data={"username": "admin@example.com", "password": "password123!"}
)
payload = {
    "name": "Docs File Connector 2",
    "source": "file",
    "input_type": "load_state",
    "connector_specific_config": {"file_locations": []},
    "refresh_freq": 86400,
    "prune_freq": None,
    "disabled": False,
    "access_type": "public"
}
r2 = session.post(f"{BASE_URL}/api/manage/admin/connector", json=payload)
print("Create connector:", r2.status_code, r2.text)
if r2.status_code == 200:
    conn_id = r2.json()["id"]
    r4 = session.put(f"{BASE_URL}/api/manage/connector/{conn_id}/credential/0", json={
        "name": "Docs CC Pair",
        "is_public": True,
        "access_type": "public"
    })
    print("Link CC Pair:", r4.status_code, r4.text)
