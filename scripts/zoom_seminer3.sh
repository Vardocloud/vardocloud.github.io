#!/bin/bash
# zoom_seminer3.sh — 19:00 için sade ffmpeg switch (CDP yok, hızlı)
REC_DIR=/home/ubuntu/recordings/kampus_zirvesi
SOCKET=/tmp/pulse-zKO69W804zvm/native
export PULSE_SERVER="unix:${SOCKET}"
export LD_LIBRARY_PATH="/tmp/pulseaudio_extract/usr/lib/x86_64-linux-gnu:/tmp/pulseaudio_extract/usr/lib/pulse-17.0+dfsg1/modules"

echo "[$(date '+%H:%M:%S')] === Seminer 3 (19:00) başlıyor ==="

# 1. Chrome canlı mı?
CHROME_OK=$(curl -sf http://localhost:9333/json/version > /dev/null 2>&1 && echo "OK" || echo "NO")
if [ "$CHROME_OK" = "NO" ]; then
    echo "Chrome ölü, restart deneniyor..."
    Xvfb :99 -screen 0 1280x720x24 -ac &>/dev/null &
    sleep 1
    bash /home/ubuntu/.hermes/scripts/zoom-chrome-9333.sh --remote-debugging-port=9333 --remote-allow-origins=* &
    sleep 10
fi

# 2. Socket doğrula (5sn timebox)
for i in 1 2 3 4 5; do
    if [ -S "$SOCKET" ]; then break; fi
    NS=$(find /tmp -name "native" -type s 2>/dev/null | head -1)
    if [ -n "$NS" ]; then SOCKET="$NS"; export PULSE_SERVER="unix:${NS}"; break; fi
    sleep 1
done

# 3. Eski ffmpeg'i öldür (hızlı)
for pid in $(pgrep -f "ffmpeg.*zoom_rec" 2>/dev/null); do
    kill "$pid" 2>/dev/null
done
sleep 2

# 4. Yeni ffmpeg'i başlat
OUTPUT="${REC_DIR}/seminer3_1900.mp3"
echo "Yeni kayıt: $OUTPUT"
ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k -t 01:05:00 "$OUTPUT" &
FPID=$!

# 5. 3sn bekle doğrula
sleep 3
if kill -0 "$FPID" 2>/dev/null; then
    echo "✅ Kayıt başladı (PID: $FPID)"
else
    echo "❌ Kayıt başarısız!"
fi
