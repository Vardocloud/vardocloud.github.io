# VNC Fallback for Manual Auth

## Architecture

```
Xvfb :99 → Chrome browser on :99
    → x11vnc (port 5900)
        → websockify --web . (port 6082, dual HTTP+WS)
            → SSH tunnel (port 443) → public HTTPS URL
```

## Port Map

| Layer | Port | Protocol |
|-------|------|----------|
| Xvfb | :99 | X11 display |
| x11vnc | 5900 | RFB/VNC (localhost) |
| websockify+noVNC | 6082 | HTTP + WebSocket |
| Serveo/localhost.run | 443 | HTTPS (public) |

## Key Techniques

### websockify `--web .` Dual Mode
Without `--web .`, websockify returns HTTP 405 for non-WebSocket requests. With the flag, it serves noVNC static files and proxies WebSocket on the same port. Change directory to the noVNC clone before starting.

### SSH Tunnel URL Capture
Hermes background process captures show empty output for SSH tunnels. Use Python subprocess with file redirection to capture the URL line containing "Forwarding" (Serveo) or the `.lhr.life` URL (localhost.run).

### Cloudflare Tunnel (alternative to SSH tunnels)

When SSH tunnels (Serveo, localhost.run) are blocked or unreliable, use `cloudflared` for a direct tunnel to Cloudflare's edge:

```bash
# Install (one-time):
curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /tmp/cloudflared
chmod +x /tmp/cloudflared

# Start tunnel (Hermes terminal background):
/tmp/cloudflared tunnel --url http://localhost:6080

# Output includes trycloudflare.com URL after ~5s:
# Your quick Tunnel has been created! Visit it at:
# https://exchanges-refine-altered-nightlife.trycloudflare.com
```

**Pros vs SSH tunnels:**
- No SSH keys, no SSH server, no account needed
- More reliable (Cloudflare's infrastructure vs third-party SSH jumpboxes)
- Faster URL generation (~5s vs 8-12s)
- Hermes `terminal(background=true)` output is captured correctly (unlike SSH tunnels)

**Cons:**
- Random URL each time (no custom subdomain)
- ~200ms added latency (Cloudflare edge routing)
- Binary not pre-installed (~25MB download)

**URL format:** `https://<random-words>.trycloudflare.com/vnc.html`

### Service URL Patterns
- Serveo: `https://<hash>-<ip>.serveousercontent.com/vnc.html`
- localhost.run: `https://<hash>.lhr.life/vnc.html`

## Pitfalls

- **x11vnc port conflict:** Kill previous instances before starting
- **Old websockify on same port:** Verify port availability, kill with fuser
- **Start order:** x11vnc first, THEN websockify — reverse order gives connection refused
- **Do NOT request credentials in chat:** VNC exists so user enters password on their own device
- **SSH tunnel background capture:** Use Python subprocess, not Hermes bg terminal

### 🚨 x11vnc 0.9.17+: `-noxshm` Removed, Use `-noshm` Instead

x11vnc versions ≥0.9.17 (Debian trixie, 2025+) **removed the `-noxshm` flag**. Using it produces:

```
*** unrecognized option(s) ***
    [1]  -noxshm
```

And without SHM disabled, x11vnc crashes on common Xvfb setups:

```
X Error of failed request:  BadAccess (attempt to access private resource denied)
  Major opcode of failed request:  130 (MIT-SHM)
```

**Fix:** Replace `-noxshm` with `-noshm`:

```bash
# OLD (broken on x11vnc 0.9.17+):
x11vnc -display :99 -noxshm -rfbport 5901 -rfbauth ~/.vnc/passwd ...

# NEW (works everywhere):
x11vnc -display :99 -noshm -rfbport 5901 -rfbauth ~/.vnc/passwd ...
```

**Why this happens:** Xvfb is often started without MIT-SHM extension support. x11vnc tries to attach a shared memory segment via `X_ShmAttach` and gets `BadAccess`. `-noshm` tells x11vnc to fall back to `XGetImage` polling instead.

**Full working startup (with password auth):**
```bash
# Create password first (one-time):
x11vnc -storepasswd vanitas123 ~/.vnc/passwd

# Start server:
x11vnc -display :99 -noshm -rfbport 5902 \
  -rfbauth ~/.vnc/passwd -forever -shared -bg \
  -o ~/.vnc/x11vnc.log
```

**Verify:**
```bash
ps aux | grep x11vnc   # should show process
cat ~/.vnc/x11vnc.log | tail -5  # no MIT-SHM error
```

### Port Selection Convention

| Port | Service | Notes |
|------|---------|-------|
| 5900 | x11vnc (default) | May conflict with stale processes |
| 5901-5902 | x11vnc (fallback) | Preferred: avoids stale-instance conflicts |
| 6080 | websockify+noVNC | HTTP + WebSocket (`--web .`) |

## Decision Tree

Automated auth attempt
  ├── CDP login successful? → Done
  ├── 403 WebSocket / CDP fail? → Try manual cookie import
  │     ├── Cookies fresh? → Done
  │     └── Session revoked / passkey? → VNC FALLBACK
  ├── Google passkey / 2FA challenge? → VNC FALLBACK
  ├── "Try again" infinite loop? → VNC FALLBACK
  └── Write ops still fail after import? → VNC FALLBACK
