# Dual Chrome Architecture for Multi-Account NotebookLM

**Date:** 13 Temmuz 2026
**Status:** Active (replaces single-Chrome multi-account approach)

## Problem

Google cookies are **domain-scoped**. A single Chrome instance can only hold
one Google account's session cookies at a time. Using `?authuser=N` URL parameter
to switch between accounts does NOT change which cookies are stored — Chrome
maintains one set of cookies per domain regardless of how many tabs are open.

This means a single keepalive Chrome cannot serve two MCP profiles reliably.
When `nlm login --cdp-url` extracts cookies, it gets the **currently active
account's** cookies and writes them to ALL profiles.

## Solution: Dual Chrome

Each Google account gets its own dedicated Chrome process with:
- Separate `--user-data-dir` (isolates cookies, localStorage, session state)
- Separate CDP port (allows independent WebSocket access)
- Separate startup script

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Container                      │
│                                                          │
│  Chrome 1 (port 18800)           Chrome 2 (port 18801)  │
│  ┌─────────────────────┐         ┌─────────────────────┐│
│  │ --user-data-dir:    │         │ --user-data-dir:    ││
│  │  chrome_profile_    │         │  chrome_profile_    ││
│  │  notebooklm         │         │  notebooklm_legacy  ││
│  │                      │         │                      ││
│  │ Account:             │         │ Account:             ││
│  │ kenshin4155@gmail    │         │ isimgorulsunn@gmail  ││
│  └─────────┬───────────┘         └──────────┬──────────┘│
│            │ CDP                             │ CDP        │
│            ▼                                 ▼            │
│  nlm login --cdp-url             nlm login --cdp-url      │
│  http://127.0.0.1:18800          http://127.0.0.1:18801   │
│  --profile pro --force           --profile legacy --force │
│            │                                 │            │
│            ▼                                 ▼            │
│  ~/.notebooklm-mcp-cli/         ~/.notebooklm-mcp-cli/    │
│  profiles/pro/cookies.json      profiles/legacy/cookies.json│
└─────────────────────────────────────────────────────────┘
```

## Configuration Mapping

| Chrome | Port | User-Data-Dir | Start Script | MCP Profile | Account |
|--------|------|---------------|-------------|-------------|---------|
| Primary | 18800 | `/home/ubuntu/.hermes/chrome_profile_notebooklm` | `start-chrome-keepalive.sh` | `pro` | kenshin4155 |
| Legacy | 18801 | `/home/ubuntu/.hermes/chrome_profile_notebooklm_legacy` | `start-chrome-keepalive-legacy.sh` | `legacy` | isimgorulsunn |

## Key Files

| File | Purpose |
|------|---------|
| `~/.hermes/scripts/nb_keepalive.py` (v5.0) | Dual Chrome keepalive + cookie sync |
| `~/.hermes/scripts/start-chrome-keepalive.sh` | Launch Chrome 1 (port 18800, pro) |
| `~/.hermes/scripts/start-chrome-keepalive-legacy.sh` | Launch Chrome 2 (port 18801, legacy) |
| `~/.hermes/scripts/start-notebooklm-mcp-pro.sh` | MCP server wrapper — pins `pro` profile before start |
| `~/.hermes/scripts/start-notebooklm-mcp-legacy.sh` | MCP server wrapper — pins `legacy` profile before start |

## MCP Server Side (Hermes Integration)

Each MCP server reads `auth.default_profile` from `nlm config` at startup.
To have both profiles available simultaneously, register two separate servers
via `hermes config set`:

- `mcp_servers.notebooklm` → starts via `start-notebooklm-mcp-pro.sh` → `mcp_notebooklm_*` tools use kenshin4155
- `mcp_servers.notebooklm_legacy` → starts via `start-notebooklm-mcp-legacy.sh` → `mcp_notebooklm_legacy_*` tools use isimgorulsunn

Each wrapper script calls `nlm config set auth.default_profile <name> --quiet`
before exec-ing the MCP server. Since the config is read once at startup,
concurrent servers don't interfere.

**Tool naming convention:**
- `mcp_notebooklm_notebook_list` → kenshin4155 (pro, 44 notebooks)
- `mcp_notebooklm_legacy_notebook_list` → isimgorulsunn (legacy, 42 notebooks)

## nb_keepalive.py v5.0 Logic

The `CDP_INSTANCES` dict defines the mapping. For each instance:

1. **Check health:** `curl http://127.0.0.1:<port>/json/version`
2. **Restart if dead:** Run the instance's `start_script`
3. **Extract cookies:** Connect via WebSocket to CDP, navigate to notebooklm.google.com, call `Network.getCookies`
4. **Verify auth:** httpx test → ensure not redirected to accounts.google.com
5. **Write to MCP profile:** Save cookies to `~/.notebooklm-mcp-cli/profiles/<mcp_profile>/cookies.json`
6. **nlm login sync:** `nlm login --cdp-url http://127.0.0.1:<port> --profile <mcp_profile> --force`
7. **On failure:** Try autologin → 3x failure → Telegram SOS

Each instance is handled independently — if one Chrome is down, the other continues.

## Switching Between Profiles

The default MCP profile is set via:
```bash
nlm config set auth.default_profile pro
```

To use a specific profile for a single operation:
```bash
nlm --profile legacy notebook list
```

## Troubleshooting

### Chrome won't start on port 18801
Check that Xvfb is running: `ps aux | grep Xvfb`
Both Chrome instances share the same DISPLAY=:99.

### "SingletonLock" error on second Chrome
Different `--user-data-dir` values prevent this. If it occurs, remove stale lock files:
```bash
rm -f /home/ubuntu/.hermes/chrome_profile_notebooklm_legacy/Singleton*
```

### One Chrome dies but the other survives
`nb_keepalive.py` handles each independently. A dead Chrome gets restarted by its
own `start_script`. The healthy Chrome continues unaffected.
