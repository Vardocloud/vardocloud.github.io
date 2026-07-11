#!/usr/bin/env python3
"""Watch BWS secrets + auth.json, sync new keys to .env on Dashboard key entry.
Only syncs when auth.json changes (Dashboard updated a key via `hermes auth add`).
Does NOT blindly overwrite .env on every poll — only on detected changes.

Flow: Dashboard -> hermes auth add -> auth.json mtime changes
  --> watch_bws_sync.py detects -> reads from BWS -> writes to .env
  --> proxy picks up new key instantly (reads .env per-request)
"""
import os, subprocess, json, time
from datetime import datetime

ENV_PATH = os.path.expanduser("~/.hermes/.env")
AUTH_PATH = os.path.expanduser("~/.hermes/auth.json")
BWS_BIN = os.path.expanduser("~/.hermes/bin/bws")
PROXY_KEY_URL = "http://127.0.0.1:19998/key"
POLL_INTERVAL = 5  # seconds
LOG_FILE = os.path.expanduser("~/.hermes/logs/watch_bws_sync.log")

WATCH_CONFIG = [
    {"pool": "opencode-go", "bws_key": "OPENCODE_GO_API_KEY", "env_var": "OPENCODE_GO_API_KEY"},
    {"pool": "opencode-zen", "bws_key": "OPENCODE_ZEN_API_KEY", "env_var": "OPENCODE_ZEN_API_KEY"},
]


def log(msg):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
            f.flush()
    except Exception:
        pass


def get_bws_token():
    token = os.environ.get("BWS_ACCESS_TOKEN", "")
    if not token:
        tf = os.path.expanduser("~/.hermes/bw-cli/access_token")
        if os.path.exists(tf):
            token = open(tf).read().strip()
    return token


def bws_get_value(token, secret_key_name):
    """Get a single secret's value from BWS by key name."""
    env = os.environ.copy()
    env["BWS_ACCESS_TOKEN"] = token
    result = subprocess.run(
        [BWS_BIN, "secret", "list"],
        capture_output=True, text=True, timeout=10, env=env
    )
    if result.returncode != 0:
        return ""
    secrets = json.loads(result.stdout)
    for s in secrets:
        if s.get("key") == secret_key_name:
            val = subprocess.run(
                [BWS_BIN, "secret", "get", s["id"]],
                capture_output=True, text=True, timeout=10, env=env
            )
            if val.returncode == 0:
                data = json.loads(val.stdout)
                return data.get("value", "")
    return ""


def get_env_value(var_name):
    if not os.path.exists(ENV_PATH):
        return ""
    for line in open(ENV_PATH):
        if line.startswith(var_name + "="):
            return line.split("=", 1)[1].strip().strip("\"'")
    return ""


def set_env_value(var_name, value):
    lines = []
    found = False
    if os.path.exists(ENV_PATH):
        for line in open(ENV_PATH):
            if line.startswith(var_name + "="):
                lines.append(f"{var_name}={value}\n")
                found = True
            else:
                lines.append(line)
    if not found:
        lines.append(f"{var_name}={value}\n")
    with open(ENV_PATH, "w") as f:
        f.writelines(lines)


def notify_proxy(key_value):
    try:
        import urllib.request
        data = json.dumps({"key": key_value}).encode()
        req = urllib.request.Request(PROXY_KEY_URL, data=data,
            headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception:
        return False


def main():
    # Retry BWS token until available (Bitwarden applies secrets after proxy starts)
    token = get_bws_token()
    retries = 0
    while not token and retries < 30:
        log(f"Waiting for BWS token... (attempt {retries+1}/30)")
        time.sleep(5)
        token = get_bws_token()
        retries += 1
    if not token:
        log("ERROR: No BWS_ACCESS_TOKEN after 30 retries, giving up")
        return

    log(f"Watching {AUTH_PATH} for key changes (poll={POLL_INTERVAL}s)...")
    log("Config: " + str([c["pool"] for c in WATCH_CONFIG]))

    last_mtime = os.path.getmtime(AUTH_PATH) if os.path.exists(AUTH_PATH) else 0

    while True:
        try:
            time.sleep(POLL_INTERVAL)
            current_mtime = os.path.getmtime(AUTH_PATH) if os.path.exists(AUTH_PATH) else last_mtime

            # Only process if auth.json changed or if this is the first check
            needs_check = (current_mtime != last_mtime)
            last_mtime = current_mtime

            if not needs_check:
                continue

            log("auth.json changed, checking BWS for updates...")

            for cfg in WATCH_CONFIG:
                bws_val = bws_get_value(token, cfg["bws_key"])
                if not bws_val:
                    continue
                env_val = get_env_value(cfg["env_var"])
                if bws_val == env_val:
                    continue

                log(f"  {cfg['pool']}: BWS={bws_val[:12]}... env={env_val[:12]}... -> syncing to .env")
                set_env_value(cfg["env_var"], bws_val)
                ok = notify_proxy(bws_val)
                log(f"  {cfg['pool']}: .env updated + proxy {'NOTIFIED' if ok else 'UNREACHABLE'}")

        except KeyboardInterrupt:
            log("Stopped")
            break
        except Exception as e:
            log(f"ERROR: {e}")


if __name__ == "__main__":
    main()
