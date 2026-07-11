#!/usr/bin/env python3
"""NotebookLM Session Keep-Alive v4.0 — MCP-native, no nlm dependency.

NotebookLM now uses MCP (cookie-based auth via Chrome CDP).
nlm CLI is no longer needed — auth is managed via:
  1. Chrome CDP keepalive + cookie extraction (primary)
  2. nb_autologin.py via Selenium (fallback)

Flow (every 20min):
  1. Check Chrome CDP is alive
  2. Extract fresh cookies via cdp_extract_both.py (with 502 retry)
  3. On CDP failure: try autologin
  4. On 3x autologin failure: Telegram SOS alert
"""

import json, subprocess, sys, os, time
from datetime import datetime
from pathlib import Path

CDP_PORT = 18800
MAX_RETRIES = 3
CDP_MAX_RETRIES = 5
BACKOFF_BASE = 30

LOCK_FILE = os.path.expanduser("~/.hermes/logs/nb_keepalive.lock")
LOG_FILE = os.path.expanduser("~/.hermes/logs/nb_keepalive.log")
LAST_LOGIN_FILE = os.path.expanduser("~/.hermes/logs/nb_last_login.txt")
ALERT_SCRIPT = os.path.expanduser("~/.hermes/scripts/nb_telegram_alert.py")
AUTOLOGIN_SCRIPT = os.path.expanduser("~/.hermes/scripts/nb_autologin.py")
CDP_EXTRACT_SCRIPT = os.path.expanduser("~/.hermes/scripts/cdp_extract_both.py")

PROFILES = ["pro", "legacy"]


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
    """Detect Cloudflare 502/503/504 or transient server errors."""
    markers = [
        "502", "503", "504",
        "cloudflare", "Cloudflare",
        "bad gateway", "Bad gateway",
        "origin_bad_gateway",
        "service unavailable", "Service Unavailable",
        "too many requests", "Too Many Requests",
        "rate limit", "Rate limit",
        "temporarily", "Temporarily",
        "try again", "Try again",
    ]
    return any(m in output for m in markers)


def ensure_chrome_alive():
    """Check if Chrome CDP is reachable; restart if dead."""
    try:
        import urllib.request
        urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/version", timeout=3)
        return True
    except Exception:
        log("Chrome CDP not responding, attempting restart...")
        start_script = os.path.expanduser("~/.hermes/scripts/start-chrome-keepalive.sh")
        if os.path.exists(start_script):
            subprocess.Popen(["bash", start_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(8)
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/version", timeout=3)
                log("Chrome restarted successfully")
                return True
            except Exception:
                pass
        log("Chrome CDP still dead after restart")
        return False


def cdp_refresh_all_with_retry(retries=CDP_MAX_RETRIES):
    """Extract cookies via CDP with exponential backoff on 502."""
    for attempt in range(retries):
        if not os.path.exists(CDP_EXTRACT_SCRIPT):
            log("  ❌ CDP extract script not found")
            break

        result = subprocess.run(
            ["python3", CDP_EXTRACT_SCRIPT],
            capture_output=True, text=True, timeout=90
        )

        combined = result.stdout + result.stderr

        if "httpx: OK" in combined:
            log("  ✅ CDP cookie extraction succeeded")
            return True

        if is_transient_error(combined):
            backoff = BACKOFF_BASE * (2 ** attempt)
            log(f"  ⚠️ CDP got Cloudflare error (attempt {attempt+1}/{retries}), backoff {backoff}s...")
            if attempt < retries - 1:
                time.sleep(backoff)
            continue

        log(f"  ⚠️ CDP failed (non-transient): {combined[-200:]}")
        break

    return False


def sync_windows_mcp():
    """Sync dict-format cookies to Windows MCP."""
    log("  ℹ️ Windows MCP sync: dict files ready at /tmp/{p}_dict.json")


def autologin_with_retry(profile):
    """Run nb_autologin.py with exponential backoff."""
    for attempt in range(MAX_RETRIES):
        backoff = BACKOFF_BASE * (2 ** attempt)
        log(f"  🔄 Login {profile} attempt {attempt+1}/{MAX_RETRIES} (backoff: {backoff}s)...")

        result = subprocess.run(
            ["python3", AUTOLOGIN_SCRIPT, "--profile", profile],
            capture_output=True, text=True, timeout=180
        )

        combined = result.stdout + result.stderr

        if result.returncode == 0:
            log(f"  ✅ Auto-login {profile} succeeded")
            return True

        if is_transient_error(combined):
            log(f"    ⚠️ autologin got transient error (attempt {attempt+1}), retrying...")
        elif result.stdout:
            log(f"    output: {result.stdout[-200:]}")

        if attempt < MAX_RETRIES - 1:
            time.sleep(backoff)

    return False


def send_sos(profile, reason):
    """Send Telegram SOS alert."""
    try:
        msg = (
            f"NotebookLM: {profile} auth expired and recovery failed.\n"
            f"Reason: {reason}\n"
            "Manual VNC login needed: http://localhost:6080/vnc.html\n"
            "Then: python3 ~/.hermes/scripts/cdp_extract_both.py"
        )
        subprocess.run(
            ["python3", ALERT_SCRIPT, "--message", msg, "--reason", f"{profile}_{reason}"],
            capture_output=True, text=True, timeout=10
        )
        log(f"  ✅ Telegram SOS sent ({profile})")
    except Exception as e:
        log(f"  ❌ Telegram SOS failed: {e}")


def main():
    log("═══ Keep-alive check ═══")

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
        # Step 1: Ensure Chrome is alive
        if not ensure_chrome_alive():
            log("❌ Chrome CDP unavailable — aborting")
            return

        # Step 2: Extract fresh cookies via CDP (with 502 retry)
        log("  🔄 Refreshing cookies via CDP...")
        cdp_ok = cdp_refresh_all_with_retry()

        if cdp_ok:
            sync_windows_mcp()
            with open(LAST_LOGIN_FILE, "w") as f:
                f.write(datetime.now().isoformat())
            log("═══ Cookies refreshed successfully ═══")
            return

        # Step 3: CDP failed — try autologin
        log("═══ CDP failed — trying autologin ═══")
        any_ok = False
        for profile in PROFILES:
            if autologin_with_retry(profile):
                any_ok = True
                # Re-extract cookies after login
                cdp_refresh_all_with_retry()
            else:
                send_sos(profile, "autologin_3x_failed")

        if any_ok:
            sync_windows_mcp()
            with open(LAST_LOGIN_FILE, "w") as f:
                f.write(datetime.now().isoformat())
            log("═══ Recovered via autologin ═══")
        else:
            log("═══ ALL RECOVERY FAILED — SOS sent ═══")

    finally:
        try:
            os.unlink(LOCK_FILE)
        except (FileNotFoundError, OSError):
            pass


if __name__ == "__main__":
    main()
