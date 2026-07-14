# Google Auth Rejection — NotebookLM MCP

## Symptom

Every automated login attempt ends at:
```
https://accounts.google.com/v3/signin/rejected?continue=...
```
with message: "Couldn't sign you in — This browser or app may not be secure"

## Attempted Solutions (all failed)

| Approach | Result | Date |
|----------|--------|------|
| undetected-chromedriver 3.5.5 | ❌ rejected | 20 Haz |
| Downgrade to uc 3.5.4 + version_main=149 | ❌ rejected | 20 Haz |
| WARP+ proxy (Cloudflare IP 104.x.x.x) | ❌ rejected | 20 Haz |
| `--disable-blink-features=AutomationControlled` | ❌ rejected | 20 Haz |
| `Page.addScriptToEvaluateOnNewDocument` (4 anti-detection patches) | ❌ rejected | 20 Haz |
| "Try again" button → email → Next | ❌ rejected again | 20 Haz |

## Root Cause

Google uses **browser fingerprinting**, not just IP or navigator.webdriver checks:

- Canvas fingerprint
- WebGL fingerprint
- AudioContext fingerprint  
- Font list fingerprint
- Screen resolution + color depth
- Timezone + language match
- Chrome runtime properties
- Installed extensions / plugins
- `navigator.hardwareConcurrency`
- WebDriver active flag (multiple layers)

`undetected-chromedriver` patches about 20-30 signals but Google detects dozens more that a headless/datacenter browser inevitably leaks.

## Working Solutions

### ✅ Cookie Import (Reliable)
User exports cookies from their own Chrome (where Google trusts the browser):

1. User opens `notebooklm.google.com` in their personal Chrome
2. F12 → Application → Cookies → `notebooklm.google.com`
3. Select all → Export as JSON
4. Import via `notebooklm-mcp import-profile --from-profile cookies.json`
5. Or copy cookies into Chrome profile at `auth.profile_dir/Default/Cookies`

### ✅ Owned Notebook Workaround
If only read operations are needed, use `notebook_query` directly — no auth required for read-only MCP tools.

### ❌ Automated CDP Login (Unreliable)
Even with all anti-detection measures, Google consistently blocks automated logins. Not recommended.
