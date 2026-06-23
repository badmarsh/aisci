from __future__ import annotations
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print('Navigating to http://localhost:2026...')
        await page.goto('http://localhost:2026')
        print('Page title:', await page.title())
        
        # Wait for the UI to load
        await page.wait_for_selector('body')
        
        # Let's see if we can find some text that indicates the app loaded
        content = await page.content()
        if 'DeerFlow' in content or 'deerflow' in content.lower():
            print('DeerFlow UI found in page content.')
        else:
            print('Could not find DeerFlow in page content. Taking screenshot...')
            
        await page.screenshot(path='screenshot.png')
        print('Screenshot saved to screenshot.png')
        
        await browser.close()

asyncio.run(main())
