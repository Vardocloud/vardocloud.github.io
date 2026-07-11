#!/bin/bash
# Gmail check for unread emails — no_agent wrapper
# Delegates to Python parser for reliable JSON handling
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/gmail_check.py"
