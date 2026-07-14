# NotebookLM Auth — Working Approach (24 Haz 2026)

## Root Cause
Cookie-only auth (`nlm login --manual`, HTTP cookie import) **fails from server IP** — Google redirects to accounts.google.com because the browser fingerprint (User-Agent, WebGL, fonts, TLS params) doesn't match the cookie origin.

## ✅ Working Approach
Use **old notebooklm-mcp** (v2.0.11, `pip install notebooklm-mcp`) with undetected-chromedriver + live Chrome profile.

### Hermes Config
```yaml
notebooklm-mcp:
    args: ["server"]
    command: /usr/local/bin/notebooklm-mcp
    enabled: true
    env:
      NOTEBOOKLM_PROFILE_DIR: /home/ubuntu/.hermes/chrome_profile_notebooklm
    timeout: 120
```

### Setup via CLI
```bash
hermes config set mcp_servers.notebooklm-mcp.command /usr/local/bin/notebooklm-mcp
hermes config set mcp_servers.notebooklm-mcp.args '["server"]'
hermes config set mcp_servers.notebooklm-mcp.env '{"NOTEBOOKLM_PROFILE_DIR": "/home/ubuntu/.hermes/chrome_profile_notebooklm"}'
```

### VNC-Assisted Login Flow (When Session Lost)
1. Kill all notebooklm Chrome processes: `pkill -f "chrome.*notebooklm"`
2. Remove lock files: `rm -f ~/.hermes/chrome_profile_notebooklm/Singleton*`
3. Start VNC stack: Xvfb + x11vnc + websockify + cloudflared
4. Start MCP: `NOTEBOOKLM_PROFILE_DIR=... DISPLAY=:99 /usr/local/bin/notebooklm-mcp server`
5. MCP starts undetected-chromedriver → Chrome opens on VNC display
6. User connects via noVNC and logs into Google
7. MCP detects auth → tools become available

### Test
```bash
# After MCP is running, test with healthcheck
# Hermes MCP tool: mcp_notebooklm_mcp_healthcheck()
# Expected: {status: "healthy", authenticated: true}
```

## ❌ What Does NOT Work
| Method | Reason |
|--------|--------|
| `nlm login --manual -f cookies.json` | Google rejects server-originated cookies (fingerprint mismatch) |
| nlm CLI (`nlm list notebooks`) | Same cookie rejection; nlm uses HTTP-only auth |
| Cookie import to Chrome SQLite DB | Chrome 149 encrypts cookie values; decryption key unavailable |
| Any headless-only approach | undetected-chromedriver needs headed mode for Google auth |

## Comparison of Available Tools
| Binary | Package | Use Case |
|--------|---------|----------|
| `/usr/local/bin/notebooklm-mcp` | `pip install notebooklm-mcp` (v2.0.11) | **MCP server** — undetected-chromedriver + profile |
| `/home/ubuntu/.local/bin/nlm` | jacob-bd/notebooklm-mcp-cli | **Diagnostic only** — `nlm doctor`, `nlm login --check` |
| `/home/ubuntu/.local/bin/notebooklm-mcp` | jacob-bd/notebooklm-mcp-cli | **Same as nlm** — points to notebooklm_tools |
