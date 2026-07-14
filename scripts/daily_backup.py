#!/usr/bin/env python3
"""Daily GitHub backup for ~/.hermes — no_agent cron script."""

import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

HERMES = Path.home() / ".hermes"
BWS = HERMES / "bin" / "bws"
TOKEN_ID = "c601ddd0-cb11-46ae-a5ab-b48400d7bc11"
REMOTE = "https://github.com/Vardocloud/vardocloud.github.io.git"

os.chdir(str(HERMES))

# Get token from BWS
result = subprocess.run([str(BWS), "secret", "get", TOKEN_ID],
                        capture_output=True, text=True, timeout=15)
token = json.loads(result.stdout)["value"]

# Write credential file
cred_path = Path.home() / ".git-credentials"
cred_path.write_text(
    f"https://isimgorulsunn%40gmail.com:{token}@github.com\n"
)
cred_path.chmod(0o600)

# Git config
subprocess.run(["git", "config", "user.name", "Vanitas Backup"], capture_output=True)
subprocess.run(["git", "config", "user.email", "isimgorulsunn@gmail.com"], capture_output=True)
subprocess.run(["git", "config", "credential.helper", "store"], capture_output=True)

# Add changes (specific dirs only — avoid large .config/)
dirs = ["skills/", "scripts/", "wiki/", "config.yaml", ".gitignore",
        "AGENTS.md", "MEMORY.md", "SOUL.md", "CONTEXT.md"]
for d in dirs:
    if (HERMES / d).exists():
        subprocess.run(["git", "add", d], capture_output=True, timeout=180)

# Check if anything changed
diff = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
if diff.returncode == 0:
    print("[SILENT]")
    sys.exit(0)

# Commit and push
today = date.today().isoformat()
subprocess.run(["git", "commit", "-m", f"Daily backup - {today}"], capture_output=True, timeout=120)
push = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, timeout=60)
print(push.stdout.strip()[-200:] if push.stdout else "Push OK")
