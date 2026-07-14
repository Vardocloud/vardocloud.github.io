#!/usr/bin/env python3
"""NotebookLM Session Keep-Alive v5.0 — dual Chrome, dual MCP profile.

Architecture:
  Chrome 1 (port 18800) → profile: chrome_profile_notebooklm     → MCP: pro (kenshin4155)
  Chrome 2 (port 18801) → profile: chrome_profile_notebooklm_legacy → MCP: legacy (isimgorulsunn)

Flow (every 20min per Chrome):
  1. Check Chrome CDP is alive; restart if dead
  2. Extract fresh cookies via CDP (with 502 retry)
  3. Sync cookies to MCP auth profile
  4. On CDP failure: try autologin
  5. On 3x autologin failure: Telegram SOS alert
"""

import json, subprocess, sys, os, time, asyncio, websockets, httpx, urllib.request
from datetime import datetime
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────
CDP_INSTANCES = {
    "pro": {
        "port": 18800,
        "profile_dir": "/home/ubuntu/.hermes/chrome_profile_notebooklm",
        "start_script": "/home/ubuntu/.hermes/scripts/start-chrome-keepalive.sh",
        "mcp_profile": "pro",
        "account": "kenshin4155",
    },
    "legacy": {
        "port": 18801,
        "profile_dir": "/home/ubuntu/.hermes/chrome_profile_notebooklm_legacy",
        "start_script": "/home/ubuntu/.hermes/scripts/start-chrome-keepalive-legacy.sh",
        "mcp_profile": "legacy",
        "account": "isimgorulsunn",
    },
}

KEEP_DOMAINS = {"notebooklm.google.com", "google.com", "accounts.google.com"}
MAX_RETRIES = 3
CDP_MAX_RETRIES = 5
BACKOFF_BASE = 30

LOCK_FILE = os.path.expanduser("~/.hermes/logs/nb_keepalive.lock")
LOG_FILE = os.path.expanduser("~/.hermes/logs/nb_keepalive.log")
LAST_LOGIN_FILE = os.path.expanduser("~/.hermes/logs/nb_last_login.txt")
ALERT_SCRIPT = os.path.expanduser("~/.hermes/scripts/nb_telegram_alert.py")
AUTOLOGIN_SCRIPT = os.path.expanduser("~/.hermes/scripts/nb_autologin.py")


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except IOError:
        pass


def is_transient_error(output):
    markers = [
        "502", "503", "504", "cloudflare", "Cloudflare",
        "bad gateway", "Bad gateway", "origin_bad_gateway",
        "service unavailable", "Service Unavailable",
        "too many requests", "Too Many Requests",
        "rate limit", "Rate limit", "temporarily", "try again",
    ]
    return any(m.lower() in output.lower() for m in markers)


# ── Chrome health ────────────────────────────────────────────────

def ensure_chrome_alive(name, cfg):
    """Check if Chrome CDP is reachable; restart if dead."""
    port = cfg["port"]
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=3)
        return True
    except Exception:
        log(f"  [{name}] Chrome CDP port {port} not responding, restarting...")
        start_script = cfg["start_script"]
        if os.path.exists(start_script):
            subprocess.Popen(["bash", start_script],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(8)
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=3)
                log(f"  [{name}] Chrome restarted on port {port}")
                return True
            except Exception:
                pass
        log(f"  [{name}] Chrome CDP port {port} still dead after restart")
        return False


# ── Cookie extraction (per port) ─────────────────────────────────

async def extract_cookies_from_port(port):
    """Connect to CDP port, navigate to notebooklm, extract cookies."""
    try:
        tabs = httpx.get(f"http://127.0.0.1:{port}/json", timeout=5).json()
    except Exception as e:
        log(f"    CDP port {port} unreachable: {e}")
        return None

    ws_url = None
    for t in tabs:
        if t.get("type") == "page":
            ws_url = t["webSocketDebuggerUrl"]
            break
    if not ws_url:
        log(f"    No open page on port {port}")
        return None

    async with websockets.connect(ws_url) as ws:
        # Navigate to notebooklm
        await ws.send(json.dumps({
            "id": 1, "method": "Page.navigate",
            "params": {"url": "https://notebooklm.google.com/"}
        }))
        await asyncio.sleep(5)

        # Check we're logged in (not on accounts.google.com)
        await ws.send(json.dumps({
            "id": 2, "method": "Runtime.evaluate",
            "params": {"expression": "window.location.href", "returnByValue": True}
        }))
        actual_url = ""
        for _ in range(10):
            msg = json.loads(await ws.recv())
            if msg.get("id") == 2:
                actual_url = msg.get("result", {}).get("result", {}).get("value", "")
                break

        if "accounts.google.com" in actual_url:
            log(f"    Port {port}: NOT LOGGED IN (redirected to accounts.google.com)")
            return None

        # Extract cookies
        await ws.send(json.dumps({
            "id": 3, "method": "Network.getCookies",
            "params": {"urls": ["https://notebooklm.google.com/"]}
        }))
        cdp_cookies = []
        for _ in range(10):
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
            if domain not in KEEP_DOMAINS:
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

        log(f"    Port {port}: {len(cdp_cookies)} raw → {len(deduped)} filtered cookies | "
            f"url={actual_url[:60]}")

        # httpx quick test
        jar = httpx.Cookies()
        for c in deduped:
            n, v, dom = c["name"], c["value"], c.get("domain", "")
            if n and v and dom:
                jar.set(n, v, domain=dom, path=c.get("path", "/"))
        h = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        }
        with httpx.Client(cookies=jar, headers=h, follow_redirects=True, timeout=15) as client:
            resp = client.get("https://notebooklm.google.com/")
            ok = "accounts.google.com" not in str(resp.url)
            log(f"    httpx: {'OK' if ok else 'FAIL'}")
            if not ok:
                return None

        return deduped


def cdp_extract_with_retry(name, cfg):
    """Extract cookies from named Chrome instance with retry."""
    port = cfg["port"]
    for attempt in range(CDP_MAX_RETRIES):
        try:
            cookies = asyncio.run(extract_cookies_from_port(port))
            if cookies:
                return cookies
        except Exception as e:
            log(f"    [{name}] CDP extraction error: {e}")

        backoff = BACKOFF_BASE * (2 ** attempt)
        log(f"    [{name}] CDP retry {attempt+1}/{CDP_MAX_RETRIES}, backoff {backoff}s...")
        if attempt < CDP_MAX_RETRIES - 1:
            time.sleep(backoff)

    return None


# ── MCP auth sync (per profile) ──────────────────────────────────

def find_nlm():
    for p in [os.path.expanduser("~/.local/bin/nlm"),
              os.path.expanduser("~/.local/share/uv/tools/notebooklm-mcp-cli/bin/nlm")]:
        if os.path.exists(p):
            return p
    return None


def sync_mcp_auth_for(instance_name, cfg, cookies):
    """Write cookies to MCP profile and run nlm login."""
    mcp_profile = cfg["mcp_profile"]

    # Write cookies.json directly
    prof_dir = Path(f"/home/ubuntu/.notebooklm-mcp-cli/profiles/{mcp_profile}")
    prof_dir.mkdir(parents=True, exist_ok=True)
    cookie_path = prof_dir / "cookies.json"
    json.dump(cookies, open(cookie_path, "w"), indent=2, ensure_ascii=False)
    os.chmod(cookie_path, 0o600)
    log(f"    [{instance_name}] Wrote {len(cookies)} cookies → {cookie_path}")

    # Also sync via nlm login (for token extraction)
    nlm_path = find_nlm()
    if not nlm_path:
        log(f"    [{instance_name}] ⚠️ nlm CLI not found, skipping login sync")
        return True  # cookies written is good enough

    try:
        result = subprocess.run(
            [nlm_path, "login", "--provider", "openclaw",
             "--cdp-url", f"http://127.0.0.1:{cfg['port']}",
             "--profile", mcp_profile, "--force"],
            capture_output=True, text=True, timeout=120
        )
        output = result.stdout + result.stderr
        if result.returncode == 0 and "Successfully authenticated" in output:
            acct = cfg["account"]
            log(f"    [{instance_name}] ✅ MCP auth synced ({acct})")
            return True
        else:
            log(f"    [{instance_name}] ⚠️ MCP login sync failed: {output[-150:]}")
            return False
    except subprocess.TimeoutExpired:
        log(f"    [{instance_name}] ⚠️ MCP login sync timed out")
        return False
    except Exception as e:
        log(f"    [{instance_name}] ⚠️ MCP login sync error: {e}")
        return False


# ── Autologin fallback ───────────────────────────────────────────

def autologin_with_retry(name, cfg):
    for attempt in range(MAX_RETRIES):
        backoff = BACKOFF_BASE * (2 ** attempt)
        log(f"    [{name}] Auto-login attempt {attempt+1}/{MAX_RETRIES} (backoff: {backoff}s)...")
        result = subprocess.run(
            ["python3", AUTOLOGIN_SCRIPT, "--profile", cfg["mcp_profile"]],
            capture_output=True, text=True, timeout=180
        )
        combined = result.stdout + result.stderr
        if result.returncode == 0:
            log(f"    [{name}] ✅ Auto-login succeeded")
            return True
        if is_transient_error(combined):
            log(f"    [{name}] transient error, retrying...")
        if attempt < MAX_RETRIES - 1:
            time.sleep(backoff)
    return False


def send_sos(name, cfg, reason):
    try:
        msg = (
            f"NotebookLM [{name}] ({cfg['account']}): auth expired and recovery failed.\n"
            f"Port {cfg['port']} | Reason: {reason}\n"
            f"Manual VNC login needed: http://localhost:6080/vnc.html\n"
            f"Keepalive restart: bash {cfg['start_script']}"
        )
        subprocess.run(
            ["python3", ALERT_SCRIPT, "--message", msg, "--reason", f"{name}_{reason}"],
            capture_output=True, text=True, timeout=10
        )
        log(f"    [{name}] ✅ Telegram SOS sent")
    except Exception as e:
        log(f"    [{name}] ❌ Telegram SOS failed: {e}")


# ── Main ─────────────────────────────────────────────────────────

def main():
    log("═══ Keep-alive check (dual Chrome) ═══")

    # Lock
    try:
        os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
        if os.path.exists(LOCK_FILE):
            try:
                old_pid = int(open(LOCK_FILE).read().strip())
                os.kill(old_pid, 0)
                log("⚠️ Another keepalive running, aborting")
                return
            except (ProcessLookupError, PermissionError, ValueError, IOError):
                pass
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))
    except IOError:
        pass

    try:
        all_ok = True

        for name, cfg in CDP_INSTANCES.items():
            log(f"─── [{name}] {cfg['account']} (port {cfg['port']}) ───")

            # Step 1: Ensure Chrome alive
            if not ensure_chrome_alive(name, cfg):
                log(f"  [{name}] ❌ Chrome dead, trying autologin...")
                if autologin_with_retry(name, cfg):
                    time.sleep(5)
                else:
                    send_sos(name, cfg, "chrome_dead")
                    all_ok = False
                    continue

            # Step 2: Extract cookies
            log(f"  [{name}] Extracting cookies via CDP...")
            cookies = cdp_extract_with_retry(name, cfg)

            if cookies:
                # Step 3: Sync to MCP
                sync_mcp_auth_for(name, cfg, cookies)
                log(f"  [{name}] ✅ Done — {len(cookies)} cookies synced")
            else:
                # Try autologin
                log(f"  [{name}] CDP extraction failed, trying autologin...")
                if autologin_with_retry(name, cfg):
                    time.sleep(5)
                    cookies = cdp_extract_with_retry(name, cfg)
                    if cookies:
                        sync_mcp_auth_for(name, cfg, cookies)
                        log(f"  [{name}] ✅ Recovered via autologin")
                    else:
                        send_sos(name, cfg, "autologin_success_but_no_cookies")
                        all_ok = False
                else:
                    send_sos(name, cfg, "autologin_failed")
                    all_ok = False

        # Update last login timestamp
        if all_ok:
            with open(LAST_LOGIN_FILE, "w") as f:
                f.write(datetime.now().isoformat())
            log("═══ All profiles refreshed ✅ ═══")
        else:
            log("═══ Some profiles failed — SOS sent ═══")

    finally:
        try:
            os.unlink(LOCK_FILE)
        except (FileNotFoundError, OSError):
            pass


if __name__ == "__main__":
    main()
