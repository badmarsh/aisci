import os
import sys
from deerflow.client import DeerFlowClient

def test_models():
    os.environ['DEER_FLOW_PROJECT_ROOT'] = '/home/ubuntu/aisci/deployment/deer-flow'
    client = DeerFlowClient()
    print('DeerFlowClient initialized.')
    
    models = client.list_models()
    model_names = [m['name'] for m in models.get('models', [])]
    print(f'Registered models: {model_names}')
    
    for m in ['openrouter-gemini-2.5-flash', 'nvidia-llama-3-1-nemotron-70b-instruct']:
        if m not in model_names:
            print(f'ERROR: Model {m} not found!')
            sys.exit(1)
        else:
            print(f'SUCCESS: {m} is configured.')
            
test_models()
