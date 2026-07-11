#!/bin/bash
# zoom-chrome-9334.sh — YouTube için ikinci Chrome
export PULSE_SINK=zoom_rec_2
export DISPLAY=${DISPLAY:-:99}
export DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/dbus-live/socket
PULSE_SOCK=$(find /tmp -name "native" -type s 2>/dev/null | head -1)
[ -n "$PULSE_SOCK" ] && export PULSE_SERVER="unix:$PULSE_SOCK"

mkdir -p /tmp/zoom_profile2/Default
cat > /tmp/zoom_profile2/Default/Preferences << 'PREFS'
{
  "profile": {"content_settings": {"exceptions": {
    "media_stream_mic": {"https://youtube.com,https://www.youtube.com": {"setting": 1}}
  }}},
  "browser": {"first_run_complete": true}
}
PREFS
rm -f /tmp/zoom_profile2/Singleton*

exec /usr/bin/chromium \
  --no-sandbox \
  --remote-debugging-port=9334 \
  --remote-allow-origins=* \
  --user-data-dir=/tmp/zoom_profile2 \
  --no-first-run --no-default-browser-check \
  --disable-features=TranslateUI \
  --ozone-platform=x11 --window-size=1280,720 \
  --use-fake-device-for-media-stream \
  --use-fake-ui-for-media-stream \
  --disable-dev-shm-usage about:blank
