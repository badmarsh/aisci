import requests
import os
import json
import time

api_key = os.environ.get('NVIDIA_API_KEY')
if not api_key:
    with open('/home/ubuntu/aisci/deployment/deer-flow/.env', 'r') as f:
        for line in f:
            if line.startswith('NVIDIA_API_KEY='):
                api_key = line.strip().split('=', 1)[1]
                break

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

print('Fetching available models from NVIDIA...')
response = requests.get('https://integrate.api.nvidia.com/v1/models', headers=headers)
models = [m['id'] for m in response.json().get('data', [])]

# Filter for reasonable top-tier models to test
targets = [m for m in models if 'llama-3' in m.lower() or 'nemotron' in m.lower() or 'mistral' in m.lower() or 'gemma' in m.lower() or 'phi' in m.lower()]

# Keep a diverse subset to avoid rate limits
selected_targets = [
    'meta/llama-3.1-405b-instruct',
    'meta/llama-3.1-70b-instruct',
    'meta/llama-3.1-8b-instruct',
    'nvidia/llama-3.1-nemotron-70b-instruct',
    'mistralai/mistral-large-2-instruct',
    'mistralai/mixtral-8x22b-v0.1',
    'google/gemma-2-27b-it',
    'microsoft/phi-3.5-mini-instruct'
]

# Add any from selected_targets that exist in models, plus a few from targets if needed
test_models = set(selected_targets).intersection(set(models))

print(f'Testing {len(test_models)} models...')

working_models = []
failed_models = []

for model in test_models:
    print(f'Testing {model}... ', end='', flush=True)
    payload = {
        'model': model,
        'messages': [{'role': 'user', 'content': 'hi'}],
        'max_tokens': 5
    }
    try:
        res = requests.post('https://integrate.api.nvidia.com/v1/chat/completions', headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            print('SUCCESS')
            working_models.append(model)
        else:
            print(f'FAILED: {res.status_code} - {res.text}')
            failed_models.append(model)
    except Exception as e:
        print(f'ERROR: {e}')
    time.sleep(1)

print('\n=== RESULTS ===')
print('Working models:')
for m in working_models:
    print(f'  - {m}')

