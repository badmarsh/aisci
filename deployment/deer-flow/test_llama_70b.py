import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

async def test_llama_70b():
    api_key = os.getenv("NVIDIA_API_KEY")
    model = "meta/llama-3.1-70b-instruct"
    print(f"Testing {model}...")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 5
    }
    base_url = "https://integrate.api.nvidia.com/v1"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{base_url}/chat/completions", json=payload, headers=headers, timeout=20.0)
            print(f"  Result: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"  Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_llama_70b())
