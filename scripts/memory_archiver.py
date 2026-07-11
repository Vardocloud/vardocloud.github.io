"""
Memory Archiver - pushes evicted memory entries to NotebookLM
Runs as Hermes cron job every 6 hours
Uses Hermes HTTP API to invoke MCP tools through gateway
"""

import os, json, time, sys

ARCHIVE_PATH = os.path.expanduser("~/.hermes/memories/ARCHIVE.md")
# Track processed entries by timestamp
PROCESSED_LOG = os.path.expanduser("~/.hermes/memories/ARCHIVE_PROCESSED.log")
NOTEBOOK_ID = "6c7f3daa-1640-4fad-9917-ec44bc432e58"
MAX_PER_RUN = 3
GATEWAY_URL = "http://127.0.0.1:8642"

if not os.path.exists(ARCHIVE_PATH):
    print("OK: No ARCHIVE.md")
    sys.exit(0)

with open(ARCHIVE_PATH, encoding="utf-8") as f:
    raw = f.read().strip()

if not raw:
    print("OK: ARCHIVE.md empty")
    sys.exit(0)

# Parse entries from ARCHIVE.md
# Format: [timestamp] [evicted from memory/user]\n<content>\n---\n
entries = []
current = []
for line in raw.split("\n"):
    if line.strip() == "---":
        if current:
            entries.append("\n".join(current).strip())
            current = []
    else:
        current.append(line)
if current:
    entries.append("\n".join(current).strip())

# Filter out already processed entries
processed_ids = set()
if os.path.exists(PROCESSED_LOG):
    with open(PROCESSED_LOG) as f:
        processed_ids = set(f.read().strip().split("\n"))

print("ARCHIVE.md entries: %d, already processed: %d" % (len(entries), len(processed_ids)))

new_entries = [e for i, e in enumerate(entries) if str(i) not in processed_ids]
if not new_entries:
    print("OK: All entries already processed")
    sys.exit(0)

# Try to add sources via HTTP API
pushed = 0
for i, entry in enumerate(new_entries[:MAX_PER_RUN]):
    title_line = entry.split("\n")[0][:80]
    text_preview = entry[:200]
    
    # Use Hermes tool HTTP API to call notebooklm-mcp
    payload = json.dumps({
        "tool": "notebooklm-mcp",
        "action": "add_source",
        "params": {
            "notebook_id": NOTEBOOK_ID,
            "source_type": "text",
            "text": text_preview,
            "title": "Memory Archive: %s" % title_line
        }
    })
    
    try:
        import urllib.request
        req = urllib.request.Request(
            "%s/api/tools/call" % GATEWAY_URL,
            data=payload.encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        resp = urllib.request.urlopen(req, timeout=30)
        result = resp.read().decode()
        print("PUSHED[%d]: %s" % (i, title_line))
        pushed += 1
    except Exception as e:
        print("FAIL[%d]: %s - %s" % (i, title_line, str(e)[:80]))
        # Gateway might not have tool HTTP API - fallback to silent
        pass

# Mark as processed
with open(PROCESSED_LOG, "a") as f:
    for i in range(min(len(new_entries), MAX_PER_RUN)):
        f.write(str(i) + "\n")

# Clean up ARCHIVE.md if all processed
if pushed >= len(new_entries) or pushed >= len(entries):
    os.remove(ARCHIVE_PATH)
    print("Cleaned ARCHIVE.md (all entries processed)")
else:
    # Keep unprocessed entries
    remaining = entries[MAX_PER_RUN:] if len(entries) > MAX_PER_RUN else []
    with open(ARCHIVE_PATH, "w", encoding="utf-8") as f:
        f.write("\n---\n\n".join(remaining))
    print("%d entries remaining in ARCHIVE.md" % len(remaining))

print("Done: %d pushed" % pushed)
