import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

async def test_nvidia(name, model, api_key):
    print(f"Testing {name} ({model})...")
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
            resp = await client.post(f"{base_url}/chat/completions", json=payload, headers=headers, timeout=10.0)
            if resp.status_code == 200:
                print(f"  [OK] {name}")
                return True
            else:
                print(f"  [FAIL] {name}: {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            print(f"  [ERROR] {name}: {str(e)}")
            return False

async def main():
    models_to_test = [
        ("nvidia-llama-3.1-70b", "meta/llama-3.1-70b-instruct", os.getenv("NVIDIA_API_KEY")),
        ("nvidia-llama-3.1-8b", "meta/llama-3.1-8b-instruct", os.getenv("NVIDIA_API_KEY")),
        ("nvidia-gemma-2-27b", "google/gemma-2-27b-it", os.getenv("NVIDIA_API_KEY")),
    ]
    
    tasks = [test_nvidia(n, m, k, ) for n, m, k in models_to_test if k]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
