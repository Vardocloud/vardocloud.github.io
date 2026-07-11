#!/bin/bash
# zoom_s2.sh — Seminer 2 (18:00) wrapper
SOCK=$(find /tmp -name "native" -type s 2>/dev/null | head -1)
export PULSE_SERVER="unix:$SOCK"
export LD_LIBRARY_PATH="/tmp/pulseaudio_extract/usr/lib/x86_64-linux-gnu:/tmp/pulseaudio_extract/usr/lib/x86_64-linux-gnu/pulseaudio"
FFMPEG_PID=$(pgrep -f "ffmpeg.*zoom_rec" | head -1)
[ -n "$FFMPEG_PID" ] && kill "$FFMPEG_PID" 2>/dev/null && sleep 2
OUTPUT="/home/ubuntu/recordings/kampus_zirvesi_2/seminer2_1800.mp3"
nohup ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k -t 01:05:00 "$OUTPUT" > /tmp/ffmpeg_s2.log 2>&1 &
echo "✅ seminer2_1800 başlatıldı ($!)"
