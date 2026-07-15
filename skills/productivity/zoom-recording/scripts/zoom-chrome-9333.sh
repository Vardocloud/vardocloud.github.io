#!/bin/bash
# zoom-chrome-9333.sh — DÜZGÜN Chrome wrapper (--disable-gpu YOK!)
#
# ~/.hermes/scripts/zoom-chrome-1.sh ve zoom-chrome-2.sh'de
# --disable-gpu flag'i var. Bu flag getUserMedia'i (dolayısıyla
# Zoom ses kaydını) bozar. Bu script DOĞRU flag'lerle başlatır.
#
# Kullanım:
#   terminal("bash ~/.hermes/skills/productivity/zoom-recording/scripts/zoom-chrome-9333.sh --remote-debugging-port=9333", background=true)

export PULSE_SINK=zoom_rec
export DISPLAY=${DISPLAY:-:99}

# D-Bus adresleri — start_pulseaudio.sh ile tutarlı olmalı
DBUS_SOCK=$(find /tmp -name "system_bus_socket" -type s 2>/dev/null | head -1)
if [ -n "$DBUS_SOCK" ]; then
  export DBUS_SYSTEM_BUS_ADDRESS="unix:path=$DBUS_SOCK"
fi
export DBUS_SESSION_BUS_ADDRESS=${DBUS_SESSION_BUS_ADDRESS:-unix:path=/tmp/dbus-session}

# PulseAudio socket
PULSE_SOCK=$(find /tmp -name "native" -type s 2>/dev/null | head -1)
if [ -n "$PULSE_SOCK" ]; then
  export PULSE_SERVER="unix:$PULSE_SOCK"
fi

# Media permission pre-grant için profile
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
  --disable-dev-shm-usage \
  "$@"
