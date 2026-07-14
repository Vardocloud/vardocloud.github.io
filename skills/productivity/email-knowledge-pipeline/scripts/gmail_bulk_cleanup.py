#!/usr/bin/env python3
"""
Gmail bulk cleanup — mark as read + archive (remove INBOX) for processed emails.

Kullanım:
    python3 /home/ubuntu/.hermes/skills/productivity/email-knowledge-pipeline/scripts/gmail_bulk_cleanup.py

Özellikler:
- UNREAD mailleri okundu işaretler (--remove-labels UNREAD)
- INBOX'taki tüm mailleri arşivler (--remove-labels INBOX)
- Gmail ID truncation güvenli: JSON parse ile tam ID alır
- "No messages found" durumunu sessizce handle eder
- ALL_PROXY="" zorunlu (Google API auth için)
- --remove-labels comma-separated (script'in space-separated kabul etmediği gerçek bug — 7 Haz 2026)
- Batch özet: başarılı/başarısız sayıları, başına örnek 5 mail listesi

Çıktı: stdout'a işlem özeti, /tmp/email_cleanup.log'a detaylı log
"""
import json
import subprocess
import os
import sys
from pathlib import Path

GAPI = os.path.expanduser("~/.hermes/skills/productivity/google-workspace/scripts/google_api.py")
LOG_FILE = "/tmp/email_cleanup.log"


def run_gmail(*args, timeout=30):
    """Run google_api.py gmail subcommand. Returns (returncode, stdout, stderr)."""
    env = os.environ.copy()
    env["ALL_PROXY"] = ""
    r = subprocess.run(
        ["python3", GAPI, "gmail", *args],
        capture_output=True, text=True, timeout=timeout, env=env
    )
    return r.returncode, r.stdout, r.stderr


def search(query, max_results=100):
    """Search Gmail and return list of message dicts. Returns [] on empty/error."""
    rc, out, err = run_gmail("search", query, "--max", str(max_results))
    if rc != 0:
        log(f"SEARCH ERROR ({query}): {err[:200]}")
        return []
    if not out.strip() or "No messages found" in out:
        return []
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        log(f"JSON PARSE ERROR ({query}): {out[:200]}")
        return []


def modify(msg_id, remove_labels):
    """Remove labels from a message. Returns True on success.
    CRITICAL: --remove-labels expects COMMA-SEPARATED string, not space-separated list!
    The CLI argparse help says "Comma-separated label IDs to remove" but treats it
    as a single arg. Passing space-separated causes "unrecognized arguments" error.
    """
    rc, out, err = run_gmail("modify", msg_id, "--remove-labels", ",".join(remove_labels), timeout=15)
    if rc != 0:
        log(f"MODIFY ERROR ({msg_id}): {err[:200]}")
    return rc == 0


def log(msg):
    """Append to log file and stdout."""
    line = f"[email_cleanup] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass


def main():
    log("=" * 50)
    log(f"Gmail bulk cleanup started (PID {os.getpid()})")

    # STEP 1: Mark all UNREAD as read
    unread = search("is:unread", 50)
    log(f"Found {len(unread)} UNREAD emails")
    for m in unread[:5]:
        log(f"  unread: {m['from'][:40]} | {m['subject'][:60]}")
    marked_read = sum(1 for m in unread if modify(m["id"], ["UNREAD"]))
    log(f"Marked read: {marked_read}/{len(unread)}")

    # STEP 2: Archive all INBOX emails (broader scope, not just 7d)
    inbox = search("in:inbox", 100)
    log(f"Found {len(inbox)} INBOX emails")
    archived = 0
    for m in inbox:
        if modify(m["id"], ["INBOX"]):
            archived += 1
    log(f"Archived: {archived}/{len(inbox)}")

    log("=" * 50)
    log(f"Summary: marked_read={marked_read}, archived={archived}")
    log("Run `gmail search 'in:inbox'` to verify (should return 0).")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        log(f"FATAL: {e}")
        sys.exit(1)
