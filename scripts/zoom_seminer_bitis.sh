#!/bin/bash
# 20:00 - 2 PARALEL KAYIT: Zoom (seminer4) + Vimeo (projeler)
REC_DIR=/home/ubuntu/recordings/kampus_zirvesi
SOCKET=/tmp/pulse-zKO69W804zvm/native
EXTRACT=/tmp/pulseaudio_extract
export LD_LIBRARY_PATH="$EXTRACT/usr/lib/x86_64-linux-gnu:$EXTRACT/usr/lib/pulse-17.0+dfsg1/modules"

echo "[$(date '+%H:%M:%S')] === 20:00 - 2 PARALEL KAYIT BAŞLIYOR ==="

# ═══════════════ KANAL 1 — ZOOM (seminer4) ═══════════════
echo ""
echo "📹 KANAL 1: Zoom 4. Seminer"
export PULSE_SERVER="unix:${SOCKET}"

# Eski Zoom ffmpeg'ini durdur
FPID=$(pgrep -f "ffmpeg.*zoom_rec[^_]")
echo "Eski Zoom ffmpeg PID: $FPID"
[ -n "$FPID" ] && { kill "$FPID" 2>/dev/null; sleep 2; kill -9 "$FPID" 2>/dev/null || true; }

# Yeni Zoom ffmpeg
ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k -t 01:05:00 "${REC_DIR}/seminer4_2000.mp3" &
ZPID=$!
echo "Zoom kaydı başladı (PID: $ZPID)"

# ═══════════════ KANAL 2 — VIMEO (projeler) ═══════════════
echo ""
echo "🎥 KANAL 2: Vimeo Proje Sunumları"
export PULSE_SERVER="unix:${SOCKET}"

# Chrome 9334'tü Vimeo sayfasını aç
echo "Vimeo sayfası açılıyor (Chrome 9334)..."
curl -sf -X PUT "localhost:9334/json/new?https://vimeo.com/event/6030572/d96adf2156?fl=so&fe=fs" > /dev/null 2>&1
sleep 8

# Vimeo ffmpeg (zoom_rec_2 monitor)
ffmpeg -y -f pulse -i zoom_rec_2.monitor -c:a libmp3lame -b:a 128k "${REC_DIR}/vimeo_projeler_2000.mp3" &
VPID=$!
echo "Vimeo kaydı başladı (PID: $VPID)"

# ═══════════════ DOĞRULA ═══════════════
sleep 3
echo ""
echo "=== DOĞRULAMA ==="

if kill -0 "$ZPID" 2>/dev/null; then echo "✅ Zoom seminer4: $(ls -lh ${REC_DIR}/seminer4_2000.mp3 2>/dev/null | awk '{print $5}')"; else echo "❌ Zoom kaydı başarısız!"; fi
if kill -0 "$VPID" 2>/dev/null; then echo "✅ Vimeo projeler: $(ls -lh ${REC_DIR}/vimeo_projeler_2000.mp3 2>/dev/null | awk '{print $5}')"; else echo "❌ Vimeo kaydı başarısız!"; fi

# ═══════════════ TÜM ZOOM SEMİNER RAPORU ═══════════════
echo ""
echo "📁 === KAMPÜSTEN SAHAYA ZİRVESİ - TAM RAPOR ==="
echo "=========================================="
TOTAL=0
for f in "$REC_DIR"/seminer*.mp3; do
    if [ -f "$f" ]; then
        NAME=$(basename "$f")
        SZ=$(ls -lh "$f" | awk '{print $5}')
        DU=$(ffprobe -hide_banner "$f" 2>&1 | grep Duration | awk '{print $2}' | tr -d ,)
        echo "  ✅ $NAME | $SZ | $DU"
        TOTAL=$((TOTAL+1))
    fi
done
echo "=========================================="
echo "Toplam $TOTAL Zoom seminer kaydı"
echo "🎥 Vimeo canlı yayın kaydı devam ediyor..."
echo "================================"
