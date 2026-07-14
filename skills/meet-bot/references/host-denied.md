# Host Denied Admission — Diagnostic Guide

## Symptom

```bash
hermes meet status
# {
#   "ok": true,
#   "alive": false,
#   "inCall": false,
#   "error": "host denied admission",
#   "leaveReason": "denied",
#   "joinAttemptedAt": <timestamp>,
#   "joinedAt": null,
#   "lobbyWaiting": false
# }
```

## Two Possible Root Causes

### 1. Host actually denied (REAL)
1. Bot navigated to meet.google.com URL ✅
2. Bot clicked "Ask to join" button ✅
3. Bot appeared in lobby as guest name (e.g., "Sudenaz") ✅
4. Host saw the join request and clicked **Deny** ❌
5. Bot detected "You can't join this video call" text on page → set `error: "host denied admission"`

**Fix:** Message the host to accept, or use an authed account (no lobby).

### 2. False positive — "browser not supported" interstitial (FAKE ⚠️)
1. Bot navigated to meet URL ✅
2. Google Meet showed "This browser version is no longer supported" interstitial ✅
3. Interstitial page contains "You can't join this video call" in the warning banner ✅
4. `_detect_denied()` sees this text and incorrectly returns True ❌
5. Bot sets `error: "host denied admission"` even though it never reached the join screen

**Key indicator:** Edel says "bana istek gelmedi" (no join request arrived).

**Fix:** Call `_handle_unsupported_browser()` after `page.goto()` to dismiss the banner,
kill the redirect countdown timer, and click "Continue without microphone".
See `references/browser-unsupported.md` for the full fix.

## Detection Code (meet_bot.py:783+)

The `_detect_denied()` function checks for these English strings in page body:
- `You can't join this video call` ← Also appears in "browser unsupported" banner!
- `You were removed from the meeting`
- `No one responded to your request to join`

## Diagnostics Commands

```bash
# Full status
hermes meet status

# Raw status.json
cat ~/.hermes/workspace/meetings/<meeting-id>/status.json

# Bot log (usually minimal)
cat ~/.hermes/workspace/meetings/<meeting-id>/bot.log
```

## Known Instance

2026-05-25: kaf-qrzs-vjz — Two attempts, both denied. Name "Sudenaz", host unknown.
2026-06-13: kkd-ugsq-mkn — False positive. "browser not supported" interstitial caused detection error.
