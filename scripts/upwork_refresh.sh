#!/bin/bash
# Upwork Session+Cookie Refresh — no_agent script
# Scheduled: every 4 hours, handles both session and cookie refresh
set -e

cd /home/ubuntu/.hermes
output=$(/home/ubuntu/.local/bin/proxychains4 -q -f /home/ubuntu/.local/etc/proxychains.conf node upw_session_refresh.cjs 2>&1)
exit_code=$?

if echo "$output" | grep -qi "error\|fail\|invalid\|blocked\|unauthorized"; then
    echo "⚠️ Upwork refresh failed (exit=$exit_code):"
    echo "$output"
elif [ $exit_code -ne 0 ]; then
    echo "⚠️ Upwork refresh crashed (exit=$exit_code)"
    echo "$output"
else
    echo "[SILENT]"
fi
