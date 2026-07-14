# opencode-go Weekly Rate Limit Case Study — 2026-06-07

## Incident Summary
**Job:** `Bundle Gündem İşleme` (job_id: `93582f1545d2`)
**Schedule:** `15 6,10,16 * * *` (3×/day = 21×/week)
**Error:** `RuntimeError: HTTP 429: Weekly usage limit reached. Resets in 16hr 45min.`

## Root Cause
- Job used `deepseek-v4-flash` via `custom:opencode-go` (paid provider with weekly quota)
- 21 executions/week exceeded the free workspace quota
- Other routine jobs (APA, Gmail Deep Dive, Skool, Daily Synthesis, Half Security) already used `opencode-zen` free tier and were unaffected

## Resolution
Migrated the job to free tier:
```json
{
  "model": "deepseek-v4-flash-free",
  "provider": "opencode-zen"
}
```

## Systematic Cleanup (Same Session)
Following the Bundle fix, user requested migration of ALL remaining opencode-go jobs to free tier:

| Job | Before | After |
|-----|--------|-------|
| Bundle Gündem | deepseek-v4-flash / opencode-go | deepseek-v4-flash-free / opencode-zen |
| Tam Güvenlik (Haftalık) | glm-5.1 / opencode-go | nemotron-3-ultra-free / opencode-zen |
| weekly_curator | qwen3.7-max / opencode-go | nemotron-3-ultra-free / opencode-zen |

## Result
**All 23 cron jobs now run on free tiers:**
- 17 jobs on `opencode-zen` (deepseek-v4-flash-free, nemotron-3-ultra-free, mimo-v2.5-free)
- 2 jobs on `Pollinations` (gpt-5.4-mini) — APA & LinkedIn writing only (per SOUL.md)
- 4 jobs are `no_agent: true` shell scripts
- **0 jobs on `custom:opencode-go`** (paid)

## Key Learnings
1. **opencode-go weekly quota is workspace-level** — cannot be bypassed by key rotation (proxy injects internal key)
2. **opencode-zen free models support tool calling** — unlike Pollinations, they can use web_search, terminal, file ops
3. **Strategy D model assignment works** — routine → free flash, deep analysis → free ultra, writing → free flash/Pollinations
4. **Migration is trivial** — single `cronjob update` call with new model/provider

## Prevention
- When creating new routine cron jobs, default to `opencode-zen` + `deepseek-v4-flash-free`
- Reserve `custom:opencode-go` for: Kanban workers needing paid models, complex coding, heavy reasoning
- Monitor `agent.log` for 429 patterns weekly