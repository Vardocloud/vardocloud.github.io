# Google OAuth Testing Mode Token Lifecycle

## The 7-Day Expiry Cycle

When the OAuth app is in **Testing mode** (Google Cloud Console → OAuth consent screen → Testing), refresh tokens expire after ~7 days. This is Google's policy for unverified apps — it prevents long-term unattended access.

### Timeline

| Day | Event |
|-----|-------|
| Day 0 | OAuth setup completed. Token saved. |
| Day 0-6 | Token works. Daily keepalive refreshes access_token. |
| Day ~7 | Refresh_token revoked by Google. `invalid_grant` errors begin. |
| Day 7+ | All API calls fail. Must re-authorize. |

### Error Signatures

**`setup.py --check`:**
```
REFRESH_FAILED: ('invalid_grant: Token has been expired or revoked.', ...)
```

**Direct token refresh:**
```
HTTP 400: {"error": "invalid_grant", "error_description": "Token has been expired or revoked."}
```

**Script failures (no_agent cron):**
```
Script exited with code 2
stdout:
⚠️ Google token expired! Edel'e bildir
```

## Full Reproduction Recipe

### 1. PKCE + localhost redirect_uri bug

If `setup.py` generates auth URLs with `autogenerate_code_verifier=True`, the exchange fails:

```
ERROR: Token exchange failed: (invalid_grant) code_verifier or verifier is not needed.
```

**Environment:** Any setup where `REDIRECT_URI = "http://localhost"`
**Why:** Google doesn't require/accept PKCE for localhost redirect URIs.
**Fix:** Set `autogenerate_code_verifier=False` and handle `code_verifier=None` in the exchange flow.

### 2. Token path confusion

When two token files exist:
- `google_token.json` — actively refreshed by daily keepalive cron
- `google_token_ubuntu.json` — stale, NOT refreshed

Scripts pointing to the stale file fail silently:
```
google.auth.exceptions.RefreshError: 
('invalid_grant: Token has been expired or revoked.', 
 {'error': 'invalid_grant', 'error_description': 'Token has been expired or revoked.'})
```

**Fix:** Ensure all scripts reference `google_token.json` (not `google_token_ubuntu.json`).

### 3. gmail_check.sh JSON parsing failure

When `no_agent` scripts parse `google_api.py` output:

**Bug:** Script greps `^Subject:` but `google_api.py` returns JSON array.
**Result:** `COUNT` always 0 → `[SILENT]` even when emails exist.
**Fix:** Use Python for JSON parsing instead of bash grep.

Example fix pattern:
```python
import json, sys
msgs = json.load(sys.stdin)
for m in msgs:
    print(f"  {m['from']} — {m['subject']}")
    print(f"    ↳ {m['snippet']}")
```

## Recovery Steps

```bash
# 1. Generate new auth URL (PKCE disabled)
python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-url

# 2. Send URL to user → they authorize → paste back the code URL

# 3. Exchange code
python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-code "CODE_OR_URL"

# 4. Verify
python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check
# → Should print "AUTHENTICATED"

# 5. Clean up stale token files if any
rm -f ~/.hermes/google_token_ubuntu.json
rm -f ~/.hermes/google_token_ubuntu.json.bak
```

## Prevention Matrix

| Approach | Expires | Effort |
|----------|---------|--------|
| Testing mode + monthly re-auth | ~7 days | Low |
| Production (published app) | Never | High (Google verification) |
| Service Account (no user) | Never | Medium (no Gmail/Calendar user data) |

For Edel's setup (single user, personal Gmail), Testing mode with monthly re-auth is the practical choice.
