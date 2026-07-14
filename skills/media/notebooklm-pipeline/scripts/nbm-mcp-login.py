#!/usr/bin/env python3
"""
NotebookLM MCP Login — Option I
Cleans profile, logs in via Playwright persistent context, empties storage_state
so MCP's Selenium doesn't corrupt the session on restart.

Usage:
  python3 nbm-mcp-login.py

Requires: bw-serve running on port 8087 (for credentials),
          Playwright, Chromium
"""
import asyncio, json, urllib.request, shutil, os
from datetime import datetime

BW_ID = "8a95abcd-65dd-4aa5-a255-b4660182d7cf"
BW_URL = f"http://127.0.0.1:8087/object/item/{BW_ID}"
MCP_PROFILE = os.path.expanduser("~/.hermes/chrome_profile_notebooklm")
STORE = os.path.expanduser("~/.notebooklm/profiles/default/storage_state.json")
NBOOK = "https://notebooklm.google.com/notebook/6c7f3daa-1640-4fad-9917-ec44bc432e58"

def get_creds():
    req = urllib.request.Request(BW_URL)
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read())
    l = d["data"]["login"]
    return l["username"], l["password"]

async def main():
    print("=== NBM MCP Login (Option I) ===")
    u, p = get_creds()
    
    # Empty storage_state so MCP doesn't try to inject Playwright cookies via Selenium
    with open(STORE, "w") as f:
        json.dump({"cookies": [], "origins": []}, f)
    print("🧹 storage_state.json emptied")
    
    # Clean profile dir but keep it existing
    if os.path.exists(MCP_PROFILE):
        shutil.rmtree(MCP_PROFILE, ignore_errors=True)
    os.makedirs(MCP_PROFILE, exist_ok=True)
    print(f"🧹 Profile cleaned: {MCP_PROFILE}")
    
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        # Launch persistent context INTO MCP profile
        # headless=False with display=:99 is more reliable — headless may trigger bot rejection
        browser = await pw.chromium.launch_persistent_context(
            MCP_PROFILE,
            headless=False,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--display=:99"],
            viewport={"width": 1280, "height": 900},
        )
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        print("📄 Navigating to NotebookLM...")
        await page.goto(NBOOK, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(4000)
        
        for attempt in range(20):
            url = page.url
            print(f"\n--- Attempt {attempt+1} ---")
            print(f"📍 {url[:130]}")
            
            # Early exit for bot protection — don't waste attempts
            if "signin/rejected" in url:
                print("\n⚠️ GOOGLE BOT PROTECTION ACTIVE!")
                print("   All automated attempts will fail for 30+ min.")
                print("   Use VNC for manual login (see references/vnc-novnc-container-setup.md)")
                break
            
            # CORRECT login check: must be on notebooklm domain AND not on accounts
            if "notebooklm.google.com" in url and "accounts" not in url:
                print("✅ LOGGED IN!")
                break
            
            if not url.startswith("https://accounts.google.com"):
                await page.wait_for_timeout(3000)
                continue
            
            # Priority order with is_visible() checks — see SKILL.md pitfalls
            acct = await page.query_selector(f'[data-identifier="{u}"]')
            if acct:
                print("📌 Account chooser")
                await acct.click()
                await page.wait_for_timeout(5000)
                continue
            
            email = await page.query_selector("#identifierId")
            if email and await email.is_visible():
                print("📌 Email")
                await email.fill(u)
                await page.wait_for_timeout(500)
                nxt = await page.query_selector("#identifierNext")
                if nxt: await nxt.click()
                else: await page.keyboard.press("Enter")
                await page.wait_for_timeout(5000)
                continue
            
            pwf = await page.query_selector('input[type="password"]')
            if pwf and await pwf.is_visible():
                print("📌 Password")
                await pwf.fill(p)
                await page.wait_for_timeout(500)
                nxt = await page.query_selector("#passwordNext")
                if nxt: await nxt.click()
                else: await page.keyboard.press("Enter")
                await page.wait_for_timeout(5000)
                continue
            
            taw = await page.query_selector('a:has-text("Try another way")')
            if taw and await taw.is_visible():
                print("📌 Try another way")
                await taw.click()
                await page.wait_for_timeout(5000)
                continue
            
            epo = await page.query_selector('[data-value="PASSWORD"]')
            if epo:
                print("📌 Enter password option")
                await epo.click()
                await page.wait_for_timeout(5000)
                continue
            
            print("⏳ Waiting...")
            await page.wait_for_timeout(3000)
        
        print(f"\n🏁 Final URL: {page.url[:150]}")
        
        # Check for signin/rejected
        if "signin/rejected" in page.url:
            print("\n⚠️ GOOGLE BOT PROTECTION ACTIVE!")
            print("   'signin/rejected' means this IP/Chrome fingerprint is flagged.")
            print("   Solutions:")
            print("   a) Wait 30+ min and retry (cooldown is IP-based)")
            print("   b) Switch IP/proxy")
            print("   c) Use VNC (x11vnc + noVNC + Cloudflare tunnel) for manual login")
            print("   See vault: references/vnc-novnc-container-setup.md")
        
        # Save storage state (empty — MCP won't use it)
        state = await browser.storage_state()
        with open(STORE, "w") as f:
            json.dump(state, f, indent=2)
        
        gc = len([c for c in state.get("cookies", []) if "google" in c.get("domain", "")])
        print(f"💾 Saved: {len(state['cookies'])} cookies ({gc} Google)")
        
        if "notebooklm.google.com" in page.url and "accounts" not in page.url:
            print("\n✅ Profile ready! MCP will find the logged-in session.")
            # Now empty it again for MCP compatibility
            with open(STORE, "w") as f:
                json.dump({"cookies": [], "origins": []}, f)
            print("🧹 storage_state.json re-emptied for MCP compatibility")
        elif "signin/rejected" in page.url:
            print("\n⚠️ Google bot protection active. Cannot login automatically.")
        else:
            print("\n⚠️ Login incomplete. Check the page manually.")
        
        await browser.close()
        print("👋 Done")

if __name__ == "__main__":
    asyncio.run(main())
