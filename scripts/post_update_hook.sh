#!/bin/bash
# Hermes post-update hook
# Called by Hermes if hooks are enabled.
# If smart_update.sh already ran recently, skip to avoid double-restore.

export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus

FLAG_FILE="/tmp/hermes_smart_update_$(date +%Y%m%d)"

# If smart_update already ran in the last 5 minutes, skip
if [ -f "$FLAG_FILE" ]; then
    FLAG_AGE=$(( $(date +%s) - $(stat -c %Y "$FLAG_FILE" 2>/dev/null || echo 0) ))
    if [ "$FLAG_AGE" -lt 300 ]; then
        echo "Smart update already ran recently, skipping hook."
        exit 0
    fi
fi

# Run the full post-update pipeline
python3 "$HOME/.hermes/scripts/restore_config.py" --post-update