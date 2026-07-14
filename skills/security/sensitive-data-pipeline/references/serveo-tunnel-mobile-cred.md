# Serveo Tunnel + HTML Form — Mobile Credential Capture

## When to Use

User is on mobile (phone/tablet), cannot open local HTML files, and needs to enter credentials/tokens without them reaching the primary LLM context. The HTML form must be accessible over HTTPS via a public URL.

## Architecture

```
1. Vanitas: start local HTTP server on high port (8080)
   cd <skill-templates-dir>/
   python3 -m http.server 8080   (background, notify_on_complete=false)

2. Vanitas: open SSH reverse tunnel to serveo.net
   ssh -o StrictHostKeyChecking=no \
       -o ServerAliveInterval=30 \
       -R 80:localhost:8080 serveo.net

3. Serveo gives back: "Forwarding HTTP traffic from https://<hash>.serveousercontent.com"

4. User opens https://<hash>.serveousercontent.com/<form>.html on phone

5. User fills form, clicks "Kod Olustur", gets VANITAS_SECURE::<base64>

6. User pastes code into chat — Vanitas decodes in terminal, processes data

7. Cleanup: pkill -f "python3 -m http.server" ; pkill -f "serveo.net"
```

## serveo.net Details

- **No account required** — connect and get a random subdomain
- **HTTPS only** (Let's Encrypt cert, valid for 3 months, auto-renewed)
- **Rate limit:** generous, no auth token needed
- **Warning page:** serveo inserts an interstitial on first visit for non-pro users; user clicks through
- **Connection:** SSH port forwarding only — the server makes an outbound SSH connection, so no inbound firewall ports needed (bypasses Oracle Cloud security lists, UFW, etc.)
- **Keepalive:** Pass `-o ServerAliveInterval=30` to prevent SSH timeout

## Comparison with Alternatives

| Method | Auth Required | Works on Mobile | Bypasses Cloud Firewall | Effort |
|--------|--------------|-----------------|------------------------|--------|
| serveo.net | None | ✅ HTTPS | ✅ Outbound SSH only | Low |
| localhost.run | None | ✅ HTTPS | ✅ Outbound SSH only | Low |
| ngrok | Account + auth token | ✅ HTTPS | ✅ Outbound tunnel | Medium |
| Cloudflare Tunnel | Account + cloudflared | ✅ HTTPS | ✅ Outbound tunnel | High |
| Local data: URI | None | ❌ Entity too large | ✅ N/A | Low |
| Serve via port 80/443 | None | ✅ HTTP | ❌ Blocked by Oracle | Medium |

## Pitfalls

- serveo.net interstitial warning page scares some users — explain it's normal
- SSH tunnel may drop after ~2h inactivity; reconnect if needed
- The tunnel URL is ephemeral — cannot be reused after SSH disconnect
- Python http.server is single-threaded; only one user at a time
- Port 8080 may be blocked by UFW — that's fine, the tunnel only needs localhost access
- Always clean up background processes after done
- **If serveo.net fails silently (no URL in output, empty stdout for 10s+), switch to localhost.run** immediately — don't waste time debugging

---

## Alternative: localhost.run

When serveo.net is slow, drops connections, or fails to assign a URL, use **localhost.run** instead.

### Setup

Same as serveo, but connect to `nokey@localhost.run`:

```bash
ssh -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -R 80:localhost:<PORT> nokey@localhost.run
```

### How It Differs from serveo.net

| Feature | serveo.net | localhost.run |
|---------|-----------|---------------|
| URL format | `https://<hash>.serveousercontent.com` | `https://<hash>.lhr.life` |
| Warning page | Yes (interstitial for non-pro) | None — direct to page |
| Connection ID | No | Yes — printed on connect |
| QR code | No | Yes (for mobile) |
| Reliability | Intermittent (Oracle Cloud) | More consistent |
| Usability | May scare user | Feels cleaner |

### When to Use

- **serveo fails** to produce a URL (stdout stays empty after 10+ seconds)
- **Previous serveo attempts** on this server have been flaky
- **User is unfamiliar** and the interstitial would confuse them
- **Anywhere serveo is documented** — just substitute the SSH command

### The complete tunnel flow (localhost.run)

```bash
# 1. Start HTTP server (background)
cd /home/ubuntu/.hermes/skills/security/sensitive-data-pipeline/templates
python3 -m http.server <PORT> --bind 127.0.0.1
# (background, no notify_on_complete)

# 2. Verify server works
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:<PORT>/bw-token-form.html
# → 200

# 3. Open tunnel (background)
ssh -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -R 80:localhost:<PORT> nokey@localhost.run

# 4. Wait for "tunneled with tls termination" in log, extract URL
# e.g. "https://70425b28db2995.lhr.life"
process(action='log', session_id='...')

# 5. Give user the full URL: https://<hash>.lhr.life/bw-token-form.html

# 6. After user pastes the base64 → cleanup
pkill -f "python3 -m http.server"   # kills the server
process(action='kill', session_id='...')  # kills the tunnel
```
