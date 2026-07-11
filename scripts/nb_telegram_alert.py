#!/usr/bin/env python3
"""NotebookLM Telegram SOS Alert.

Sends a message to Edel's Telegram when NotebookLM auth fails 3x.
Zero dependencies — only uses urllib + os.environ.

Usage:
  python3 nb_telegram_alert.py --message "NotebookLM auth expired. Manual login needed."
  python3 nb_telegram_alert.py --message "Custom message" --reason "captcha"

Exit codes:
  0 = message sent successfully
  1 = send failed (network, token invalid)
  2 = missing args
"""
import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime


def send_telegram(message: str) -> dict:
    """Send message to Telegram bot API. Returns API response dict."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    channel = os.environ.get("TELEGRAM_HOME_CHANNEL", "")

    if not token:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN not set"}
    if not channel:
        return {"ok": False, "error": "TELEGRAM_HOME_CHANNEL not set"}

    # Parse channel: chat_id:message_thread_id (e.g., -1003917030255:12)
    parts = channel.split(":")
    chat_id = parts[0]
    message_thread_id = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None

    # Add timestamp prefix
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"\U0001F514 NotebookLM Alert\n{ts}\n\n{message}"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": full_message,
        "parse_mode": "HTML",
    }
    if message_thread_id:
        payload["message_thread_id"] = message_thread_id

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:200]}"}
    except urllib.error.URLError as e:
        return {"ok": False, "error": f"URL error: {e.reason}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Send NotebookLM SOS alert to Telegram")
    parser.add_argument("--message", "-m", required=True, help="Alert message")
    parser.add_argument("--reason", "-r", default="", help="Failure reason (optional, appended)")
    args = parser.parse_args()

    full_msg = args.message
    if args.reason:
        full_msg += f"\n\nReason: {args.reason}"

    result = send_telegram(full_msg)

    if result.get("ok"):
        msg_id = result.get("result", {}).get("message_id", "?")
        print(f"✅ Telegram alert sent (message_id={msg_id})")
        sys.exit(0)
    else:
        error = result.get("error", "unknown")
        print(f"❌ Telegram send failed: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()