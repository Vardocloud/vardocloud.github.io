# JSON API Parsing in no_agent Scripts

## The Problem

Hermes API wrappers (like `google_api.py`) return JSON output. Shell-based
parsing (`grep`, `awk`, `sed`) is fragile against JSON:

```bash
# WRONG — breaks on JSON format
OUTPUT=$(python3 google_api.py gmail search "is:unread" --max 10)
COUNT=$(echo "$OUTPUT" | grep -c "^Subject:" || true)  # Always 0 — JSON has "subject": not ^Subject:
```

JSON output looks like:
```json
[
  {
    "id": "19f4b114035f21bc",
    "from": "Someone <someone@example.com>",
    "subject": "Hello",
    "snippet": "Message preview...",
    "date": "Fri, 10 Jul 2026 ..."
  }
]
```

Shell patterns like `^Subject:` never match because:
- Keys are lowercase (`"subject":` not `Subject:`)
- Values are in JSON string format, not plain text headers
- Arrays and objects have structural nesting

## The Fix: Delegate to a Python Helper

Create a Python script that handles JSON parsing, then call it from the shell
wrapper:

**`check_service.py`** (standalone Python):
```python
#!/usr/bin/env python3
"""Consumes API output, parses JSON, produces clean output."""
import json, os, sys, subprocess

HOME = os.path.expanduser("~")
HERMES_HOME = os.environ.get("HERMES_HOME", f"{HOME}/.hermes")

# Set token path if needed
os.environ["HERMES_GOOGLE_TOKEN_PATH"] = f"{HERMES_HOME}/google_token.json"

GAPI = f"{HERMES_HOME}/skills/productivity/google-workspace/scripts/google_api.py"

result = subprocess.run(
    ["python3", GAPI, "gmail", "search", "is:unread", "--max", "10"],
    capture_output=True, text=True, timeout=30
)

if result.returncode != 0:
    sys.exit(1)  # silent fail for cron

try:
    msgs = json.loads(result.stdout)
except json.JSONDecodeError:
    sys.exit(0)  # no output = nothing to do

if not msgs:
    print("[SILENT]")  # no_agent: empty stdout = no delivery
    sys.exit(0)

# Process and print results
for m in msgs:
    print(f"  {m.get('from','?')} — {m.get('subject','?')}")
    print(f"    ↳ {m.get('snippet','')[:120]}")
```

**`check_service.sh`** (shell wrapper — called by cron):
```bash
#!/bin/bash
# Thin wrapper — delegates to Python for reliable parsing
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/check_service.py"
```

## Benefits

| Approach | Robustness | Maintainability | Error Handling |
|----------|-----------|-----------------|----------------|
| Shell grep/awk | ❌ Fragile (JSON format changes break it) | ❌ Hard to extend | ❌ Silent failures |
| Python sub-script | ✅ Proper JSON parsing | ✅ Easy to add fields/filters | ✅ Explicit exceptions |
| Python (standalone cron) | ✅ Best | ✅ Best | ✅ Best |

## When to Use

- Any no_agent cron script that consumes API output in JSON format
- When you need to filter, sort, or group results before delivery
- When the output shape is complex (arrays of objects with nested fields)

## Example: Priority Detection

```python
priority_keywords = ["edu.tr", "apa.org", "prolific"]
priority_msgs = []
other_msgs = []

for m in msgs:
    combined = (m.get("from","") + " " + m.get("subject","") + " " + m.get("snippet","")).lower()
    if any(k in combined for k in priority_keywords):
        priority_msgs.append(m)
    else:
        other_msgs.append(m)

if priority_msgs:
    print(f"⭐ Priority ({len(priority_msgs)}):")
    for m in priority_msgs:
        print(f"  {m['from']} — {m['subject']}")
```

## Pitfalls

- `set -e` in shell wrapper: if Python script crashes, shell wrapper exits
  non-zero → cron records `last_status: error`
- Always use `timeout=` in `subprocess.run()` to prevent hung processes
- Capture both stdout and stderr. Stderr goes to cron logs, stdout is delivered
- `[SILENT]` convention: empty meaningful output = no Telegram delivery
