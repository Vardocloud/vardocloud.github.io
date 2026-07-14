# Legacy MCP: PleasePrompto/notebooklm-mcp v2.0.0 (RETIRED)

**Retired:** 10 Temmuz 2026
**Replaced by:** jacob-bd/notebooklm-mcp-cli v0.8.1

## Why Retired
- Limited to 20 tools — only Audio Overview for Studio content
- Node.js/Playwright — bundled Chromium cookie encryption mismatch with system Chromium
- Required custom patches (executablePath, selector fixes)
- No CLI for script/no-agent use

## Last Working Config
- **Package:** `notebooklm-mcp` (npm)
- **Binary:** `/home/ubuntu/.npm-global/bin/notebooklm-mcp`
- **Chrome Profile:** `~/.local/share/notebooklm-mcp/chrome_profile`
- **Config:** `~/.config/notebooklm-mcp/`
- **Library:** `~/.local/share/notebooklm-mcp/library.json`

## What to Do If Referenced
If an old session or cron references this MCP:
1. Symlink at `~/.local/bin/notebooklm-mcp` should point to `/usr/local/bin/notebooklm-mcp` (new)
2. Old npm binary can be uninstalled: `npm uninstall -g notebooklm-mcp`
3. Old chrome profile can be deleted: `rm -rf ~/.local/share/notebooklm-mcp/`
4. Old config: `rm -rf ~/.config/notebooklm-mcp/`

Do NOT delete keepalive Chrome profile at `~/.hermes/chrome_profile_notebooklm/` — keepalive still needs it.
