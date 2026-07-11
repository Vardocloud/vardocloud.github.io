#!/bin/bash
# verify_system.sh — Post-update system verification
# Exit 0 = all OK, 1+ = issues found
set -uo pipefail

export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus

FAILED=0

check() {
    local name="$1"
    local cmd="$2"
    local expected="${3:-}"
    
    result=$(eval "$cmd" 2>/dev/null) || true
    if [ -n "$expected" ]; then
        if echo "$result" | grep -q "$expected"; then
            echo "  OK $name: $result"
        else
            echo "  FAIL $name: expected '$expected', got '$result'"
            FAILED=$((FAILED + 1))
        fi
    else
        if [ $? -eq 0 ]; then
            echo "  OK $name"
        else
            echo "  FAIL $name"
            FAILED=$((FAILED + 1))
        fi
    fi
}

echo "=== Hermes System Verification ==="
echo "Time: $(date)"
echo ""

echo "--- Core Services ---"
check "Gateway" "systemctl --user is-active hermes-gateway" "active"
check "Proxy" "systemctl --user is-active hermes-pollinations-proxy" "active"

echo ""
echo "--- Gateway Health ---"
GW_CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 http://127.0.0.1:8642/health 2>/dev/null || echo "000")
if [ "$GW_CODE" = "200" ] || [ "$GW_CODE" = "404" ]; then
    echo "  OK Gateway HTTP: $GW_CODE"
else
    echo "  FAIL Gateway HTTP: $GW_CODE (expected 200/404)"
    FAILED=$((FAILED + 1))
fi

echo ""
echo "--- Pollinations Proxy ---"
PX_CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 --max-time 15 \
    http://127.0.0.1:19999/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model":"openai","messages":[{"role":"user","content":"ping"}],"stream":false}' 2>/dev/null || echo "000")
if [ "$PX_CODE" = "200" ]; then
    echo "  OK Proxy HTTP: $PX_CODE"
else
    echo "  FAIL Proxy HTTP: $PX_CODE (expected 200)"
    FAILED=$((FAILED + 1))
fi

echo ""
echo "--- NLM Auth ---"
if /home/ubuntu/.local/bin/nlm login --check 2>/dev/null | grep -q "valid\|Authenticated"; then
    echo "  OK NLM auth: valid"
else
    echo "  WARN NLM auth: needs refresh (non-critical)"
fi

echo ""
echo "--- Crontab ---"
CRON_COUNT=$(crontab -l 2>/dev/null | grep -v '^#' | grep -v '^$' | wc -l)
if [ "$CRON_COUNT" -ge 8 ]; then
    echo "  OK Crontab: $CRON_COUNT entries"
else
    echo "  FAIL Crontab: only $CRON_COUNT entries (expected >=8)"
    FAILED=$((FAILED + 1))
fi

echo ""
echo "--- Symlinks ---"
for bin in nlm notebooklm-mcp; do
    if [ -L "$HOME/.local/bin/$bin" ]; then
        target=$(readlink -f "$HOME/.local/bin/$bin")
        if [ -x "$target" ]; then
            echo "  OK $bin -> $target"
        else
            echo "  FAIL $bin -> $target (not executable)"
            FAILED=$((FAILED + 1))
        fi
    else
        echo "  FAIL $bin: symlink missing"
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo "--- Disk Space ---"
DISK_AVAIL=$(df -h / | tail -1 | awk '{print $4}')
DISK_PCT=$(df -h / | tail -1 | awk '{print $5}' | tr -d '%')
echo "  Available: $DISK_AVAIL ($DISK_PCT% used)"
if [ "$DISK_PCT" -gt 95 ] 2>/dev/null; then
    echo "  FAIL Disk usage critical: $DISK_PCT%"
    FAILED=$((FAILED + 1))
elif [ "$DISK_PCT" -gt 90 ] 2>/dev/null; then
    echo "  WARN Disk usage high: $DISK_PCT%"
else
    echo "  OK Disk usage"
fi

echo ""
echo "--- MCP Servers ---"
for mcp in context-mode pollinations-mcp; do
    if pgrep -f "$mcp" >/dev/null 2>&1; then
        echo "  OK $mcp: running"
    else
        echo "  WARN $mcp: not running (may start on demand)"
    fi
done

echo ""
echo "=== Result: $FAILED issue(s) found ==="
exit $FAILED