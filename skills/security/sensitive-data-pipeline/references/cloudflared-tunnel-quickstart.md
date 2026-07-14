# Cloudflared Quick Tunnels — Secure Pipeline

## Why cloudflared over SSH tunnels

| Feature | cloudflared | localhost.run | serveo.net |
|---|---|---|---|
| Free tier | ✅ Full | ❌ Broken (June 2026) | ⚠️ Flaky |
| Auth required | ❌ None | ❌ None | ❌ None |
| Setup time | ~5 seconds | N/A (broken) | ~10 seconds |
| HTTPS | ✅ Auto | ✅ | ✅ |
| Works on Oracle Cloud ARM64 | ✅ | ❌ | ⚠️ Sometimes |

## Quick Commands

### Start tunnel
```bash
# 1. Start local HTTP server
cd /tmp && python3 -m http.server 9999 &

# 2. Start cloudflared tunnel
cloudflared tunnel --url http://127.0.0.1:9999 2>&1 | tee /tmp/cf_tunnel.log &

# 3. Extract URL (after ~5s)
sleep 5 && grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cf_tunnel.log
```

### Verify tunnel is working
```bash
TUNNEL_URL=$(grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cf_tunnel.log)
curl -s "$TUNNEL_URL" | head -20
```

### Cleanup
```bash
pkill -f "cloudflared tunnel"
pkill -f "python3.*9999"
rm -f /tmp/cf_tunnel.log
```

### Full secure pipeline example
```bash
# Copy template to /tmp
cp ~/.hermes/skills/security/sensitive-data-pipeline/templates/bw-token-form.html /tmp/secure_page.html

# Serve on port 9999
cd /tmp && python3 -c "
import http.server
http.server.HTTPServer(('127.0.0.1', 9999), http.server.SimpleHTTPRequestHandler).serve_forever()
" &

# Tunnel
cloudflared tunnel --url http://127.0.0.1:9999 2>&1 | tee /tmp/cf_tunnel.log &

# Get URL
sleep 5 && grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cf_tunnel.log
```

## Installation Check
```bash
which cloudflared && cloudflared --version
# Expected: /usr/local/bin/cloudflared, version 2026.x.x
```

If not installed:
```bash
# ARM64 (Oracle Cloud)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared
```

## Notes
- Tunnel URL is random and changes each time — cannot be reused
- No authentication required for anonymous tunnels
- Tunnel stays alive until process is killed
- Rate limit: generous for occasional use
