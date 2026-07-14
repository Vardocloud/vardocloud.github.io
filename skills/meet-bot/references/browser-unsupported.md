# Browser Unsupported — Google Meet Interstitial Bypass

## Problem

Google Meet displays **"This browser version is no longer supported"** for
Playwright's bundled Chromium (version 148+, nightly/dev channel). The page
shows a 55-second countdown, then redirects to the Google Workspace marketing
page. The bot never reaches the actual meeting.

## Detection

Symptoms in `status.json`:
- `error: "host denied admission"` ← FALSE POSITIVE
- `leaveReason: "denied"`
- `joinAttemptedAt` set, `joinedAt` null
- Edel did NOT receive a join request

The banner text `"You can't join this video call"` triggers `_detect_denied()`
even though no denial actually happened.

## Root Cause

Playwright's bundled Chromium (version 148+) is a **nightly/dev build**.
Google Meet's server-side check detects the version and sends a different HTML
page (the interstitial). This is NOT a client-side issue — the actual meeting
page never loads underneath.

**Even with User-Agent spoofing, the check still passes because Google uses
additional signals (CDP connection, Chrome version API, etc.).**

## Solution A: Camoufox (RECOMMENDED) ⭐

Camoufox is the ONLY browser that fully bypasses Google Meet detection on ARM64:

```bash
pip install camoufox
```

Usage:
```python
from camoufox import Camoufox
import time

with Camoufox(headless=True) as browser:
    page = browser.new_page()
    page.goto("https://meet.google.com/...", wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)
    # Now shows "Your name" + "Ask to join" — no workaround needed!
```

## Solution B: JS Interstitial Bypass (for Chromium)

If you MUST use Chromium, add `_handle_unsupported_browser()` to `meet_bot.py`.
This function dismisses the banner, kills all JS timers (preventing redirect),
and clicks "Continue without microphone".

### The Fix: `_handle_unsupported_browser()`

```python
def _handle_unsupported_browser(page) -> None:
    """Dismiss 'browser not supported' banner and prevent redirect countdown."""
    try:
        page.evaluate("""
        (() => {
            // 1. Dismiss the warning banner
            const els = document.querySelectorAll('button, [role="button"], a, span, div');
            for (const el of els) {
                const text = (el.textContent || '').trim();
                if (text === 'Dismiss') { el.click(); break; }
            }
            // 2. Kill ALL timers to prevent redirect
            const maxId = setTimeout(() => {}, 0);
            for (let i = 1; i <= maxId; i++) { clearTimeout(i); clearInterval(i); }
            // 3. MutationObserver to kill new timers
            const observer = new MutationObserver(() => {
                const m = setTimeout(() => {}, 0);
                for (let i = 1; i <= m; i++) { clearTimeout(i); clearInterval(i); }
            });
            observer.observe(document.body || document.documentElement,
                { childList: true, subtree: true, attributes: false });
            // 4. Click "Continue without microphone"
            setTimeout(() => {
                for (const el of document.querySelectorAll('a, button, [role="button"], span, div')) {
                    if ((el.textContent || '').trim().includes('Continue without microphone')) {
                        el.click(); break;
                    }
                }
            }, 1000);
        })();
        """)
    except Exception:
        pass
```

**Insertion point in `run_bot()`:**
```python
page.goto(url, wait_until="domcontentloaded", timeout=30_000)
_handle_unsupported_browser(page)  # NEW
page.wait_for_timeout(3000)
_try_guest_name(page, guest_name)
_click_join(page, state)
```

### Limitations of JS Bypass

The interstitial countdown is powered by `setInterval`/`requestAnimationFrame`
which are continuously recreated. The MutationObserver approach catches most
new timers, but the page may still redirect after the natural timeout.
**Best effort — not guaranteed.**

## Solution C: Firefox (with permission handling)

Firefox avoids the "unsupported browser" check but introduces permission issues:

1. **"Getting ready..." loading**: Wait 15-25s for this to finish
2. **"Click Allow" mic prompt**: Must click it or grant via API
3. **`context.grant_permissions(["microphone"])`** — call before navigation
4. **No `permissions` key in `context_args`** — Firefox doesn't support it

See `meet-bot/SKILL.md` → "Firefox Workaround" for full details.

## Test Results (13 Haz 2026)

| Browser | Version | GM Result | Notes |
|---------|---------|-----------|-------|
| Playwright Chromium | 148.0.7778.0 | ❌ Blocked | "unsupported" interstitial |
| Brave | 1.86.148 (Chromium 144) | ❌ Blocked | Same detection |
| Brave | 1.91.172 (Chromium 149) | ❌ Blocked | Same detection |
| Snap Chromium | 149.0.7827.53 | ❌ Blocked | Same detection |
| Playwright Firefox | 150.0.2 | ⚠️ Permission | "Click Allow" needed |
| **Camoufox** | 0.4.11 | **✅ WORKS** | Full pre-join UI visible |
