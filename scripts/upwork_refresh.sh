#!/bin/bash
# Upwork Session+Cookie Refresh — no_agent script
# Scheduled: every 4 hours, handles both session and cookie refresh
# Strategy: direct (no proxy) → proxychains4/WARP fallback → report
set -e

cd /home/ubuntu/.hermes

# Try direct first (WSL has residential IP — no WARP needed)
output=$(timeout 90 node upw_session_refresh.cjs 2>&1)
exit_code=$?

# If direct fails, try via proxychains/WARP as fallback
if [ $exit_code -ne 0 ]; then
    echo "⚠️ Direct failed (exit=$exit_code), trying proxychains/WARP..."
    output=$(/home/ubuntu/.local/bin/proxychains4 -q -f /home/ubuntu/.local/etc/proxychains.conf timeout 120 node upw_session_refresh.cjs 2>&1)
    exit_code=$?
fi

if echo "$output" | grep -qi "error\|fail\|invalid\|blocked\|unauthorized"; then
    echo "⚠️ Upwork refresh failed (exit=$exit_code):"
    echo "$output"
    exit 1
elif [ $exit_code -ne 0 ]; then
    echo "⚠️ Upwork refresh crashed (exit=$exit_code)"
    echo "$output"
    exit 1
else
    echo "[SILENT]"
fi
