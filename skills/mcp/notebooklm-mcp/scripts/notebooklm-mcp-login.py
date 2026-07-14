#!/usr/bin/env python3
"""
NotebookLM MCP Login Script — connects to MCP's headless Chrome via CDP,
handles account chooser, passkey bypass, password login, and exports state.
Usage: python3 notebooklm_login.py
Dependencies: playwright, bw-serve (Bitwarden) on localhost:8087
"""
import asyncio, json, urllib.request, shutil, os
from datetime import datetime

# CONFIG — change these per environment
CDP_PORT = 49831         # MCP Chrome's remote debugging port
BW_ITEM_ID = "8a95abcd-65dd-4aa5-a255-b4660182d7cf"  # Bitwarden item ID
MCP_PROFILE = os.path.expanduser("~/.hermes/chrome_profile_notebooklm")
STORAGE_PATH = os.path.expanduser("~/.notebooklm/profiles/default/storage_state.json")
NOTEBOOK_URL = "https://notebooklm.google.com/notebook/NOTEBOOK_ID_HERE"

def get_cdp_url(port):
    """Discover the full WebSocket URL from Chrome's /json/version"""
    import http.client
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    conn.request("GET", "/json/version")
    resp = conn.getresponse()
    data = json.loads(resp.read())
    return data["webSocketDebuggerUrl"]

def get_credentials():
    """Fetch Google credentials from Bitwarden via bw-serve API"""
    req = urllib.request.Request(f"http://127.0.0.1:8087/object/item/{BW_ITEM_ID}")
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read())
    login = d["data"]["login"]
    return login["username"], login["password"]

async def login_flow(page, username, password):
    """Iterative login handler — tries each known Google login page state"""
    for attempt in range(15):
        url = page.url
        print(f"  [{attempt+1}] {url[:120]}")

        if "notebook" in url and "accounts" not in url and "notebooklm" in url:
            return True  # logged in

        if not url.startswith("https://accounts.google.com"):
            await page.wait_for_timeout(3000)
            continue

        # 1. Account chooser
        acct = await page.query_selector(f'[data-identifier="{username}"]')
        if acct:
            print("  → account chooser")
            await acct.click()
            await page.wait_for_timeout(5000)
            continue

        # 2. Email input
        email = await page.query_selector("#identifierId")
        if email and await email.is_visible():
            print("  → email input")
            await email.fill(username)
            await page.wait_for_timeout(500)
            nxt = await page.query_selector("#identifierNext")
            if nxt: await nxt.click()
            else: await page.keyboard.press("Enter")
            await page.wait_for_timeout(5000)
            continue

        # 3. Password (visible only)
        pwf = await page.query_selector('input[type="password"]')
        if pwf and await pwf.is_visible():
            print("  → password input")
            await pwf.fill(password)
            await page.wait_for_timeout(500)
            nxt = await page.query_selector("#passwordNext")
            if nxt: await nxt.click()
            else: await page.keyboard.press("Enter")
            await page.wait_for_timeout(5000)
            continue

        # 4. "Try another way" (passkey bypass)
        taw = await page.query_selector('a:has-text("Try another way"), button:has-text("Try another way")')
        if taw and await taw.is_visible():
            print("  → try another way")
            await taw.click()
            await page.wait_for_timeout(5000)
            continue

        # 5. "Enter your password" option
        epo = await page.query_selector('[data-value="PASSWORD"]')
        if epo:
            print("  → enter password option")
            await epo.click()
            await page.wait_for_timeout(5000)
            continue

        # Unknown state — wait
        print("  ⏳ waiting...")
        await page.wait_for_timeout(3000)

    return False

async def main():
    from playwright.async_api import async_playwright
    cdp_url = get_cdp_url(CDP_PORT)
    username, password = get_credentials()
    print(f"✅ Connecting to Chrome CDP...")

    async with async_playwright() as pw:
        browser = await pw.chromium.connect_over_cdp(cdp_url)
        ctx = browser.contexts[0]
        page = await ctx.new_page()

        await page.goto(NOTEBOOK_URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(4000)

        success = await login_flow(page, username, password)
        print(f"\n✅ Logged in: {success}")

        # Export state
        state = await ctx.storage_state()
        with open(STORAGE_PATH, "w") as f:
            json.dump(state, f, indent=2)
        gc = len([c for c in state.get("cookies", []) if "google" in c.get("domain", "")])
        print(f"💾 Saved: {len(state['cookies'])} cookies ({gc} Google)")

        # Empty storage_state so MCP doesn't try to inject them
        with open(STORAGE_PATH, "w") as f:
            json.dump({"cookies": [], "origins": []}, f)
        print(f"🧹 Emptied storage_state.json (MCP will use profile directly)")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
