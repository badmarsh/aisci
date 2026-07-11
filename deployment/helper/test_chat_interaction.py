from __future__ import annotations
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print('Navigating to http://localhost:2026...')
        await page.goto('http://localhost:2026')
        
        await page.wait_for_selector('body')
        await page.wait_for_timeout(3000)
        
        # Let's try contenteditable
        chat_box = page.locator('[contenteditable="true"]')
        if await chat_box.count() > 0:
            print(f"Found {await chat_box.count()} contenteditable elements. Typing into the first one...")
            await chat_box.first.fill("Hello, this is a test from Playwright!")
            await chat_box.first.press("Enter")
        else:
            print("No contenteditable found. Trying generic input...")
            inputs = page.locator('input')
            if await inputs.count() > 0:
                print(f"Found {await inputs.count()} inputs. Typing into the last one...")
                await inputs.last.fill("Hello, this is a test from Playwright!")
                await inputs.last.press("Enter")
            else:
                print("No inputs found either.")
                
        print("Waiting 15 seconds for a response...")
        await page.wait_for_timeout(15000)
        
        body_text = await page.locator('body').inner_text()
        print("--- BODY TEXT AFTER 15 SECONDS ---")
        print(body_text[-1500:])
        print("-----------------")
        
        await page.screenshot(path='screenshot_final.png')
        print('Screenshot saved to screenshot_final.png')
        
        await browser.close()

asyncio.run(main())
