# APA Email Tracking Link Extraction

When APA content is delivered via email newsletter (Editor's Choice, Science Spotlight, Practice Update), the wiki entry may have `sources: [mailto:...]` instead of a public URL. These emails contain `click.info.apa.org/?qs=...` tracking links that redirect to the actual content.

## Workflow

1. **Gmail API**: Search for the email using `gmail search "from:(info.apa.org) subject:\"Editor's Choice\""`
2. **Get full body**: `gmail get MESSAGE_ID` and extract the HTML body
3. **Find tracking links**: Search for `click.info.apa.org/?qs=` in the body
4. **Resolve URL**: `curl -sIL -o /dev/null -w "%{url_effective}" --max-time 10 "TRACKING_URL"` — follows redirect to actual page
5. **Add to NotebookLM**: `nlm source add <UUID> --url "RESOLVED_URL" --title "..." --wait`

## Gmail Token Expiration

If Gmail API reports `REFRESH_FAILED: Token has been expired or revoked`:
- Solution: Run `$GSETUP --auth-url` to get a new auth URL, send to Edel for browser approval
- Alternative: Use `nlm login` CLI (works independently of Gmail) for NotebookLM operations
- Browser fallback: Navigate to Gmail directly if login cookies are available

## APA Newsletter Types

| Newsletter | Frequency | Typical Subject | Source Field in Wiki |
|-----------|-----------|-----------------|---------------------|
| Editor's Choice | Biweekly | "APA Editor's Choice — DD Mon YYYY" | `sources: [mailto:apa-editors-choice-...]` |
| Science Spotlight | Biweekly | "APA Science Spotlight — DD Mon YYYY" | `sources: [mailto:apa-science-spotlight-...]` |
| Practice Update | Weekly | "APA Practice Update — DD Mon YYYY" | `sources: [mailto:apa-practice-update-...]` |
| Media Watch | Weekly | "APA Media Watch" | `sources: [media-watch-...]` |

## Known Limitations
- Public archive of these newsletters does NOT exist on apa.org
- Only accessible via email or Gmail API
- If Gmail token is expired, browser login is needed

## Gmail API Fallback: IMAP

If Gmail API refresh token is expired/revoked:

### Option 1 (PRIMARY — Fastest, Already Configured): Himalaya CLI

Himalaya IMAP client is already installed at `~/.local/bin/himalaya` with a preconfigured account (`gmail`) and stored App Password at `~/.config/himalaya/gmail_pass`. Works consistently even when Gmail OAuth token is expired.

**Setup (one-time):**
```bash
# Config already exists at ~/.config/himalaya/config.toml
# App Password stored at ~/.config/himalaya/gmail_pass
# Current App Password: uazv jjlh ceba xksj (valid as of 10 Tem 2026)
```

**APA email search:**
```bash
# List APA emails (note: from "apa.org" NOT "info.apa.org")
himalaya envelope list --account gmail from "apa.org"

# Read a specific APA email body
himalaya message read <ID> --account gmail

# Export raw email (for HTML parsing / link extraction)
himalaya message export <ID> --account gmail

# Filter by date range
himalaya envelope list --account gmail from "apa.org" after "2026-07-01"
```

**APA newsletter types that come to isimgorulsunn@gmail.com (confirmed 10 Tem 2026):**
| Newsletter | From Address | Typical Subject |
|-----------|-------------|-----------------|
| Media Watch | APA Public Affairs | "APA Media Watch: ..." |
| Practice Update | APA Practice News | "Practice Update: ..." |
| Editor's Choice | American Psychological Association | "This Week's Editor's Choice Articles" |
| CE Roundup | APA Continuing Education | "APA CE Roundup: ..." |
| Member Update | APA Membership | "Member Update: ..." |
| Event Invites | APA Membership | "You're Invited: New Events..." |
| Monitor on Psychology | Monitor Digital | "APA's July/August 2026 Monitor on Psychology" |

Note: All come from the `apa.org` domain, but specific sub-addresses vary. Always use `from "apa.org"` as the broadest filter.

### Option 2: App Password via Python IMAP (Legacy)
```python
import imaplib, ssl, email
from email.header import decode_header

ctx = ssl.create_default_context()
mail = imaplib.IMAP4_SSL('imap.gmail.com', 993, ssl_context=ctx)
mail.login('isimgorulsunn@gmail.com', 'APP_PASSWORD')  # 16-character app password
mail.select('INBOX')
status, messages = mail.search(None, 'FROM', 'apa.org')
# Fetch and parse each message
```

The user needs to generate an app password at https://myaccount.google.com/apppasswords
(1 dk sürer — "Mail" için bir app password oluşturur, 16 karakterli kod verir)

### Tracking Link Resolution

APA emails contain tracking links in the format `https://click.info.apa.org/?qs=<base64_token>`. These resolve to the actual article URL via HTTP redirect.

**Resolve with curl:**
```bash
curl -sI -L --max-redirs 5 "https://click.info.apa.org/?qs=ABB7InYiOjE..." 2>&1 | grep -i "^location:" | tail -1
# Output example:
# Location: https://psycnet.apa.org/fulltext/2027-37562-001.html
```

**Confirmed URL destinations (10 Tem 2026 tests):**
- `psycnet.apa.org/fulltext/...` → APA PsycNET articles (**403 Forbidden** without login)
- `www.apa.org/topics/...` → APA topic pages (**200 OK**, public)
- `www.apa.org/events/...` → APA event pages (**200 OK**, public)
- `www.apa.org/education-career/ce/...` → CE pages (**200 OK**, public)
- `us.cnn.com/...` / `www.cnbc.com/...` / `www.forbes.com/...` → External news (public)
- `convention.apa.org/...` → Convention pages (public)
- `preferences.apa.org/quickunsubscribe?...` → Unsubscribe links (skip)
- `apamr.co1.qualtrics.com/...` → Survey links

**Bulk resolution script:**
```python
import subprocess, re

links = ["https://click.info.apa.org/?qs=LINK1", "https://click.info.apa.org/?qs=LINK2"]
for link in links:
    result = subprocess.run(["curl", "-sI", "-L", "--max-redirs", "5", link],
                          capture_output=True, text=True, timeout=15)
    locations = re.findall(r'^location:\s*(.*?)$', result.stdout, re.IGNORECASE | re.MULTILINE)
    final_url = locations[-1] if locations else "NO_REDIRECT"
    print(f"→ {final_url}")
    time.sleep(0.3)  # Rate limit
```

### Option 2: Browser Gmail (Cookie-Based)
- Navigate to `https://mail.google.com/mail/u/0/#search/from%3Ainfo.apa.org`
- If Chromium profile has active Gmail session → works immediately
- If redirected to login → cookie expired, need user login

### Option 3: Gmail OAuth Re-auth
Generate a new auth URL using the client credentials in `~/.hermes/google_token.json`:
```python
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_config(client_config, scopes)
# Prints auth URL -> user approves -> new token saved
```
