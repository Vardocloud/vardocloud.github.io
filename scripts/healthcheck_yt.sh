#!/bin/bash
# healthcheck_yt.sh — YouTube kaydı sağlık kontrolü
FFPID=$(pgrep -f "ffmpeg.*yt_seminer" | head -1)
if [ -n "$FFPID" ]; then
    FILE_SIZE=$(stat -c%s /home/ubuntu/recordings/10temmuz/yt_seminer.mp3 2>/dev/null || echo "0")
    echo "✅ YouTube ffmpeg PID=$FFPID | Dosya: ${FILE_SIZE}B"
else
    echo "❌ YouTube ffmpeg ölü! Canlı yayın bitmiş olabilir."
    # yt-dlp ile tekrar dene
    export PATH=$PATH:/home/ubuntu/.local/bin
    M3U8=$(python3 -m yt_dlp -f 91 --get-url --extractor-args "youtube:player_client=android" "https://www.youtube.com/live/IQrboLJvDFg" 2>/dev/null | tail -1)
    if [ -n "$M3U8" ]; then
        nohup ffmpeg -y -i "$M3U8" -vn -c:a libmp3lame -b:a 128k -t 02:00:00 "/home/ubuntu/recordings/10temmuz/yt_seminer.mp3" > /tmp/yt_ffmpeg.log 2>&1 &
        echo "✅ YouTube ffmpeg yeniden başlatıldı (PID $!)"
    fi
fi
