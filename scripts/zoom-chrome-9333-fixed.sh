#!/bin/bash
# zoom-chrome-9333-fixed.sh — Chrome + PulseAudio + D-Bus doğru env ile
# Kullanım: terminal(background=true, command="bash ~/.hermes/scripts/zoom-chrome-9333-fixed.sh")

export PULSE_SINK=zoom_rec
export DISPLAY=${DISPLAY:-:99}
export DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/dbus-live/socket

# PulseAudio socket'ini bul
PULSE_SOCK=$(find /tmp -name "native" -type s 2>/dev/null | head -1)
if [ -n "$PULSE_SOCK" ]; then
  export PULSE_SERVER="unix:$PULSE_SOCK"
fi

# Media pre-grant
mkdir -p /tmp/zoom_profile/Default
cat > /tmp/zoom_profile/Default/Preferences << 'PREFS'
{
  "profile": {"content_settings": {"exceptions": {
    "media_stream_mic": {"https://zoom.us,https://app.zoom.us": {"setting": 1}},
    "media_stream_camera": {"https://zoom.us,https://app.zoom.us": {"setting": 1}}
  }}},
  "browser": {"first_run_complete": true},
  "download": {"default_directory": "/home/ubuntu/recordings"}
}
PREFS

exec /usr/bin/chromium \
  --no-sandbox \
  --remote-debugging-port=9333 \
  --remote-allow-origins=* \
  --user-data-dir=/tmp/zoom_profile \
  --no-first-run \
  --no-default-browser-check \
  --disable-features=TranslateUI \
  --ozone-platform=x11 \
  --window-size=1280,720 \
  --use-fake-device-for-media-stream \
  --use-fake-ui-for-media-stream \
  --disable-dev-shm-usage
