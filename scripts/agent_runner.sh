#!/bin/bash
# Ekip — Multi-Agent Runner (v2 — light_agent.py tabanlı)
# Kullanım: ./agent_runner.sh <agent> "<görev>" [--background]
# Örnek:    ./agent_runner.sh kodcu "Python palindrome fonksiyonu yaz"

AGENT="$1"
TASK="$2"
MODE="${3:-foreground}"
RUNNER="$HOME/.hermes/scripts/light_agent.py"

# Geçerli agent kontrolü
case "$AGENT" in
  kodcu|analist|yazar|yardimci) ;;
  *)
    echo "❌ Bilinmeyen agent: $AGENT"
    echo "   Kullanılabilir: kodcu | analist | yazar | yardimci"
    exit 1
    ;;
esac

if [ "$MODE" = "--background" ]; then
  LOG="/tmp/agent_${AGENT}_$(date +%H%M%S).log"
  python3 "$RUNNER" "$AGENT" "$TASK" > "$LOG" 2>&1 &
  echo "🚀 $AGENT başlatıldı | PID: $! | Log: $LOG"
else
  python3 "$RUNNER" "$AGENT" "$TASK"
fi
