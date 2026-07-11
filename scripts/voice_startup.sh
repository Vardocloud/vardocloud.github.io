#!/bin/bash
# Voice Services Startup v2 — Vanitas Voice Agent + Voiceprint (Tailscale)
# container başlangıcında entrypoint tarafından çalıştırılır

LOCKFILE="/tmp/voice_startup.lock"
if [ -f "$LOCKFILE" ]; then
    exit 0
fi
touch "$LOCKFILE"

cleanup() { rm -f "$LOCKFILE"; }
trap cleanup EXIT

VOICE_AGENT_DIR="/home/ubuntu/vanitas-web"
VIPRINT_SCRIPT="$VOICE_AGENT_DIR/voiceprint_service.py"
LOG_FILE="/home/ubuntu/.hermes/logs/voice_startup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Voice servisler başlatılıyor..."

# node_modules kontrolü
if [ ! -d "$VOICE_AGENT_DIR/node_modules" ]; then
    log "node_modules bulunamadı, npm install çalıştırılıyor..."
    cd "$VOICE_AGENT_DIR" && npm install 2>&1 | tail -3 >> "$LOG_FILE"
fi

# 1. Voice Agent (port 3005)
cd "$VOICE_AGENT_DIR" && nohup node server.mjs > /tmp/voice_agent.log 2>&1 &
sleep 4
if curl -sf http://127.0.0.1:3005/ > /dev/null 2>&1; then
    log "Voice Agent başlatıldı (port 3005)"
else
    log "Voice Agent başlatılamadı — watchdog 2dk içinde tekrar dener"
fi

# 2. Voiceprint Service (port 5050)
log "Voiceprint servisi başlatılıyor..."
nohup python3 "$VIPRINT_SCRIPT" > /tmp/voiceprint.log 2>&1 &
sleep 3
if curl -sf http://127.0.0.1:5050/health > /dev/null 2>&1; then
    log "Voiceprint servisi başlatıldı (port 5050)"
else
    log "Voiceprint servisi başlatılamadı"
fi

log "Voice servis başlatma tamamlandı"
