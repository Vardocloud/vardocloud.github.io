# Cloudflared Connectivity Issues — 12 Tem 2026

## QUIC / HTTP2 Blocked Scenario

Cloudflared quick tunnel may fail to connect to Cloudflare edge servers even when the API is reachable.

### Symptoms
```
UDP Connectivity  region1.v2.argotunnel.com  FAIL    QUIC connection failed
TCP Connectivity  region1.v2.argotunnel.com  FAIL    HTTP/2 connection is blocked or unreachable
Cloudflare API    api.cloudflare.com:443     PASS    API is reachable
ERROR: Allow outbound QUIC traffic on port 7844 or use HTTP2.
```

### Root Cause
Docker/WSL environment sometimes blocks outbound QUIC (port 7844) and HTTP/2 to Cloudflare's argotunnel edge. Regular HTTPS (port 443) to api.cloudflare.com works fine, but the tunnel protocol can't establish connections.

### Attempted Fixes (None Worked Reliably)
- `--protocol http2` flag — same FAIL result
- `--protocol quic` (default) — same FAIL result  
- Switching URL from `host.docker.internal` to `localhost` — no effect on connectivity
- The issue resolves after time (hours) — likely Cloudflare edge-side rate limiting or temp block

### Workaround
Use **Tailscale Funnel** as primary access method. Cloudflared is a fallback that may not work in all network conditions.

### When Cloudflared Works
- First tunnel in a session usually establishes fine
- After 4+ hours, connections start failing (QUIC timeout)
- Killing and restarting cloudflared does NOT fix — the block persists
- Wait several hours or use Tailscale Funnel instead
