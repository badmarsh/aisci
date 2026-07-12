import requests

def test_endpoint(name, url, key):
    headers = {'Authorization': f'Bearer {key}'}
    try:
        res = requests.get(f'{url}/models', headers=headers, timeout=5)
        print(f'{name}: {res.status_code}')
    except Exception as e:
        print(f'{name}: Failed -> {e}')

test_endpoint('OpenRouter', 'https://openrouter.ai/api/v1', 'test-openrouter-key')
test_endpoint('NVIDIA NIM', 'https://integrate.api.nvidia.com/v1', 'test-nvidia-key')
