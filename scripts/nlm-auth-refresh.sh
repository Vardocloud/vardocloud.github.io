#!/bin/bash
# NotebookLM Auth Check + Auto-Refresh + Telegram Alert
# Cron: Every 12 hours (0 */12 * * *)
# If auth expired: try headless refresh, if failed: Telegram alert

# Load secrets from .env
set -a
source "$HOME/.hermes/.env"
set +a

NLM_BIN=/home/ubuntu/node_modules/.bin/nlm
LOG_FILE="$HOME/.nlm/auth_check.log"
DATE=$(date '+%Y-%m-%d %H:%M')

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Check auth
AUTH_OUTPUT=$($NLM_BIN login --check 2>&1)

if echo "$AUTH_OUTPUT" | grep -qi "valid"; then
    echo "[$DATE] Auth valid" >> "$LOG_FILE"
    exit 0
fi

echo "[$DATE] Auth expired, attempting refresh..." >> "$LOG_FILE"

# Attempt headless refresh
REFRESH_OUTPUT=$(python3 ~/.nlm/refresh_cookies.py 2>&1)

if echo "$REFRESH_OUTPUT" | grep -qi "successfully\|valid\|refreshed"; then
    echo "[$DATE] Refresh successful" >> "$LOG_FILE"
    exit 0
fi

echo "[$DATE] Refresh FAILED: $REFRESH_OUTPUT" >> "$LOG_FILE"

# Telegram alert
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d chat_id="${TELEGRAM_HOME_CHANNEL}" \
    --data-urlencode "text=NotebookLM auth yenileme basarisiz! Telefonundan Chrome'a girip cookies.json export edip atar misin?" \
    --connect-timeout 10 \
    --max-time 30 > /dev/null 2>&1

exit 1
