#!/usr/bin/env python3
"""NotebookLM Bootstrap Warmup — runs once 30s after container start.

Purpose:
  After container restart, the keepalive loop won't fire for up to 1 hour.
  If auth expired during downtime, this catches it early.

Flow:
  1. Wait 30 seconds (let Chrome + BWS fully start)
  2. Run nb_keepalive.py once
  3. Exit (keepalive loop handles ongoing checks)
"""
import subprocess
import sys
import time
from datetime import datetime


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def main():
    log("Bootstrap warmup: waiting 30s for services to stabilize...")
    time.sleep(30)

    # Lighthouse: Run initial memory cleanup (expired TTL entries)
    log("Bootstrap warmup: running initial Lighthouse memory cleanup...")
    try:
        import sys as _sys
        _sys.path.insert(0, "/home/ubuntu/hermes-agent")
        from tools.memory_tool import lighthouse_cleanup_expired
        result = lighthouse_cleanup_expired()
        log(f"  Cleanup: {result}")
    except Exception as e:
        log(f"  Cleanup error: {e}")

    keepalive = "/home/ubuntu/.hermes/scripts/nb_keepalive.py"
    log("Bootstrap warmup: running initial keepalive check...")

    try:
        result = subprocess.run(
            ["python3", keepalive],
            capture_output=True, text=True, timeout=300
        )
        if result.stdout:
            print(result.stdout[-500:])
        if result.stderr:
            print(result.stderr[-200:], file=sys.stderr)
        log(f"Bootstrap warmup complete (exit code: {result.returncode})")
    except subprocess.TimeoutExpired:
        log("Bootstrap warmup: keepalive timed out (300s)")
    except Exception as e:
        log(f"Bootstrap warmup error: {e}")


if __name__ == "__main__":
    main()