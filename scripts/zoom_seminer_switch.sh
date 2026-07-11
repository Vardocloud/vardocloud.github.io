#!/bin/bash
# zoom_seminer_switch.sh — No-agent Zoom seminer kayıt değiştirme
# 2 Tem 2026 Kampüsten Sahaya Zirvesi
# Kullanım: zoom_seminer_switch.sh <seminer_adi>
# Örnek: zoom_seminer_switch.sh seminer2_1800

SEMINER=$1
REC_DIR=/home/ubuntu/recordings/kampus_zirvesi
SOCKET=/tmp/pulse-zKO69W804zvm/native

export PULSE_SERVER="unix:${SOCKET}"
export LD_LIBRARY_PATH="/tmp/pulseaudio_extract/usr/lib/x86_64-linux-gnu:/tmp/pulseaudio_extract/usr/lib/pulse-17.0+dfsg1/modules"

mkdir -p "$REC_DIR"

echo "[$(date '+%H:%M:%S')] === $SEMINER başlıyor ==="

# 1. Mevcut ffmpeg'i durdur
FFPID=$(pgrep -f "ffmpeg.*zoom_rec" 2>/dev/null)
if [ -n "$FFPID" ]; then
    echo "[$(date '+%H:%M:%S')] Eski ffmpeg durduruluyor (PID: $FFPID)..."
    # Önce bitmesini beklemeden kill et (1s05dk sürecek şekilde ayarlı, ama yeni seminer için kes)
    kill "$FFPID" 2>/dev/null
    sleep 2
    # Hâlâ çalışıyorsa force
    kill -9 "$FFPID" 2>/dev/null || true
    echo "[$(date '+%H:%M:%S')] Eski ffmpeg durduruldu"
fi

# 2. PulseAudio socket doğrula
if [ ! -S "$SOCKET" ]; then
    echo "[$(date '+%H:%M:%S')] HATA: PulseAudio socket bulunamadı!"
    # PulseAudio hala çalışıyor mu kontrol et
    if pgrep -f "pulseaudio" > /dev/null; then
        # Socket'i tekrar bul
        NS=$(find /tmp -name "native" -type s 2>/dev/null | head -1)
        if [ -n "$NS" ]; then
            export PULSE_SERVER="unix:${NS}"
            echo "[$(date '+%H:%M:%S')] Socket bulundu: $NS"
        else
            echo "[$(date '+%H:%M:%S')] KRİTİK: PulseAudio çalışmıyor"
            exit 2
        fi
    else
        echo "[$(date '+%H:%M:%S')] KRİTİK: PulseAudio çalışmıyor"
        exit 2
    fi
fi

# 3. Chrome canlı mı?
CHROME_OK=$(curl -sf http://localhost:9333/json/version 2>/dev/null | python3 -c "import sys,json; print('OK')" 2>/dev/null)
if [ "$CHROME_OK" != "OK" ]; then
    echo "[$(date '+%H:%M:%S')] Chrome 9333 yanıt vermiyor, yeniden başlatılıyor..."
    # Xvfb kontrol
    pgrep -f "Xvfb.*:99" > /dev/null || Xvfb :99 -screen 0 1280x720x24 -ac &
    sleep 1
    # Chrome başlat
    nohup bash /home/ubuntu/.hermes/scripts/zoom-chrome-9333.sh \
        --remote-debugging-port=9333 --remote-allow-origins=* \
        > /tmp/chrome_9333.log 2>&1 &
    CHROME_PID=$!
    sleep 10
    # Doğrula
    if curl -sf http://localhost:9333/json/version > /dev/null 2>&1; then
        echo "[$(date '+%H:%M:%S')] Chrome yeniden başladı"
        # Rejoin — Zoom sayfasına git
        curl -sf -X PUT "localhost:9333/json/new?https://app.zoom.us/wc/join/87515805783" > /dev/null 2>&1
        sleep 8
        # Form doldur + join (CDP ile)
        python3 /tmp/custom_join2.py 2>/dev/null
        echo "[$(date '+%H:%M:%S')] Rejoin yapıldı"
    else
        echo "[$(date '+%H:%M:%S')] Chrome başlatılamadı!"
        exit 3
    fi
fi

# 4. Toplantı hâlâ aktif mi kontrol et (tab title)
TITLE=$(curl -sf http://localhost:9333/json 2>/dev/null | python3 -c "
import sys,json
tabs=json.load(sys.stdin)
for t in tabs:
    u=t.get('url','')
    if 'wc/' in u and 'zoom' in u:
        print(t.get('title',''))
        break
" 2>/dev/null)

if [ -n "$TITLE" ]; then
    echo "[$(date '+%H:%M:%S')] Zoom toplantı durumu: $TITLE"
else
    echo "[$(date '+%H:%M:%S')] UYARI: Zoom tab bulunamadı, yeniden join deneniyor..."
    curl -sf -X PUT "localhost:9333/json/new?https://app.zoom.us/wc/join/87515805783" > /dev/null 2>&1
    sleep 8
    python3 /tmp/custom_join2.py 2>/dev/null
fi

# 5. Yeni ffmpeg başlat
OUTPUT="${REC_DIR}/${SEMINER}.mp3"
echo "[$(date '+%H:%M:%S')] Yeni kayıt başlatılıyor: $OUTPUT"
ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k -t 01:05:00 "$OUTPUT" &
FFPID=$!
echo "[$(date '+%H:%M:%S')] ffmpeg PID: $FFPID"

# 6. Doğrula
sleep 3
if kill -0 "$FFPID" 2>/dev/null; then
    FSIZE=$(ls -lh "$OUTPUT" 2>/dev/null | awk '{print $5}')
    echo "[$(date '+%H:%M:%S')] ✅ Kayıt başladı: $OUTPUT ($FSIZE)"
else
    echo "[$(date '+%H:%M:%S')] ❌ Kayıt başlatılamadı!"
    exit 4
fi

echo "[$(date '+%H:%M:%S')] === $SEMINER hazır ==="
