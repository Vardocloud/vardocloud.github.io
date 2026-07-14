# Case Study: base_url Contamination (2026-06-06 evening_precheck)

## Background
`evening_precheck` cron job ran daily at 21:00 to check tomorrow's calendar, create reminders, and warm-check any early-morning events. Originally configured with `gpt-5.4-mini` via `custom:Pollinations`.

## Trigger
Job started failing with:
```
RuntimeError: content_policy_blocked: HTTP 400: 400 Bad Request: azure-openai error:
The response was filtered due to the prompt triggering Azure OpenAI's content management policy.
```

## Diagnosis Attempts (in order)

### 1. Prompt Rewrite (Turkish → English)
**Hypothesis:** Turkish prompt + `sohbet` skill together tripped Azure filters.
**Action:** Changed prompt from Turkish to English, removed potentially triggering words ("tactics" → "natural conversational tone").
**Result:** Same error. Azure filter was NOT prompt-content driven — it was the combined system prompt context.

### 2. Further Simplification
**Hypothesis:** Even the English prompt + loaded skills created a "suspicious" combined context.
**Action:** Reduced prompt to minimal: "Check tomorrow's calendar. Create reminders if needed. If empty, stay quiet. Reply in Turkish."
**Result:** Same error. Confirmed the issue was NOT prompt text — Azure was filtering the full system context.

### 3. Pollinations Health Check
**Action:** curl to `http://127.0.0.1:19999/v1/models` — timed out (proxy was running but not responding to that endpoint). Direct API hit returned 403.
**Finding:** Pollinations proxy was healthy but Azure backend was filtering our requests. Not a connectivity issue.

### 4. Provider Switch (the fix... and the new bug)
**Action:** Switched model to `deepseek-v4-flash-free` via `opencode-zen`:
```
cronjob(action='update', job_id='evening_precheck', model={"model": "deepseek-v4-flash-free", "provider": "opencode-zen"})
```
**New error:**
```
RuntimeError: Error code: 400 - Invalid model or alias: "deepseek-v4-flash-free".
Must be a valid model name or alias.
```

### 5. Root Cause Discovery
**Investigation:** Checked `jobs.json` directly with Python:
```python
import json
with open('/home/ubuntu/.hermes/cron/jobs.json') as f:
    jobs = json.load(f)
for j in jobs:
    if j['name'] == 'evening_precheck':
        print(j.get('base_url'))
```
**Output:** `http://127.0.0.1:19999/v1`

**Root cause:** `cronjob update` changed `provider` to `opencode-zen` but did NOT clear the old `base_url` from `custom:Pollinations`. The request was being sent to Pollinations' proxy (`:19999`), which doesn't know about `deepseek-v4-flash-free` — that model only exists on `opencode-zen`'s built-in endpoint.

### 6. Fix
```python
patch(path='/home/ubuntu/.hermes/cron/jobs.json',
      old_string='"base_url": "http://127.0.0.1:19999/v1"',
      new_string='"base_url": null')
```
**Result:** Job ran successfully with `last_status: ok`.

## Key Insight
`cronjob(action='update')` modifies `model` and `provider` fields atomically but leaves `base_url` untouched. When changing providers, always verify `base_url` matches:

| Provider | Correct base_url |
|----------|-----------------|
| `opencode-zen` | `null` (always) |
| `custom:opencode-go` | `http://127.0.0.1:19998/v1` |
| `custom:Pollinations` | `http://127.0.0.1:19999/v1` |

## Timeline
- 21:00 — Job scheduled, failed (Azure filter)
- 21:05 — Prompt changed to English, still failed
- 21:10 — Prompt simplified further, still failed
- 21:15 — Pollinations health check, confirmed proxy alive but Azure filtering
- 21:20 — Switched to deepseek-v4-flash-free + opencode-zen
- 21:22 — New error: "Invalid model or alias" — base_url contamination discovered
- 21:25 — base_url cleared to null, job ran successfully
- Total time to resolve: ~25 min
