#!/bin/bash
# Zoom recording setup — PulseAudio + Chrome + ffmpeg
# 17 Haz 2026 — Edel'in çift toplantısı için
set -e

LOG="/home/ubuntu/.hermes/logs/zoom_setup.log"
exec > >(tee -a "$LOG") 2>&1
echo "=== Zoom Setup $(date) ==="

# 1. PulseAudio null-sink (zaten varsa hata vermeden devam et)
echo "[1/4] PulseAudio null-sink..."
pactl load-module module-null-sink sink_name=zoom_rec 2>/dev/null || echo "  (zaten yüklü)"
sleep 1

# 2. Chrome profilini kopyala (NotebookLM profili join formunu render eder)
echo "[2/4] Chrome profil kopyası..."
rm -rf /tmp/zoom_profile 2>/dev/null
cp -r /tmp/nlm_chrome_profile /tmp/zoom_profile 2>/dev/null || {
    echo "  NotebookLM profili yok, boş profil oluşturuluyor..."
    mkdir -p /tmp/zoom_profile
}
# Pre-grant media permissions
mkdir -p /tmp/zoom_profile/Default
cat > /tmp/zoom_profile/Default/Preferences << 'PREFS'
{"profile":{"content_settings":{"exceptions":{"media_stream_camera":{"https://app.zoom.us:443":{"last_modified":"13300000000000000","setting":1},"https://*.zoom.us:443":{"last_modified":"13300000000000000","setting":1}},"media_stream_mic":{"https://app.zoom.us:443":{"last_modified":"13300000000000000","setting":1},"https://*.zoom.us:443":{"last_modified":"13300000000000000","setting":1}}}}}
PREFS

# 3. Chrome başlat (DISABLE-GPU KULLANMA!)
echo "[3/4] Chrome başlatılıyor (port 9333)..."
# Önce varsa kill et
pkill -f "chrome.*remote-debugging-port=9333" 2>/dev/null || true
sleep 2

PULSE_SINK=zoom_rec DISPLAY=:99 \
  /data/ubuntu/cache/ms-playwright/chromium-1223/chrome-linux/chrome \
  --no-sandbox --remote-debugging-port=9333 --remote-allow-origins=* \
  --user-data-dir=/tmp/zoom_profile --no-first-run \
  --no-default-browser-check --disable-features=TranslateUI \
  --ozone-platform=x11 --window-size=1280,720 \
  --use-fake-device-for-media-stream --use-fake-ui-for-media-stream &

CHROME_PID=$!
echo "  Chrome PID: $CHROME_PID"

# Chrome'un hazır olmasını bekle
for i in $(seq 1 15); do
    if curl -s http://localhost:9333/json/version > /dev/null 2>&1; then
        echo "  Chrome ready (${i}s)"
        break
    fi
    sleep 1
done

# 4. ffmpeg kaydı başlat
echo "[4/4] ffmpeg kaydı başlatılıyor..."
mkdir -p /home/ubuntu/recordings
REC_FILE="/home/ubuntu/recordings/zoom_meeting1_$(date +%Y%m%d_%H%M).mp3"

# Varsa eski ffmpeg'i kill et
pkill -f "ffmpeg.*zoom_rec.monitor" 2>/dev/null || true
sleep 1

ffmpeg -y -f pulse -i zoom_rec.monitor \
  -c:a libmp3lame -b:a 128k "$REC_FILE" &
FFMPEG_PID=$!

sleep 2
# Ses var mı kontrol
SIZE=$(stat -c%s "$REC_FILE" 2>/dev/null || echo 0)
echo "  ffmpeg PID: $FFMPEG_PID, kayıt: $REC_FILE (${SIZE} bytes)"

# PID'leri kaydet
echo "$CHROME_PID" > /tmp/zoom_chrome.pid
echo "$FFMPEG_PID" > /tmp/zoom_ffmpeg.pid
echo "$REC_FILE" > /tmp/zoom_rec_file.txt

echo "=== Setup tamam ==="
echo "REC_FILE=$REC_FILE"
