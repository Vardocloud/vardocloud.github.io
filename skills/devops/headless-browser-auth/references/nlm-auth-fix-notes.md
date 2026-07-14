# NLM Auth Fix — 8 Haziran 2026

## Initial Problem

NotebookLM MCP reported `auth_status: "stale"`. Studio operations (slide_deck, audio, report) blocked.

## Root Causes

### 1. Snap Chromium incompatibility
Snap `chromium-browser` has disconnected X11 interface → Xvfb/Xauthority errors.
**Fix:** Playwright standalone Chromium with `--headless=new`. No X server needed.

### 2. MCP "stale" IS often real expiry
Initial assumption: "stale is just a 7-day heuristic, operations work fine."
✅ **Read ops** (list, query, source_add) work fine.
❌ **Write ops** (studio_create, report create) may still fail with "expired" / PERMISSION_DENIED.
**Cause:** NotebookLM read & write tokens have different lifetimes. Write token expires faster.

### 3. WebSocket CDP 403 (Chrome 148+)
`--remote-allow-origins=*` Chrome flag is INSUFFICIENT for WebSocket connections.
**Fix:** Skip CDP entirely, use `nlm login --manual -f cookies.json`.

## What Worked

- `nlm login --cdp-url` (Playwright Chrome) → 61 cookies (read ops work)
- `nlm login --manual -f cookies.json` → 47 cookies (works for write if cookies are fresh)
- **But:** Even after --manual import, write ops may still fail if cookies are truly expired
- `nlm login --check` → "Authentication valid" (read-only test, not write!)

## What Still Blocked (as of 8 June 2026)

- `studio_create` (slide_deck, audio, video, report) → "expired"
- `nlm report create` → PERMISSION_DENIED (code 7)
- **Workaround:** Read-only query + HTML browser screenshot for visual content
- **Permanent fix needs:** Fresh cookie export from user's desktop browser

## Final State

- Account: isimgorulsunn@gmail.com
- Cookies: Last imported 8 June 2026, status unknown (read works, write blocked)
- Auto-refresh: Cron job every 12 hours (attempts --cdp-url, falls back to alert)
- Refresh method: Headless Playwright Chrome + `nlm login --cdp-url`
- **Verification:** `nlm report create --confirm -y` before trusting auth status
