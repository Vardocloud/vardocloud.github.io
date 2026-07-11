#!/bin/bash
export DISPLAY=:99
PROFILE=/home/ubuntu/.hermes/chrome_profile_notebooklm
rm -f $PROFILE/Singleton* $PROFILE/Default/Singleton*
exec chromium \
  --no-sandbox --disable-dev-shm-usage --disable-gpu \
  --remote-debugging-port=18800 --remote-allow-origins=* \
  --user-data-dir=$PROFILE \
  --window-size=1280,1024 \
  https://notebooklm.google.com
