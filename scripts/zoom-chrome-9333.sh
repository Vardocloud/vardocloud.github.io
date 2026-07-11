#!/bin/bash
# zoom-chrome-9333.sh — DÜZGÜN Chrome (--disable-gpu YOK, skill talimatı)
export PULSE_SINK=zoom_rec
export DISPLAY=:99
export LD_LIBRARY_PATH="/tmp/pulseaudio_extract/usr/lib/x86_64-linux-gnu:/tmp/pulseaudio_extract/usr/lib/x86_64-linux-gnu/pulseaudio"
PULSE_SOCK=$(find /tmp -name "native" -type s 2>/dev/null | head -1)
export PULSE_SERVER="unix:$PULSE_SOCK"

mkdir -p /tmp/zoom_profile
mkdir -p /tmp/zoom_profile/Default

# Media permission pre-grant
cat > /tmp/zoom_profile/Default/Preferences << 'PREFS'
{
  "profile": {"content_settings": {"exceptions": {"media_stream_mic": {"https://zoom.us,https://app.zoom.us": {"setting": 1}},"media_stream_camera": {"https://zoom.us,https://app.zoom.us": {"setting": 1}}}}},
  "browser": {"first_run_complete": true},
  "download": {"default_directory": "/home/ubuntu/recordings"}
}
PREFS

exec /usr/bin/chromium \
  --no-sandbox --remote-debugging-port=9333 --remote-allow-origins=* \
  --user-data-dir=/tmp/zoom_profile --no-first-run \
  --no-default-browser-check --disable-features=TranslateUI \
  --ozone-platform=x11 --window-size=1280,720 \
  --use-fake-device-for-media-stream --use-fake-ui-for-media-stream \
  --disable-dev-shm-usage \
  "$@"
