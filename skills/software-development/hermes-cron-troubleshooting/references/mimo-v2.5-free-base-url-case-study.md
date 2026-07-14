# Case Study: mimo-v2.5-free "Invalid model" via base_url Contamination (2026-06-08 morning_greeting)

## Background
`morning_greeting` cron job ran daily at 07:00 to greet Edel, check the calendar, and prepare reminders. Configured with `mimo-v2.5-free` via `opencode-zen`.

## Error
```
RuntimeError: Error code: 400 - {'success': False, 'error': {'message': 'Invalid model or alias: "mimo-v2.5-free". Must be a valid model name or alias.', 'code': 'BAD_REQUEST', 'timestamp': '2026-06-08T04:00:48.520Z'}, 'status': 400}
```

## Diagnosis

### Step 1: Check cron job config
Listed all jobs via `cronjob(action='list')`. Found `morning_greeting` with:
- `model`: `mimo-v2.5-free`
- `provider`: `opencode-zen`
- `base_url`: `http://127.0.0.1:19999/v1`

### Step 2: Compare with working job
`evening_precheck` had the same model+provider but **no base_url** — and it worked. The contrast immediately flagged `base_url` as the culprit.

### Step 3: Verify the mismatch
`http://127.0.0.1:19999/v1` is the Pollinations UA proxy. Pollinations doesn't serve `mimo-v2.5-free` — that model only exists on `opencode-zen`'s built-in endpoint. The stale `base_url` was routing requests to the wrong proxy.

## Root Cause
The `base_url` was set to the Pollinations proxy (`:19999`) from a previous configuration. When the provider was changed to `opencode-zen`, the `cronjob(action='update')` tool:
- Updated `model` ✓
- Updated `provider` ✓  
- Did NOT clear `base_url` ✗

## Fix
Removed the `base_url` field directly from `~/.hermes/cron/jobs.json`:

```
patch(
  path='/home/ubuntu/.hermes/cron/jobs.json',
  old_string='"base_url": "http://127.0.0.1:19999/v1"',
  new_string=''
)
```

The patch also removed the trailing comma from the preceding line, maintaining valid JSON.

After fix, verified:
```
"model": "mimo-v2.5-free",
"provider": "opencode-zen",
"paused_at": null,
"paused_reason": null
```
— no `base_url` field present.

## Key Insight
The error message `"Invalid model or alias: 'mimo-v2.5-free'"` is misleading — the model IS valid. The actual problem is the endpoint receiving the request. Always check `base_url` when provider changes don't match expectations.

## Timeline
- 07:00 — Job scheduled, failed with "Invalid model" error
- ~08:30 — Edel reported error, investigation started
- ~08:31 — `cronjob list` revealed base_url contamination
- ~08:32 — `base_url` removed from jobs.json via patch
- ~08:33 — `cronjob run` test passed (base_url: null)
- Total time to resolve: ~3 min

## Cross-Reference
- Same pattern as `references/base-url-contamination-case-study.md` (evening_precheck, deepseek-v4-flash-free + opencode-zen + Pollinations base_url)
- Key difference: `mimo-v2.5-free` model instead of `deepseek-v4-flash-free`
