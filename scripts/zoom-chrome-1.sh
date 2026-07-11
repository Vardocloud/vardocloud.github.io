#!/bin/bash
# zoom-chrome-1.sh — Chrome'u PULSE_SINK=zoom_rec ile başlatan wrapper
# Kullanım: ./zoom-chrome-1.sh [ek_flaglar...]
# NOT: --disable-gpu KULLANMA! Skill talimatı: ses servisini öldürür.
export PULSE_SINK=zoom_rec
export DISPLAY=${DISPLAY:-:99}
exec /usr/bin/chromium \
  --no-sandbox \
  --disable-dev-shm-usage \
  --no-first-run \
  --no-default-browser-check \
  --disable-features=TranslateUI \
  --ozone-platform=x11 \
  --window-size=1280,720 \
  --use-fake-device-for-media-stream \
  --use-fake-ui-for-media-stream \
  "$@"
