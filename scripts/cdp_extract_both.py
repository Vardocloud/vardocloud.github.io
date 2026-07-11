"""Extract cookies for BOTH profiles via CDP with authuser switching."""
import json, asyncio, websockets, httpx, re, os
from pathlib import Path

KEEP = {"notebooklm.google.com", "google.com", "accounts.google.com"}

async def extract_for_profile(ws, profile, authuser=None):
    """Navigate to notebooklm (optionally with authuser), extract cookies, filter, save."""
    
    # Navigate
    url = f"https://notebooklm.google.com/{'?authuser=' + str(authuser) if authuser is not None else ''}"
    await ws.send(json.dumps({"id": 1, "method": "Page.navigate", "params": {"url": url}}))
    await asyncio.sleep(5)
    
    # Get actual URL and account info
    await ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate",
        "params": {"expression": "window.location.href", "returnByValue": True}}))
    actual_url = ""
    for _ in range(5):
        msg = json.loads(await ws.recv())
        if msg.get("id") == 2:
            actual_url = msg.get("result", {}).get("result", {}).get("value", "")
            break
    
    okay = "accounts.google.com" not in actual_url
    print(f"Navigate: {url[:60]} -> {'OK' if okay else 'LOGIN'} | {actual_url[:80]}")
    
    if not okay:
        print(f"  SKIP: not logged in for this account")
        return None
    
    # Extract cookies for notebooklm URL
    await ws.send(json.dumps({"id": 3, "method": "Network.getCookies",
        "params": {"urls": ["https://notebooklm.google.com/"]}}))
    cdp_cookies = []
    for _ in range(5):
        msg = json.loads(await ws.recv())
        if msg.get("id") == 3:
            cdp_cookies = msg.get("result", {}).get("cookies", [])
            break
    
    # Filter
    filtered = []
    for c in cdp_cookies:
        domain = (c.get("domain", "") or "").lstrip(".")
        name = c.get("name", "")
        if name.startswith("__Host-"):
            continue
        if domain not in KEEP:
            continue
        c["domain"] = domain
        filtered.append(c)
    
    # Dedup
    seen = set()
    deduped = []
    for c in filtered:
        if c["name"] not in seen:
            seen.add(c["name"])
            deduped.append(c)
    
    # Save
    prof_dir = Path(f"/home/ubuntu/.notebooklm-mcp-cli/profiles/{profile}")
    prof_dir.mkdir(parents=True, exist_ok=True)
    json.dump(deduped, open(prof_dir / "cookies.json", "w"), indent=2, ensure_ascii=False)
    os.chmod(prof_dir / "cookies.json", 0o600)
    
    # storage_state
    state = {"cookies": deduped}
    sp = Path("/home/ubuntu/.notebooklm/profiles/default/storage_state.json")
    sp.parent.mkdir(parents=True, exist_ok=True)
    json.dump(state, open(sp, "w"), indent=2, ensure_ascii=False)
    os.chmod(sp, 0o600)
    
    # Dict for Windows
    d = {c["name"]: c["value"] for c in deduped}
    json.dump(d, open(f"/tmp/{profile}_dict.json", "w"), indent=2)
    
    print(f"  {profile}: {len(cdp_cookies)} -> {len(deduped)} cookies, SID={deduped[0]['value'][:25] if deduped else 'NONE'}")
    
    # httpx quick test
    jar = httpx.Cookies()
    for c in deduped:
        n, v, dom = c["name"], c["value"], c.get("domain", "")
        if n and v and dom:
            jar.set(n, v, domain=dom, path=c.get("path", "/"))
            if dom == "google.com":
                jar.set(n, v, domain="googleusercontent.com", path=c.get("path", "/"))
    
    h = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1",
    }
    
    with httpx.Client(cookies=jar, headers=h, follow_redirects=True, timeout=15) as client:
        resp = client.get("https://notebooklm.google.com/")
        url = str(resp.url)
        ok = "accounts.google.com" not in url
        print(f"  httpx: {'OK' if ok else 'FAIL'}")
    
    return deduped

async def main():
    tabs = httpx.get("http://127.0.0.1:18800/json", timeout=5).json()
    ws_url = None
    for t in tabs:
        if t.get("type") == "page":
            ws_url = t["webSocketDebuggerUrl"]
            break
    
    if not ws_url:
        print("No Chrome tab")
        return
    
    async with websockets.connect(ws_url) as ws:
        # Extract pro (authuser=0)
        print("=== PRO (authuser=0) ===")
        await extract_for_profile(ws, "pro", 0)
        
        # Extract legacy (authuser=1)
        print("=== LEGACY (authuser=1) ===")
        await extract_for_profile(ws, "legacy", 1)
        
        # Navigate back to default
        await ws.send(json.dumps({"id": 99, "method": "Page.navigate",
            "params": {"url": "https://notebooklm.google.com/"}}))

asyncio.run(main())
