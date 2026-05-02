import asyncio
import os
import sys

# Add the harness package to sys.path
sys.path.append("/home/ubuntu/aisci/deployment/deer-flow/backend/packages/harness")

from deerflow.client import DeerFlowClient

async def test_onyx_search():
    # We need to set the environment variables for the client if it runs in-process
    # but since it's probably talking to the gateway via HTTP if it's a client...
    # Actually, the summary said it's an "in-process wrapper" that uses the same config.
    
    # Let's set the env vars just in case
    os.environ["ONYX_API_KEY"] = "on_h4V-xqopLatkD0GUZhVKGkzMvtRY8BBlW-PYi2ge3YumIIm7LD3IGvUeqKPImOvp22Z0w8uO897wCNYogmE0HJ46pIqujyQjRh9uXoev4gIgFA-3Mqi7KHvaNoQ6RZ-Zk0OHkDe1NR5K5ksXRkBmQWHhUeebFCecuNBpEN6pBdofONZtqEQL9i4j-rs9uNo5hwy2LNG53cvTf763i8q1UpuaCgJ4ykgRkm4lrzQHBWCkyH2gaKBb_UB2GluE4nce"
    os.environ["ONYX_API_BASE"] = "http://localhost:80/api" # Use localhost since we are on the host
    os.environ["DEER_FLOW_CONFIG_PATH"] = "/home/ubuntu/aisci/deployment/deer-flow/config.yaml"
    
    client = DeerFlowClient()
    
    print("Sending message to DeerFlow with Onyx search request...")
    
    # We ask it to use the onyx_search tool specifically
    query = "Search Onyx for information about Tsallis statistics and its application in heavy ion collisions."
    
    async for event in client.stream(query, thread_id="test-onyx-001"):
        if event.type == "message":
            print(f"Assistant: {event.data.get('content', '')}")
        elif event.type == "tool_call":
            print(f"Tool Call: {event.data.get('name')} with args {event.data.get('args')}")
        elif event.type == "tool_output":
            print(f"Tool Output: {event.data.get('output')[:200]}...")

if __name__ == "__main__":
    asyncio.run(test_onyx_search())
