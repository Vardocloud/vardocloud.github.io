#!/bin/bash
# Kampüsten Sahaya 2. Gün — Saatlik Kayıt Değiştirici
# Kullanım: zoom_switch.sh <label> <süre>
# Örnek: zoom_switch.sh seminer2_1800 01:05:00

LABEL="${1:-seminer}"
DURATION="${2:-01:05:00}"

# Eski ffmpeg'i bul ve durdur
FFMPEG_PID=$(pgrep -f "ffmpeg.*zoom_rec" | head -1)
if [ -n "$FFMPEG_PID" ]; then
    kill "$FFMPEG_PID" 2>/dev/null
    sleep 2
fi

# PulseAudio socket
SOCK=$(find /tmp -name "native" -type s 2>/dev/null | head -1)
export PULSE_SERVER="unix:$SOCK"
export LD_LIBRARY_PATH="/tmp/pulseaudio_extract/usr/lib/x86_64-linux-gnu:/tmp/pulseaudio_extract/usr/lib/x86_64-linux-gnu/pulseaudio"

# Yeni kayıt başlat
OUTPUT="/home/ubuntu/recordings/kampus_zirvesi_2/${LABEL}.mp3"
nohup ffmpeg -y -f pulse -i zoom_rec.monitor \
  -c:a libmp3lame -b:a 128k \
  -t "$DURATION" \
  "$OUTPUT" > /tmp/ffmpeg_${LABEL}.log 2>&1 &

echo "✅ ${LABEL} başlatıldı -> $OUTPUT ($DURATION)"
echo "PID: $!"
