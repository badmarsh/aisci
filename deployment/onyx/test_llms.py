#!/usr/bin/env python3
"""
Test all configured LLM models in Onyx LiteLLM
Checks connectivity, parameters, and quota status
"""

import requests
import json
import time
from typing import Dict, List, Tuple

LITELLM_BASE = "http://onyx-litellm:4001"

# Models configured in onyx-litellm_config.yaml
MODELS_TO_TEST = [
    {
        "name": "qwen-max",
        "type": "chat",
        "provider": "dashscope",
        "test_prompt": "Say 'OK' if you can hear me"
    },
    {
        "name": "qwen-omni-flash",
        "type": "chat",
        "provider": "dashscope",
        "test_prompt": "Say 'OK' if you can hear me"
    },
    {
        "name": "qwen-vl-vision",
        "type": "vision",
        "provider": "dashscope",
        "test_prompt": "Describe what you see",
        "skip": True  # Needs image input
    },
    {
        "name": "qwen-embedder",
        "type": "embedding",
        "provider": "ollama",
        "test_input": "test embedding"
    },
    {
        "name": "qwen-reranker",
        "type": "reranker",
        "provider": "dashscope",
        "skip": True  # Different API format
    },
    {
        "name": "local-context-model",
        "type": "chat",
        "provider": "ollama",
        "test_prompt": "Say 'OK' if you can hear me"
    },
    {
        "name": "local-vision-model",
        "type": "vision",
        "provider": "ollama",
        "skip": True  # Needs image input
    },
    {
        "name": "nvidia/nvidia-nemotron-nano-9b-v2",
        "type": "chat",
        "provider": "nvidia",
        "test_prompt": "Say 'OK' if you can hear me"
    },
    {
        "name": "nvidia/llama-3.1-nemotron-nano-vl-8b-v1",
        "type": "vision",
        "provider": "nvidia",
        "skip": True  # Needs image input
    },
    {
        "name": "meta/llama-3.1-8b-instruct",
        "type": "chat",
        "provider": "nvidia",
        "test_prompt": "Say 'OK' if you can hear me"
    }
]

def test_chat_model(model_name: str, prompt: str) -> Tuple[bool, str, Dict]:
    """Test a chat completion model"""
    try:
        response = requests.post(
            f"{LITELLM_BASE}/v1/chat/completions",
            json={
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 50,
                "temperature": 0.1
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return True, content[:100], data
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}", {}

    except Exception as e:
        return False, f"Exception: {str(e)}", {}

def test_embedding_model(model_name: str, text: str) -> Tuple[bool, str, Dict]:
    """Test an embedding model"""
    try:
        response = requests.post(
            f"{LITELLM_BASE}/v1/embeddings",
            json={
                "model": model_name,
                "input": text
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            embedding = data.get("data", [{}])[0].get("embedding", [])
            return True, f"Embedding dimension: {len(embedding)}", data
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}", {}

    except Exception as e:
        return False, f"Exception: {str(e)}", {}

def main():
    print("=" * 80)
    print("ONYX LLM MODEL TESTING")
    print("=" * 80)
    print()

    results = []

    for model in MODELS_TO_TEST:
        model_name = model["name"]
        model_type = model["type"]
        provider = model["provider"]

        print(f"Testing: {model_name}")
        print(f"  Type: {model_type}")
        print(f"  Provider: {provider}")

        if model.get("skip"):
            print(f"  Status: ⏭️  SKIPPED (requires special input)")
            results.append({
                "model": model_name,
                "status": "skipped",
                "reason": "Requires special input format"
            })
            print()
            continue

        # Test based on type
        if model_type == "chat":
            success, message, data = test_chat_model(model_name, model["test_prompt"])
        elif model_type == "embedding":
            success, message, data = test_embedding_model(model_name, model["test_input"])
        else:
            print(f"  Status: ⏭️  SKIPPED (unknown type)")
            results.append({
                "model": model_name,
                "status": "skipped",
                "reason": "Unknown model type"
            })
            print()
            continue

        if success:
            print(f"  Status: ✅ SUCCESS")
            print(f"  Response: {message}")
            results.append({
                "model": model_name,
                "status": "success",
                "response": message
            })
        else:
            print(f"  Status: ❌ FAILED")
            print(f"  Error: {message}")
            results.append({
                "model": model_name,
                "status": "failed",
                "error": message
            })

        print()
        time.sleep(1)  # Rate limiting

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    success_count = sum(1 for r in results if r["status"] == "success")
    failed_count = sum(1 for r in results if r["status"] == "failed")
    skipped_count = sum(1 for r in results if r["status"] == "skipped")

    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"⏭️  Skipped: {skipped_count}")
    print(f"📊 Total: {len(results)}")
    print()

    if failed_count > 0:
        print("FAILED MODELS:")
        for r in results:
            if r["status"] == "failed":
                print(f"  - {r['model']}: {r['error']}")

    # Save results
    with open("/tmp/llm_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print()
    print("Results saved to: /tmp/llm_test_results.json")

if __name__ == "__main__":
    main()
