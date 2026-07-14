# Docker Environment Port Mapping (vanatis-hermes)

Discovered 21 Jun 2026 via `docker ps` on Windows host.

## Exposed Ports (host → container)

| Container Port | Host Port | Service | Notes |
|---------------|-----------|---------|-------|
| 8642/tcp | 127.0.0.1:8642 | Hermes Gateway | Primary API, always running |
| 9119/tcp | 127.0.0.1:9119 | Hermes internal | Check availability before use |
| 22/tcp | 127.0.0.1:2222 | SSH (OpenSSH) | Key-only auth |

## Companion Containers

| Hostname | Container | Purpose | Network |
|----------|-----------|---------|---------|
| `warp` | `vanatis-warp` | WARP+ SOCKS5 proxy (port 1080) | Docker bridge → 172.19.0.2 |
| `vanatis` | `vanatis-hermes` | Main Hermes agent | Docker bridge → 172.19.0.3 |
| (tailscale) | `vanatis-tailscale` | Tailscale VPN | Docker bridge |

## Port Selection Strategy for pw_server.py

When opening a temporary password-capture server:

1. **Preferred: 9119** — Known to be host-mapped (127.0.0.1 accessible from Windows)
   - But may already be in use → check first
2. **Fallback: ephemeral port** — Auto-port server, then tunnel via cloudflared:
   ```bash
   cloudflared tunnel --url http://localhost:PORT
   ```
3. **Last resort: docker exec command** — Edel runs in PowerShell:
   ```powershell
   echo -n 'SIFRE' | docker exec -i vanatis-hermes tee /tmp/pw_val.txt > $null
   docker exec vanatis-hermes chmod 600 /tmp/pw_val.txt
   ```

## Discovery Commands

```bash
# From Windows PowerShell:
docker ps

# From container (check which ports are in use):
netstat -tlnp 2>/dev/null || cat /proc/net/tcp

# Find WARP container IP:
getent hosts warp
```

## ⚠️ Important

Docker bridge IPs (172.19.0.x) may change on container/network restart.
Host-mapped ports (127.0.0.1:*) are stable across restarts.
