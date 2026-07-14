# CDP Tunneling — Visual Chrome Access Without VNC

## Problem

You need to let the user visually interact with Chrome running on the server (e.g., complete a Google login, handle a passkey challenge, or debug a page), but:
- `sudo`/root is unavailable (can't install VNC, x11vnc, or system packages)
- The user can't SSH tunnel to localhost
- `xvfb-run` fails because `xauth` isn't installed
- ngrok requires account registration and auth token

## Solution: localhost.run SSH Tunnel

[localhost.run](https://localhost.run) is a free SSH-based reverse tunnel service that requires **no registration, no auth token, no client install** — just SSH.

### Quick Start

```bash
# Expose Chrome CDP port (e.g., 40817) to the internet
ssh -o StrictHostKeyChecking=no -R 80:localhost:40817 nokey@localhost.run
```

On success, the service prints a public URL:
```
https://d9ec657db6c1e1.lhr.life tunneled with tls termination
```

### How the User Connects

**Option A — Direct DevTools (simplest):**
1. Open `https://<tunnel-url>/json` in their browser
2. Find the `devtoolsFrontendUrl` field — it contains a full `chrome-devtools://...` URL
3. Copy-paste that URL into a new tab → full Chrome DevTools opens against the server's browser
4. User can see the page, inspect elements, click buttons, type into forms

**Option B — chrome://inspect:**
1. User opens `chrome://inspect` in their OWN Chrome
2. Click "Discover network targets" → "Add target"
3. Enter `<tunnel-hostname>:80` (e.g., `d9ec657db6c1e1.lhr.life:80`)
4. The server's Chrome tab appears in the list → click "inspect"

### Finding the CDP Port

```bash
# Find Chrome's remote debugging port
ps aux | grep "remote-debugging-port" | grep -v grep | grep -oP 'remote-debugging-port=\K[0-9]+' | sort -u
```

The correct port is typically the LAST one in the list if multiple Chrome instances are running.

### Prerequisites for CDP WebSocket

Chrome MUST have the `--remote-allow-origins=*` flag for CDP WebSocket to work. Without it, `websocket-client` gets HTTP 403:

```
WebSocketBadStatusException: Handshake status 403 Forbidden
Rejected an incoming WebSocket connection from the http://127.0.0.1:... origin.
```

**Fix:** Add to `uc.ChromeOptions()` in `client.py`:
```python
options.add_argument("--remote-allow-origins=*")
```

### Architecture

```
User's Browser  ←HTTPS→  localhost.run  ←SSH→  Server  → Chrome (CDP :40817)
```

- localhost.run provides TLS termination (HTTPS)
- SSH keeps the tunnel alive as long as the process runs
- Chrome serves CDP over HTTP (no TLS) — localhost.run handles the TLS wrapping

### Limitations

| Factor | Detail |
|--------|--------|
| Tunnel lifetime | Tunnel dies when SSH process dies. Re-run to get a NEW URL each time |
| URL persistence | Each tunnel gets a random subdomain (e.g., `d9ec657db6c1e1`). No custom domain without account |
| Speed | SSH encryption adds ~50-100ms latency. Fine for manual login, slow for automation |
| Single port | One tunnel per SSH command. Need multiple tunnels for multiple ports |
| Session management | No auth on the tunnel URL — anyone with the URL can see the Chrome session. Share carefully |
| CDP HTTP only | localhost.run wraps HTTP, but Chrome DevTools page uses `chrome-devtools://` protocol which bypasses tunnel. Option B (chrome://inspect) may not work with remote hosts |

### Alternatives

| Service | Auth needed | Persistent URL | Notes |
|---------|------------|----------------|-------|
| **localhost.run** ❤️ | None | No | Recommended — no registration |
| **serveo.net** | None | Optional (custom domain) | Similar to localhost.run, sometimes slower |
| **ngrok** | Account + authtoken | Yes (paid) | Higher reliability, persistent domains |
| **bore** | None | No | Binary download needed, no TLS |
| **SSH -R** (your own VPS) | SSH key | Yes | Requires a public VPS |

### Pitfalls

- **Old Chrome processes still running:** `pkill -9 -f chromium` may not kill all children. Use `kill -9 $(ps aux | grep -E "chrome|chromium" | awk '{print $2}')` for forceful cleanup.
- **Tunnel shows wrong page:** Verify CDP port is correct. Old Chrome instances may hold stale ports.
- **localhost.run says "permission denied":** Try adding your SSH public key or use the anonymous key: `ssh -o StrictHostKeyChecking=no -R 80:localhost:PORT nokey@localhost.run`
- **Connection refused on tunnel URL:** The CDP port might not be bound to 0.0.0.0 — it defaults to 127.0.0.1. This is fine for SSH tunnels since both ends are localhost.
