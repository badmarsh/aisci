import sys
import os
import json
import asyncio

# The container already runs with the app available, but let's make sure
sys.path.insert(0, '/app/backend')
from packages.harness.deerflow.client import DeerFlowClient

def main():
    config_path = '/app/config.yaml'
    client = DeerFlowClient(config_path=config_path)
    
    try:
        # We'll use the physics-validation-director since the user wants to check physics stuff,
        # but the prompt specifically tests tools, skills, memory, and mounted drive.
        prompt = """
        Please perform a system check:
        1. Write a file named 'deerflow_container_test.txt' to /mnt/host/aisci/ containing 'Container Drive Mount Works!'.
        2. Query the Onyx knowledge base for 'Tsallis distribution'.
        3. Read the file back to verify.
        """
        response = client.chat(
            prompt,
            thread_id="test_thread_docker_001"
        )
        print("Response:", response)

    except Exception as e:
        print("Error during run:", e)

if __name__ == "__main__":
    main()
