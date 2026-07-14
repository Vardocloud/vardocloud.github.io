# Morning Greeting Script Fix

**Session:** 2026-05-23
**Script:** `~/.hermes/cron/morning_greeting.py`
**Bug:** `GOOGLE_API = SCRIPT_DIR / "google_api.py"` → resolves to `~/.hermes/cron/google_api.py` (does not exist)

## Fix Applied

Line 17 changed from:
```python
GOOGLE_API = SCRIPT_DIR / "google_api.py"
```
To:
```python
GOOGLE_API = HERMES_HOME / "skills" / "productivity" / "google-workspace" / "scripts" / "google_api.py"
```

## Verification

After fix, manually triggered with `cronjob action=run job_id=morning_greeting`. Script runs without GOOGLE_API path error.

## Related

This is the same bug pattern documented in `calendar-reminder-conventions/SKILL.md` → "Cron job script path patterns". Any Python script under `~/.hermes/cron/` that calls Google Calendar API should use `HERMES_HOME / "skills" / "productivity" / "google-workspace" / "scripts" / "google_api.py"`, never `SCRIPT_DIR / "google_api.py"`.
