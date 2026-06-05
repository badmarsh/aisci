import requests

url = "http://127.0.0.1:4001/v1/chat/completions"
headers = {"Content-Type": "application/json"}
data = {
    "model": "gemma2",
    "messages": [{"role": "user", "content": "Say hello world"}]
}

response = requests.post(url, headers=headers, json=data)
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
