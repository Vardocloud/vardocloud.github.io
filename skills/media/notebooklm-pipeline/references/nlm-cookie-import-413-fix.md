# nlm Cookie Import — HTTP 413 Prevention (24 Haz 2026)

## Problem

`nlm login --manual -f cookies.json` with an unfiltered cookie export (2000+ cookies, 870KB) causes:

```
ValueError: Failed to fetch NotebookLM page: HTTP 413
```

This happens because the HTTP client sends ALL imported cookies (including Cloudflare, Koçtaş, CapCut, etc.) to notebooklm.google.com, exceeding Google's request header size limit.

## Solution

Filter to only Google-domain cookies before import:

```bash
python3 -c "
import json
with open('cookies.json') as f:
    raw = f.read()
if raw.startswith('1|'):
    raw = raw[2:]
cookies = json.loads(raw)
filtered = [c for c in cookies if 'google' in c.get('domain','').lower()]
with open('/tmp/nblm_cookies.json', 'w') as f:
    json.dump(filtered, f)
print(f'Filtered {len(cookies)} → {len(filtered)} Google cookies')
"
rm -rf ~/.notebooklm-mcp-cli/profiles/default
nlm login --manual -f /tmp/nblm_cookies.json
```

## Profile Structure

```
~/.notebooklm-mcp-cli/profiles/default/
  cookies.json    # Flat dict: {name: value, ...}
  metadata.json   # {csrf_token, session_id, email, build_label, last_validated}
```

## Remaining Issues

Even with filtered cookies:
- Google MAY still reject cookies from a different IP/geo (redirects to `accounts.google.com`)
- CSRF token and session_id are null after import (auto-extracted on first request)
- If rejected, fallback to `nlm login` with VNC-assisted manual login

## Verification

```bash
nlm doctor          # Shows profile status, 40 cookies present, CSRF token status
nlm login --check   # Attempts validation (may fail with redirect if IP-blocked)
nlm list notebooks  # Lists notebooks if auth works
```
