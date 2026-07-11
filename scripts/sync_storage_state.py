#!/usr/bin/env python3
"""Sync cookies to MCP server's storage_state.json.

Two modes:
1. Netscape import: cookies.txt → storage_state.json (for initial import)
   Usage: python3 sync_storage_state.py --netscape /tmp/cookies_kenshin.txt

2. Profile sync: pro/cookies.json → storage_state.json (for keepalive flow)
   Usage: python3 sync_storage_state.py --profile pro

The MCP server (notebooklm-mcp) reads storage_state.json via _load_cookies().
Format: {"cookies": [{name, value, domain, path, secure, httpOnly, ...}]}
"""
import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

STORAGE_STATE_PATH = Path.home() / ".notebooklm" / "profiles" / "default" / "storage_state.json"
NLM_PROFILES_DIR = Path.home() / ".notebooklm-mcp-cli" / "profiles"


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


GOOGLE_DOMAINS = (
    "google.com", "notebooklm.google.com", "youtube.com",
    "accounts.google.com", "google.com.tr",
)

def is_google_domain(domain):
    """Check if domain belongs to Google ecosystem."""
    d = domain.lstrip(".").lower()
    for g in GOOGLE_DOMAINS:
        if d == g or d.endswith("." + g):
            return True
    return False


def parse_netscape(file_path):
    """Parse Netscape cookies.txt → list of cookie dicts (array format).

    Only Google/NotebookLM/YouTube domain cookies are kept.
    """
    cookies = []
    skipped = 0
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\r\n")
            stripped = line.strip()

            if not stripped:
                continue

            # Handle #HttpOnly_ prefix
            if stripped.startswith("#HttpOnly_"):
                line = line.replace("#HttpOnly_", "", 1)
                http_only = True
            elif stripped.startswith("#"):
                continue
            else:
                http_only = False

            parts = line.split("\t")
            if len(parts) < 7:
                continue

            domain = parts[0].strip()

            # Filter: only Google ecosystem cookies
            if not is_google_domain(domain):
                skipped += 1
                continue

            secure = parts[3].strip().upper() == "TRUE"
            expires = parts[4].strip()
            name = parts[5].strip()
            value = "\t".join(parts[6:]).strip()

            if not name:
                continue

            try:
                expires_int = int(expires)
            except ValueError:
                expires_int = -1

            cookie = {
                "name": name,
                "value": value,
                "domain": domain.lstrip("."),
                "path": parts[2].strip() or "/",
                "secure": secure,
                "httpOnly": http_only,
                "expires": expires_int if expires_int > 0 else -1,
                "session": expires_int <= 0,
                "priority": "Medium",
                "sameSite": "None" if secure else "Lax",
            }
            cookies.append(cookie)

    log(f"✅ Parsed {len(cookies)} Google cookies ({skipped} non-Google skipped)")
    return cookies, skipped


def cookies_to_storage_state(cookies):
    """Wrap cookie list in storage_state format."""
    return {"cookies": cookies}


def sync_from_profile(profile_name="pro"):
    """Copy pro/cookies.json → storage_state.json.

    nlm login --provider openclaw saves array format to cookies.json.
    MCP server needs {"cookies": [...]} format in storage_state.json.
    """
    source = NLM_PROFILES_DIR / profile_name / "cookies.json"
    if not source.exists():
        log(f"❌ Source not found: {source}")
        return False

    with open(source) as f:
        data = json.load(f)

    # cookies.json from openclaw is already a list (array format)
    if isinstance(data, list):
        # Filter: only Google ecosystem cookies
        filtered = [c for c in data if is_google_domain(c.get("domain", ""))]
        if len(filtered) < len(data):
            log(f"  Filtered: {len(data)} → {len(filtered)} cookies (removed {len(data) - len(filtered)} non-Google)")
        storage_state = cookies_to_storage_state(filtered)
    elif isinstance(data, dict) and "cookies" in data:
        # Already in storage_state format — filter cookies
        filtered = [c for c in data.get("cookies", []) if is_google_domain(c.get("domain", ""))]
        storage_state = cookies_to_storage_state(filtered)
    elif isinstance(data, dict):
        # Dict format (from --manual) — convert to array, filter by known Google cookie names
        log("⚠️ cookies.json is dict format (from --manual), converting to array...")
        cookies_list = []
        for name, value in data.items():
            cookies_list.append({
                "name": name,
                "value": value,
                "domain": ".google.com",
                "path": "/",
                "secure": True,
                "httpOnly": False,
            })
        storage_state = cookies_to_storage_state(cookies_list)
    else:
        log(f"❌ Unknown format in {source}")
        return False

    STORAGE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing
    if STORAGE_STATE_PATH.exists():
        backup = STORAGE_STATE_PATH.with_suffix(".json.bak")
        shutil.copy2(STORAGE_STATE_PATH, backup)
        log(f"  Backed up existing → {backup}")

    with open(STORAGE_STATE_PATH, "w") as f:
        json.dump(storage_state, f, ensure_ascii=False)
    os.chmod(STORAGE_STATE_PATH, 0o600)

    cookie_count = len(storage_state.get("cookies", []))
    log(f"✅ storage_state.json updated ({cookie_count} cookies from profile={profile_name})")
    return True


def sync_from_netscape(file_path):
    """Parse Netscape cookies.txt → storage_state.json."""
    if not os.path.exists(file_path):
        log(f"❌ File not found: {file_path}")
        return False

    cookies, skipped = parse_netscape(file_path)
    if not cookies:
        log(f"❌ No cookies parsed from {file_path}")
        return False

    storage_state = cookies_to_storage_state(cookies)
    STORAGE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing
    if STORAGE_STATE_PATH.exists():
        backup = STORAGE_STATE_PATH.with_suffix(".json.bak")
        shutil.copy2(STORAGE_STATE_PATH, backup)
        log(f"  Backed up existing → {backup}")

    with open(STORAGE_STATE_PATH, "w") as f:
        json.dump(storage_state, f, ensure_ascii=False)
    os.chmod(STORAGE_STATE_PATH, 0o600)

    log(f"✅ storage_state.json created ({len(cookies)} cookies from Netscape, {skipped} non-Google skipped)")
    return True


def main():
    parser = argparse.ArgumentParser(description="Sync cookies to MCP storage_state.json")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--profile", help="Sync from nlm profile cookies.json (e.g. 'pro')")
    group.add_argument("--netscape", help="Import from Netscape cookies.txt file")
    args = parser.parse_args()

    if args.profile:
        sync_from_profile(args.profile)
    elif args.netscape:
        sync_from_netscape(args.netscape)


if __name__ == "__main__":
    main()
