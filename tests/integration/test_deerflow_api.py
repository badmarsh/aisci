import sys
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(REPO_ROOT / 'deployment/deer-flow/backend'))

from packages.harness.deerflow.client import DeerFlowClient

def main():
    config_path = str(REPO_ROOT / 'deployment/deer-flow/config.yaml')
    client = DeerFlowClient(config_path=config_path)
    
    # Try to bypass authentication or see if it works without token locally?
    # Actually, maybe the client requires a token.
    try:
        models = client.list_models()
        print("Models:", models)
    except Exception as e:
        print("Models Error:", e)

    try:
        tools = client.list_tools()
        print("Tools:", tools)
    except Exception as e:
        print("Tools Error:", e)
        
    try:
        skills = client.list_skills()
        print("Skills:", skills)
    except Exception as e:
        print("Skills Error:", e)

if __name__ == "__main__":
    main()
