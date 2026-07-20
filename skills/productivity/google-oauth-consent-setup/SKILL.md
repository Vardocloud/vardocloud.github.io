---
name: google-oauth-consent-setup
description: "Google OAuth Testing mode troubleshooting, consent screen configuration, and GitHub Pages domain setup for apps using the google-workspace skill."
version: 1.0.0
metadata:
  hermes:
    tags: [google, oauth, consent-screen, testing-mode, github-pages]
    related_skills: [google-workspace]
---

# Google OAuth Consent Setup

Troubleshooting Google OAuth consent screen issues when the google-workspace skill's setup.py fails due to Testing mode or domain requirements.

## Error Recognition

When a user reports this exact error after clicking the OAuth link:

**Turkish:**
> Erişim engellendi: [app adı], Google doğrulama sürecini tamamlamadı.
> Uygulama şu anda test edilmektedir. Yalnızca geliştirici tarafından onaylanan test kullanıcıları uygulamaya erişebilir.
> Hata 403: access_denied

**English:**
> Access blocked: [app name] hasn't completed the Google verification process.
> This app is currently being tested. Only approved test users can access it.
> Error 403: access_denied

**Root cause:** The OAuth app is in **Testing** mode in Google Cloud Console. Only explicitly added test users can access it.

## Fix 1 — Quick: Add Test User

1. User goes to https://console.cloud.google.com/auth/audience
2. Selects the correct project
3. Under **Test users**, clicks **Add users**
4. Enters their Google account email
5. Clicks **Save**
6. Retries the OAuth link

## Fix 2 — Permanent: Publish to Production

For unattended use (cron jobs, scheduled tasks), publish the consent screen:

1. Go to https://console.cloud.google.com/auth/overview → **Configure Consent Screen**
2. Fill required fields:
   - **App name** (e.g. "Hermes")
   - **User support email**
   - **App domain**: needs a hosted page
   - **Privacy policy URL**: must be a live URL
   - **Authorized domains**: the domain from the App domain field
3. Add required scopes (email, profile, openid minimum)
4. Click **Publish App**

After publishing, the 7-day token expiry cycle stops and any Google account can authorize without being on a test list.

## GitHub Pages as Free Domain

When the consent screen requires an App Domain and Privacy Policy URL:

1. Create a public repo named `username.github.io` on GitHub
2. Add an `index.html` (landing page) and `privacy-policy.html` (privacy policy)
3. GitHub Pages serves at `https://username.github.io/` automatically
4. Use this as the App Domain in Google Cloud Console
5. Use `https://username.github.io/privacy-policy.html` as Privacy Policy URL

### Privacy Policy Template Requirements
- What data the app collects (e.g., Gmail messages, Calendar events, Drive files)
- How data is used (daily report summarization, event management)
- Data is not shared with third parties
- Contact email for questions
- Last updated date

## Agent Workflow for OAuth Failures

When `$GSETUP --check` returns `REFRESH_FAILED`:

```
1. Generate fresh OAuth URL with $GSETUP --auth-url
2. Send URL to user, ask them to click and copy the full redirect URL
3. If user reports 403 "access_denied" with testing message:
   → Guide to Fix 1 (add test user in Google Cloud Console)
   → Regenerate URL and retry
4. If consent screen asks for domain:
   → Guide to GitHub Pages setup
   → User needs to fill consent screen fields in Google Cloud Console
5. After successful exchange with $GSETUP --auth-code:
   → Verify with $GSETUP --check
   → Should print AUTHENTICATED
```

## Save Button Not Clickable — Switch to Testing Mode

When the user fills all consent screen fields but the **Save / Submit for Verification** button is grayed out:

1. The user is in **Production** setup mode (OAuth consent screen published)
2. The gray button means there are validation errors — often hidden
3. **Quick fix:** Switch to **Testing mode** instead:
   - In Google Cloud Console → OAuth consent screen → **Back to testing** button
   - Add the user's email as a **Test user** in the Audience section
   - Save is always clickable in Testing mode
   - Verification (Production publishing) can be done later when all fields are perfect

**Why:** Google's Production verification requires every field to be pristine (support email, logo, domain verification, privacy policy hosting, etc.). One missing field blocks the entire save. Testing mode skips verification entirely — test users just need their email added.

## Post-Setup: Token Keepalive Cron

After successful OAuth setup, the token auto-refreshes (refresh token pattern) but the stored token can still go stale if unused for extended periods. See:
- `references/testing-mode-token-lifecycle.md` — full breakdown of the 7-day expiry cycle, PKCE fix, error signatures, and recovery steps

```bash
# Via Hermes cron:
cronjob action=create \\\
  name="gmail-token-keepalive" \\\
  schedule="every 2h" \\\
  skills='["google-workspace"]' \\\
  prompt="Gmail API token'inı canlı tut. setup.py --check ile token durumunu kontrol et. Hata varsa --auth-url ile yeni auth URL'si al ve bildir. Her şey normalse sessiz kal."
```

**How it works:** `setup.py --check` calls `creds.refresh(Request())` if expired. The cron keeps the refresh token from being invalidated by Google's idle policy.

### Testing Mode 7-Day Token Expiry

If the OAuth app is in **Testing mode** (not published to Production), Google revokes the refresh token after approximately **7 days** of inactivity or after the token has been refreshed a limited number of times. This is a Google policy for unverified apps.

**Symptoms:**
- `setup.py --check` returns `REFRESH_FAILED: invalid_grant: Token has been expired or revoked.`
- Direct token refresh yields `HTTP 400: invalid_grant`
- Token file exists with valid-looking access_token and refresh_token

**Fix:** Generate a new authorization URL and have the user re-authorize:
```bash
$GSETUP --auth-url
```
Send the URL to the user, have them authorize, then:
```bash
$GSETUP --auth-code "CODE_FROM_USER"
```

**Prevention:** The daily keepalive cron runs `setup.py --check` which refreshes the access token every day, but the refresh_token itself still expires after ~7 days in Testing mode. The only permanent fix is publishing the app to Production (see Fix 2 above).

### Token Path Consistency

The OAuth token is stored at `~/.hermes/google_token.json`. If a second token file appears (e.g., `google_token_ubuntu.json` from a previous setup), it will NOT be refreshed by the keepalive cron. This causes silent failures in scripts that reference the wrong path.

**Check:** 
```bash
ls -la ~/.hermes/google_token*.json  # Only google_token.json should exist
```

**Fix:** Delete stale token files and update any script that references `google_token_ubuntu.json` to use `google_token.json` instead.

### Setup → Verify Cycle

```
1. --check          → Durum kontrolü
2. --auth-url       → Kullanıcıya URL gönder
3. --auth-code URL  → Kodu exchange et
4. --check          → Onay: AUTHENTICATED
5. Cron kur         → Token'ı canlı tut
```

### Gmail API Quick Commands (post-setup)

```bash
GAPI="python3 $HOME/.hermes/skills/productivity/google-workspace/scripts/google_api.py"

# Okunmamış mailler
$GAPI gmail search "is:unread" --max 20

# Belirli gönderenden
$GAPI gmail search "from:cloudflare.com" --max 10

# Mail içeriğini oku (ID ile)
$GAPI gmail get MESSAGE_ID

# Son 10 mail
$GAPI gmail search "in:inbox" --max 10
```

## Why API > Browser for Gmail Access

Headless browser + Google 2FA is an unreliable combination:

| Method | Result |
|--------|--------|
| `browser_navigate` + `browser_type` + `browser_click` | Google detects headless → "This browser or app may not be secure" |
| Playwright/Puppeteer headless | Stronger detection → blocked at password screen |
| Google Workspace API (OAuth) | ✅ Works reliably, no 2FA, persistent access |

**When to use what:**
- **Email READING →** Always use Google Workspace API (OAuth)
- **Email SENDING →** Use Google Workspace API (`gmail send`) or Himalaya (IMAP + App Password)
- **Browser →** Only when API cannot do what you need (certain Gmail UI features)

### 2FA Code Entry Speed Challenge

If you must use browser-based login (e.g., for initial OAuth setup or a service that requires interactive login):
- Authenticator codes expire in 30 seconds
- `browser_type` + `browser_click` tool calls have latency → often miss the window
- `browser_console` with JavaScript expression is faster (single tool call):
  ```javascript
  // Find input regardless of type/role and fill + submit
  (() => {
    const el = document.querySelector('[type="text"],[type="tel"],input:not([type="hidden"]),[role="textbox"]');
    if (!el) return 'INPUT_NOT_FOUND';
    const nativeSetter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    nativeSetter.call(el, 'KODGİR');
    el.dispatchEvent(new Event('input', {bubbles:true}));
    for (const btn of document.querySelectorAll('button')) {
      if (btn.textContent.includes('Next')) { btn.click(); break; }
    }
    return 'OK';
  })();
  ```

## Common Pitfalls

### Authorized Domains — NO Scheme

In Google Cloud Console OAuth consent screen:
- **Authorized domains:** Write `vardocloud.github.io` (NO `https://` prefix)
- **Application home page:** `https://vardocloud.github.io/` (WITH `https://`)
- **Privacy policy URL:** `https://vardocloud.github.io/privacy-policy.html` (WITH `https://`)

If the user gets "Invalid domain: must not specify the scheme" error, they typed `https://` in the Authorized domains field. This field accepts ONLY the bare domain name.

### localhost:1 Redirect Blocked by Browser

After the user approves OAuth, Google redirects to `http://localhost:1/?code=...`. Some browsers (Zen Browser, NetIQ, corporate security tools) block port 1 with:
- "This address is restricted — This address uses a network port which is normally used for purposes other than Web browsing"
- "Web sayfası geçici olarak kullanılamıyor"

**Fix:** Ask the user to:
1. Copy the ENTIRE URL from the address bar anyway (it's still there)
2. OR check browser history (Ctrl+H) — the `http://localhost:1/?code=...` URL is saved
3. OR try a different browser (Chrome, Edge, Safari don't block port 1)
4. OR click "Details" / "Advanced" on the block page to reveal the URL

### PKCE + localhost redirect_uri — `invalid_grant: code_verifier not needed`

When `setup.py --auth-url` generates an authorization URL with `redirect_uri=http://localhost` and `autogenerate_code_verifier=True`, Google's OAuth endpoint returns:

```
ERROR: Token exchange failed: (invalid_grant) code_verifier or verifier is not needed.
The code may have expired. Run --auth-url to get a fresh URL.
```

**Root cause:** Google does not require or accept PKCE (Proof Key for Code Exchange) when the redirect URI is `http://localhost` — localhost is already considered a secure redirect target. When `setup.py` sends a `code_verifier` anyway, Google returns `invalid_grant`.

**Fix (in setup.py):**
```python
# Change from:
autogenerate_code_verifier=True,
# To:
autogenerate_code_verifier=False,
```

And in the exchange function, handle missing code_verifier:
```python
code_verifier=pending_auth.get("code_verifier"),  # was pending_auth["code_verifier"]
```

The `_save_pending_auth` function should also conditionally include the verifier:
```python
payload = {"state": state, "redirect_uri": REDIRECT_URI}
if code_verifier:
    payload["code_verifier"] = code_verifier
```

**Detection:** The error message contains `code_verifier or verifier is not needed` — this is diagnostic. If you see it, the PKCE fix is needed.

**If the fix is already applied:** The auth URL will NOT contain a `code_challenge` parameter (check the URL). The pending file (`google_oauth_pending.json`) will NOT have a `code_verifier` field. This is correct for localhost redirects.

### Pending OAuth Session Missing PKCE Data

When `$GSETUP --auth-code "URL"` fails with:

```
ERROR: Pending OAuth session is missing PKCE data.
Run --auth-url again to start a fresh OAuth session.
```

**Root cause:** The `google_oauth_pending.json` file exists but was created by a mechanism OTHER than `$GSETUP --auth-url`. The file has `state` and `redirect_uri` but no `code_verifier`. Common causes:

  - A stale pending file from a previous incomplete flow
  - The auth URL was generated by a different script or manual browser flow
  - The pending file comes from an older or different OAuth setup path

**Diagnostic — check the file:**

```bash
cat ~/.hermes/google_oauth_pending.json
# Expected (from --auth-url):  {"state": "...", "code_verifier": "...", "redirect_uri": "http://localhost:1"}
# Stale (from elsewhere):      {"state": "...", "redirect_uri": "http://localhost"}
```

**Fix — always regenerate:** Don't try to salvage the existing auth code or patch the pending file. Auth codes are single-use — testing the exchange once (even via curl) consumes it permanently.

```bash
$GSETUP --auth-url   # Creates fresh pending auth with PKCE data
```

Then send the NEW URL to the user and proceed with the returned callback.

**Why you can't patch it:** The `code_verifier` was created as a SHA-256 hash challenge (`code_challenge`) embedded in the original auth URL. The user's browser used that challenge during the OAuth handshake. Any `code_verifier` you invent retroactively won't match the challenge.

### Auth Code Single-Use Rule

Every Google OAuth authorization code can be exchanged exactly **once**. After any exchange attempt (successful or failed), the code is invalidated.

  - ❌ Don't test the exchange with `curl` — you'll consume the code
  - ❌ Don't send the same callback URL twice
  - ✅ If the first exchange fails, generate a fresh auth URL and have the user re-authorize

**Safe handling pattern:**

1. User sends callback URL
2. Call `$GSETUP --auth-code "FULL_URL"` immediately — this is the only attempt
3. If setup.py says "missing PKCE data", explain and have the user re-authorize with a fresh URL

### Direct Token Exchange Without PKCE (Fallback)

If the auth URL was generated without PKCE (no `code_challenge` in the URL), a direct HTTP POST to the Google token endpoint works:

```python
import urllib.request, urllib.parse, json

data = urllib.parse.urlencode({
    'code': auth_code,
    'client_id': client_id,
    'client_secret': client_secret,
    'redirect_uri': redirect_uri,
    'grant_type': 'authorization_code',
}).encode()
req = urllib.request.Request(token_uri, data=data, method='POST')
resp = urllib.request.urlopen(req, timeout=15)
result = json.loads(resp.read())
```

**When to use:** Only when `$GSETUP --auth-code` fails with a PKCE error AND the auth URL has no `code_challenge`. Always prefer the setup.py flow first.

**After token retrieval:** Convert to google-auth format by saving to `google_token.json` with fields: `token`, `refresh_token`, `token_uri`, `client_id`, `client_secret`, `scopes` (list), and `type: "authorized_user"`.

### Password Mismatch During Manual Login via Browser Tools

When logging into Google via the Puppeteer browser (`browser_navigate` → `browser_type` → `browser_click`), the password from Bitwarden (`bw` vault) might be **outdated** if the user recently changed their password. Google shows a clear indicator:

```
StaticText "Your password was changed X hours ago"
```

**Why:** The OAuth flow (google-workspace setup.py) just creates a new token — it doesn't validate the current password. The password stored in Bitwarden's "Gmail" item might be the old password if the user changed it separately.

**Recovery:**
1. Ask the user to update the password in their Bitwarden vault ("Gmail" item)
2. Or ask the user for the new password directly (through secure channel)
3. Then re-run the browser login

**Bitwarden password retrieval pattern:**
```bash
# Unlock vault (BW_MASTER_PASSWORD env var must be set in .env)
BW_SESSION=$(bw unlock --passwordenv BW_MASTER_PASSWORD 2>/dev/null | grep "export BW_SESSION" | cut -d'"' -f2)
export BW_SESSION

# List all items to find the right one
bw list items

# Get specific item password by name
bw list items --search Gmail | python3 -c "import json,sys; data=json.load(sys.stdin); [print(f'ID: {i[\"id\"]}\\nUsername: {i[\"login\"][\"username\"]}\\nPassword: {i[\"login\"][\"password\"]}') for i in data if i.get('name')=='Gmail']"
```

### Multiple Gmail Account Pitfall for App Passwords

When using Gmail App Passwords (for Himalaya IMAP backup), the user might be on the **wrong Gmail account** when generating the password. Symptoms:

1. App Password page says "Uygulama şifreniz yok" even after creating one
2. IMAP login returns "Invalid credentials (Failure)" with valid App Password
3. The user has multiple Google accounts and the Bitwarden vault has items for different accounts

**Fix:** 
1. Ask the user to **verify which Gmail account they're signed into** at https://myaccount.google.com/security
2. If wrong, switch to the correct account and generate a fresh App Password
3. Update the `~/.config/himalaya/gmail_pass` file and test:
```bash
himalaya envelope list --page 1 --page-size 5
```

**Why this happens:** Gmail App Passwords are account-scoped. A password generated on `yarenkasari31@gmail.com` won't work for `isimgorulsunn@gmail.com` IMAP login. The error is identical to a wrong password — no "wrong account" distinction.

### GitHub Pages Repo Case Sensitivity

GitHub usernames are case-insensitive but the repo name must match exactly:
- GitHub user `Vardocloud` → repo `Vardocloud.github.io` (matches display name)
- OR `vardocloud.github.io` (also works — GitHub normalizes)
- Best practice: use whichever matches the user's GitHub display name

If the user can't find the "Add file" button after creating the repo, guide them:
1. Go to `https://github.com/<username>/<username>.github.io`
2. Click green "Code" button area → "Add file" → "Create new file"
3. NOT "New issue" — that's a different section
