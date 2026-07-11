#!/bin/bash
# Google token canlı tutma — her gün 03:00
# SADECE Gmail API token'ını kontrol eder
# NotebookLM auth'u nb_keepalive.py tarafından yönetilir (her 20dk)

set -e

TOKEN_FILE="$HOME/.hermes/google_token.json"
GAPI="python3 $HOME/.hermes/skills/productivity/google-workspace/scripts/google_api.py"

# Token dosyası var mı?
if [ ! -f "$TOKEN_FILE" ]; then
    echo "❌ Google token dosyası yok — OAuth setup gerekli"
    exit 1
fi

# Gmail API'yi dene (token canlı mı?)
RESULT=$(ALL_PROXY="" $GAPI gmail search "is:unread" --max 1 2>&1)

if echo "$RESULT" | grep -q "REFRESH_FAILED\|invalid_grant\|Token has been expired"; then
    echo "⚠️ Google token expired — yeni OAuth yetkilendirmesi gerek"
    exit 2
elif echo "$RESULT" | grep -q "error\|Error\|Traceback"; then
    echo "⚠️ Gmail API hatası (token dışı): $RESULT"
    exit 3
else
    # Token canlı — sessiz çık (bildirim gerekmez)
    exit 0
fi
