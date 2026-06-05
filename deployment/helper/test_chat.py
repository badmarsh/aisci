import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print('Navigating to http://localhost:2026...')
        await page.goto('http://localhost:2026')
        print('Page title:', await page.title())
        
        # Wait for the main UI to load
        await page.wait_for_selector('body')
        await page.wait_for_timeout(3000) # give it 3 seconds to fully render React/Vue

        # Let's dump all text to see what elements are present
        body_text = await page.locator('body').inner_text()
        print("--- BODY TEXT ---")
        print(body_text[:1000]) # First 1000 chars
        print("-----------------")
        
        # Find if our models are visible anywhere or in a dropdown
        if "Claude Sonnet 4.6" in body_text or "GPT-5.5" in body_text:
            print("SUCCESS: Found Multica models in the UI text!")
        else:
            print("Could not find Multica models in raw text. They might be in a dropdown that needs to be clicked.")

        await page.screenshot(path='screenshot_chat.png')
        print('Screenshot saved to screenshot_chat.png')
        
        await browser.close()

asyncio.run(main())
