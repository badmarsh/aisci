import sys
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'deployment/deer-flow/.env'))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'deployment/deer-flow/backend'))
from packages.harness.deerflow.client import DeerFlowClient

def main():
    config_path = os.path.join(os.path.dirname(__file__), 'deployment/deer-flow/config.yaml')
    client = DeerFlowClient(config_path=config_path)
    
    try:
        response = client.chat(
            "Please write a text file named 'deerflow_test.txt' with the content 'Hello from DeerFlow' to the directory /mnt/host/aisci/. Then verify that the file exists by reading its contents, and return the content to me. You MUST use bash or file tools to do this.",
            thread_id="test_thread_001"
        )
        print("Response:", response)

    except Exception as e:
        print("Error during run:", e)

if __name__ == "__main__":
    main()
