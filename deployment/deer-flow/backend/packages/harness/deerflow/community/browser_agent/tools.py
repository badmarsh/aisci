"""Browser Agent Tool — allows the agent to autonomously browse the web using a headless browser."""

import os
import json
import asyncio
import logging

from langchain.tools import tool

logger = logging.getLogger(__name__)


@tool("browser_agent", parse_docstring=True)
def browser_agent_tool(task: str) -> str:
    """Run an autonomous browser agent to complete a web-based task.
    
    Args:
        task: A detailed natural language description of what to do in the browser (e.g. 'Go to google.com and search for the latest news on AI, then return the top 3 headlines').
    """
    try:
        from browser_use import Agent, Browser
        from langchain_openai import ChatOpenAI
        
        # We instantiate a ChatOpenAI model, which relies on OPENAI_API_KEY being set in the environment.
        ChatOpenAI.provider = "openai"  # Monkey patch for browser-use v0.12.9
        llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
        
        # Configure the browser to run headlessly using the system Chrome executable
        browser = Browser(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            disable_security=True,
        )
        
        agent = Agent(
            task=task,
            llm=llm,
            browser=browser
        )
        
        async def run_agent():
            # Run the agent autonomously
            result = await agent.run()
            
            # Ensure browser processes are closed
            await browser.close()
            
            # The result is typically an AgentHistoryList, we can get the final result text.
            final_result = result.final_result()
            if final_result:
                return final_result
            else:
                return "Browser agent completed the task but returned no final textual result."
                
        # Run the async agent loop from a synchronous tool context
        # Check if an event loop is already running (e.g. in notebooks or async servers)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            
        return asyncio.run(run_agent())
        
    except ImportError as e:
        logger.error(f"Missing dependency for browser_agent_tool: {e}")
        return json.dumps({"error": f"Failed to import required libraries: {e}. Is browser-use installed?"}, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Browser agent failed: {e}")
        return json.dumps({"error": f"Browser agent failed to complete the task: {e}"}, ensure_ascii=False)
