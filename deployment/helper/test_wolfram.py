import requests
import os

def test_wolfram():
    app_id = os.environ.get("WOLFRAM_APP_ID")
    if not app_id:
        print("ERROR: WOLFRAM_APP_ID not found in environment.")
        return

    # Basic query to test the Short Answers API
    query = "integrate cosh(y) dy from y=-0.5 to 0.5"
    base_url = "http://api.wolframalpha.com/v1/result"
    
    print(f"Querying Wolfram Alpha API (AppID: {app_id[:4]}...): {query}")
    try:
        resp = requests.get(
            base_url,
            params={"appid": app_id, "i": query}
        )
        resp.raise_for_status()
        print(f"\nSUCCESS. Response: {resp.text}")
    except requests.exceptions.RequestException as e:
        print(f"API Request Failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="/home/ubuntu/aisci/.env")
    test_wolfram()
