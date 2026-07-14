#!/bin/bash
# transcribe-groq.sh — Groq Whisper ile toplu transkripsiyon
# Kullanım: transcribe-groq.sh <output.md> <mp3_file1> [mp3_file2] ...
# Örnek: transcribe-groq.sh transkript_apa.mp3 seminer.mp3

GRKEY=$(grep GROQ_API_KEY /home/ubuntu/.hermes/.env | head -1 | cut -d= -f2-)
OUTPUT="$1"
shift

if [ -z "$GRKEY" ]; then
  echo "❌ GROQ_API_KEY bulunamadı (.env'de tanımlı olmalı)"
  exit 1
fi
if [ -z "$OUTPUT" ] || [ $# -eq 0 ]; then
  echo "Kullanım: transcribe-groq.sh <output.md> <mp3_dosyaları...>"
  exit 1
fi

ALL_TEXT=""

for FILE in "$@"; do
  if [ ! -f "$FILE" ]; then
    echo "⚠️ Dosya yok: $FILE"
    continue
  fi
  BASENAME=$(basename "$FILE")
  echo "📝 $BASENAME ($(du -h "$FILE" | cut -f1))..."
  
  # 25MB sınırı — büyükse segmentlere böl
  SIZE=$(stat -c%s "$FILE" 2>/dev/null || echo 0)
  if [ "$SIZE" -gt 25000000 ]; then
    echo "   > 25MB, segmentlere bölünüyor..."
    CHUNK_DIR=$(mktemp -d)
    ffmpeg -y -i "$FILE" -f segment -segment_time 1200 -c copy "${CHUNK_DIR}/chunk_%03d.mp3" 2>/dev/null
    for CHUNK in "${CHUNK_DIR}"/chunk_*.mp3; do
      [ -f "$CHUNK" ] || continue
      CHUNK_TEXT=$(curl -s -X POST "https://api.groq.com/openai/v1/audio/transcriptions" \
        -H "Authorization: Bearer *** \
        -F "file=@$CHUNK" -F "model=whisper-large-v3" -F "language=tr" -F "response_format=json" | \
        python3 -c "import sys,json; print(json.load(sys.stdin).get('text',''))" 2>/dev/null)
      ALL_TEXT+="$CHUNK_TEXT\n\n"
      sleep 2
      echo "   chunk $(basename $CHUNK): $(echo $CHUNK_TEXT | wc -c) chars"
    done
    rm -rf "$CHUNK_DIR"
  else
    CHUNK_TEXT=$(curl -s -X POST "https://api.groq.com/openai/v1/audio/transcriptions" \
      -H "Authorization: Bearer *** \
      -F "file=@$FILE" -F "model=whisper-large-v3" -F "language=tr" -F "response_format=json" | \
      python3 -c "import sys,json; print(json.load(sys.stdin).get('text',''))" 2>/dev/null)
    ALL_TEXT+="$CHUNK_TEXT\n\n"
    echo "   $(echo $CHUNK_TEXT | wc -c) chars"
  fi
  sleep 2
done

# Transkripti yaz
cat > "$OUTPUT" << EOF
# Transkript

**Tarih:** $(date '+%d %B %Y')
**Dosyalar:** $*

---

$ALL_TEXT

---
*Transkript Groq Whisper (whisper-large-v3) ile oluşturulmuştur.*
EOF
echo "✅ Transkript kaydedildi: $OUTPUT ($(wc -c < "$OUTPUT") bytes, $(wc -m < "$OUTPUT") karakter)"
