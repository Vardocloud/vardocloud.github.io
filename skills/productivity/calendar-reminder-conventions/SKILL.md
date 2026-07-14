---
name: calendar-reminder-conventions
description: "Calendar reminder behavior for Edel's Google Calendar — read offset from event, calendar > profile."
version: 1.0.0
author: Vanitas
license: MIT
metadata:
  hermes:
    tags: [calendar, reminders, Google Calendar, best-practices]
    applies_to: [Edel]
---

# Calendar Reminder Conventions

Context for Edel's Google Calendar — rules for reminder timing and data priority.

## Reminder offset: read from event, don't hardcode

Edel sets per-event reminder offsets in Google Calendar:
- **Default**: 30 minutes before event start
- **When Edel changes it**: typically 1 hour (or custom)

When computing reminder time:
1. Query event reminder settings (`reminders.useDefault`, `reminders.overrides`)
2. Compute: `event_start_time − reminder_offset`
3. That computed time overrides any fixed cron schedule — event-level is source of truth
4. Show the calculation in reply: "Etkinlik 07:00'de, offset 60 dk → hatırlat 06:00'da"

## Calendar is authoritative over profile/memory

- Profile notes (e.g. "Bugün cafe mesai 17-23") are recurring context, not current-state data
- They do NOT imply anything about tomorrow or future days
- When uncertain about a date: query calendar, don't infer from profile
- "Bugün/yarn/sabah" derivations must come from calendar event dates only

## Manual cron job workflow (when `cronjob` tool is unavailable)

When `cronjob` tool is not in the available tools list, use this manual workflow:

### Step 1: Create reminder script
```bash
# ~/.hermes/cron/reminder_<event-name>_<YYYY-MM-DD>.sh
#!/bin/bash
cd /home/ubuntu/.hermes
source venv/bin/activate 2>/dev/null
LOGFILE="/home/ubuntu/.hermes/logs/cron_reminders.log"
curl -s -X POST http://localhost:8642/api/chat/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "[Natural reminder with one open-ended question]",
    "platform": "telegram"
  }' >> "$LOGFILE" 2>&1
```

### Step 2: Create follow-up script (event_end + 15min)
```bash
# ~/.hermes/cron/followup_<event-name>_<YYYY-MM-DD>.sh
#!/bin/bash
cd /home/ubuntu/.hermes
source venv/bin/activate 2>/dev/null
LOGFILE="/home/ubuntu/.hermes/logs/cron_followups.log"
curl -s -X POST http://localhost:8642/api/chat/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "[Sohbet skill follow-up: ONE question, warm tone]",
    "platform": "telegram"
  }' >> "$LOGFILE" 2>&1
```

### Step 3: Set permissions and add to crontab
```bash
chmod +x /home/ubuntu/.hermes/cron/reminder_*.sh /home/ubuntu/.hermes/cron/followup_*.sh

# Write crontab preserving existing entries
crontab -l > /tmp/crontab_edit.txt
echo "# Context comment" >> /tmp/crontab_edit.txt
echo "<cron_schedule> /home/ubuntu/.hermes/cron/<script>.sh >> /home/ubuntu/.hermes/logs/<logfile>.log 2>&1" >> /tmp/crontab_edit.txt
crontab /tmp/crontab_edit.txt
```

### Step 4: Verify
```bash
crontab -l
```

### Reminder message style
- Sohbet skill rules apply: ONE question, open-ended, warm tone
- Reminder: "<activity> <time> sonra başlıyor ☕️ Hazır mısın? Bugün yoğun olur mu sence?"
- Follow-up: "<activity> bitti mi? Nasıl geçti bugün? Yoğun muydu yoksa rahat mıydı?"

### Gateway health check
Before relying on cron-to-gateway messaging, verify gateway is up:
```bash
curl -s http://localhost:8642/health
# Expected: {"status": "ok", "platform": "hermes-agent"}
```

## Anti-patterns

❌ Inferring future events from past profile entries  
❌ Using hardcoded 30-min offset without checking actual event  
❌ Letting fixed cron time override event-specific reminder offset  
❌ Changing cron job model/provider based on old error logs — always verify error timestamp and current config before acting  
❌ Moving DeepSeek (Edel's primary model) off any cron job without explicit confirmation  
❌ Assuming `cronjob` tool is always available — check tool list first, fall back to manual shell+crontab workflow
❌ **Edel bir gün/etkinlikten bahsettiğinde takvime BAKMADAN varsayma.** "Yarın ofisteyim" dediğinde önce takvimi sorgula, yoksa ekle, varsa teyit et. Takvime bakmamak Edel'in güvenini kaybettirir. (30 Mayıs 2026)

## Cron job debugging (critical)

When `cronjob list` shows `last_status: "error"`:

1. **Check the error timestamp** — open `~/.hermes/cron/output/<job_id>/<timestamp>.md` and verify the error is from the MOST RECENT run, not an old run
2. **Cross-check current config** — the error might be from a previous provider/model configuration that's no longer active
3. **Don't assume model = problem** — a 402/balance error from last week doesn't mean the model is broken today
4. **Never change the primary model (DeepSeek) without asking Edel first** — other jobs can use fallback providers, but the main model stays unless Edel says otherwise
5. **The `GOOGLE_API` path bug** (`SCRIPT_DIR / "google_api.py"`) is documented above — check this first for any calendar-related cron failure. See `references/morning-greeting-fix-2026-05-23.md` for the actual fix applied to `morning_greeting.py`.  

## Cron job script path patterns (critical)

When cron scripts invoke `google_api.py`:

❌ `SCRIPT_DIR = Path(__file__).resolve().parent` then `GOOGLE_API = SCRIPT_DIR / "google_api.py"` — this resolves to `~/.hermes/cron/google_api.py` which does not exist

✅ `HERMES_HOME = Path.home() / ".hermes"` then `GOOGLE_API = HERMES_HOME / "skills" / "productivity" / "google-workspace" / "scripts" / "google_api.py"`

This bug appears in any Python cron script under `~/.hermes/cron/` that calls the Google Calendar API.

## Scripts

- `scripts/evening_precheck.py` — Reference implementation for pre-event reminder + post-event 5N1K follow-up job scheduling. Copy to `~/.hermes/cron/` and add to crontab (`0 21 * * *`). Handles: tomorrow's events via Google Calendar API, creates one-shot jobs for reminder (event − 2h) and follow-up (event_end + 15min), wiki context check, sohbet 5N1K prompts. Uses `HERMES_HOME / "skills" / "productivity" / "google-workspace" / "scripts" / "google_api.py"` for the API path.

```
1. Query: GAPI calendar list (with reminder data)
2. Read: reminder.useDefault + reminders.overrides
3. Compute: event_start − offset
4. Show: "Etkinlik X'te, offset Y dk → hatırlat Z'de"
```

## Direct Python API for Calendar Events (GAPI CLI timeout fallback)

The `$GAPI calendar create` CLI command can hang/timeout in some environments (Hermes terminal blocking with `BLOCKED: Command timed out`). `calendar list` works fine, but `create` hangs — likely a `gws` delegation issue in `google_api.py`.

**WORKING APPROACH — direct Python API:**

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pathlib import Path

creds = Credentials.from_authorized_user_file(
    str(Path.home() / '.hermes' / 'google_token.json'),
    ['https://www.googleapis.com/auth/calendar'])
service = build('calendar', 'v3', credentials=creds)

event = {
    'summary': 'Event Title',
    'description': 'Optional description text',
    'start': {'dateTime': '2026-06-24T21:00:00+03:00', 'timeZone': 'Europe/Istanbul'},
    'end': {'dateTime': '2026-06-24T21:30:00+03:00', 'timeZone': 'Europe/Istanbul'},
    'reminders': {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 120}]}
}
result = service.events().insert(calendarId='primary', body=event).execute()
# result['id'], result['htmlLink'] available
```

**Batch creation pattern:** Multiple events in one Python invocation (they share the same `service` object). Avoids sequential CLI calls and reduces per-event overhead. Use `ALL_PROXY=""` prefix if WARP proxy blocks Google APIs.

This approach also supports `--reminder 120` style popup reminders that push to the user's phone — no cron dependency. Cannot set SMS/email reminders via API (those are per-user defaults).

## Dual-layer reminder pattern (cron + calendar)

When the user asks you to set up a cron-based reminder (e.g. "yarın hatırlat"), ALWAYS also create a Google Calendar event as backup. Users explicitly want this ("Cron cevap üretemezse"). Triple redundancy where possible:

| Layer | Mechanism | Failure mode |
|-------|-----------|--------------|
| 1 | Cron job → Telegram message | LLM output blocked by content filter |
| 2 | Google Calendar event → phone notification | Network/API down |
| 3 | Calendar reminder (120min before) → phone push | User muted phone |

Implementation:
1. Create cron job (cronjob tool) — primary delivery
2. Create Google Calendar event (direct Python API or `$GAPI calendar create`) — fallback delivery
3. Both deliver to the same thread/chat

Do NOT skip step 2 even if the cron tool creates successfully. Calendar is the user's safety net.

## Reminder delivery

Prefer Google Calendar native event reminders (they bypass Azure content filtering).
For LLM-generated delayed messages: only use when native reminders unavailable.
Always use the event's actual reminder text verbatim — don't paraphrase.