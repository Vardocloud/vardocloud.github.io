#!/bin/bash
# Hermes Post-Update Fix Script
# Validates Pollinations proxy health after updates.
# Proxy runs as systemd user service (Restart=always).

echo "[post-update] Running health check..."

export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus

# 1. Check .env has POLLINATIONS_API_KEY
ENV_FILE="$HOME/.hermes/.env"
if [ -f "$ENV_FILE" ]; then
    if grep -q '^POLLINATIONS_API_KEY=' "$ENV_FILE" 2>/dev/null; then
        echo "[post-update] OK POLLINATIONS_API_KEY found in .env"
    else
        echo "[post-update] WARN POLLINATIONS_API_KEY missing in .env!"
    fi
else
    echo "[post-update] WARN .env file not found!"
fi

# 2. Check proxy service
if systemctl --user is-active hermes-pollinations-proxy &>/dev/null; then
    echo "[post-update] OK proxy service active"
else
    echo "[post-update] WARN proxy not active — starting..."
    systemctl --user start hermes-pollinations-proxy
    sleep 2
fi

# 3. Verify proxy responds
PRX_CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10 --max-time 25 \
    http://127.0.0.1:19999/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model":"openai","messages":[{"role":"user","content":"ping"}],"stream":false}' 2>/dev/null)

if [ "$PRX_CODE" = "200" ]; then
    echo "[post-update] OK proxy HTTP $PRX_CODE"
else
    echo "[post-update] WARN proxy HTTP $PRX_CODE — restarting..."
    systemctl --user restart hermes-pollinations-proxy
    sleep 3
    PRX_CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10 --max-time 25 \
        http://127.0.0.1:19999/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d '{"model":"openai","messages":[{"role":"user","content":"ping"}],"stream":false}' 2>/dev/null)
    echo "[post-update] After restart: HTTP $PRX_CODE"
fi

echo "[post-update] Done."
