#!/usr/bin/env bash
# Kolay kullanım için wrapper
# Kullanım: ./olustur.sh /klasor/yolu [cikti.mp3] [muzik.mp3]

set -e

IMAGE_DIR="${1:-.}"
OUTPUT="${2:-reel_cikti.mp4}"
MUSIC="${3:-}"
FONT="${4:-}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

CMD="python3 \"$SCRIPT_DIR/reel_olustur.py\" --images \"$IMAGE_DIR\" --output \"$OUTPUT\""

if [ -n "$MUSIC" ]; then
    CMD="$CMD --music \"$MUSIC\""
fi
if [ -n "$FONT" ]; then
    CMD="$CMD --font \"$FONT\""
elif [ -f "$HOME/.fonts/Roboto.ttf" ]; then
    CMD="$CMD --font \"$HOME/.fonts/Roboto.ttf\""
fi

echo "🎬 Reel oluşturuluyor..."
echo "   Görseller: $IMAGE_DIR"
echo "   Çıktı: $OUTPUT"
[ -n "$MUSIC" ] && echo "   Müzik: $MUSIC"
[ -f "$HOME/.fonts/Roboto.ttf" ] && echo "   Font: Roboto"

eval "$CMD"
