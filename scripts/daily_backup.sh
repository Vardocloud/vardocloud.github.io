#!/bin/bash
# Daily GitHub backup — ~/.hermes
# Runs: every day at 02:00

set -e
cd /home/ubuntu/.hermes

# Git config
git config user.name "Vanitas Backup"
git config user.email "isimgorulsunn@gmail.com"

# Get token from BWS, write to credential file
export PATH="/home/ubuntu/.hermes/bin:$PATH"
GIT_TOKEN=*** -c "import json,sys; print(json.load(sys.stdin)['value'])" <<< "$(bws secret get c601ddd0-cb11-46ae-a5ab-b48400d7bc11 2>/dev/null)"
echo "https://isimgorulsunn%40gmail.com:${GIT_TOKEN}@github.com" > /home/ubuntu/.git-credentials
chmod 600 /home/ubuntu/.git-credentials

# Add all changes (except ignored)
git add -A 2>/dev/null || true

# Check if anything changed
if git diff --cached --quiet; then
    echo "[SILENT]"
    exit 0
fi

# Commit and push
git commit -m "Daily backup - $(date +%Y-%m-%d)"
git push origin main 2>&1

echo "[SILENT]"
