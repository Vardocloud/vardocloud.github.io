#!/bin/bash
export DISPLAY=:99
PROFILE=/home/ubuntu/.hermes/chrome_profile_notebooklm_legacy
rm -f $PROFILE/Singleton* $PROFILE/Default/Singleton*
exec chromium \
  --no-sandbox --disable-dev-shm-usage --disable-gpu \
  --remote-debugging-port=18801 --remote-allow-origins=* \
  --user-data-dir=$PROFILE \
  --window-size=1280,1024 \
  https://notebooklm.google.com
