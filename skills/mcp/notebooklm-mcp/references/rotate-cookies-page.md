# RotateCookiesPage — Detection & Handling

Google serves `accounts.google.com/RotateCookiesPage` when it systematically
refreshes cookie signing keys across all sessions tied to an account. Unlike
`CookieMismatch` (one Chrome instance vs another), this affects ALL Chrome
instances simultaneously — including the one that generated the cookies.

## Detection

```bash
# Scan all Chrome CDP ports for RotateCookiesPage
for port in $(ps aux | grep "chromium.*remote-debugging-port" | \
  grep -v grep | sed 's/.*--remote-debugging-port=\([0-9]*\).*/\1/' | sort -u); do
  url=$(curl -s http://127.0.0.1:$port/json 2>/dev/null | \
    python3 -c "import sys,json; tabs=json.load(sys.stdin); \
    [print(t.get('url','')[:120]) for t in tabs[:3]]" 2>/dev/null)
  echo "Port $port: $url"
done
```

**Key indicator:** ALL Chrome instances with NotebookLM show `RotateCookiesPage`
in their URL as the **main page** (type `[page]`), not just as an iframe. If it's
only an iframe on some instances while the main page still shows NotebookLM,
the session is still functional — see Resolution Path step 1.

## What It Means

Google is performing a server-side key rotation on the session cookies.
During rotation:
- The old cookies become temporarily invalid
- The new cookies haven't been issued yet
- The page shows `RotateCookiesPage?og_pid=666&rot=N&origin=...`

This is Google's session hardening — it periodically rotates the encryption
keys bound to cookies. Headless/automated browser sessions are especially
vulnerable because the rotation may never complete without real user interaction.

## Why It's Different From CookieMismatch

| Aspect | CookieMismatch | RotateCookiesPage |
|--------|---------------|-------------------|
| Scope | 1 instance (new fingerprint) | ALL instances simultaneously |
| Cause | Chrome restart, profile copy | Server-side key rotation |
| Self-healing | No — manual login required | Sometimes resolves in 30-60s |
| CDP injection | Works (inject fresh cookies) | Won't help (server-side reject) |
| httpx test | Status 200 with cookie | Status 302 → accounts.google |

## Resolution Path

1. **Check if RotateCookiesPage is an iframe or the main page** — Query each Chrome CDP port (`/json` endpoint) and inspect tab TYPES:
   - `[iframe]` RotateCookiesPage + `[page]` NotebookLM → main session is still functional. Extract cookies directly.
   - `[page]` RotateCookiesPage → session truly blocked.

2. **If iframe-only: extract cookies immediately** — The Chrome still has a valid session. Use `Network.getAllCookies` CDP call and save to MCP profiles at `~/.notebooklm-mcp-cli/profiles/*/cookies.json`.

3. **If main page is RotateCookiesPage: Wait 30-60s** — Sometimes rotation completes and auto-redirects.

4. **If it persists >60s** → Manual re-login required.

5. **After re-login** → Restart via gateway restart:
   ```bash
   python3 ~/.hermes/scripts/nb_keepalive.py
   docker restart vanatis-hermes
   ```

## Observed Instance (12 Tem 2026, 14:00 UTC+3)

All 3 Chrome instances on NotebookLM affected, but with different severity:

| Port | Main Tab | Iframe | Session Status |
|------|----------|--------|---------------|
| 18800 (keepalive original) | `accounts.google.com/challenge/selection` (Too many failed attempts) | none | ❌ Broken |
| 49537 (undetected_chromedriver) | `notebooklm.google.com/notebook/<id>` | RotateCookiesPage | ✅ **Functional** (49 msgs, working input) |
| 52065 (undetected_chromedriver) | `notebooklm.google.com/notebook/<id>` | RotateCookiesPage | ✅ **Functional** |

**Key insight:** Port 18800 was broken (too many failed login attempts looping on account chooser), but ports 49537 and 52065 still had a **working NotebookLM session** with RotateCookiesPage only as an iframe. 43 valid cookies were extracted from port 52065, containing 30 auth-relevant Google cookies.

Plus one idle Chrome (port 34809) on `chrome://newtab/` — unaffected.

The MCP server (PID 30910) showed `needs_auth` and `navigate_to_notebook` failed
with `Remote end closed without connection` because its undetected_chromedriver
child had crashed. The Chrome it spawned (port 52065) was alive but on
RotateCookiesPage, and the MCP server had no CDP connection to it anymore.

**Pattern:** The MCP server's undetected_chromedriver starts Chrome, but when
RotateCookiesPage blocks notebook loading, the driver may time out and crash.
The Chrome process survives but loses its CDP parent.
