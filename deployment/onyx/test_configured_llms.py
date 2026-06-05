#!/usr/bin/env python3
import requests
import json
import time

LITELLM_BASE = "http://localhost:4001"

MODELS_TO_TEST = [
    {"name": "qwen-fast", "type": "chat", "prompt": "Identify yourself and say hello in 5 words."},
    {"name": "qwen-balanced", "type": "chat", "prompt": "Identify yourself and say hello in 5 words."},
    {"name": "qwen-max", "type": "chat", "prompt": "Identify yourself and say hello in 5 words."},
    {"name": "qwen-coder", "type": "chat", "prompt": "Write a 1-line Python function to reverse a string."},
    {"name": "nvidia-balanced", "type": "chat", "prompt": "Identify yourself and say hello in 5 words."},
    {"name": "nvidia-fast", "type": "chat", "prompt": "Identify yourself and say hello in 5 words."},
    {"name": "nvidia-reasoning", "type": "reasoning", "prompt": "Identify yourself and say hello in 5 words."},
    {"name": "qwen-embedder", "type": "embedding", "input": "testing nomic local embedding"},
    {"name": "nvidia-embedder", "type": "embedding", "input": "testing nemotron embedding via nvidia"},
]

def test_chat(model: str, prompt: str):
    print(f"Testing Chat Model: {model}...")
    try:
        t0 = time.time()
        res = requests.post(
            f"{LITELLM_BASE}/v1/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
                "temperature": 0.2
            },
            timeout=30
        )
        dt = time.time() - t0
        if res.status_code == 200:
            content = res.json()["choices"][0]["message"]["content"]
            print(f"  ✅ SUCCESS [{dt:.2f}s]: {content.strip() if content else '[null content]'}")
            return True
        else:
            print(f"  ❌ FAILED [{dt:.2f}s]: HTTP {res.status_code} - {res.text}")
            return False
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

def test_reasoning(model: str, prompt: str):
    print(f"Testing Reasoning Model: {model}...")
    try:
        t0 = time.time()
        res = requests.post(
            f"{LITELLM_BASE}/v1/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
                "temperature": 0.2
            },
            timeout=30
        )
        dt = time.time() - t0
        if res.status_code == 200:
            msg = res.json()["choices"][0]["message"]
            content = msg.get("content")
            reasoning = msg.get("reasoning_content") or msg.get("reasoning")
            if content:
                print(f"  ✅ SUCCESS [{dt:.2f}s]: Content: {content.strip()}")
            elif reasoning:
                print(f"  ✅ SUCCESS (Reasoning trace) [{dt:.2f}s]: Reasoning: {reasoning.strip()[:100]}...")
            else:
                print(f"  ❌ FAILED [{dt:.2f}s]: Returned empty response.")
            return True
        else:
            print(f"  ❌ FAILED [{dt:.2f}s]: HTTP {res.status_code} - {res.text}")
            return False
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

def test_embedding(model: str, val: str):
    print(f"Testing Embedding Model: {model}...")
    try:
        t0 = time.time()
        res = requests.post(
            f"{LITELLM_BASE}/v1/embeddings",
            json={
                "model": model,
                "input": val
            },
            timeout=30
        )
        dt = time.time() - t0
        if res.status_code == 200:
            emb = res.json()["data"][0]["embedding"]
            print(f"  ✅ SUCCESS [{dt:.2f}s]: Dim = {len(emb)}")
            return True
        else:
            print(f"  ❌ FAILED [{dt:.2f}s]: HTTP {res.status_code} - {res.text}")
            return False
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

def main():
    print("Starting LLM validation check on onyx-litellm...")
    print("-" * 50)
    for model in MODELS_TO_TEST:
        if model["type"] == "chat":
            test_chat(model["name"], model["prompt"])
        elif model["type"] == "reasoning":
            test_reasoning(model["name"], model["prompt"])
        elif model["type"] == "embedding":
            test_embedding(model["name"], model["input"])
        print("-" * 50)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
