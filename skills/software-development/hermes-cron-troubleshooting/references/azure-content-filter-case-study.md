# Azure Content Filter Case Study — morning_greeting & evening_precheck

**Date:** 2026-06-07
**Jobs Affected:** `morning_greeting`, `evening_precheck`
**Provider:** `custom:Pollinations` (model: `gpt-5.4-mini`)

## Timeline

| Time | Event |
|------|-------|
| 07:00 | `morning_greeting` runs, fails with `content_policy_blocked` from Azure OpenAI |
| 12:xx | User reports: "Limits are full. We must find a solution to use pollination models." |
| 12:xx | Diagnosis: Pollinations uses Azure OpenAI → aggressive content filter blocks even benign Turkish prompts |
| 12:xx | Fix: Move `morning_greeting` + `evening_precheck` to `custom:opencode-go` with `deepseek-v4-flash` |
| 12:xx | Additional fix: Move `linkedin_sabah` + `linkedin_aksam` FROM `opencode-zen` TO `custom:Pollinations` (per SOUL.md: APA/LinkedIn writing allowed on Pollinations) |

## Error Details

```
RuntimeError: content_policy_blocked: HTTP 400: 400 Bad Request: azure-openai error: The response was filtered due to the prompt triggering Azure OpenAI's content management policy. Please modify your prompt and retry. To learn more about our content filtering policies please read our documentation: https://go.microsoft.com/fwlink/?linkid=2198766
```

**Prompt that triggered it:**
```
Günaydın Edel! Bugün nasıl hissediyorsun? Takvimden bugünün etkinliklerine bak, varsa hatırlat. Wiki...
```

Completely benign Turkish greeting + calendar check.

## Root Cause Analysis

1. **Pollinations → Azure OpenAI backend** — The free `gpt-5.4-mini` model on Pollinations routes through Azure OpenAI
2. **Azure Content Safety** — Microsoft's content moderation system with aggressive filters
3. **False positives** — Even simple Turkish greetings trigger the filter (possibly due to language model quirks or overly sensitive patterns)
4. **Not prompt-fixable** — Changing the prompt doesn't reliably work; the filter is stochastic and platform-level

## Provider Routing Rules (from SOUL.md)

| Job Category | Provider | Model | Tool Calling |
|--------------|----------|-------|--------------|
| Routine (greetings, security, Gmail, Skool, Bundle, APA check, Deep Dive, LinkedIn check, Synthesis, Half Security) | `custom:opencode-go` | `deepseek-v4-flash` | ✅ |
| Deep Analysis (Full Security, IG Analysis) | `custom:opencode-go` | `glm-5.1` | ✅ |
| Free Tier (Vanitas Dream) | `opencode-zen` | `deepseek-v4-flash-free` | ✅ |
| **APA Writing, LinkedIn Writing** | `custom:Pollinations` | `gpt-5.4-mini` | ❌ |

## Key Insight: Tool Dependency Determines Provider

**Jobs requiring tools CANNOT use Pollinations.** Pollinations has NO tool calling support.

| Job | Tools Needed | Can Use Pollinations? |
|-----|--------------|----------------------|
| morning_greeting | google-workspace (Calendar) | ❌ |
| evening_precheck | google-workspace (Calendar) | ❌ |
| Yarım Güvenlik | terminal (ss, journalctl) | ❌ |
| Tam Güvenlik | terminal (ss, netstat, ufw) | ❌ |
| Gmail Pipeline | google-workspace, email-knowledge-pipeline | ❌ |
| Gmail Deep Dive | google-workspace, email-knowledge-pipeline | ❌ |
| Skool Check | warp-proxy, browser | ❌ |
| Bundle News | web_search, terminal | ❌ |
| APA Check | browser, notebooklm-pipeline | ❌ |
| LinkedIn Writing | **None** (pure text) | ✅ |
| Vanitas Dream | session_search, llm-wiki | ✅ (but use opencode-zen free) |

## Load Balancing Result

After fixes:

**opencode-go (Paid, Tool-Capable) — 4 jobs:**
- `morning_greeting` (0 7 * * *)
- `evening_precheck` (0 21 * * *)
- `Bundle Gündem` (15 6,10,16 * * *)
- `Tam Güvenlik` (0 7 * * 0)

**opencode-zen (Free, Tool-Capable) — 7 jobs:**
- `Vanitas Rüya` (0 4 * * *)
- `Yarım Güvenlik` (0 6 * * *)
- `APA Günlük` (30 9,15,21 * * *)
- `Gmail Pipeline` (0 10,16,22 * * *)
- `Gmail Deep Dive` (0 2 * * *)
- `Günlük Sentez` (0 23 * * *)
- `Skool Daily` (15 9 * * *)
- `IG Analiz` (45 9 * * 1-5)

**Pollinations (Free, No Tools) — 2 jobs:**
- `linkedin_sabah` (0 9 * * *)
- `linkedin_aksam` (30 20 * * *)

## Remaining Pressure

`opencode-go` still has 4 jobs (all tool-dependent, cannot move). If rate limits persist:
1. Reduce `Bundle Gündem` frequency (currently 3x/day)
2. Stagger schedules to avoid concurrent runs
3. Request quota increase from provider
4. Accept occasional failures (Watchdog will alert)

## Files Modified

- `~/.hermes/cron/jobs.json` — Updated `morning_greeting`, `evening_precheck`, `linkedin_sabah`, `linkedin_aksam`
- Verified `base_url` correctness for all changed jobs

## Verification

```bash
# Check all jobs have correct provider + base_url
python3 -c "
import json
with open('/home/ubuntu/.hermes/cron/jobs.json') as f:
    jobs = json.load(f)
for j in jobs:
    print(f\"{j['name']:30s} provider={j.get('provider','?'):20s} model={j.get('model','?'):20s} base_url={j.get('base_url','?')}\")
"
```