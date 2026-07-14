# Cloudflared Silent Failure Pattern (June 2026)

## Symptom
`cloudflared tunnel --url http://127.0.0.1:PORT` run in background (nohup, &, or Hermes `background=true`) produces **zero output**. The process runs, tunnel is created, but the URL is invisible. Tool waits forever with empty log.

## Root Cause
Cloudflared buffers stdout when not connected to a TTY. In background mode, there's no TTY, so output never flushes.

## Fix: tee to log file
```bash
cloudflared tunnel --url http://127.0.0.1:8767 --no-autoupdate 2>&1 | tee /tmp/cf_tunnel.log &
sleep 8
TUNNEL_URL=$(grep -oP 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' /tmp/cf_tunnel.log | tail -1)
```

## Or: Run in foreground briefly
```bash
timeout 10 cloudflared tunnel --url http://127.0.0.1:8767 --no-autoupdate 2>&1
# Read URL from output, then restart in background
```

## NOT an IP Ban
If foreground cloudflared works, the IP is NOT banned. The error "control stream failure" in background is an output buffering artifact, not a network block. Only diagnose IP ban when:
- Cloudflare returns error code 1010 (HTTP 403 with specific error)
- Foreground cloudflared also fails
- Direct curl to Cloudflare API times out
