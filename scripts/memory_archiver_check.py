"""
Memory Archiver Checker - monitors ARCHIVE.md and logs status
If entries need archiving, Vanitas will see the instruction in system prompt
"""

import os, sys

ARCHIVE_PATH = os.path.expanduser("~/.hermes/memories/ARCHIVE.md")
PROCESSED_LOG = os.path.expanduser("~/.hermes/memories/ARCHIVE_PROCESSED.log")

if not os.path.exists(ARCHIVE_PATH):
    sys.exit(0)

with open(ARCHIVE_PATH, encoding="utf-8") as f:
    raw = f.read().strip()

if not raw:
    os.remove(ARCHIVE_PATH)
    sys.exit(0)

# Count entries
count = raw.count("\n---\n") + 1 if raw else 0

# Get oldest timestamp
first_line = raw.split("\n")[0] if raw else ""
ts = first_line[1:20] if first_line.startswith("[") else "unknown"

print("MEMORY_ARCHIVE_PENDING=%d oldest=%s" % (count, ts))
