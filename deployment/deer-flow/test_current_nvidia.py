import requests
import os
import time

api_key = os.environ.get('NVIDIA_API_KEY')
if not api_key:
    with open('/home/ubuntu/aisci/deployment/deer-flow/.env', 'r') as f:
        for line in f:
            if line.startswith('NVIDIA_API_KEY='):
                api_key = line.strip().split('=', 1)[1]
                break

headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}

models_to_test = [
    'nvidia/llama-3.1-nemotron-70b-instruct',
    'meta/llama-3.3-70b-instruct',
    'meta/llama-3.1-405b-instruct',
    'deepseek-ai/deepseek-r1',
    'google/gemma-2-27b-it',
    'mistralai/mistral-large-2-instruct',
    'microsoft/phi-3.5-mini-instruct'
]

working = []
for model in models_to_test:
    res = requests.post('https://integrate.api.nvidia.com/v1/chat/completions', headers=headers, json={'model': model, 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 5}, timeout=10)
    if res.status_code == 200:
        working.append(model)
        print(f'{model}: SUCCESS')
    else:
        print(f'{model}: FAILED ({res.status_code})')
    time.sleep(1)

print('\nWORKING_MODELS=' + ','.join(working))
