#!/bin/bash
# transkript_all.sh — Tüm chunk'ları Groq ile transkript et
GRKEY=$(grep GROQ_API_KEY /home/ubuntu/.hermes/.env | head -1 | cut -d= -f2-)

transcribe() {
  local file="$1" out="$2"
  echo "📝 $(basename $file)..."
  curl -s -X POST "https://api.groq.com/openai/v1/audio/transcriptions" \
    -H "Authorization: Bearer $GRKEY" \
    -F "file=@$file" \
    -F "model=whisper-large-v3" \
    -F "language=tr" \
    -F "response_format=json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('text',''))" > "$out"
  echo "   -> $(wc -c < $out) bytes"
  sleep 2
}

# APA
APA_TEXT=""
for i in 0 1 2; do
  f="/home/ubuntu/recordings/10temmuz/chunks_apa/chunk_00${i}.mp3"
  o="/tmp/chunk_apa_${i}.txt"
  if [ -f "$f" ]; then
    transcribe "$f" "$o"
    APA_TEXT+="$(cat $o)\n\n"
  fi
done

cat > /home/ubuntu/recordings/10temmuz/transkript_apa.md << EOF
# APA: Back to Class — Behavioral Strategies for Emotional-Based School Avoidance

**Tarih:** 10 Temmuz 2026
**Toplam Süre:** ~45 dakika
**Chunk Sayısı:** 3

---

$APA_TEXT

---
*Transkript Groq Whisper (whisper-large-v3) ile oluşturulmuştur.*
EOF
echo "✅ APA transkript: $(wc -c < /home/ubuntu/recordings/10temmuz/transkript_apa.md) bytes"

# YouTube
YT_TEXT=""
for i in 0 1 2; do
  f="/home/ubuntu/recordings/10temmuz/chunks_yt/chunk_00${i}.mp3"
  o="/tmp/chunk_yt_${i}.txt"
  if [ -f "$f" ]; then
    transcribe "$f" "$o"
    YT_TEXT+="$(cat $o)\n\n"
  fi
done

cat > /home/ubuntu/recordings/10temmuz/transkript_yt.md << EOF
# YouTube Semineri

**Tarih:** 10 Temmuz 2026
**Toplam Süre:** ~60 dakika
**Chunk Sayısı:** 3

---

$YT_TEXT

---
*Transkript Groq Whisper (whisper-large-v3) ile oluşturulmuştur.*
EOF
echo "✅ YouTube transkript: $(wc -c < /home/ubuntu/recordings/10temmuz/transkript_yt.md) bytes"
echo "🎉 Tamamlandı!"
