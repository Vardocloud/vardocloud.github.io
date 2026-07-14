# Google OAuth Testing Mode Token Lifecycle

This reference documents the Google OAuth Testing mode limitation that affects
all cron scripts using `google_api.py`.

## The Problem

Google Cloud OAuth apps in **Testing mode** (unverified) issue refresh tokens
that expire after ~7 days. After expiry, all API calls fail with:
```
invalid_grant: Token has been expired or revoked.
```

## Detection

The `refresh_google_token.sh` script exits with code 2 and prints:
```
⚠️ Google token expired! Edel'e bildir
```

This is triggered by grep for `invalid_grant` in the API response.

## Quick Fix (re-auth without redoing client setup)

```bash
GSETUP="python ${HERMES_HOME}/skills/productivity/google-workspace/scripts/setup.py"
$GSETUP --revoke           # optional: clean up old token
$GSETUP --auth-url         # generate new auth URL → send to user
$GSETUP --auth-code CODE   # user authorizes, paste code
$GSETUP --check            # verify AUTHENTICATED
```

## Cron Script Token Path Pitfall

The cron `gmail_check.sh` had TWO bugs (fixed 10 Jul 2026):
1. Pointed to stale `google_token_ubuntu.json` instead of `google_token.json`
2. Grepped `^Subject:` on JSON output (always 0 matches)

Fix 1: Use `$HERMES_HOME/google_token.json` consistently.
Fix 2: Delegate JSON parsing to Python. See `references/json-api-parsing-pattern.md`
in this skill for the pattern.

Also affected: `morning_greeting.sh` (same stale path, fixed).
