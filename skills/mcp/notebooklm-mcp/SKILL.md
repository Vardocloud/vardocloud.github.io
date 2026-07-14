---
name: notebooklm-mcp
description: >-
  NotebookLM MCP server setup, authentication, and CLI usage. Covers the
  currently installed notebooklm-mcp-cli v0.8.6 (jacob-bd, uv) as PRIMARY,
  with the retired notebooklm-mcp v2.0.11 (pip) noted as migration source.
  Dual Chrome architecture (ports 18800/18801). Account routing:
  notebooklm-routing skill.
tags: [notebooklm, mcp, auth, google-login, uv, cli, studio, nlm]
version: "5.0"
---

# NotebookLM MCP v5.0 — notebooklm-mcp-cli v0.8.6

## Overview

**Current MCP (since 12 Tem 2026):** `notebooklm-mcp-cli` v0.8.6 — the original
jacob-bd/notebooklm-mcp-cli package, installed via `uv tool install`. Provides
a unified `notebooklm-mcp` binary (MCP server) and `nlm` CLI with **39 MCP tools**
and full Studio support.

**Migration note (12 Tem 2026):** The previous package `notebooklm-mcp v2.0.11`
(pip, fastmcp) was removed due to a critical bug: `_ensure_client()` started
the browser but never called `authenticate()`, so `_is_authenticated` remained
False and all tool calls failed with "Not authenticated or browser not ready".
The jacob-bd version handles auth correctly via the `nlm login` CDP flow.

| Aspect | Current (v0.8.6) | Retired (v2.0.11) |
|--------|-------------------|-------------------|
| Package | `notebooklm-mcp-cli` | `notebooklm-mcp` |
| Installer | `uv tool install` | `pip install` |
| Binary | `notebooklm-mcp` (PATH) | `/usr/local/bin/notebooklm-mcp` |
| CLI | `nlm` (full tooling) | `notebooklm-mcp test/init/server` only |
| Auth CLI | `nlm login --cdp-url` | `notebooklm-mcp init` |
| Auth check | `nlm login --check` / `nlm doctor` | `notebooklm-mcp test -n <id>` |
| Startup time | ~35s (initial) | ~30s |
| MCP tools | 39 | 39 |
| Auth bug | ✅ Works | ❌ `authenticate()` never called |

## Installation

```bash
# Install (or upgrade)
uv tool install notebooklm-mcp-cli --force

# What you get:
# - ~/.local/bin/notebooklm-mcp  (MCP server)
# - ~/.local/bin/nlm             (CLI tool)
```

**Do NOT use pip** — the pip version (`notebooklm-mcp v2.0.11`) is a
repackaged fork with the auth bug. Only the uv-installed package works.

### Register as Hermes MCP Server

```bash
hermes mcp remove notebooklm
# Note: server takes ~35s to start; use 120s timeout
hermes mcp add notebooklm \
  --command /home/ubuntu/.local/bin/notebooklm-mcp \
  --args "--transport stdio"
hermes config set mcp_servers.notebooklm.timeout 120
hermes config set mcp_servers.notebooklm.enabled true
```

Or use a wrapper script for env setup:
```bash
cat > ~/.hermes/scripts/start-notebooklm-mcp.sh << 'EOF'
#!/bin/bash
export PATH="$HOME/.local/bin:$HOME/.local/share/uv/tools/notebooklm-mcp-cli/bin:$PATH"
exec /home/ubuntu/.local/bin/notebooklm-mcp --transport stdio
EOF
chmod +x ~/.hermes/scripts/start-notebooklm-mcp.sh
hermes mcp add notebooklm --command ~/.hermes/scripts/start-notebooklm-mcp.sh
```

**Pitfall – startup timeout:** The MCP server takes ~35s to initialize
(loading dependencies, verifying auth). The default Hermes MCP test timeout
(40s) can be too tight. Use `timeout: 120` in the MCP config.

**Alternative – HTTP transport:** Start the server independently, then
add as HTTP MCP:
```bash
export PATH="$HOME/.local/bin:$HOME/.local/share/uv/tools/notebooklm-mcp-cli/bin:$PATH"
notebooklm-mcp --transport http --port 8001 --debug &
# After it starts (~35s):
hermes mcp add notebooklm --url http://127.0.0.1:8001/mcp
```

## Authentication

Auth is managed via `nlm login`, which uses CDP to extract cookies from a
running Chrome instance. The primary auth source is the **Keepalive Chrome**
(port 18800).

### First-Time Auth

```bash
# From keepalive Chrome (port 18800, already logged into NotebookLM):
nlm login --provider openclaw --cdp-url http://127.0.0.1:18800 --force
# Expected: "Successfully authenticated! Account: isimgorulsunn@gmail.com"
```

### Multi-Account Setup (Dual Chrome Architecture)

**Google cookies are domain-scoped.** A single Chrome instance can only hold one
Google account's cookies at a time. Using `?authuser=N` does NOT allow extracting
different accounts' cookies from the same Chrome. The solution is two separate
Chrome instances, each with its own `--user-data-dir` and CDP port:

| Instance | CDP Port | Profile Dir | Google Account | MCP Profile |
|----------|----------|-------------|---------------|-------------|
| Chrome 1 | 18800 | `chrome_profile_notebooklm` | `kenshin4155@gmail.com` | `pro` |
| Chrome 2 | 18801 | `chrome_profile_notebooklm_legacy` | `isimgorulsunn@gmail.com` | `legacy` |

**Setup (one-time):**
```bash
# Start both Chrome instances:
bash ~/.hermes/scripts/start-chrome-keepalive.sh          # port 18800 (pro)
bash ~/.hermes/scripts/start-chrome-keepalive-legacy.sh   # port 18801 (legacy)
```
Then login to each via VNC (`http://localhost:6080/vnc.html`).

**Auth each profile from its dedicated Chrome:**
```bash
# Pro (kenshin4155) — from Chrome on port 18800:
nlm login --provider openclaw --cdp-url http://127.0.0.1:18800 --profile pro --force

# Legacy (isimgorulsunn) — from Chrome on port 18801:
nlm login --provider openclaw --cdp-url http://127.0.0.1:18801 --profile legacy --force
```

**Set default profile:**
```bash
nlm config set auth.default_profile pro
```

**Check:**
```bash
nlm login --check                      # checks default profile
nlm login --check --profile pro        # specific profile
nlm login --check --profile legacy
```

**Dual MCP Server Setup (Hermes):** The MCP server reads `auth.default_profile` from
`nlm config` at startup. To have both profiles available simultaneously, register
TWO separate MCP servers — each pinned to a different profile via its wrapper script:

```bash
# Start script: ~/.hermes/scripts/start-notebooklm-mcp-pro.sh
#!/bin/bash
export PATH="$HOME/.local/bin:$HOME/.local/share/uv/tools/notebooklm-mcp-cli/bin:$PATH"
nlm config set auth.default_profile pro --quiet 2>/dev/null
exec /home/ubuntu/.local/bin/notebooklm-mcp --transport stdio

# Start script: ~/.hermes/scripts/start-notebooklm-mcp-legacy.sh
#!/bin/bash
export PATH="$HOME/.local/bin:$HOME/.local/share/uv/tools/notebooklm-mcp-cli/bin:$PATH"
nlm config set auth.default_profile legacy --quiet 2>/dev/null
exec /home/ubuntu/.local/bin/notebooklm-mcp --transport stdio
```

Register both in Hermes:
```bash
hermes config set mcp_servers.notebooklm.command /home/ubuntu/.hermes/scripts/start-notebooklm-mcp-pro.sh
hermes config set mcp_servers.notebooklm.enabled true
hermes config set mcp_servers.notebooklm_legacy.command /home/ubuntu/.hermes/scripts/start-notebooklm-mcp-legacy.sh
hermes config set mcp_servers.notebooklm_legacy.enabled true
```

Result: `mcp_notebooklm_*` tools use `kenshin4155` (pro),
`mcp_notebooklm_legacy_*` tools use `isimgorulsunn` (legacy).
No profile switching needed — both are available simultaneously.

**Pitfall — `nlm config set` is global:** The `nlm config set auth.default_profile` call
in the wrapper script mutates the shared `config.toml`. This is safe because each MCP
server reads config only at startup, and the servers start sequentially. For HTTP
transport servers started simultaneously, use separate config files instead.

For architecture details, see `references/dual-chrome-architecture.md`.

### Auth Verification

```bash
nlm login --check
# ✓ Authentication valid!
#   Notebooks found: 42
#   Account: isimgorulsunn@gmail.com

nlm doctor
# Shows: cookies present, CSRF token, account, profiles
```

### Keepalive-MCP Bridge (Auto-Refresh)

Every 20 minutes, `nb_keepalive.py` v5.0 runs and syncs cookies from **both**
keepalive Chrome instances to their respective MCP profiles:

- Port 18800 → extracts cookies → syncs to MCP `pro` profile (kenshin4155)
- Port 18801 → extracts cookies → syncs to MCP `legacy` profile (isimgorulsunn)

Each port is handled independently — if one Chrome is down, the other continues.
This ensures MCP auth stays valid without manual intervention.

### ⚠️ Keepalive Chrome Profile Lock

Keepalive Chrome (port 18800) and any new Chrome instance cannot share the
same `--user-data-dir` simultaneously. However, the MCP server's auth is now
**independent** — it uses `~/.notebooklm-mcp-cli/profiles/*/cookies.json`,
not the Chrome profile directly. So both can run concurrently.

### ✅ Multi-Account Cookie Sync — Dual Chrome (FIXED 13 Tem 2026)

**Old problem (12 Tem):** With a single Chrome, `nlm login` extracted cookies for
the active account only and overwrote all MCP profiles.

**Fix (13 Tem): Dual Chrome Architecture.** Each Google account has its own
Chrome instance with separate `--user-data-dir` and CDP port:
- Port 18800 (`chrome_profile_notebooklm`) → MCP `pro` (kenshin4155)
- Port 18801 (`chrome_profile_notebooklm_legacy`) → MCP `legacy` (isimgorulsunn)

`nb_keepalive.py` v5.0 extracts cookies from each port independently and syncs to
the correct MCP profile. No more cross-account overwriting.

**If keepalive Chrome dies (restart scenario):**
1. VNC access lost temporarily → login via `http://localhost:6080/vnc.html`
2. MCP auth is NOT affected (cookie files remain valid ~24h)
3. `nb_keepalive.py` cron restarts both Chromes within 20 minutes
4. On next cron tick, cookies are extracted from each port independently

## CLI Reference (nlm)

```bash
nlm --help                # Top-level help
nlm login --help          # Auth options
nlm notebook list         # List all notebooks
nlm notebook get <id>     # Notebook details
nlm source add <nb> --url <url>  # Add source
nlm studio create <nb>    # Generate artifact (audio, video, slides, etc.)
nlm download artifact <id> # Download artifact
nlm doctor                # Full diagnostic
nlm config show           # Current config
nlm login --check         # Auth status
```

### MCP Server CLI

```bash
notebooklm-mcp --help
# Options: --transport stdio|http|sse, --host, --port, --path
#           --stateless, --debug, --query-timeout

# Start MCP server (stdio is default):
notebooklm-mcp --transport stdio

# HTTP mode:
notebooklm-mcp --transport http --port 8001
```

## Profile Storage

```bash
~/.notebooklm-mcp-cli/
├── config.toml                       # CLI config (auth.default_profile, output format)
├── profiles/
│   ├── legacy/                       # isimgorulsunn@gmail.com
│   │   ├── cookies.json              # Cookie list (JSON array)
│   │   └── metadata.json
│   ├── pro/                          # kenshin4155@gmail.com
│   │   ├── cookies.json
│   │   └── metadata.json
│   └── default/                      # Fallback profile
│       ├── cookies.json
│       └── metadata.json
```

**Default profile:** controlled by `auth.default_profile` in `config.toml`.
Set via: `nlm config set auth.default_profile pro`

## Hosted MCP Server

For persistent operation, run the MCP server as a background HTTP service:

```bash
export PATH="$HOME/.local/bin:$HOME/.local/share/uv/tools/notebooklm-mcp-cli/bin:$PATH"
notebooklm-mcp --transport http --port 8001 --debug &
# Check health:
curl http://127.0.0.1:8001/health
# → {"status":"healthy","service":"notebooklm-mcp","version":"0.8.6"}
```

## `nlm` Binary Note (12 Tem 2026)

The system previously had `nlm` as a symlink to a Node.js lifecycle manager
(groupon/nlm). This is no longer relevant. The current `nlm` is the actual
NotebookLM CLI tool from the `notebooklm-mcp-cli` package, installed via uv:

```bash
$ which nlm
~/.local/bin/nlm
$ nlm --version
# (shows notebooklm-mcp-cli version)
```

## Keepalive System (Dual Chrome)

| Cron Job | Schedule | Script | Purpose |
|----------|----------|--------|---------|
| `nb_keepalive_2h` | `*/20 * * * *` | `nb_keepalive.py` (v5.0) | Dual Chrome CDP keepalive + MCP auth sync |

### Keepalive Architecture

Two Chrome instances run on separate ports, each dedicated to one Google account:

| Chrome | Port | User-Data-Dir | Account → MCP Profile |
|--------|------|---------------|----------------------|
| Primary | 18800 | `chrome_profile_notebooklm` | kenshin4155 → `pro` |
| Legacy | 18801 | `chrome_profile_notebooklm_legacy` | isimgorulsunn → `legacy` |

### Keepalive Flow (per Chrome, every 20 min)

1. Check Chrome CDP is alive on its port; restart if dead
2. Extract cookies via CDP (direct WebSocket, with 502 retry)
3. Sync to correct MCP profile (`nlm login --cdp-url http://127.0.0.1:<PORT>`)
4. On CDP failure: try autologin with retry
5. On 3x autologin failure: Telegram SOS alert for that profile only

## Studio Artifact Generation Times

| Artifact Type | Typical Time |
|---------------|-------------|
| Quiz (2-5 questions) | ~30-60s |
| Flashcards | ~30-90s |
| Report | ~30-60s |
| Mind Map | ~20-40s |
| Infographic | ~30-60s |
| Slide Deck (short) | ~45-120s |
| Audio Overview | ~2-5 min |
| Video Overview | ~3-8 min |

## Troubleshooting

### MCP server won't connect (timeout)
The server takes ~35s to start. Ensure `timeout: 120` in Hermes config.
Test directly: `notebooklm-mcp --transport http --port 8001 &`

### Auth valid but MCP says "Not authenticated"
Old session cached. Use `/reload-mcp` or start a new Hermes session.

### "nlm: command not found"
The nlm binary is in `~/.local/bin/` which must be in PATH.
Or use full path: `~/.local/share/uv/tools/notebooklm-mcp-cli/bin/nlm`

### Keepalive Chrome stops working
The cron job (`nb_keepalive_2h`) auto-restarts it within 20 minutes.
For immediate recovery: `python3 ~/.hermes/scripts/nb_keepalive.py`

### CookieMismatch after container restart
Even with valid cookies, Google may reject them after a container restart
(different Chrome fingerprint). Solution:
1. Run `nb_keepalive.py` to refresh cookies from the restarted Chrome
2. If still fails: VNC login at `http://localhost:6080/vnc.html`
3. Re-sync: `nlm login --provider openclaw --cdp-url http://127.0.0.1:18800 --force`

## Migration from v2.0.11 (pip → uv)

If migrating from the old pip package:
```bash
# 1. Remove old package
pip3 uninstall notebooklm-mcp -y
rm -f /usr/local/bin/notebooklm-mcp /home/ubuntu/.local/bin/notebooklm-mcp

# 2. Install new package
uv tool install notebooklm-mcp-cli --force

# 3. Authenticate
nlm login --provider openclaw --cdp-url http://127.0.0.1:18800 --force

# 4. Re-register in Hermes
hermes mcp remove notebooklm
hermes mcp add notebooklm --command /home/ubuntu/.local/bin/notebooklm-mcp --args "--transport stdio"
hermes config set mcp_servers.notebooklm.timeout 120
hermes config set mcp_servers.notebooklm.enabled true

# 5. Remove the authfix wrapper if used
rm -f ~/.hermes/scripts/notebooklm_mcp_authfix.py
```

## Related Skills

- `notebooklm-pipeline` (media) — Pipeline workflows (YouTube → NBLM → podcast)
- `notebooklm-cdp-recovery` (mcp) — Deep CDP auth recovery procedures
- `notebooklm-studio` (media) — Studio artifact generation details
