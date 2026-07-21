---
name: headless-browser-auth
description: "Headless browser cookie authentication for services without API auth — Playwright Chromium CDP, cookie import/refresh, auto-refresh cron jobs."
category: devops
triggers:
  - notebooklm auth expired
  - cookie auth stale
  - nlm login failed
  - headless chrome cdp setup
  - cookie refresh cron
  - VNC tunnel manual auth
  - x11vnc noVNC setup
  - Google passkey block
  - ssh tunnel url capture
---

# Headless Browser Cookie Auth

For services that **only support browser-based authentication** (NotebookLM, some internal tools, Google Workspace add-ons), use headless Playwright Chromium with CDP for automated cookie refresh.

## 0. Camofox Managed Persistence (Hermes Native — Simplest)

**For services accessed within Hermes browser (gemini.google.com, etc.), use Camofox managed_persistence instead of external Playwright/CDP.** This is the native Hermes solution:

```bash
hermes config set browser.camofox.managed_persistence true
hermes config set browser.engine camofox
```

**Why this works:** Camofox (Firefox fork) saves cookies/logins/session state to a persistent profile directory. Login ONCE → session survives across page reloads and Hermes restarts. 

**⚠️ CRITICAL — Session persistence across tool calls (21 Jul 2026):** Camofox `managed_persistence` preserves the session on disk, but **Hermes `browser_*` tool calls may spawn fresh Camofox instances** that don't share the same in-memory state. In practice, `browser_navigate` → login → `browser_snapshot` (same page) works within a single continuous flow, but after the next `browser_navigate` to a different URL, the session can go blank. **Do NOT open new tabs or navigate away during the auth flow** — complete login in one sequence. If the session goes blank between tool calls, the Camofox instance may have been recycled. Re-navigate to the target URL — if cookies are on disk, the session *may* still be alive.

**Why headless Chrome doesn't work for Google:** Google classifies headless Chrome as an untrusted device and refuses to persist session cookies, even after successful 2FA (confirmed 3 Jul 2026, reconfirmed 21 Jul 2026 with Chromium 149). The `--disable-blink-features=AutomationControlled` flag does NOT bypass Google's sign-in detection — the "Couldn't sign you in" block fires at the email entry stage before any credentials are checked. Camofox (Firefox fork) avoids this detection because it presents as a regular Firefox browser.

**2FA flow with Camofox (Gemini login — 21 Jul 2026):** 
- SMS: Shows "Unavailable on this device" in Camofox — can't use it.
- Authenticator: 30-second timeout too tight for browser-based typing — can't keep up.
- **Tap Yes is the best option:** Push notification with 2-digit number match (e.g., 86, 93). Phone displays 3 numbers; user taps the matching one.

**⚠️ Session persistence after Tap Yes (CRITICAL):** After user approves on phone, the browser page must complete the redirect naturally. Do NOT `browser_navigate` to a new URL — this kills the pending session and you'll see "Sign in" again. Instead, after the user confirms approval, use `browser_snapshot` on the SAME page to verify the redirect completed. Once on gemini.google.com/app with the sidebar visible (showing account name + "Pro" badge), the session is locked in — Camofox managed_persistence saves it to disk.

## Pattern Selection Decision Tree

| Scenario | Use |
|----------|-----|
| Gemini / Google services via Hermes browser | **Camofox managed_persistence** (this section) |
| NotebookLM MCP server auth | Pattern A/B/C (CDP + cookie import) |
| Manual intervention needed (CAPTCHA, passkey) | Pattern F (VNC fallback) |

## Core Pattern (Legacy — Playwright/CDP)

1. Start headless Chrome with CDP (no X server needed)
2. Connect auth CLI via CDP (`nlm login --cdp-url`)
3. Import cookies to service's credential store
4. Set up periodic cron refresh (every 12h)

## Playwright Chromium (No Xvfb)

The snap `chromium-browser` has X11/Xauthority issues on headless servers. **Use Playwright's standalone Chromium instead:**

```bash
# Find the binary
find ~/.cache/ms-playwright -name "chrome" -path "*/chrome-linux/*"
# Typical path: ~/.cache/ms-playwright/chromium-1223/chrome-linux/chrome
```

### Start Headless Chrome with CDP

```bash
CHROME=~/.cache/ms-playwright/chromium-1223/chrome-linux/chrome
$CHROME --headless=new --no-sandbox --disable-gpu \
  --disable-dev-shm-usage --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-profile --no-first-run \
  --disable-default-apps about:blank
```

Key flags:
- `--headless=new`: No X server needed
- `--remote-debugging-port=9222`: CDP endpoint
- `--user-data-dir`: Persistent profile for cookies
- **No DISPLAY, no XAUTHORITY, no Xvfb required**

## Cookie Auth Patterns

### Pattern A: nlm login with CDP

```bash
nlm login --cdp-url http://127.0.0.1:9222 --force
```

### Pattern B: Manual cookie import

Export cookies from a real browser as JSON, then:

```bash
nlm login --manual -f /path/to/cookies.json
```

Update auth.json with CSRF token and session ID from metadata.

### Pattern C: Full refresh script

In `refresh_cookies.py`:
1. `nlm login --check` → if valid, update auth.json and exit
2. If expired → start headless Chrome → `nlm login --cdp-url` → update auth.json
3. If all fails → alert for manual intervention

### Pattern E: Cloudflare Tunnel for noVNC (alternative to SSH tunnels)

When SSH tunnels (Serveo, localhost.run) are unreliable or blocked, use Cloudflare Tunnel for temporary VNC access:

```bash
# Install cloudflared
curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
  -o /tmp/cloudflared && chmod +x /tmp/cloudflared

# Start tunnel (background with terminal tool)
/tmp/cloudflared tunnel --url http://localhost:6080
# → URL: https://<random-words>.trycloudflare.com
```

The trycloudflare.com URL is random and only valid while the tunnel runs. Combined with VNC password auth, it's reasonably secure for temporary sessions.

**Advantages over SSH tunnels:**
- No SSH key setup needed
- More reliable (direct Cloudflare connection, no intermediate SSH server)
- Faster URL generation (~5s vs 8-12s for SSH tunnels)
- Works from Hermes background processes (`terminal(background=true)`)

**Disadvantages:**
- No custom domain (random URL each time)
- Requires cloudflared binary (not pre-installed on most servers)

**When to use:** SSH tunnels fail, no SSH keys configured, or container has internet access but no SSH to public services.

### Pattern F: Cloudflare Bot Management bypass via cookie injection (Enterprise sites)

For sites behind **Enterprise-tier Cloudflare Bot Management** (Upwork, etc.), browser automation always fails on form submit. The only working bypass is cookie injection from a real browser session.

See `references/cloudflare-bot-mgmt-cookie-bypass.md` for:
- Complete Camoufox implementation (Node.js)
- SameSite normalization (required for Playwright)
- ARM64 compatibility notes
- Comparison table of all tested methods

```javascript
// Quick start: load cookies into Camoufox BEFORE navigation
const cookies = JSON.parse(fs.readFileSync('/tmp/cookies.json'));
await page.context().addCookies(cookies);
await page.goto('https://target-site.com');
```

### Pattern F: VNC Fallback for Manual Intervention (LAST RESORT)

When automated CDP methods fail (Google passkey, 2FA, anti-bot loops), set up a VNC tunnel so the user can complete auth manually in their own browser.

**Trigger conditions:** CDP rejected with passkey/security challenge, cookie import succeeds but write ops fail, session actively revoked.

**Stack:** Xvfb → Chrome (attached to display) → x11vnc (converts X display to VNC) → websockify + noVNC (VNC to WebSocket + web UI on single port via `--web .`) → SSH tunnel (Serveo/localhost.run)

**⚠️ x11vnc 0.9.17+ MIT-SHM bypass:** Use `-noshm` flag (not deprecated `-noxshm`). See `references/vnc-fallback-auth.md` for the exact startup command and explanation.

**Key insight — websockify `--web .`:** Serves both noVNC static files (HTTP) and WebSocket proxy on the same port. No separate HTTP server needed. Without this flag, websockify returns 405 for non-WebSocket requests.

**SSH tunnel URL capture (Hermes workaround):** Hermes `terminal(background=true)` shows empty output for SSH tunnels. Use Python `subprocess.Popen` with file output redirection instead, then read the URL after 8-12 seconds.

**Do not ask for passwords/tokens in conversation.

**CDP Bridge alternative (when x11vnc/websockify unavailable):** If the container restarted or VNC stack isn't installed, use a lightweight Python HTTP server that connects to Chrome CDP directly. The user submits their password through a simple web form → Python server types it into Chrome via `Input.insertText` → clicks Next. No Xvfb, no VNC, no websockify needed. See `references/cdp-password-bridge.md`.

**⚠️ CRITICAL — Headless Chrome gets rejected by Google (20 Haz 2026):** Even with `undetected-chromedriver`, WARP+ proxy, `--disable-blink-features=AutomationControlled`, and CDP anti-detection scripts, `--headless=new` Chrome ALWAYS gets "Couldn't sign you in" (signin/rejected) from Google. **Fix:** Start Chrome WITHOUT `--headless` on Xvfb display:
```bash
# 1. Start Xvfb
Xvfb :99 -screen 0 1920x1080x24 -ac &

# 2. Start Chrome without --headless on that display
export DISPLAY=:99
chromium --no-first-run --no-sandbox --test-type \
  --window-size=1920,1080 --start-maximized \
  --disable-blink-features=AutomationControlled \
  --remote-debugging-port=36241 --remote-allow-origins=* \
  --proxy-server=socks5://warp:1080 \
  https://notebooklm.google.com
```
This bypasses the "Couldn't sign you in" block because Google's detection scripts expect a visible window. With Xvfb, Chrome thinks it has a real display.

**Google auth flow (20 Haz 2026, passkey era):** After logging in from a non-headless Chrome, the flow is:
1. **Account chooser** — select `isimgorulsunn@gmail.com`
2. **Passkey challenge** — "Verifying it's you... Complete sign-in using your passkey"
3. **Click "Try another way"** — `document.querySelector('[role="button"]')` with text matching
4. **"Choose how you want to sign in"** — select "Enter your password" via XPath:
5. **Password page** — URL: `/challenge/pwd`

**"Too many failed attempts" variant (23 Haz 2026):** When Google detects repeated failed login attempts (e.g. from stale password tries), it shows a MORE aggressive passkey prompt at `/v3/signin/challenge/pk/presend`:
- H1: "Use your passkey to confirm it's really you"
- H2: "Too many failed attempts"
- Body text: "Your device will ask for your fingerprint, face, or screen lock"
- "Try another way" is still available but the threshold for passkey is lower
- **Solution:** Either (a) user approves passkey on phone, or (b) click "Try another way" → "Enter your password" → supply correct password in one shot

**"Tap Yes on your phone" shortcut (23 Haz 2026):** After successfully entering the password (not before), Google shows a 2-Step Verification page with multiple options if 2FA is enabled. The simplest option is **"Tap Yes on your phone or tablet"** — it sends a notification to the user's phone. The user can:
1. Click "Tap Yes on your phone or tablet" (JS: `document.querySelector('[role="link"]')` matching text)
2. Wait for the push notification on their phone
3. Approve → login completes automatically

This avoids needing SMS codes, authenticator app codes, or backup codes. The user's phone must be connected to the internet and have Google Play Services with the Google account signed in.

**Compare numbers detail (3 Tem 2026):** The "Tap Yes" page shows a `figure` element containing `StaticText` with a number (e.g., `"82"`, `"96"`, `"86"`). The user's phone displays 3 different numbers. They tap the one matching the browser's number. This number is randomly generated per session.

**⚠️ Headless limitation (3 Tem 2026):** Even after successful phone approval via compare-numbers, **headless Chrome does NOT persist the session**. Google classifies headless browsers as untrusted devices and refuses to save session cookies permanently. After redirect, the sign-in page appears again. **Use Google Authenticator code instead** for headless environments.

### Google Authenticator Code Flow (3 Tem 2026)

When "Tap Yes" phone push doesn't persist the session, the **Google Authenticator** app provides a more reliable 2FA bypass:

1. On the 2FA page, click **"Try another way"** → **"Get a verification code from the Google Authenticator app"**
2. This opens a simple "Enter code" textbox — no phone notification needed
3. **Speed matters:** Authenticator codes expire every 30 seconds. Pre-stage all steps (email → password → Try another way → Authenticator selection) so you're waiting **at the code input screen** when asking the user for the code
4. User reads the 6-digit code from their phone → type it → click Next
5. If code expires ("Wrong code"), ask user to wait for the next code cycle (~30s)

**Why this works better than "Tap Yes" in headless:**
- No session persistence issue — Google accepts the code as proof of identity
- No phone notification dependency (user doesn't need to receive push)
- Works consistently across headless/headed modes

**Speed trick — browser_console JavaScript injection (3 Tem 2026):** `browser_type` + `browser_click` (2 tool calls) risk ref ID'lerin arada değişmesini. Bunun yerine kullanıcı kodu söylediğinde **tek `browser_console` call** ile DOM'dan input'u bul, native value setter ile doldur, event dispatch et ve Next butonuna tıkla. Detaylı kod: `references/google-2fa-authenticator-flow.md` → 🚀 browser_console JavaScript Injection bölümü.

**Detailed reference:** `references/google-2fa-authenticator-flow.md`
   document.evaluate("//*[text()='Enter your password']", document, null, 
       XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue?.click()
   ```
5. **Password page** — URL: `/challenge/pwd`

**CDP typing:** Use `Input.insertText` (not `Runtime.evaluate` with value=) for typing into the password field, then `Runtime.evaluate` to find and click "Next".

**Container restart resilience (20 Haz 2026):** After container restart, ALL services die:
- Xvfb (virtual display)
- x11vnc (VNC server)
- websockify/noVNC (Web VNC)
- Serveo/localhost.run tunnels
- Chrome (restarts in headless mode automatically)
- NotebookLM MCP server (restarts with empty profile)

**Recovery checklist:** 
1. Rebuild the VNC stack if needed: Xvfb → x11vnc → websockify → noVNC (see references/vnc-fallback-auth.md)
2. Relink Chrome profile: `ln -sf /home/ubuntu/.hermes/chrome_profile_notebooklm /home/ubuntu/chrome_profile_notebooklm`
3. **MCP profile symlink** (if MCP config uses `auth.profile_dir: ./chrome_profile_notebooklm`):
   ```bash
   MCP_CWD=$(readlink -f /proc/$(pgrep -f "notebooklm-mcp" | head -1)/cwd)
   ln -sf /home/ubuntu/.hermes/chrome_profile_notebooklm "$MCP_CWD/chrome_profile_notebooklm"
   ```
4. Restart MCP server: `kill $(pgrep -f "notebooklm-mcp" | head -1)` — Hermes auto-restarts from config.yaml within seconds
5. Verify auth: `mcp_notebooklm_mcp_healthcheck()` → `{authenticated: true}` after restart
6. Serveo tunnel URL: use Python subprocess, not Hermes background:
   ```python
   import subprocess
   proc = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no", "-R", "80:localhost:6082", "serveo.net"],
       stdout=open("/tmp/tunnel.txt","w"), stderr=subprocess.STDOUT)
   # Read URL after 8-12s:
   url = open("/tmp/tunnel.txt").read().split("https://")[1].split()[0]
   ```

See `references/vnc-fallback-auth.md` for full setup commands, port map, decision tree, and troubleshooting.  
See `references/cdp-password-bridge.md` for the CDP bridge alternative when VNC stack is missing (working code + instructions).
See `references/cdp-bitwarden-auth.md` for the Python websockets + CDP + Bitwarden pattern — lightweight alternative to Playwright for form-filling auth flows without `nlm login --cdp-url`.
See `references/notebooklm-mcp-auth-recipe-2026-06-23.md` for the concrete NotebookLM MCP auth fix sequence — Playwright CDP injection into MCP Chrome, "Try another way" bypass, profile recovery after crash, and the `launch_persistent_context` approach.

### Pattern D: Manual cookie import (FALLBACK — en güvenilir)

CDP WebSocket 403 hatası alındığında (%100 başarısızlık oranı) veya Chrome profili boş olduğunda:

```bash
nlm login --manual -f /path/to/cookies.json
```

CookieFile her iki formatı destekler: Netscape (cURL) veya JSON (Chrome extension export).

**Ne zaman kullan:** CDP `--remote-allow-origins=*` Chrome 148'de çalışmazsa, ilk kurulumda, kullanıcı tarayıcısında oturum açmışsa.

## Auto-Refresh Cron Setup

### 1. Place refresh script in `~/.hermes/scripts/`

```bash
#!/bin/bash
# nlm-auth-refresh.sh
NLM_BIN=~/.local/bin/nlm
AUTH=$($NLM_BIN login --check 2>&1)
if echo "$AUTH" | grep -qi "valid"; then exit 0; fi
python3 ~/.nlm/refresh_cookies.py
```

### 2. Register as no_agent cron job

Schedule every 12 hours (0 */12 * * *), script-based, no LLM tokens consumed.

## File Locations

| Location | Content |
|----------|---------|
| `~/.notebooklm-mcp-cli/profiles/default/` | cookies.json, metadata.json |
| `~/.notebooklm-mcp-cli/auth.json` | MCP auth (generated) |
| `~/.nlm/refresh_cookies.py` | Headless refresh script |
| `~/.nlm/check_auth.sh` | Auth check + refresh wrapper |

## AuthHealthChecker Architecture (v0.7.1+)

AuthHealthChecker (`services/auth.py`) uses a **two-phase probe strategy**:

1. **Phase 1 — Homepage probe:** HTTS GET to `notebooklm.google.com/` with browser-like headers (`_PAGE_FETCH_HEADERS`: UA, Accept, Sec-Fetch-*). Checks if response URL contains `accounts.google.com` (redirect = expired) or returns non-200.
2. **Phase 2 — API fallback (only if Phase 1 fails):** Creates a `NotebookLMClient` and calls `list_notebooks()`. The API endpoint (`notebooklm.google.com/api/...`) is more lenient than the homepage and often accepts cookies that the homepage rejects.

```python
# Simplified flow:
probe = _probe_homepage(cookies)  # → notebooklm.google.com/
if probe.valid:                    return "configured"
if probe.reason == "expired":       # ← accounts.google.com redirect
    api_probe = _probe_api(cookies) # → list_notebooks()
    if api_probe.valid:             return "configured"  # false positive avoided!
# Both failed:
return "stale"
```

**Important:** In v0.7.1, the homepage probe already hits `notebooklm.google.com/` (NOT `www.google.com`), using proper browser-like headers including Sec-Fetch-*. This was fixed upstream — no manual probe URL patching needed.

**Key insight for "stale" diagnosis:** If BOTH probes fail, the "stale" status is accurate — it's not a false positive. The API probe (`list_notebooks`) shares the same authentication as CLI read operations (`nlm login --check`), so if both fail, auth is genuinely broken.

### Diagnostics: Stale But Cookies Non-Expired

A common confusing scenario: `cookies.json` shows 61 cookies with valid expiry dates, but both probes return "stale". **This means Google has actively revoked the session** — cookie expiry dates are the *maximum* lifetime, not a guarantee.

Common causes:
- Password changed on any device using this Google account
- Google account security event (suspicious login detection, new device login)
- Session manually revoked from Google Account settings
- Cookie rotation (Google replaces session cookies periodically)

**Diagnostic flow:**
1. Check cookie expiry → all valid → session was revoked, not expired
2. Check nlm login --check → fails → confirms genuine auth failure
3. Solution: User must re-export cookies from a trusted browser

### MCP Selenium Cookie Injection Limitation (NotebookLM MCP)

NotebookLM MCP uses **Selenium (undetected_chromedriver)** internally (`client.py:_load_cookies()`), not Playwright. When Playwright-exported `storage_state.json` is loaded via Selenium's `driver.add_cookie()`, many Google auth cookies fail silently due to:
- `Secure` flag mismatches (Selenium requires HTTPS context)
- `HttpOnly` cookies that Selenium can't inject after page load
- `SameSite` attribute incompatibility
- Domain format differences (Playwright uses `.google.com`, Selenium expects `google.com`)

**Result:** Even with valid Playwright-exported cookies, the MCP's `_is_authenticated` remains False.

**Workarounds:**
1. **Playwright connect_over_cdp to MCP Chrome** — MCP's Chrome runs on display :99 with remote-debugging-port. Connect via Playwright, complete login there, export storage_state from that same context.
2. **CDP + Bitwarden auth** — Use `references/cdp-bitwarden-auth.md` pattern instead of MCP's cookie loader.
3. **VNC manual login** — Fall back to VNC when headless auth fails.
3. Solution: User must re-export cookies from a trusted browser
```

### Verifying External AI Analysis

External AI analysis of code issues (like GLM-5.1's auth analysis) should always be **validated against the actual source code** before applying patches. Plausible-sounding claims about missing headers or wrong endpoints can be confidently debunked by reading `services/auth.py`, `core/auth.py`, and `core/base.py`.

## Pitfalls

- **Snap Chromium** has X11 issues on headless servers → use Playwright Chromium
- **"stale" with `live=False`** is a heuristic (7-day), but **"stale" with `live=True`** (both probes run) is an accurate verdict — check which mode was used
- **"stale with valid cookies"**: if cookies are non-expired but both probes fail, the session was actively revoked by Google — re-export is the only fix
- **ProcessSingleton error** → lock files from crashed Chrome. Fix: `rm -f {profile_dir}/Singleton*`
- **nlm login --cdp-url** needs a profile with existing Google session cookies
- **Manual import (--manual)** is always available as fallback
- **Auth expiry**: verify with actual write operations (`nlm report create ... --confirm -y`), not just `--check`
- **Google sign-in blocked?** Before debugging browser methods, run `scripts/test-google-signin.py` to check if the account is flagged. If ALL methods fail identically, the account/IP is blocked — not the browser.
- **Cron auth_monitor.sh false-positive DOWN alarms:** `systemctl --user is-active` user crontab icinde `XDG_RUNTIME_DIR` set edilmedigi icin sessizce basarisiz olur → servis calisiyor olsa bile "DOWN" raporlanir. Cozum: `export XDG_RUNTIME_DIR=/run/user/$(id -u)` ve `export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus` script basinda. Detay: `references/cron-systemd-user-pitfall.md`

### 🚨 Google "signin/rejected" Bot Blockade

After **repeated automated login attempts** from the same IP (even with correct credentials),
Google shows a `/v3/signin/rejected` page. This is a **server-side account+IP flag** that
affects ALL automation methods: Playwright, Camofox, Selenium, headless, headed, fresh profiles, etc.

**Diagnostic signal:** URL contains `/signin/rejected?continue=...&rrk=46`. The `rrk` parameter
is Google's internal risk score — 46 means the account/IP has been aggressively flagged.

**Cross-method verification (21 Jul 2026):** When ALL four methods fail identically with
`signin/rejected`, the problem is *not* the browser — it's the account flag:
- ❌ Camofox (Firefox fork) → `signin/rejected?rrk=46`
- ❌ Headless Chromium + CDP → `signin/rejected?rrk=46`  
- ❌ Xvfb + headed Chromium → `signin/rejected?rrk=46`
- ❌ Playwright (fresh context) → `signin/rejected?rrk=46`

This uniform failure across all engines (including the one that *previously worked*) is the
definitive signal that the account is temporarily blocked, not the browser method.

**Symptom:** URL contains `/signin/rejected?continue=...`, only 3 session cookies saved
(vs 53-73 on successful login). The block fires at the *email entry stage* — before
any credentials are checked.

**Solutions (in order of reliability):**
1. **Wait** — Google's block is temporary (hours to a day); do not retry during the block.
   Every retry may extend the block duration.
2. **Change IP** — Different source IP or proxy may bypass
3. **Cookie import from trusted browser** — Export cookies from a browser already logged in
   on a different IP, import into the automation profile. See `references/google-cookie-export-import.md`.
4. **VNC manual login** — Human completes the verification once; cookies then work for hours
5. **Phone approval** — "Tap Yes on your phone" option may bypass the block

**Rapid diagnostic script:** Use `scripts/test-google-signin.py` (Playwright) to quickly
check whether the account is blocked WITHOUT consuming browser tool calls:
```bash
DISPLAY=:99 python3 scripts/test-google-signin.py
# Output: PAGE_LOADED_OK → not blocked; BLOCKED → wait
```

**Prevention:** 
- Limit automated login retries to 2 per session. 
- If first attempt hits passkey/2FA, fall back to VNC immediately — do NOT retry with different parameters.
- If `signin/rejected` appears once, STOP all browser-based login attempts for that account for at least 2 hours.

**Related:** See `references/cdp-headless-chromium-google-block.md` for the specific CDP headless Chromium dead-end (21 Jul 2026) — `--headless=new` is a guaranteed block for Google sign-in, even with stealth flags.

### 🚨 Playwright Password Field `is_visible()` Check

Google login pages frequently contain **hidden** `input[type="password"]` elements
(for autofill/password manager detection). Playwright's `query_selector` finds them but
`fill()` on an invisible element throws `TimeoutError: element is not visible`.

**Fix:** Always test visibility before interacting:
```python
pw_inp = await page.query_selector('input[type="password"]')
if pw_inp and await pw_inp.is_visible():
    await pw_inp.fill(password)
```

**Priority order for login flow selectors:**
1. Account chooser (`[data-identifier="user@email.com"]`)
2. Email input (`#identifierId`) with `is_visible()`
3. Password input with `is_visible()`  ← hidden elements exist!
4. "Try another way" link with `is_visible()`
5. "Enter your password" option (`[data-value="PASSWORD"]`)

### 🚨 Playwright Cookie Format Incompatible with Selenium MCP

The `notebooklm-mcp` uses **Selenium (undetected_chromedriver)** internally. Its
`_load_cookies()` reads Playwright-format `storage_state.json` and attempts
`driver.add_cookie()` for each cookie. Many Google auth cookies fail silently:

- `Secure` cookies need HTTPS context (not yet established)
- `HttpOnly` cookies can't be injected after page load
- `SameSite` attribute format differences
- Domain prefix dot (`.google.com` vs `google.com`)

**Effect:** Even with perfectly valid Playwright-exported cookies, MCP's `_is_authenticated`
stays `False` after restart.

**Workaround:** Use Playwright's `launch_persistent_context(MCP_PROFILE, ...)` to write
cookies directly into MCP's Chrome profile SQLite database. Then start MCP — it finds
the profile already logged in. See `references/notebooklm-mcp-auth-recipe-2026-06-23.md`.

### 🚨 ARM64 Chromium Binary Yolu (Playwright Headless Shell)

Bu sunucu **Oracle Cloud ARM64 (aarch64)** üzerinde çalışır. Playwright'ın `chromium` paketi ARM64 için `chrome` binary'si içermez — bunun yerine `headless_shell` kullanılır.

**Binary yolu:**
```
~/.cache/ms-playwright/chromium_headless_shell-1223/chrome-linux/headless_shell
```

**Doğrulama:**
```bash
file ~/.cache/ms-playwright/chromium_headless_shell-1223/chrome-linux/headless_shell
# → ELF 64-bit LSB pie executable, ARM aarch64
```

**Playwright ile kullanım:**
```python
from playwright.async_api import async_playwright
async with async_playwright() as p:
    browser = await p.chromium.launch(
        headless=True,
        executable_path='/home/ubuntu/.cache/ms-playwright/chromium_headless_shell-1223/chrome-linux/headless_shell',
        args=['--no-sandbox', '--disable-dev-shm-usage']
    )
```

**Önemli farklar:**
| Özellik | x86_64 (standart) | ARM64 (bu sunucu) |
|---------|-------------------|-------------------|
| Binary | `chrome` | `headless_shell` |
| Dizin | `chromium-1223/chrome-linux/chrome` | `chromium_headless_shell-1223/chrome-linux/headless_shell` |
| Selenium `webdriver.Chrome()` | Çalışır | ❌ `Unsupported platform: linux/aarch64` |
| SeleniumBase UC driver | Çalışır | ❌ `Exec format error` (x86 binary) |

**Kural:** ARM64'te headless browser otomasyonu için **Playwright** kullan. Selenium ve SeleniumBase aarch64 desteklemez.

### 🚨 WebSocket CDP 403 (Chrome 148+)

`--remote-allow-origins=*` flag'i Chrome 148'de **çalışmaz** — WebSocket bağlantıları hala 403 Forbidden döner. Belirti:

```
WebSocketBadStatusException: Handshake status 403 Forbidden
```

Bu bir origin/sunucu güvenlik kısıtlaması — Chrome flag'i yetersiz kalıyor.

**Çözüm:** CDP'yi tamamen atla, `nlm login --manual -f cookies.json` kullan.

### 🚨 Cookie Deduplication (61→27 Kayıp)

`cookies.json` dosyasında aynı isimde farklı domain/path için birden fazla cookie bulunabilir (ör. 3 tane `HSID`, 3 tane `SID`). Ancak `cookies_to_header(cookies: dict[str, str])` fonksiyonu **dict** aldığı için aynı isimdeki cookie'lerden sadece sonuncusu kalır, diğerleri sessizce kaybolur.

**Etkisi:** 61 cookie → 27 cookie. Kritik domain-specific cookie'ler (ör. notebooklm.google.com'a özel SID) ezilmiş olabilir.

**Belirti:** Cookie'ler yeni ve expiry süreleri geçerli olmasına rağmen `nlm login --check` fail. `_fetch_notebooklm_homepage`'te gönderilen Cookie header'ı eksik.

**Teşhis:**
```python
cookie_dict = {c["name"]: c["value"] for c in cookies if "name" in c and "value" in c}
print(f"Düşüş: {len(cookies)} → {len(cookie_dict)}")
```

**Çözüm:** Bu `notebooklm-mcp-cli` kütüphane seviyesinde bir sınırlama. Alternatif yok — kütüphane internal'da dict kullanıyor. En güvenilir yol: kullanıcının Chrome'undan export (gerçek Chrome tüm duplicate cookie'leri doğru yönetir) + `nlm login --manual`.

### 🚨 `nlm login --manual` Sessiz CSRF Bozulması

`nlm login --manual -f cookies.json` çalıştığında:
1. Cookie'ler başarıyla import edilir ✅
2. CSRF token'ı extract etmek için `_fetch_notebooklm_homepage()` çağrılır
3. Homepage `accounts.google.com`'a redirect olursa → sayfa login sayfasıdır, NotebookLM içeriği değil
4. CSRF extractor yanlış elementi yakalar → **JavaScript fonksiyonu** (örn. `function(a){var b=this,c=Zl(`) CSRF olarak kaydedilir
5. CLI "Successfully authenticated!" yazar ama auth hala bozuktur

**Belirti:** `nlm login --manual` "başarılı" ama `nlm login --check` hala "expired". `auth.json`'da `csrf_token: "function(a){...}"`

**Teşhis:**
```bash
python3 -c "import json; a=json.load(open('~/.notebooklm-mcp-cli/auth.json')); print(a.get('csrf_token','')[:40])"
# → "function(a){var b=this,c=Zl("  → BOZUK!
```

**Kök neden:** `_fetch_notebooklm_homepage` accounts.google.com'a redirect olduğu için sayfa içeriği NotebookLM'e ait değil. CSRF extractor sayfadaki rastgele bir JavaScript fonksiyonunu yakalıyor.

**Ne yapmalı:**
- CLI "başarılı" dese bile `csrf_token`'ı doğrula
- Eğer CSRF bozuksa: manuel olarak NotebookLM sayfasından (`view-source:https://notebooklm.google.com/`) `_csrftoken` değerini al ve `auth.json`'a yaz
- En garantili yol: `nlm login --cdp-url` (gerçek Chrome oturumu ile) — cookie'ler ve CSRF birlikte doğru alınır

### 🚨 Auth Asimetrisi (Read ✅ / Write ❌)

Kritik: `nlm login --check` başarılı olsa bile yazma işlemleri bloke olabilir:

| İşlem | Durum |
|-------|-------|
| `notebook_list` | ✅ Çalışır |
| `notebook_query` | ✅ Çalışır |
| `source_add(type="text")` | ✅ Çalışır |
| `studio_create` (slide_deck, audio, report) | ❌ "expired" |
| `nlm report create` | ❌ PERMISSION_DENIED (code 7) |

**Nedeni:** NotebookLM'in okuma ve yazma token'ları farklı sürelere sahip. CLI `--check` sadece okuma token'ını test eder. Yazma token'ı daha hızlı expire olur.

**Doğrulama prosedürü:** `nlm login --check` yerine doğrudan yazma testi yap:
```bash
nlm report create <NOTEBOOK_ID> --format "Briefing Doc" --confirm -y
```
PERMISSION_DENIED alırsan yazma kapalıdır. Sadece `--check` valid demek yetmez.

**Belirtiler:**
- MCP `refresh_auth: {"status":"expired"}` → sadece 7-gün heuristic DEĞİL, gerçekten expired
- `nlm login` valid dedikten sonra hala PERMISSION_DENIED

## Verification

```bash
# 1. CLI auth check (read-only — yetersiz!)
nlm login --check

# 2. WRITE testi (zorunlu! — read check yetmez)
# Bir notebook ID al, sonra:
nlm report create <NOTEBOOK_ID> --format "Briefing Doc" --confirm -y
# PERMISSION_DENIED → yazma kapalı, yeniden auth gerek

# 3. MCP server status (canlı)
mcp_notebooklm_mcp_server_info
# auth_status: "stale" → gerçek expired olabilir, write test yap

# 4. Service operations test
# Read: notebook_list, notebook_query (genelde çalışır)
# Write: studio_create (sorunlu, test et)
```
