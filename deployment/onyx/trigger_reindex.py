import requests

def trigger():
    base_url = "http://localhost:8080"
    session = requests.Session()
    
    # Login
    login_url = f"{base_url}/auth/login"
    login_data = {
        "username": "marekjurk@proton.me",
        "password": "marekjurk@proton.me"
    }
    print(f"Logging in to {login_url}...")
    # Onyx uses form data for login
    response = session.post(login_url, data=login_data)
    if response.status_code != 204:
        print(f"Login failed: {response.status_code} {response.text}")
        return

    print("Login successful.")

    # Trigger reindex for each connector
    connectors = [0, 2] # connector_ids
    for connector_id in connectors:
        run_once_url = f"{base_url}/manage/admin/connector/run-once"
        payload = {
            "connector_id": connector_id,
            "credential_ids": [],
            "from_beginning": True
        }
        print(f"Triggering reindex for connector {connector_id}...")
        response = session.post(run_once_url, json=payload)
        if response.status_code == 200:
            print(f"Successfully triggered connector {connector_id}: {response.json()}")
        else:
            print(f"Failed to trigger connector {connector_id}: {response.status_code} {response.text}")

if __name__ == "__main__":
    trigger()
