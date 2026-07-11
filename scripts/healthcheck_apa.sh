#!/bin/bash
# healthcheck_apa.sh — APA kaydı sağlık kontrolü (no-agent)
# Her 5 dk'da bir çalışır: ffmpeg ölüyse yeniden başlat
PA_BASE=/tmp/pulseaudio_extract
export LD_LIBRARY_PATH=$PA_BASE/usr/lib/x86_64-linux-gnu:$PA_BASE/usr/lib/x86_64-linux-gnu/pulseaudio:$PA_BASE/usr/lib/pulse-17.0+dfsg1/modules
export PULSE_SERVER="unix:/tmp/pulse-YiS0IhPtYxro/native"

FFMPEG_PID=$(pgrep -f "ffmpeg.*zoom_rec" | head -1)
if [ -n "$FFMPEG_PID" ]; then
    # ffmpeg çalışıyor — dosya kontrolü
    FILE_SIZE=$(stat -c%s /home/ubuntu/recordings/10temmuz/apa_ebsa_part4.mp3 2>/dev/null || echo "0")
    echo "✅ ffmpeg PID=$FFMPEG_PID | Dosya: ${FILE_SIZE}B"
else
    # ffmpeg ölü — Chrome hala canlı mı?
    CHROME_OK=$(curl -sf http://localhost:9333/json/version >/dev/null 2>&1 && echo "1" || echo "0")
    if [ "$CHROME_OK" = "1" ]; then
        echo "❌ ffmpeg ölü! Chrome canlı. Yeniden başlatılıyor..."
        # Part numarasını bul
        PART=4
        while [ -f "/home/ubuntu/recordings/10temmuz/apa_ebsa_part${PART}.mp3" ]; do
            PART=$((PART + 1))
        done
        nohup ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k \
            -t 00:30:00 "/home/ubuntu/recordings/10temmuz/apa_ebsa_part${PART}.mp3" \
            > /tmp/ffmpeg_part${PART}.log 2>&1 &
        echo "✅ ffmpeg part${PART} başlatıldı (PID $!)"
    else
        echo "⏹️  Chrome da ölü — seminer bitmiş"
    fi
fi
