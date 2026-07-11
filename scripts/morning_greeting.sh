#!/bin/bash
# morning_greeting.sh — Günaydın mesajı + takvim özeti
# no_agent script, output directly delivered to Telegram

export HERMES_GOOGLE_TOKEN_PATH="$HOME/.hermes/google_token.json"

GAPI="${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/google_api.py"

# Bugünün tarihi
TODAY=$(date +%Y-%m-%d)
DAYNAME=$(date +%A)

# Takvimden bugünün etkinlikleri
EVENTS=$(python3 "$GAPI" calendar list --date "$TODAY" 2>&1)
EVENT_COUNT=$(echo "$EVENTS" | grep -c "^Summary:" || true)

# Güne göre selamlama
case $DAYNAME in
  Monday|Pazartesi) GREETING="Haftaya güzel başla" ;;
  Tuesday|Salı)     GREETING="Günaydın, üretken bir gün" ;;
  Wednesday|Çarşamba) GREETING="Haftanın ortası, enerjini koru" ;;
  Thursday|Perşembe) GREETING="Günaydın, hafta sonu yaklaşıyor" ;;
  Friday|Cuma)      GREETING="Son gün, harika bir bitiş" ;;
  Saturday|Cumartesi) GREETING="Hafta sonu, keyfini çıkar" ;;
  Sunday|Pazar)     GREETING="Pazar, dinlenme günü" ;;
esac

echo "☀️ Günaydın Edel! $GREETING."
echo ""

if [ "$EVENT_COUNT" -gt 0 ]; then
    echo "📅 Bugün $EVENT_COUNT etkinliğin var:"
    echo "$EVENTS" | while IFS= read -r line; do echo "   $line"; done
else
    echo "📅 Bugün takviminde etkinlik yok — rahat bir gün."
fi

echo ""
echo "Haydi başlayalım! 🚀"
