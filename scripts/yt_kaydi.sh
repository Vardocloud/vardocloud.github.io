#!/bin/bash
# yt_kaydi.sh – YouTube canlı yayın (ffmpeg ile m3u8 stream)
export PATH=$PATH:/home/ubuntu/.local/bin
mkdir -p /home/ubuntu/recordings/10temmuz

# Önce m3u8 URL'ini al
M3U8_URL=$(python3 -m yt_dlp -f 91 --get-url --extractor-args "youtube:player_client=android" "https://www.youtube.com/live/IQrboLJvDFg" 2>/dev/null | tail -1)

if [ -z "$M3U8_URL" ]; then
    echo "❌ m3u8 URL alınamadı"
    exit 1
fi
echo "📥 m3u8: ${M3U8_URL:0:80}..."

# ffmpeg ile stream'i indir (sadece ses)
nohup ffmpeg -y -i "$M3U8_URL" -vn -c:a libmp3lame -b:a 128k \
    -t 02:00:00 \
    "/home/ubuntu/recordings/10temmuz/yt_seminer.mp3" \
    > /tmp/yt_ffmpeg.log 2>&1 &
echo "✅ ffmpeg ile YouTube kaydı başlatıldı (PID $!)"
