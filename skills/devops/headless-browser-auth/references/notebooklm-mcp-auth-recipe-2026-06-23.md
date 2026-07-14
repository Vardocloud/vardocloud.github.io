# NotebookLM MCP Auth Fix — 23 Haz 2026

## Root Cause

NotebookLM MCP (`notebooklm-mcp`) uses **Selenium (undetected_chromedriver)** internally. Its
`_load_cookies()` method reads Playwright-format `storage_state.json` and tries to inject cookies
via `driver.add_cookie()`. This **silently fails for many Google auth cookies** because:

| Issue | Detail |
|-------|--------|
| `Secure` flag | Selenium requires HTTPS context before adding Secure cookies |
| `HttpOnly` | Cannot inject via JS after page load |
| `SameSite` | Attribute format incompatibility between Playwright and Selenium |
| Domain format | Playwright uses `.google.com` (dot prefix), Selenium wants `google.com` — `lstrip(".")` helps but not always |

**Result:** Even with perfectly valid Playwright-exported cookies (expiry Dec 2026), MCP's
`_is_authenticated` stays `False`.

## Working Approach: CDP Injection into MCP Chrome

**This worked once** (then Google's bot detection blocked repeated attempts):

1. MCP's Chrome runs on display `:99` with `--remote-debugging-port=49831` (or similar)
2. Connect via Playwright `connect_over_cdp` to MCP's Chrome
3. Handle the login flow: account chooser → "Try another way" → "Enter your password"
4. Export `storage_state.json`
5. Restart MCP (it re-reads storage_state, which has the same cookies that just failed...)

**Why it doesn't persist:** MCP restart → `_load_cookies` re-runs → same Selenium incompatibility
→ auth fails again. The only way to make it stick is to bake cookies into the Chrome profile
itself, not via storage_state.json.

## The Once-Successful Login Script

```python
# Key flow: connect to MCP's Chrome CDP, handle "Try another way" passkey bypass
from playwright.async_api import async_playwright

async with async_playwright() as pw:
    browser = await pw.chromium.connect_over_cdp(CDP_URL)
    ctx = browser.contexts[0]
    page = await ctx.new_page()
    await page.goto(NOTEBOOK_URL, wait_until="domcontentloaded", timeout=30000)
    
    # Retry loop with priority-ordered selectors:
    for attempt in range(10):
        url = page.url
        # Check for success:
        if "notebook" in url and "accounts" not in url:
            break  # LOGGED IN!
        
        # 1. Account chooser — click known account
        acct = await page.query_selector('[data-identifier="user@gmail.com"]')
        if acct: await acct.click(); await page.wait_for_timeout(4000)
        
        # 2. Email input (#identifierId) — only if visible
        # 3. Password input — only if visible (is_visible() check required!)
        # 4. "Try another way" link — click to bypass passkey
        # 5. "Enter your password" option — click after Try Another Way
    
    state = await ctx.storage_state()
    with open(STORE, "w") as f:
        json.dump(state, f, indent=2)
```

## The "Try Another Way" Bypass (Passkey → Password)

Google's modern login flow (2026) defaults to passkey/phone notification. To force password:

```
Page: /signin/challenge/pk/presend  ("Use your passkey to confirm it's you")
  → Click "Try another way"
  → Page: /signin/challenge/selection  
  → Click "Enter your password" ([data-value="PASSWORD"]
  → Page: /signin/challenge/pwd  (password input visible)
```

Playwright selectors that work:
```python
# Try another way (multiple possible elements)
await page.query_selector('a:has-text("Try another way"), button:has-text("Try another way")')

# Enter your password option (appears after clicking Try Another Way)
await page.query_selector('[data-value="PASSWORD"]')
```

**⚠️ `is_visible()` check:** Many pages have hidden `input[type="password"]` elements
(for autofill). Always check `await element.is_visible()` before interacting — otherwise
Playwright throws TimeoutError on invisible elements.

## Google "signin/rejected" Blockade

After repeated automated login attempts from the same IP, Google shows a **/signin/rejected**
page. This is Google's bot detection — it blocks ALL automated login attempts regardless of
headless/headed mode, Playwright/Selenium, or profile freshness.

**Symptoms:**
- URL: `https://accounts.google.com/v3/signin/rejected?continue=...`
- Only 3 cookies saved (vs 53-73 on successful login)
- Happens with both headless and headed Chrome

**Solutions:**
1. **Wait** — Google's block is temporary (hours to a day)
2. **Change IP** — Different source IP may bypass the block
3. **VNC manual login** — Human completes the CAPTCHA/verification once, then cookies work
4. **Phone approval** — If you have the "Tap Yes on your phone" option, that bypasses the block

## Profile Recovery After Chrome Crash

When `pkill -9 chromium` kills Chrome processes, the profile's `Local State` file gets corrupted:

```bash
# Check if corrupted:
cat ~/.hermes/chrome_profile_notebooklm/Local\ State | python3 -m json.tool
# → "Expecting value" error

# Check ownership (may be root if Chrome ran as root):
ls -la ~/.hermes/chrome_profile_notebooklm/Local\ State
# → -rw------- 1 root root ...

# Fix:
# If owned by root (no sudo in container): delete the file and let Chrome recreate it
rm -f ~/.hermes/chrome_profile_notebooklm/Local\ State
# Or if root-owned files exist, clean all of them:
find ~/.hermes/chrome_profile_notebooklm -user root -delete

# Singleton lock files from crashed sessions:
find ~/.hermes/chrome_profile_notebooklm -name "Singleton*" -delete
```

## Storage State Comparison

| State | Cookies | Google Cookies | Status |
|-------|---------|---------------|--------|
| Fresh login (23 Haz) | 73 | 53 | ✅ Working |
| Headless auto-login | 3 | 3 | ❌ No auth |
| Empty/cleared | 0 | 0 | ❌ No auth |

## Key Insight: Playwright `launch_persistent_context`

Instead of MCP's broken `_load_cookies()`, use Playwright's `launch_persistent_context`
to write cookies directly into the Chrome profile:

```python
browser = await pw.chromium.launch_persistent_context(
    MCP_PROFILE,  # same as MCP's --user-data-dir
    headless=True,
    args=["--no-sandbox", "--disable-dev-shm-usage"],
)
# Login happens → cookies are written to MCP_PROFILE/Default/Cookies (SQLite)
# MCP starts later → same profile → already logged in
```

This bypasses the Selenium cookie injection entirely. **But** the profile must be clean
(no corrupted `Local State`) and Google bot detection can still block on first login.
