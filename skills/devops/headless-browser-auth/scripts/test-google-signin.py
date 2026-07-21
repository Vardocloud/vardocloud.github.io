#!/usr/bin/env python3
"""Quick diagnostic: Is Google sign-in blocked for this account/IP?

Usage: DISPLAY=:99 python3 test-google-signin.py [email]

Exit codes:
  0 = page loaded, email entry reached (not blocked)
  1 = BLOCKED at page load (signin/rejected before email)
  2 = BLOCKED after email entry
  3 = reached password page (account exists, browser accepted)
  4 = unknown state / error
"""

import asyncio, sys
from playwright.async_api import async_playwright

EMAIL = sys.argv[1] if len(sys.argv) > 1 else "test@gmail.com"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--window-size=1920,1080",
            ],
        )
        page = await browser.new_page()
        
        # Step 1: Load sign-in page
        await page.goto(
            "https://accounts.google.com/v3/signin/identifier"
            "?flowName=GlifWebSignIn&flowEntry=ServiceLogin"
        )
        await page.wait_for_timeout(3000)
        content = await page.content()
        
        if "Couldn't sign you in" in content:
            print("BLOCKED_IMMEDIATELY: Google rejected before email entry")
            await browser.close()
            sys.exit(1)
        
        print("PAGE_LOADED_OK: Sign-in page reached")
        
        # Step 2: Enter email
        try:
            email_input = await page.wait_for_selector(
                'input[name="identifier"]', timeout=5000
            )
            await email_input.fill(EMAIL)
            await page.wait_for_timeout(500)
            
            next_btn = await page.query_selector('button:has-text("Next")')
            if not next_btn:
                print("ERROR: No Next button found")
                await browser.close()
                sys.exit(4)
            
            await next_btn.click()
            await page.wait_for_timeout(3000)
            
            content2 = await page.content()
            
            if "Couldn't sign you in" in content2:
                print(f"BLOCKED_AT_EMAIL: {EMAIL} rejected")
                await browser.close()
                sys.exit(2)
            
            if "Enter your password" in content2 or "Welcome" in content2:
                print("PASSWORD_PAGE_REACHED: Browser accepted, ready for auth")
                await browser.close()
                sys.exit(3)
            
            # Unknown state — dump info
            url = page.url
            title = await page.title()
            print(f"UNKNOWN_STATE: url={url}, title={title}")
            await browser.close()
            sys.exit(4)
            
        except Exception as e:
            print(f"ERROR: {e}")
            await browser.close()
            sys.exit(4)

asyncio.run(main())
