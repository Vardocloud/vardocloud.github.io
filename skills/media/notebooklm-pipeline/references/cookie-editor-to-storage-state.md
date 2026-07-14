# Cookie-Editor Export → Playwright Storage State Conversion

When the user exports cookies via **Cookie-Editor** Chrome extension, convert them to Playwright `storage_state.json` format for the notebooklm-mcp server.

## Source Format (Cookie-Editor JSON)

```json
[{
  "domain": "notebooklm.google.com",
  "expirationDate": 1815554133.516048,
  "hostOnly": false,
  "httpOnly": true,
  "name": "OSID",
  "path": "/",
  "sameSite": "unspecified",
  "secure": true,
  "session": false,
  "storeId": "0",
  "value": "g.a000..."
}]
```

## Target Format (Playwright storage_state.json)

```json
{
  "cookies": [{
    "name": "OSID",
    "value": "g.a000...",
    "domain": "notebooklm.google.com",
    "path": "/",
    "expires": 1815554133,
    "httpOnly": true,
    "secure": true,
    "sameSite": "None"
  }],
  "origins": []
}
```

## Conversion Rules

| Source | Target | Notes |
|--------|--------|-------|
| `expirationDate` | `expires` | Convert float to int |
| `sameSite: "unspecified"` | `sameSite: "None"` | Playwright uses Lax/Strict/None |
| `sameSite: "no_restriction"` | `sameSite: "None"` | Same mapping |
| `domain: ".google.com"` | `secure: true` | Google cookies are always Secure |
| `domain: ".google.com"` | `sameSite: "None"` | Cross-site Google cookies |
| Missing top-level | `origins: []` | Always empty array |

## Required Cookie Categories

Include ALL of these for successful auth (not just notebooklm subdomain):

| Category | Examples | Purpose |
|----------|----------|---------|
| Session tokens | SID, __Secure-1PSID, __Secure-3PSID | Primary auth |
| SSO tokens | SSID, APISID, SAPISID, HSID | Google SSO |
| Secure session | __Secure-1PSIDTS, __Secure-3PSIDTS | Session binding |
| Channel IDs | SIDCC, __Secure-1PSIDCC, __Secure-3PSIDCC | Channel binding |
| NotebookLM-specific | OSID, __Secure-OSID (notebooklm.google.com) | Notebook access |
| LSID/PLSID | LSID (accounts.google.com, o.notebooklm.google.com) | Service-specific auth |
| NID | NID (.google.com) | Preferences/session |
| GAPS | __Host-GAPS (accounts.google.com) | Google Accounts |
| ACCOUNT_CHOOSER | ACCOUNT_CHOOSER | Account selector state |

## Python Conversion Script

```python
import json

with open('cookies.json') as f:
    raw = f.read()

# Remove Cookie-Editor prefix if present
if raw[0].isdigit() and raw[1] == '|':
    raw = raw[2:]

source = json.loads(raw)

playwright_cookies = []
for c in source:
    domain = c.get('domain', '')
    # Filter only Google domains needed for NotebookLM
    if not any(d in domain for d in [
        'notebooklm.google.com', '.google.com', 'accounts.google.com'
    ]):
        continue
    
    expires = c.get('expirationDate', 1815554133)
    if expires == 0:
        expires = 1815554133
    
    ss = c.get('sameSite', 'unspecified')
    if ss in ('unspecified', 'no_restriction'):
        ss = 'None'
    
    playwright_cookies.append({
        'name': c['name'],
        'value': c['value'],
        'domain': domain,
        'path': c.get('path', '/'),
        'expires': int(expires),
        'httpOnly': c.get('httpOnly', False),
        'secure': c.get('secure', False) or domain.startswith('.'),
        'sameSite': ss
    })

storage_state = {'cookies': playwright_cookies, 'origins': []}

with open('storage_state.json', 'w') as f:
    json.dump(storage_state, f, indent=2)

print(f'Converted {len(source)} → {len(playwright_cookies)} cookies')
```

## CookieMismatch After Import

If `notebooklm-mcp test` navigates to `https://accounts.google.com/CookieMismatch`:

**Cause:** Google detected the cookies originated from a different browser environment (different IP, user agent, device fingerprint).

**Fix:** User must export cookies WHILE actively on notebooklm.google.com (the page must be loaded):
1. Open `notebooklm.google.com` in Chrome (must show the notebook, not just logged in)
2. Cookie-Editor → **Export** (this must happen while the notebook page is the active tab)
3. Fresh export carries the active session token Google can verify
4. Convert and save → `notebooklm-mcp test` should show "Already authenticated via persistent session!"

## Where to Save

Profile path: `~/.notebooklm/profiles/default/storage_state.json`

After saving:
```bash
notebooklm-mcp test -n YOUR_NOTEBOOK_ID
# Look for: "✅ Already authenticated via persistent session!"
```

Then restart the MCP server or gateway for changes to take effect.
