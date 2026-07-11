#!/bin/bash
# Voice Watchdog v2 — Vanitas Voice Agent + Voiceprint (Tailscale)
# no-agent cron script — her 2 dk'da bir çalışır, servisleri kontrol eder
# Output: non-empty = sorun var (Telegram'a düşer), empty = her şey iyi (sessiz)

VOICE_AGENT_DIR="/home/ubuntu/vanitas-web"
VIPRINT_SCRIPT="$VOICE_AGENT_DIR/voiceprint_service.py"
LOG_FILE="/home/ubuntu/.hermes/logs/voice_watchdog.log"

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

changes=""

# ── Node_modules kontrolü ──
if [ ! -d "$VOICE_AGENT_DIR/node_modules" ]; then
    log "⚠️ node_modules bulunamadı, npm install çalıştırılıyor..."
    cd "$VOICE_AGENT_DIR" && npm install 2>&1 | tail -3 >> "$LOG_FILE"
fi

# ── 1. Voice Agent (port 3005) ──
if ! curl -sf --max-time 5 http://127.0.0.1:3005/ > /dev/null 2>&1; then
    log "⚠️ Voice Agent kapalı, başlatılıyor..."
    cd "$VOICE_AGENT_DIR" && nohup node server.mjs > /tmp/voice_agent.log 2>&1 &
    sleep 3
    if curl -sf http://127.0.0.1:3005/ > /dev/null 2>&1; then
        log "✅ Voice Agent başlatıldı"
        changes+="Voice Agent yeniden başlatıldı. "
    else
        log "❌ Voice Agent başlatılamadı"
        changes+="Voice Agent başlatılamadı! "
    fi
fi

# ── 2. Voiceprint Service (port 5050) ──
if ! curl -sf http://127.0.0.1:5050/health > /dev/null 2>&1; then
    log "⚠️ Voiceprint servisi kapalı, başlatılıyor..."
    cd "$VOICE_AGENT_DIR" && nohup python3 "$VIPRINT_SCRIPT" > /tmp/voiceprint.log 2>&1 &
    sleep 2
    if curl -sf http://127.0.0.1:5050/health > /dev/null 2>&1; then
        log "✅ Voiceprint servisi başlatıldı"
        changes+="Voiceprint servisi yeniden başlatıldı. "
    else
        log "❌ Voiceprint servisi başlatılamadı"
        changes+="Voiceprint servisi başlatılamadı! "
    fi
fi

# ── Çıktı: sadece değişiklik varsa mesaj gönder ──
if [ -n "$changes" ]; then
    echo "🔊 Voice Watchdog: $changes"
fi
