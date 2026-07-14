# Container Restart → CookieMismatch (12 Tem 2026)

## Scenario

Hermes container was restarted (WSL Docker). After restart:
- All services came up fine (gateway, voice, proxy, cron)
- Keepalive Chrome resumed on port 18800
- nb_keepalive.py refreshed cookies via CDP
- But notebooklm-mcp MCP server still returned needs_auth

## Root Cause

Google accounts.google.com/CookieMismatch. Chrome fingerprint (PID, session DB, process tree) changed after restart. Google treated the same cookies from a "different" browser as invalid.

## Diagnostic Timeline

```
13:19 — Gateway restart (config fix)
13:21 — MCP healthcheck: needs_auth
13:25 — nb_keepalive.py: "CDP cookie extraction succeeded"
13:26 — MCP healthcheck: still needs_auth
13:29 — nb_keepalive.py: "Refresh cookies via CDP" (forced)
13:29 — MCP healthcheck: still needs_auth
13:31 — Killed keepalive Chrome (PID 113) — profile lock conflict hypothesis
13:31 — MCP server restarted in GUI mode (no --headless)
13:41 — MCP server log: "NotebookLM client initialized and authenticated"
13:41 — MCP healthcheck: still "needs_auth" (DISCREPANCY CONFIRMED)
13:43 — navigate_to_notebook: SUCCESS
13:43 — set_default_notebook: SUCCESS
13:44 — chat_with_notebook: "Not authenticated or browser not ready"
13:49 — notebooklm-mcp test -n <id>: "CookieMismatch" CONFIRMED
14:00 — Keepalive restart (cdp_extract_both → httpx OK)
14:02 — storage_state.json manually synced from CLI cookies
14:02 — httpx test: Status=200, NotebookLM accessible
14:04 — MCP chat: still "Not authenticated or browser not ready"
14:06 — notebooklm-mcp init --headless: still CookieMismatch
```

## Key Findings

| Finding | Detail |
|---------|--------|
| healthcheck unreliable | Returns needs_auth when server is actually authenticated and can navigate |
| Navigation ≠ Chat | navigate_to_notebook works (auth passes) but chat fails (driver not ready) |
| Cookie count is a red herring | "Loaded 23 cookies from storage_state" doesn't mean valid; Google still shows CookieMismatch |
| Keepalive kill didn't fix auth | Killing PID 113 removed profile lock but cookies were already stale from restart |
| Manual re-login required | After container restart, there is NO automated fix path — only VNC/CLI re-auth works |

## Cookie Source Divergence (CRITICAL FINDING 12 Tem)

**The keepalive's `cdp_extract_both.py` saves cookies to CLI profiles, NOT to the MCP server's storage_state.** These are two completely different directory trees:

| Store | Path | Updated by |
|-------|------|-----------|
| **MCP server storage_state** | `~/.notebooklm/profiles/default/storage_state.json` | NotebookLM client init |
| **CLI/keepalive cookies** | `~/.notebooklm-mcp-cli/profiles/{legacy,pro}/cookies.json` | `cdp_extract_both.py` (20min cron) |

Even though both contain 23 cookies with the same SID, the MCP server reads from `storage_state.json` while the keepalive writes to the CLI profiles. These are NOT automatically synced.

**Fix applied:** Manual cookie conversion script:
```python
# Read from CLI, convert to storage_state format, write
fresh = json.load(open('~/.notebooklm-mcp-cli/profiles/legacy/cookies.json'))
storage = {'cookies': []}
for c in fresh:
    storage['cookies'].append({
        'name': c['name'], 'value': c['value'],
        'domain': c['domain'], 'path': c.get('path', '/'),
        'expires': c.get('expires', time.time() + 86400),
        'httpOnly': c.get('httpOnly', False),
        'secure': c.get('secure', True),
        'sameSite': c.get('sameSite', 'Lax'),
    })
json.dump(storage, open('storage_state.json', 'w'))  # overwrite
```

**Result after sync:** httpx test passes (Status=200, NotebookLM accessible) but Selenium/undetected_chromedriver still rejects cookies. See Selenium add_cookie limitation below.

## httpx Diagnostic Confirmation

The cookies in storage_state.json are **objectively valid** — they authenticate against NotebookLM via plain HTTP requests:

```python
import httpx, json
cookies = {c['name']: c['value'] for c in storage['cookies']}
r = httpx.get('https://notebooklm.google.com/notebook/<id>',
    cookies=cookies, follow_redirects=True, timeout=10)
# → Status=200, final URL=notebooklm.google.com ✅
```

But the SAME cookies injected via Selenium `add_cookie()` fail:
```
Loaded 23 cookies from storage_state
Current URL after navigation: accounts.google.com/CookieMismatch
```

**Implication:** The cookies are NOT expired. The problem is how undetected_chromedriver injects them into Chrome's runtime, not the cookies themselves.

## Selenium add_cookie Domain Limitation

The MCP server's `_load_cookies` does:
```python
self.driver.get('https://notebooklm.google.com')  # redirects to CookieMismatch
for cookie in data.get('cookies', []):
    try:
        self.driver.add_cookie(cookie)  # fails silently for wrong domain
    except Exception:
        continue
```

**Why it fails:** After the initial `driver.get()` redirects to `accounts.google.com/CookieMismatch`, `add_cookie()` can only set cookies for `accounts.google.com`. Cookies for `notebooklm.google.com` domain (like `__Secure-OSID`) are rejected with "invalid cookie domain" and silently skipped.

**CDP `Network.setCookies` would bypass this** because it sets cookies directly at the CDP level without domain restrictions. This is the path forward if manual re-login isn't viable.

## What DIDN'T Work

- Killing keepalive Chrome to free profile lock
- Running nb_keepalive.py manually multiple times
- Updating chrome-port-map.json to point to 18800
- Switching between headless and GUI modes
- Multiple gateway restarts
- Manual storage_state.json sync from CLI cookies

## What WOULD Fix It

- **VNC manual login** → notebooklm.google.com → re-login (tested working pattern)
- **notebooklm-mcp init <notebook_url>** (CLI browser auth flow)
- **CDP Network.setCookies injection** into MCP's Chrome runtime (bypasses add_cookie domain limit)
- **Drop headless mode and connect MCP to keepalive Chrome** via CDP port (hypothetical — not tested, MCP server doesn't support this natively)
