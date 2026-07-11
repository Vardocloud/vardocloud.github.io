#!/usr/bin/env python3
"""NotebookLM Auto-Login via CDP + Bitwarden (bw-serve HTTP API).
Connects to running Chrome on CDP_PORT, logs into Google,
updates nlm cookies. Triggered by nb_keepalive.py when session expired.

Lighthouse enhancements:
- RotateCookiesPage handler (detect + re-navigate)
- Captcha/challenge/phone detection + graceful fail
- Lock file (prevent parallel execution)
- WebSocket import fix (websocket-client, not websockets)
- Retry-aware logging
- Multi-account: pro (kenshin4155) + legacy (isimgorulsunn)
"""
import argparse
import asyncio, json, urllib.request, os, sys, time
from datetime import datetime

import pyotp

CDP_PORT = 18800
NOTEBOOK_URL = "https://notebooklm.google.com"
BW_SERVE = "http://127.0.0.1:8087"
TOTP_SECRET_FILE_LEGACY = os.path.expanduser("~/.hermes/.nb_totp_secret")
LOCK_FILE = os.path.expanduser("~/.hermes/logs/nb_autologin.lock")
FAIL_REASON_FILE = os.path.expanduser("~/.hermes/logs/nb_autologin_fail_reason.txt")

BWS_ITEM_MAP = {
    "pro": "google-pro",
    "legacy": "google-isimgorulsunn",
}


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def acquire_lock():
    """Prevent parallel execution. Returns True if lock acquired."""
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    if os.path.exists(LOCK_FILE):
        try:
            pid = int(open(LOCK_FILE).read().strip())
            # Check if process is still running
            try:
                os.kill(pid, 0)
                log(f"⚠️ Another nb_autologin running (PID {pid}), aborting")
                return False
            except (ProcessLookupError, PermissionError):
                pass  # Stale lock, remove
        except (ValueError, IOError):
            pass
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    return True


def release_lock():
    try:
        os.unlink(LOCK_FILE)
    except FileNotFoundError:
        pass


def write_fail_reason(reason):
    """Write failure reason for nb_keepalive.py to read."""
    try:
        with open(FAIL_REASON_FILE, "w") as f:
            f.write(f"{datetime.now().isoformat()}: {reason}")
    except IOError:
        pass


def bws_get(item_id):
    """Get Bitwarden item via bw-serve HTTP API."""
    req = urllib.request.Request(f"{BW_SERVE}/object/item/{item_id}")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def get_google_creds(profile_name="legacy"):
    """Get Google email + password from Bitwarden.

    profile_name: 'pro' → google-pro item (kenshin4155)
                  'legacy' → google item (isimgorulsunn)
    """
    bw_item_name = BWS_ITEM_MAP.get(profile_name, "google")
    items_req = urllib.request.Request(f"{BW_SERVE}/list/object/items")
    with urllib.request.urlopen(items_req, timeout=10) as r:
        items = json.loads(r.read())

    for item in items.get("data", {}).get("data", []):
        name = item.get("name", "").lower()
        if name == bw_item_name:
            data = bws_get(item["id"])
            login = data["data"]["login"]
            return login["username"], login["password"]

    raise RuntimeError(f"Google credentials not found in Bitwarden (item: {bw_item_name}, profile: {profile_name})")


def get_totp(profile_name="legacy"):
    """Generate TOTP code.

    profile_name: 'pro' → TOTP from Bitwarden google-pro item
                  'legacy' → TOTP from ~/.hermes/.nb_totp_secret
    """
    if profile_name == "pro":
        bw_item_name = BWS_ITEM_MAP["pro"]
        items_req = urllib.request.Request(f"{BW_SERVE}/list/object/items")
        with urllib.request.urlopen(items_req, timeout=10) as r:
            items = json.loads(r.read())
        for item in items.get("data", {}).get("data", []):
            if item.get("name", "").lower() == bw_item_name:
                data = bws_get(item["id"])
                totp_secret = data["data"].get("login", {}).get("totp")
                if totp_secret:
                    return pyotp.TOTP(totp_secret).now()
                break
        raise RuntimeError(f"TOTP secret not found in Bitwarden item '{bw_item_name}'")
    else:
        with open(TOTP_SECRET_FILE_LEGACY) as f:
            secret = f.read().strip().replace(" ", "")
        return pyotp.TOTP(secret).now()


async def eval_js(ws, js, msg_id=1):
    """Evaluate JS in page, return value."""
    await ws.send(json.dumps({
        "id": msg_id, "method": "Runtime.evaluate",
        "params": {"expression": js, "returnByValue": True, "awaitPromise": True}
    }))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get("id") == msg_id:
            return resp.get("result", {}).get("result", {}).get("value")


async def cdp(ws, method, params=None, cid=1):
    await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get("id") == cid:
            return resp.get("result", {})


async def login_flow(username, password, totp_code=None):
    """Full Google login flow via CDP. Returns True on success, False on fail."""
    from websockets import connect

    log("Connecting to Chrome CDP...")
    tabs = json.loads(urllib.request.urlopen(
        f"http://127.0.0.1:{CDP_PORT}/json", timeout=5
    ).read().decode())
    page = next((t for t in tabs if t.get("type") == "page"), None)
    if not page:
        log("No page found")
        return False, "no_chrome_page"
    page_ws = page["webSocketDebuggerUrl"]

    async with connect(page_ws) as ws:
        await cdp(ws, "Page.enable", cid=2)
        await cdp(ws, "Runtime.enable", cid=3)
        await cdp(ws, "Page.navigate", {"url": NOTEBOOK_URL}, cid=4)
        await asyncio.sleep(8)
        await cdp(ws, "Page.enable", cid=2)
        await cdp(ws, "Runtime.enable", cid=3)
        await cdp(ws, "Page.navigate", {"url": NOTEBOOK_URL}, cid=4)
        await asyncio.sleep(8)

        cid_counter = 10

        for attempt in range(15):  # 15 attempts, ~45s total
            url = await eval_js(ws, "window.location.href", msg_id=cid_counter) or ""
            title = await eval_js(ws, "document.title", msg_id=cid_counter + 1) or ""
            cid_counter += 2
            log(f"  [{attempt+1}] url={url[:80]} | title={title[:50]}")

            # SUCCESS: Already on NotebookLM
            if "notebooklm.google.com" in url and "accounts" not in url:
                log("✅ Already logged in!")
                return True, "success"

            # RotateCookiesPage — Google cookie rotation stuck
            if "RotateCookiesPage" in url:
                log("  → RotateCookiesPage detected, waiting + re-navigate...")
                await asyncio.sleep(5)
                await cdp(ws, "Page.navigate", {"url": NOTEBOOK_URL}, cid=cid_counter)
                cid_counter += 1
                await asyncio.sleep(5)
                continue

            # ACCOUNT CHOOSER — click the right account
            clicked = await eval_js(ws, f"""
                (function(){{
                    var el = document.querySelector('[data-identifier="{username}"]');
                    if(el){{ el.click(); return "clicked"; }}
                    return null;
                }})()
            """, msg_id=cid_counter)
            cid_counter += 1
            if clicked:
                log("  → account chooser clicked")
                await asyncio.sleep(5)
                continue

            # EMAIL INPUT
            has_email = await eval_js(ws, '!!document.querySelector("#identifierId")', msg_id=cid_counter)
            cid_counter += 1
            if has_email:
                log("  → filling email")
                await cdp(ws, "Input.insertText", {"text": username}, cid=cid_counter)
                cid_counter += 1
                await asyncio.sleep(1)
                await eval_js(ws, 'document.querySelector("#identifierNext")?.click()', msg_id=cid_counter)
                cid_counter += 1
                await asyncio.sleep(5)
                continue

            # PASSWORD
            has_pwd = await eval_js(ws, '!!document.querySelector("input[type=password]")', msg_id=cid_counter)
            cid_counter += 1
            if has_pwd:
                log("  → filling password")
                await cdp(ws, "Input.insertText", {"text": password}, cid=cid_counter)
                cid_counter += 1
                await asyncio.sleep(1)
                await eval_js(ws, 'document.querySelector("#passwordNext")?.click()', msg_id=cid_counter)
                cid_counter += 1
                await asyncio.sleep(5)
                continue

            # TOTP (2FA)
            has_totp = await eval_js(ws, '!!document.querySelector("input[autocomplete=\\"one-time-code\\"]")', msg_id=cid_counter)
            cid_counter += 1
            if has_totp:
                code = totp_code or get_totp()
                log(f"  → entering TOTP: {code}")
                await cdp(ws, "Input.insertText", {"text": code}, cid=cid_counter)
                cid_counter += 1
                await asyncio.sleep(1)
                await eval_js(ws, 'document.querySelector("#totpNext, form button[type=submit]")?.click()', msg_id=cid_counter)
                cid_counter += 1
                await asyncio.sleep(5)
                continue

            # "Try another way" (passkey bypass)
            taw = await eval_js(ws, """
                (function(){
                    var btns = document.querySelectorAll('[role=button], button');
                    for(var b of btns){
                        if(b.innerText.includes('Try another way')){ b.click(); return true; }
                    }
                    return false;
                })()
            """, msg_id=cid_counter)
            cid_counter += 1
            if taw:
                log("  → try another way")
                await asyncio.sleep(3)
                continue

            # "Enter your password" option
            epo = await eval_js(ws, """
                (function(){
                    var el = document.evaluate("//*[text()='Enter your password']",
                        document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if(el){ el.click(); return true; }
                    return false;
                })()
            """, msg_id=cid_counter)
            cid_counter += 1
            if epo:
                log("  → enter password option")
                await asyncio.sleep(3)
                continue

            # TOTP option after "try another way"
            totp_option = await eval_js(ws, """
                (function(){
                    var links = document.querySelectorAll('[role=link], [role=button], li');
                    for(var l of links){
                        var t = l.innerText || '';
                        if(t.includes('Authenticator app') || t.includes('Google Authenticator') ||
                           t.includes('TOTP') || t.includes('verification code from app')){
                            l.click(); return true;
                        }
                    }
                    return false;
                })()
            """, msg_id=cid_counter)
            cid_counter += 1
            if totp_option:
                log("  → TOTP option selected")
                await asyncio.sleep(3)
                continue

            # Captcha detection
            captcha = await eval_js(ws, """
                (function(){
                    var body = document.body.innerText || '';
                    var has_recaptcha = !!document.querySelector('.g-recaptcha, #recaptcha, iframe[src*="recaptcha"]');
                    var has_hcaptcha = !!document.querySelector('.h-captcha, iframe[src*="hcaptcha"]');
                    if(has_recaptcha || has_hcaptcha || body.includes('not a robot') || body.includes('unusual activity')){
                        return 'captcha';
                    }
                    return null;
                })()
            """, msg_id=cid_counter)
            cid_counter += 1
            if captcha:
                log("  ❌ CAPTCHA detected — cannot auto-solve")
                write_fail_reason("captcha_detected")
                return False, "captcha"

            # Phone verification detection
            phone = await eval_js(ws, """
                (function(){
                    var body = document.body.innerText || '';
                    if(body.includes('phone number') || body.includes('text message') ||
                       body.includes('verify your identity') || body.includes('send a code')){
                        return 'phone';
                    }
                    return null;
                })()
            """, msg_id=cid_counter)
            cid_counter += 1
            if phone:
                log("  ❌ Phone verification required")
                write_fail_reason("phone_verification_required")
                return False, "phone"

            # "Verify it's you" / suspicious activity
            suspicious = await eval_js(ws, """
                (function(){
                    var body = document.body.innerText || '';
                    if(body.includes('Verify it') || body.includes('suspicious') ||
                       body.includes('unusual activity') || body.includes('confirm your identity')){
                        return 'suspicious';
                    }
                    return null;
                })()
            """, msg_id=cid_counter)
            cid_counter += 1
            if suspicious:
                log("  ❌ Suspicious activity / verify challenge")
                write_fail_reason("verify_challenge")
                return False, "suspicious"

            # Unknown state — wait and retry
            log("  ⏳ waiting...")
            await asyncio.sleep(3)

        log("  ❌ Login timed out after 15 attempts")
        write_fail_reason("timeout_15attempts")
        return False, "timeout"

    # async with automatically closes ws


async def main():
    parser = argparse.ArgumentParser(description="NotebookLM Auto-Login via CDP + Bitwarden")
    parser.add_argument("--profile", default="legacy", choices=["pro", "legacy"],
                        help="Profile to login: pro (kenshin4155) or legacy (isimgorulsunn)")
    args = parser.parse_args()
    profile = args.profile

    if not acquire_lock():
        sys.exit(1)  # Another instance running

    try:
        log(f"Getting Google credentials from BWS (profile={profile})...")
        username, password = get_google_creds(profile)
        code = get_totp(profile)
        log(f"  ✓ user: {username[:3]}... | TOTP ready | profile={profile}")

        success, reason = await login_flow(username, password, totp_code=code)
        log(f"Login {'✅ OK' if success else '❌ FAILED'} ({reason})")

        if success:
            log(f"✅ Login successful — cookies written to Chrome CDP (profile={profile})")
            # MCP kullanıyoruz, nlm binary'sine gerek yok
            # Cookie'ler zaten login flow'da Chrome'a yazıldı
            # cdp_extract_both.py sonraki keepalive'da alır
        else:
            log(f"⚠️ Login failed: {reason}")
    except Exception as e:
        log(f"❌ Error: {e}")
        write_fail_reason(f"exception: {e}")
    finally:
        release_lock()


if __name__ == "__main__":
    asyncio.run(main())