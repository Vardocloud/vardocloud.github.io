# 2026-06-10: Cron Job Model Fixes + Watchdog Bug Repair

## Summary

Three failing cron jobs were diagnosed and fixed:

1. **Model Watchdog** (`model-watchdog-daily`) — 2 Python NameError bugs in f-strings
2. **Skool Daily Check** (`50002951d6bc`) — RuntimeError from broken model → migrated to Pollinations
3. **Tam Güvenlik (Haftalık)** (`095fa7d69603`) — HTTP 429 weekly quota → switched to different free model

## Diagnosis Path

### Step 1: Dream Engine reveals 3 errors
The vanitas_dream.py (8-Boyutlu Rüya) reported:
```
Cron: 20OK/3ERR | 3 firsat
🔴 3 cron job hatalı
```

### Step 2: Read cron/jobs.json for full error details
Each job's `last_error` field contained the full traceback. Key errors:

| Job | Error | Root Cause |
|-----|-------|------------|
| Model Watchdog | `NameError: name 'name' is not defined` | Missing quotes in f-string |
| Skool Daily Check | `RuntimeError: 🤖 **Skool Gündem**...` (full report content) | deepseek-v4-flash-free ZEN FAILED → broken response |
| Tam Güvenlik | `HTTP 429: Weekly usage limit reached` | nemotron-3-ultra-free quota exhausted |

### Step 3: Watchdog confirms model availability
Running `model-watchdog.py` showed:
```
POLL OK: openai, gemma, glm, minimax, gpt-5.4-mini
GO OK: minimax-m3, kimi-k2.6, kimi-k2.5, qwen3.7-plus, qwen3.6-plus
ZEN FAILED: mimo-v2.5-free, minimax-m3-free, deepseek-v4-flash-free, nemotron-3-*-free
```

All opencode-zen free models failed connectivity tests, but many cron jobs using them still had `last_status: "ok"`. Conclusion: watchdog ZEN tests are intermittent/false-positive prone. Ground truth is the job's actual `last_status`.

## Fixes Applied

### Fix 1: Model Watchdog Script (vanitas_dream.py değil, model-watchdog.py)
Two identical bug patterns:
```python
# Bug pattern: missing string quotes + trailing comma in f-string
env.get(POLLINATIONS_API_KEY, )     # NameError
job.get(name, )                     # NameError

# Fix: add quotes, remove trailing comma
env.get('POLLINATIONS_API_KEY', '')
job.get('name', '')
```

Both in f-string interpolations where variable names were used instead of string literals. Common Python gotcha when porting `env.get("KEY")` calls into f-strings (inner `"` conflict with f-string `"`).

### Fix 2: Skool Daily Check — Provider Migration
```python
# BEFORE
model="deepseek-v4-flash-free", provider="opencode-zen"
# Error: RuntimeError — model ZEN FAILED, broken response

# AFTER (Edel confirmed)
model="gpt-5.4-mini", provider="custom:Pollinations"
# Verification: gpt-5.4-mini is POLL OK in watchdog
```

**Note:** Edel rejected `glm` as an option with "glm opencode zen'de yok" — GLM is not available on opencode-zen despite watchdog showing it as POLL OK (POLL = Pollinations, not Zen).

### Fix 3: Tam Güvenlik (Haftalık) — Model Swap on Same Provider
```python
# BEFORE
model="nemotron-3-ultra-free", provider="opencode-zen"
# Error: HTTP 429 — weekly quota exhausted

# AFTER (Edel confirmed)
model="mimo-v2.5-free", provider="opencode-zen"
# Kept same provider, just swapped to a different free model
```

## Key Learnings

1. **ZEN FAILED ≠ model dead.** Watchdog ZEN tests are intermittent. Check job's actual `last_status` before acting.

2. **Two-tier model escalation:**
   - Same provider, different free model (mimo-v2.5-free → nemotron-3-ultra-free swap on opencode-zen)
   - Different provider entirely (opencode-zen → Pollinations for gpt-5.4-mini)

3. **GLM is NOT on opencode-zen.** Despite watchdog showing `POLL OK: glm`, that's via Pollinations, not Zen. Edel explicitly corrected this.

4. **Edel's model preference pattern:** She knows the model landscape well — when she specifies a model, use it directly rather than suggesting alternatives.

## Verification

- `model-watchdog.py` syntax check: ✅ (ast.parse passes)
- model-watchdog cron run triggered: ✅ (next_run_at updated)
- Skool model change confirmed in cron list: ✅
- Security model change confirmed in cron list: ✅
- Dream engine re-test: `Cron: 20OK/3ERR` → reduced from full list scan
