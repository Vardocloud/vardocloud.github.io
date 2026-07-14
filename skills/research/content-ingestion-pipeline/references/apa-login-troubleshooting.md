# APA Login Troubleshooting (Updated 10 Tem 2026)

SSO login for APA content access (PsycNET, Monitor on Psychology, CE).

## Known Login Methods

### 1. Direct APA SSO (email + password) ✅ CONFIRMED WORKING
- URL: `https://sso.apa.org/apasso/idm/login`
- Email: `isimgorulsunn@gmail.com`
- Password: stored in Bitwarden Password Manager as item "APA"
- After 5 failed attempts: "locked out of one-time code login" — password login still works
- APA member name on account: "Vatinas Reister"
- **Google OAuth ("Log in with Google")**: NOT working — shows "Please verify your email" dialog

### 2. Credential Retrieval (Bitwarden)
APA password is stored in **Bitwarden Password Manager (bw)**, not BWS.

```bash
# Step 1: Get BW master password from BWS
export BW_PW=$(~/.hermes/bin/bws secret list | python3 -c "
import json,sys
data = json.load(sys.stdin)
for s in data:
    if s['key'] == 'BW_MASTER_PASSWORD':
        print(s['value'], end='')
")

# Step 2: Unlock bw CLI (password stays in env var, never on command line)
SESSION_KEY=$(~/.hermes/bin/bw unlock --passwordenv BW_PW --raw 2>&1)
unset BW_PW

# Step 3: Search for APA item
BW_SESSION="$SESSION_KEY" ~/.hermes/bin/bw list items --search "APA"
```

**APA Item:**
- Name: "APA"
- Username: isimgorulsunn@gmail.com
- URI: https://sso.apa.org/apasso/idm/apalogin?ERIGHTS_TARGET=https://www.apa.org

## bw-serve REST API (port 8087, v2026.6.2)

| Endpoint | Method | Status |
|----------|--------|--------|
| `/status` | GET | ✅ Returns vault state ("unlocked"/"locked") |
| `/sync` | POST | ✅ Syncs vault cache |
| `/unlock` | POST | ✅ Body: `{"password":"..."}` — unlocks vault |
| `/lock` | POST | ✅ Locks vault |
| `/generate` | GET | ✅ Password generation (405 on POST) |
| `/list/objects` | POST | ❌ 404 — NOT available in v2026.6.2 |

**Note:** `/list/objects` endpoint is missing in v2026.6.2. Use `bw CLI` with BWS master password for item listing.

## Known Failures

| Failure | Root Cause | Resolution |
|---------|-----------|------------|
| "email/username or password is incorrect" | Wrong password OR wrong email | Get correct password from Bitwarden |
| "lockout of one-time code" after 5 attempts | Brute force protection | Password login still works |
| Google OAuth "verify your email" | Google identity not linked to APA | Abandon Google OAuth — use email+password |
| PsycNET fulltext 403 even after login | APA membership ≠ all journal access | Only abstract/record view available |
| Chromium has no APA cookies | Headless profile | Session cookies in browser tool memory |

## APA Content Access Levels

| Content | URL Pattern | Access |
|---------|------------|--------|
| Monitor on Psychology | `www.apa.org/monitor/2026/07-08/` | ✅ Public (article pages) |
| Monitor PDF (full issue) | `www.apa.org/monitor/2026/2026-07-08-monitor.pdf` | 🔒 Member login (browser) |
| APA Topic Pages | `www.apa.org/topics/...` | ✅ Public |
| APA Events | `www.apa.org/events/...` | ✅ Public |
| CE Pages | `www.apa.org/education-career/ce/...` | ✅ Public |
| PsycNET Full Text | `psycnet.apa.org/fulltext/20XX-XXXXX-001.html` | 🔒 Journal subscription (not included in basic membership) |
| PsycNET Record | `psycnet.apa.org/record/20XX-XXXXX-001` | ✅ Public (abstract only) |
| Click tracking links | `click.info.apa.org/?qs=...` | ✅ Public (redirects to actual URL) |

## Email Source Domains (Confirmed via IMAP)

- `apa.org` → Editor's Choice, Science Spotlight
- `public.affairs@apa.org` → Media Watch
- `APA Practice News` → Practice Update
- `APA Continuing Education` → CE Roundup
- `APA Membership` → Member Update, Event Invitations
- `Monitor Digital` → Monitor on Psychology
- `APA Advocacy` → Advocacy alerts
- `PsycCareers` → Job listings
