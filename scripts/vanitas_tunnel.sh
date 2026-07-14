#!/bin/bash
# Vanitas Cloudflare Tunnel Keeper v2
# Sadece URL değiştiğinde çıktı verir — sessiz bakım

TUNNEL_PID_FILE="/tmp/cloudflared_tunnel.pid"
TUNNEL_URL_FILE="/tmp/cloudflared_tunnel_url.txt"
TUNNEL_PREV_FILE="/tmp/cloudflared_tunnel_prev.txt"
LOGFILE="/tmp/cloudflared_tunnel.log"
BIN="/home/ubuntu/.hermes/bin/cloudflared"

# Check if tunnel is alive
if [ -f "$TUNNEL_PID_FILE" ]; then
    PID=$(cat "$TUNNEL_PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        # Tunnel is running — check URL
        if [ -s "$TUNNEL_URL_FILE" ]; then
            URL=$(cat "$TUNNEL_URL_FILE")
            PREV=""
            [ -f "$TUNNEL_PREV_FILE" ] && PREV=$(cat "$TUNNEL_PREV_FILE")
            if [ "$URL" != "$PREV" ]; then
                echo "$URL" > "$TUNNEL_PREV_FILE"
                echo "🌐 Vanitas Voice hazır: $URL"
            fi
            # else: URL same — silent exit, no delivery
        fi
        exit 0
    fi
    # Stale PID
    rm -f "$TUNNEL_PID_FILE"
fi

# Start fresh tunnel
nohup "$BIN" tunnel --url http://host.docker.internal:3005 \
    --no-autoupdate > "$LOGFILE" 2>&1 &
echo $! > "$TUNNEL_PID_FILE"

# Wait and capture URL
sleep 12
URL=$(grep -oP 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' "$LOGFILE" | head -1)
if [ -n "$URL" ]; then
    echo "$URL" > "$TUNNEL_URL_FILE"
    echo "$URL" > "$TUNNEL_PREV_FILE"
    echo "🌐 Vanitas Voice hazır: $URL"
    echo "Not: Telefon HTTPS üzerinden mikrofon kullanabilir."
else
    echo "⏳ Tünel başlatıldı, 15sn sonra URL hazır olacak..."
fi
