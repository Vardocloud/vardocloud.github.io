# VNC + noVNC Container Setup

> VNC-assisted manual login for NotebookLM Google auth.
> Container port 6080'de noVNC web arayüzü.

## Stack Components

- **Xvfb**: Sanal framebuffer (display :99 veya :100)
- **x11vnc**: X11 → VNC bridge
- **noVNC**: WebSocket → VNC (port 6080)
- **cloudflared**: Public tunnel (opsiyonel)

## Başlatma

```bash
# Xvfb
Xvfb :99 -screen 0 1920x1080x24 -ac &

# x11vnc
x11vnc -display :99 -forever -shared -nopw -noxdamage -nodpms &

# noVNC
/usr/share/novnc/utils/novnc_proxy --vnc localhost:5900 --listen 6080 &

# Chrome
DISPLAY=:99 chromium --user-data-dir=~/.hermes/chrome_profile_notebooklm \
  --no-first-run --no-sandbox --disable-dev-shm-usage --disable-gpu \
  https://notebooklm.google.com
```

## Stale Xvfb Check

```bash
ps aux | grep Xvfb
# root-owned Xvfb :99 varsa farklı display kullan (:100)
```

## MIT-SHM Crash Fix

```bash
x11vnc -display :100 -forever -shared -nopw -noxdamage -nodpms
```
