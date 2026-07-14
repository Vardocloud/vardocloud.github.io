---
name: turkish-locale-pitfalls
description: Common Turkish locale pitfalls across tools, APIs, and data processing — İ/i casefold, emoji prefixes, date formats, and locale-sensitive searches.
version: 1.0.0
author: Vanitas
---

# Turkish Locale Pitfalls

Common Turkish-specific issues when working with text matching, APIs, and
data processing. Turkish has unique characters (İ/ı/ğ/ü/ş/ö/ç) that cause
silent failures in standard Python/code routines.

## Key Pitfalls

### 1. Turkish İ vs i — Python casefold() is Broken

**Problem**: Python's `str.casefold()` does NOT normalize Turkish İ (U+0130)
to ASCII `i`. It produces `i + COMBINING DOT ABOVE (U+0307)`, which makes
substring matching silently fail.

```python
>>> "İdman".casefold()
'i\u0307dman'       # i + combining dot above
>>> "idman" in "İdman".casefold()
False               # SURPRISE — combining char breaks match
```

**Fix**: Replace İ with i before lowercasing, or use direct substring:

```python
# SIMPLEST — replace İ manually
query = "idman"
if query in summary.lower().replace('İ', 'i'): ...

# OR Unicode normalization
import unicodedata
normalized = unicodedata.normalize('NFKC', summary).lower()
if query in normalized: ...
```

The same bug affects `str.lower()` in non-Turkish locales (tr_TR locale
handles it correctly, en_US does not).

### 2. Emoji Prefixes in Turkish Summaries

Turkish users heavily prefix event/task titles with emoji + space:

- `🧠 İdman — Gün 5`
- `📬 APA bültenlerine kaydol`
- `📝 VIZJA Başvurusu`
- `🏋️ Gün 1: Bacak`

**Don't**: Match by startswith or exact match.
**Do**: Strip leading emoji or use flexible substring matching:

```python
import re
# Strip leading emoji + optional trailing space
clean = re.sub(r'^[\U0001F300-\U0001FAFF\U0001F600-\U0001F64F\U00002702-\U000027B0\U000024C2-\U0001F251]+\s*', '', summary)
if query in clean.lower().replace('İ', 'i'): ...
```

### 3. Google Calendar Default Max is 25

When using `google_api.py calendar list`, the default maxResults is 25.
For comprehensive operations (delete-all matching a pattern, full audit),
always override:

```bash
$GAPI calendar list --start 2026-01-01T00:00:00Z --end 2026-12-31T23:59:59Z --max 250
```

Without this, older events silently vanish from results. The Calendar API
caps single-page responses at 2500, so pagination is needed for >2500 events.

### 4. Cross-Calendar Searches

The `google_api.py` script queries `--calendar primary` by default. To
search ALL calendars (including shared/holiday/secondary), use the Python
API directly:

```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from pathlib import Path
import os

HERMES_HOME = Path(os.environ.get('HERMES_HOME', '~/.hermes')).expanduser()
TOKEN_PATH=*** / 'google_token.json'

creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

service = build('calendar', 'v3', credentials=creds)

# List all calendars
calendars = []
page_token = None
while True:
    cal_list = service.calendarList().list(pageToken=page_token).execute()
    calendars.extend(cal_list.get('items', []))
    page_token = cal_list.get('nextPageToken')
    if not page_token:
        break

# Search each for matching events
for cal in calendars:
    events = service.events().list(
        calendarId=cal['id'],
        timeMin='2026-01-01T00:00:00Z',
        timeMax='2026-12-31T23:59:59Z',
        maxResults=250,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    for e in events.get('items', []):
        summary = e.get('summary', '')
        if target in summary.lower().replace('İ', 'i'):
            print(f"[{cal.get('summary','')}] {summary} | {e['id']}")
```

## Related

- `google-workspace` — Google API wrapper that exhibits pitfalls #3 and #4
- Localization issues affect: PostgreSQL ILIKE, JavaScript .toLowerCase(), 
  Java String.toLowerCase(), and most regex engines

## Triggers

Load this skill when:
- User mentions Turkish characters, locale, or encoding issues
- Searching text that may contain Turkish İ/ı/ğ/ü/ş/ö/ç
- Working with Google Calendar events in Turkish
- User complains about "bulamadın" or "göremedin" (couldn't find) when searching
- Processing user-created content with emoji-prefixed titles
