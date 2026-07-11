#!/bin/bash
# NotebookLM Auth Monitor + Telegram Alert
# Cron: Her 4 saatte
# nlm'nin 3-katmanli auto-recovery'si fail oldugunda bildirim gonderir

set -a
source "$HOME/.hermes/.env" 2>/dev/null
set +a

NLM_BIN=~/.local/bin/nlm
LOG_FILE=~/.nlm/auth_check.log
DATE="$(date '+%Y-%m-%d %H:%M')"

RESULT=$("$NLM_BIN" login --check 2>&1)
echo "[$DATE] $RESULT" >> "$LOG_FILE"

if echo "$RESULT" | grep -q "valid\|Authentication valid"; then
    exit 0
fi

echo "[$DATE] AUTH FAILED - Telegram alert" >> "$LOG_FILE"

if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_HOME_CHANNEL" ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_HOME_CHANNEL}" \
        --data-urlencode "text=notebooklm auth FAILED - tum recovery katmanlari basarisiz. VNC ile nlm login gerekebilir." \
        --connect-timeout 10 --max-time 30 > /dev/null 2>&1
fi

exit 1
