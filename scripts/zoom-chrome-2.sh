#!/bin/bash
# zoom-chrome-2.sh — 2. Chrome'u PULSE_SINK=zoom_rec_2 ile başlatan wrapper
# Kullanım: ./zoom-chrome-2.sh [ek_flaglar...]
# Bu script, 30 Haz 2026'da yaşanan PULSE_SINK env kaybı hatasını önler.
# background=True ile terminal()'den çağrıldığında env değişkenleri
# inherit edilmez, bu yüzden export işlemi script içinde yapılır.
# NOT: --disable-gpu KULLANMA! Skill talimatı: ses servisini öldürür.
export PULSE_SINK=zoom_rec_2
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
