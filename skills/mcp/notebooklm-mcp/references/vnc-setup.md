# VNC Setup for Headless Environments

When Google blocks headless Chrome login attempts ("signin/rejected"), you need
a visible display. Use x11vnc + noVNC + Cloudflare Tunnel for web-based VNC access.

## Stack

```
Cloudflare Tunnel (trycloudflare.com)
   ↓ port 6080
noVNC (websockify)
   ↓ port 5900
x11vnc
   ↓ display :99
Xvfb (virtual framebuffer)
```

## Commands

```bash
# 1. Start x11vnc (always use -noshm with Xvfb)
x11vnc -display :99 -forever -shared -passwd hermes123 -rfbport 5900 -noshm

# 2. Install noVNC
git clone --depth 1 https://github.com/novnc/noVNC.git /tmp/noVNC

# 3. Start noVNC
/tmp/noVNC/utils/novnc_proxy --vnc localhost:5900 --listen 6080

# 4. Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
  -o /tmp/cloudflared && chmod +x /tmp/cloudflared

# 5. Start tunnel
/tmp/cloudflared tunnel --url http://localhost:6080 --no-autoupdate

# 6. Get URL from logs (look for "trycloudflare.com")
```

## Access

Open `https://RANDOM.trycloudflare.com/vnc.html` in any browser.

## Troubleshooting

- `x11vnc` needs `-noshm` (MIT-SHM not available with Xvfb)
- `x11vnc` needs `-no6` if IPv6 port is already in use
- Kill ALL x11vnc processes before starting fresh: `pkill -9 -f x11vnc`
- Verify port with Python: `import socket; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1',5900))`
- `nc`, `ss`, `netstat` may not exist in minimal containers
- Cloudflare quick tunnels last ~1 hour and need no account
