---
name: hermes-cron-troubleshooting
description: Diagnose Hermes cron job failures — delivery to wrong Telegram topic, silent thread fallback, truncation errors from free models, model/provider selection.
---

# Hermes Cron Job Troubleshooting

Systematic diagnosis for Hermes Agent cron job failures. Covers delivery misrouting, model errors, and silent fallbacks.

## Trigger Conditions
- Cron job delivers to wrong Telegram topic/thread
- `RuntimeError: Response remained truncated after N continuation attempts`
- Job output appears in general chat instead of target topic
- "delivered to X" in logs but user sees it in different thread
- Model/provider changes cause unexpected failures

## Pitfall: Telegram Thread Delivery — `origin.thread_id` vs `deliver`

### Symptom
Job config has correct `deliver: "telegram:<chat_id>:<thread_id>"` but messages land in general chat (thread 1).

### Root Cause
The `origin.thread_id` (set when job was CREATED) differs from the `deliver.thread_id`. If Telegram adapter hits a silent `thread_fallback` (thread not found → 2 retries → drops `message_thread_id`), the message falls back to the general chat with NO WARNING logged at INFO level.

The adapter in `gateway/platforms/telegram.py` (lines ~1976-2007):
```python
if _is_thread_not_found_error(send_err) and effective_thread_id is not None:
    if not retried_thread_not_found:
        retried_thread_not_found = True
        continue  # retry once with same thread_id
    # Second failure: silently drop message_thread_id
    logger.warning("Thread %s not found, retrying without message_thread_id", ...)
    used_thread_fallback = True
    effective_thread_id = None
    continue
```

### Fix
**Delete and recreate the job FROM the target topic.** This aligns `origin.thread_id` with `deliver.thread_id`:
```bash
# 1. List to find job_id
cronjob(action='list')

# 2. Remove old job
cronjob(action='remove', job_id='<old_id>')

# 3. Recreate with same config — origin will now be correct
cronjob(action='create', ...)
```

After recreation, verify both fields match:
```python
# Check in ~/.hermes/cron/jobs.json
"deliver": "telegram:<chat_id>:2920"
"origin": {"thread_id": "2920"}  # Now matches!
```

### Why Not Just Update `deliver`?
`cronjob(action='update', ...)` can change `deliver` but CANNOT change `origin`. The `origin` field is immutable — set at creation time.

### Why Recreating the Job Doesn't Always Fix It
Even with `origin.thread_id` matching `deliver.thread_id`, the Telegram adapter can still trigger silent `thread_fallback`. This happens when the Telegram API transiently returns "thread not found" (network hiccup, forum reindex, rate limit disguised as 404). Two consecutive failures → adapter drops `message_thread_id` → message lands in general chat. The scheduler logs a WARNING but the user sees a misrouted message with no visible error.

### Alternative Fix: Bypass Auto-Delivery with `send_message` Tool

**More reliable than job recreation.** Modify the cron job prompt to explicitly call `send_message` with the correct thread target, bypassing the scheduler's auto-delivery chain entirely:

```markdown
5. İşin bitince send_message tool'unu kullanarak sonucu ŞU hedefe gönder:
   target="telegram:-1003917030255:2920"
   
   Göndereceğin mesaj şu formatta olsun:
   >Rapor başlığı...
   >- bulgu 1
   >- bulgu 2
```

**Why this works:**
- `send_message` tool connects to the live Telegram adapter with a fresh session
- It does NOT go through the scheduler's `_deliver_result()` → `adapter.send(metadata={...})` path
- No `thread_fallback` mechanism — if the thread truly doesn't exist, it fails HARD with a visible error
- Verified working even when the auto-delivery chain silently drops thread_id

**When to use this vs job recreation:**
| Situation | Use |
|-----------|-----|
| Job was created from wrong topic → `origin.thread_id != deliver.thread_id` | Delete + recreate |
| `origin` matches but messages still go to general chat | `send_message` bypass |
| Critical delivery that must NEVER silently fail | `send_message` bypass |
| Simple job, no tools needed in prompt | Job recreation |

**Prompt modification checklist for `send_message` bypass:**
1. Remove or override the `[SILENT]` auto-delivery instruction from the job prompt
2. Add explicit `send_message(target="telegram:<chat_id>:<thread_id>")` at the end
3. Format the message inline in the prompt as a template for the cron agent
4. Verify with manual `cronjob(action='run', ...)` → check target topic

## Pitfall: Free Model Truncation Errors

### Symptom
```
RuntimeError: Response remained truncated after 3 continuation attempts
```
or job completes but output is partial/corrupted.

### Root Cause
`opencode-zen` (free models like `deepseek-v4-flash-free`) has a lower output token limit. Heavy jobs that produce large responses (15+ news items, wiki updates, NotebookLM archiving) exceed this limit.

The model keeps trying to continue the truncated response but hits the limit again (up to 3 attempts), then fails.

### Fix
Route heavy jobs to `custom:opencode-go` provider with paid models:
```python
model={"model": "deepseek-v4-flash", "provider": "custom:opencode-go"}
```

**Rule of thumb:** If a job prompt says "TÜM haberleri çek", "hepsini işle", "detailed report" → use `custom:opencode-go`. Routine light jobs (greetings, simple checks) can stay on `opencode-zen`.

## Pitfall: Pollinations 128 Tool Limit (LinkedIn Job'ları)

### Symptom
```
RuntimeError: Error code: 400 - {'success': False, 'error': {'message': "400 Bad Request: azure-openai error: Invalid 'tools': array too long. Expected an array with maximum length 128, but got an array with length 135 instead.", ...}}
```

Cron job fails immediately with HTTP 400. The model (gpt-5.4-mini via Pollinations) never receives the prompt.

### Root Cause
Pollinations routes `gpt-5.4-mini` through Azure OpenAI, which enforces a **128 tool definition limit**. Hermes loads all tools by default (~135+ tools) in its registry. However, `enabled_toolsets` in the cron job config filters the tools **before** they're sent to the API (via `model_tools.py:get_tool_definitions()`), reducing the array from ~135 to ~15-20 tools — well under the 128 limit.

This is NOT a content filtering issue — it's a tool count limit at the provider API level. The model itself doesn't even get to process the prompt if the tool array exceeds 128.

### Fix: enabled_toolsets ile Tool Sayısını Sınırla

`enabled_toolsets` **işe yarar** — Hermes'in `get_tool_definitions()` fonksiyonu, `enabled_toolsets` set edildiğinde sadece o kategorilerdeki araçları API'a gönderir:

```python
model={"model": "gpt-5.4-mini", "provider": "custom:Pollinations"}
enabled_toolsets = ["terminal", "web", "file", "search", "delegation"]
```

**Doğru yapılandırma (çalışan):**
- Model: `gpt-5.4-mini` (Pollinations)
- Provider: `custom:Pollinations`
- enabled_toolsets: `["terminal", "web", "file", "search", "delegation"]`

Bu şekilde tool sayısı ~15-20'ye düşer ve Pollinations üzerinden LinkedIn yazıları çalışmaya devam eder.

### ⚠️ Pitfall: Önce "Önceden Çalışıyor muydu?" Diye Sor

Pollinations hatasıyla karşılaştığında **hemen model/provider değiştirme**. Önce şunu sor:

1. **Bu cron job önceden çalışıyor muydu?** — Eğer çalışıyorsa, son değişiklik ne?
2. **Çalışırken aynı model/provider'ı kullanıyor muydu?** — Hiç değişmediyse, sorun model/provider'da değil, başka bir yerde (ör. enabled_toolsets bozuldu, job config değişti).
3. **Hata mesajını oku:** 128 tool limit hatası → `enabled_toolsets` ekle/control et. Başka bir hata → farklı çözüm.

Bu sırayı atlayıp direkt model değiştirmek = yanlış kök neden analizi.

### Doğru Çözüm: enabled_toolsets İle Pollinations'ı Koru

LinkedIn cron job'ları Pollinations üzerinde `enabled_toolsets` ile düzgün çalışır. Model/provider değişikliği yapmaya gerek yoktur.

### Verification After Fix
1. [ ] `enabled_toolsets` set edildi (`["terminal","web","file","search","delegation"]`)
2. [ ] Model: `gpt-5.4-mini`, Provider: `custom:Pollinations`
3. [ ] Manual `cronjob action='run'` succeeds without 400 error
4. [ ] Journal log shows no "Invalid 'tools'" or "array too long" errors

---

## Pitfall: Azure Content Filtering on Pollinations (gpt-5.4-mini)

### Symptom
```
RuntimeError: content_policy_blocked: HTTP 400: 400 Bad Request: azure-openai error: The response was filtered due to the prompt triggering Azure OpenAI's content management policy.
```

Even benign prompts like `"Günaydın Edel! Bugün nasıl hissediyorsun? Takvimden bugünün etkinliklerine bak..."` get blocked.

### Root Cause
`custom:Pollinations` routes to Azure OpenAI endpoints which enforce aggressive content moderation. The filter is **prompt-agnostic** — it can trigger on perfectly harmless Turkish greetings, calendar checks, or routine summaries. This is a platform-level filter, not a prompt issue.

### Fix
**Do not use Pollinations for routine/recurring jobs.** Reserve `gpt-5.4-mini` via Pollinations ONLY for:
- APA yazıları (APA content writing)
- LinkedIn yazıları (LinkedIn post writing)

Per SOUL.md: *"APA ve LinkedIn YAZILAR: gpt-5.4-mini (Pollinations) — Pollinations devam ediyor"*

For ALL other jobs (greetings, security checks, Gmail processing, Skool monitoring, Bundle news, daily synthesis, etc.), use:
- `custom:opencode-go` with `deepseek-v4-flash` (paid, tool-capable) — routine jobs
- `custom:opencode-go` with `glm-5.1` (paid, tool-capable) — deep analysis
- `opencode-zen` with `deepseek-v4-flash-free` / `mimo-v2.5-free` (free, tool-capable) — free tier jobs
### When Pollinations Is Acceptable

| Job Type | Pollinations OK? | Reason |
|----------|------------------|--------|
| APA writing (direct curl) | ✅ Yes | Explicitly allowed by SOUL.md. Uses EKİP curl calls, NOT Hermes agent loop |
| LinkedIn post writing | ✅ Yes (with enabled_toolsets) | `enabled_toolsets: ["terminal","web","file","search","delegation"]` ile tool sayısı ~15-20'ye düşer, 128 limitinin altında kalır. Model = `gpt-5.4-mini`, Provider = `custom:Pollinations` |
| Morning/evening greetings | ⚠️ Conditional | **Azure filter hatası alıyorsa** → ❌ Kullanma. **Token yenilenmişse (yeni API key) ve çalışıyorsa** → ✅ Kullanılabilir. `enabled_toolsets: ["terminal","web","file","search"]` ile 128 limitini aş. 2026-06-08 itibarıyla morning_greeting Pollinations'da çalışıyor. |
| Security audits | ❌ No | Needs tools (ss, netstat, journalctl) |
| Gmail/email processing | ❌ No | Needs google-workspace tools |
| Skool monitoring | ❌ No | Needs browser/warp-proxy tools |
| Bundle news ingestion | ❌ No | Needs web search + high output volume |
| Daily synthesis | ❌ No | Needs session_search + llm-wiki tools |

## Pitfall: Root-Owned Hermes Assets Breaking Ubuntu Cron Jobs

### Symptom
Cron script fails with `PermissionError` on a file under `/home/ubuntu/.hermes/`. Error messages include:
```
PermissionError: [Errno 13] Permission denied: '...google_token.json'
PermissionError: [Errno 13] Permission denied: '.../data/sentez_debug/...'
logging: Permission denied: '.../logs/job_recovery.log'
tee: /tmp/security_score.txt: Permission denied
```

### Root Cause
The Hermes entrypoint (`entrypoint.sh`) runs as root during container startup, and some initialization steps create files/directories under `$HERMES_HOME` as root. The Hermes gateway process itself (and therefore all cron job scripts) runs as `ubuntu`. When a root-owned file has `600` or `644` permissions, ubuntu can't write to it — and sometimes can't even read it.

Common root-owned files: `google_token.json`, `data/sentez_debug/`, `logs/job_recovery.log`, `logs/chrome-startup.log`, `logs/nb_keepalive_loop.log`.

### Diagnosis
```bash
find /home/ubuntu/.hermes -not -user ubuntu -ls 2>/dev/null
```

### Fix by Asset Type

| Asset | Fix |
|-------|-----|
| `google_token.json` (root:600) | Create alternative token from `.bak` file via Google OAuth refresh, set `HERMES_GOOGLE_TOKEN_PATH` env var override in `google_api.py`. See reference file. |
| `data/sentez_debug/` (root-owned) | Change path to `/tmp/sentez_debug/` (world-writable). |
| `logs/*.log` (root:644) | `rm -f <path>` — directory owner (ubuntu) can delete files within it. File gets recreated as ubuntu-owned on next run. |

### Prevention
- Use `/tmp/` paths for debug/cache directories that may be created by initialization scripts
- Add `find ~/.hermes -not -user $USER -ls` to periodic health checks
- For OAuth tokens: maintain a `.bak` copy with readable permissions, or store refresh credentials in Bitwarden Secrets Manager

### Reference
- `references/root-owned-asset-permission-fix.md` — Full fix procedures with step-by-step for Google OAuth token recovery, debug directory remapping, and log cleanup.

---

## Pitfall: opencode-go Weekly Usage Limit (HTTP 429)

### Symptom
```
RuntimeError: HTTP 429: Weekly usage limit reached. Resets in 16hr 45min. To continue using this model now, enable usage from your available balance: https://opencode.ai/workspace/...
```

### Root Cause
`custom:opencode-go` provider enforces a **weekly usage quota** on free accounts. Routine cron jobs running multiple times per day (e.g., Bundle Gündem: 3×/day = 21×/week) exhaust this quota quickly.

The proxy at `:19998` injects the internal API key from `auth.json` — the client's Authorization header is ignored — so there's no per-user key rotation workaround. The quota is workspace-level.

### Fix: Route Routine Jobs to `opencode-zen` Free Tier
Use `opencode-zen` provider with free models that support tool calling:

| Job Category | Model | Provider | Tool Calling | Cost |
|--------------|-------|----------|--------------|------|
| Routine (greetings, Gmail, Skool, APA, Bundle, Deep Dive, Daily Synthesis, Half Security) | `deepseek-v4-flash-free` | `opencode-zen` | ✅ | FREE |
| Deep Analysis (Full Security, IG Analysis) | `nemotron-3-ultra-free` | `opencode-zen` | ✅ | FREE |
| Writing (Vanitas Dream, APA posts, LinkedIn posts) | `deepseek-v4-flash-free` / `gpt-5.4-mini` | `opencode-zen` / `Pollinations` | ✅ / ❌ | FREE |
| Paid-only (complex coding, heavy reasoning) | `deepseek-v4-flash` / `glm-5.1` | `custom:opencode-go` | ✅ | Paid |

**Migration Pattern:**
```python
# BEFORE (paid, hits weekly limit)
model={"model": "deepseek-v4-flash", "provider": "custom:opencode-go"}

# AFTER (free, no limit, tool-capable)
model={"model": "deepseek-v4-flash-free", "provider": "opencode-zen"}
```

### When to Keep Jobs on opencode-go
- Jobs requiring paid-only models (`glm-5.1`, `kimi`, `qwen`, `mimo-v2.5` non-free)
- Kanban workers that need specific paid model capabilities
- Jobs where free tier output quality is demonstrably insufficient

### Verification After Migration
1. [ ] Job runs without 429 error
2. [ ] Tool calling still works (web search, terminal, file ops)
3. [ ] Output quality acceptable for the job's purpose
4. [ ] `cronjob run` test passes

---

## Pitfall: Cron next_run Corruption After Manual `run` or Failed Schedule

### Symptom
After calling `cronjob(action='run')` with `job_id`, or after a provider/model update, the cron job's `next_run_at` jumps FAR into the future (days or weeks ahead), skipping multiple scheduled runs. The job is `enabled=true` and `last_status=ok`, but it won't fire at the next expected time.

**Example timeline:**
```
Schedule: "30 9,15,21 * * *"  (daily at 09:30, 15:30, 21:30)
Last run: 2026-06-11T09:37     (OK)
Next run: 2026-06-13T21:30     ← SKIPPED 6 runs (11 Haz 15:30, 21:30 + 12 Haz 09:30, 15:30, 21:30 + 13 Haz 09:30, 15:30)
```

### Root Cause
`cronjob(action='run')` triggers an immediate execution but may corrupt the internal `next_run_at` calculation. The scheduler's next-run computation uses `last_run_at` as its anchor point, and a manual `run` can shift this anchor in unexpected ways — especially when the schedule uses comma-separated hour lists (`9,15,21`) instead of step values (`*/6`).

The scheduler's algorithm appears to:
1. Round `last_run_at` down to the nearest schedule window
2. Add one full schedule **day** instead of the next schedule **window**
3. This compounds if the schedule has multiple runs per day — the window-finding logic may skip an entire day of windows

**Not the same as:** missing `origin.thread_id` or delivery misrouting. The job IS alive and enabled — it just won't fire until the corrupted `next_run_at` arrives.

### What Does NOT Fix It
| Approach | Result |
|----------|--------|
| `cronjob(action='update', schedule=...)` with SAME schedule | ❌ next_run unchanged |
| `cronjob(action='pause')` then `cronjob(action='resume')` | ❌ next_run unchanged |
| `cronjob(action='remove')` | ❌ Fails with `{'error': "'id'", 'success': false}` |
| Direct SQLite manipulation (`~/.hermes/cron/jobs.db`) | ❌ Table is empty — cron data stored elsewhere (in-memory or different backend) |

### Workarounds

**Workaround A — Recreate the job (preferred):**
1. Find the job's current prompt via session_search or cron prompt history
2. `cronjob(action='create')` with a NEW job_id (same name, prompt, schedule, skills, model, deliver)
3. Leave the old job as-is (it will fire at the corrupted next_run and self-correct after)

```python
# Step 1: Find the prompt from past sessions
session_search(query="cron prompt update job_id YOUR_JOB_ID")

# Step 2: Create a new job with identical config
cronjob(action='create',
        name='Same Human Name',
        prompt='... (full prompt) ...',
        schedule='30 9,15,21 * * *',
        skills=['skill1', 'skill2'],
        model={"model": "deepseek-v4-flash-free", "provider": "opencode-zen"},
        deliver='telegram:chat_id:thread_id')
```

**Workaround B — Let it self-correct (last resort):**
The corrupted next_run WILL eventually arrive, and the job WILL fire. After that run, the next_next_run should be correct. This is the safest option if the gap is ≤48 hours.

### Prevention
- **Avoid `cronjob(action='run')` for production cron jobs.** Use it only for testing brand-new jobs. Once a job is in production with a proven track record, let the scheduler handle timing.
- When you need to verify a job works, check `last_status` from `cronjob(action='list')` instead of triggering a manual run.
- If a manual test IS necessary, expect next_run corruption and plan to recreate the job afterward.
- Always verify `next_run_at` in the `cronjob(action='list')` output after ANY schedule or `run` operation.

### Verification After Workaround
1. [ ] `cronjob(action='list')` shows correct next_run_at
2. [ ] next_run_at falls within the next 24 hours (not days away)
3. [ ] Job fires at the expected time (wait and verify)
4. [ ] Journal/log shows no schedule errors

---

### Pitfall: opencode-zen Free Models Fail Watchdog But Work in Cron (Intermittent Availability)

### Symptom
```
[2026-06-10 04:01:08]   ZEN FAILED: mimo-v2.5-free
[2026-06-10 04:01:08]   ZEN FAILED: deepseek-v4-flash-free
[2026-06-10 04:01:09]   ZEN FAILED: nemotron-3-ultra-free
```
All free models on opencode-zen fail the watchdog's connectivity test (Model Watchdog reports them as "ZEN FAILED"). But the SAME cron jobs using these models continue to work — `last_status: "ok"` on numerous jobs.

### Root Cause
The `opencode-zen` free tier has **intermittent availability**. Connectivity probes (simple `chat/completions` with short prompts) may fail during high-load periods or when the free tier API is briefly rate-limiting new connections. However, established cron sessions with queued requests often succeed minutes later.

This is NOT a permanent model outage — it's a transient API gate check that the watchdog's rapid-fire probing triggers more easily than a real cron run does.

### Diagnosis

| Signal | Interpretation |
|--------|---------------|
| Watchdog says ZEN FAILED | Model MAY be down. Check again in 5-10 min. |
| `last_status: "error"` on cron job | Model IS down (429 or timeout). Needs switch. |
| `last_status: "ok"` despite ZEN FAILED | Model is working — watchdog alarm was transient. |
| Dogfood/browser usage works | Free tier is up. Watchdog test was false positive. |

**Primary diagnostic:** Check the cron job's actual `last_run_at` and `last_status` in `jobs.json`, **not** the watchdog output. The watchdog is a probe; the job's last run is the ground truth.

### Fix
**Do NOT switch models preemptively** based on watchdog ZEN FAILED alone. Follow this decision tree:

```
ZEN FAILED in watchdog
  ├─ Job's last_status == "ok" → Ignore, model is working
  ├─ Job's last_status == "error"
  │     ├─ Error is HTTP 429 → Model quota exhausted. Switch to different
  │     │   model on same provider, or different provider entirely.
  │     └─ Error is other → Check if specific job prompt/skills issue
  └─ 3+ consecutive watchdog runs show ZEN FAILED for ALL free models
       └─ Transient outage. Wait 30 min, re-run watchdog.
```

**Concrete model switch patterns from 2026-06-10:**
```python
# Skool Daily Check: deepseek-v4-flash-free ZEN FAILED + error on job
# → Switch to Pollinations gpt-5.4-mini (always available)
cronjob(action='update', job_id='50002951d6bc',
        model={"model": "gpt-5.4-mini", "provider": "custom:Pollinations"})

# Tam Güvenlik (Haftalık): nemotron-3-ultra-free HTTP 429 + error on job
# → Switch to mimo-v2.5-free on same provider (different free model)
cronjob(action='update', job_id='095fa7d69603',
        model={"model": "mimo-v2.5-free", "provider": "opencode-zen"})
```

## Pitfall: Free Tier Rate Limit Exhaustion — Cumulative Cron Usage

### Symptom
One or more cron jobs fail with `HTTP 429` / `FreeUsageLimitError: Rate limit exceeded` while other jobs using the same provider continue to work, or eventually also fail as the day progresses.

**Example from 2026-07-14:**
```
Günlük Sentez (23:00) → HTTP 429: FreeUsageLimitError: Rate limit exceeded
```
While earlier-running jobs (Ekonomi Sabah 08:00, LinkedIn kuyruk 08:00, Skool 10:00, Karusel sabah 10:00) succeeded earlier in the day.

### Root Cause
The `opencode-zen` free tier (`deepseek-v4-flash-free`, `nemotron-3-ultra-free`, etc.) has a **shared daily request/token quota** across ALL jobs using that provider. When 6-8 cron jobs each make 1-3 API calls per day, plus Hermes auxiliary systems (compression, curator, session_search, skills_hub, MCP, etc.) also hit the same endpoint, the cumulative usage exceeds the free daily limit.

This is **not** a single-job rate limit — it is a **system-wide aggregate** issue. Each individual job may stay under its own limit, but their combined usage exhausts the free tier before all jobs complete.

### Diagnosis

**Step 1: Count jobs by provider**
```python
import json
with open('/home/ubuntu/.hermes/cron/jobs.json') as f:
    jobs = json.load(f)['jobs']

from collections import Counter
provider_counts = Counter()
for j in jobs:
    if j.get('enabled', False) and j.get('last_status') != 'completed':
        provider = j.get('provider', 'no_agent')
        provider_counts[provider] += 1

print(f"Enabled jobs by provider ({sum(provider_counts.values())} total):")
for prov, count in provider_counts.most_common():
    print(f"  {prov}: {count}")
```

**Step 2: Identify the 429 pattern**

| Signal | Interpretation |
|--------|---------------|
| Only 1 job failed with 429 | That job exceeded the provider per-request rate limit |
| Several jobs failed later in the day | Cumulative daily quota exhausted |
| All jobs fail simultaneously | Provider outage or account-level block |
| 429 clears next day, repeats same pattern | Confirmed: cumulative usage > daily limit |

### Fix Options

**Option A — Distribute jobs across providers (preferred):**
Move some jobs to a different provider:

| Source | Alternative 1 | Alternative 2 |
|--------|---------------|---------------|
| `opencode-zen` free flash | `custom:opencode-go` paid (port 19998) | NVIDIA free tier |
| `opencode-zen` free ultra | `custom:opencode-go` paid | NVIDIA free tier |

**Option B — Reduce free tier load:**
- Nightly jobs (23:00+) hit exhausted limit most often — schedule heavy jobs earlier in the day
- Merge small jobs sharing the same provider into fewer runs
- Use `no_agent=true` scripts where possible (no LLM quota consumption)

**Option C — Add retry with backoff to no_agent scripts:**
```python
import time
import urllib.error

def call_with_retry(url, data, headers, max_retries=3):
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                wait = 60 * (2 ** attempt)
                print(f"429, {wait}s bekleniyor (deneme {attempt+2}/{max_retries})...")
                time.sleep(wait)
            else:
                raise
```

### Prevention
- **Default strategy:** Routine cron → `opencode-zen` free. Critical/heavy cron → `custom:opencode-go` paid. This reserves free tier capacity for jobs that need it least.
- **Audit monthly:** Run the provider counter script to catch provider drift.
- **Watch for clusters:** If 6+ jobs share the same free provider, proactively split them before the limit is hit.
- **New jobs:** Check `cronjob list` first to see current provider balance before choosing.
- **NVIDIA free tier: selective model reliability.** Not all listed models work. Tested matrix (15 Tem 2026):

  | Model | Status | Turkish | Notes |
  |-------|--------|---------|-------|
  | `minimaxai/minimax-m3` | ✅ Reliable | 🟢 Good | Best choice — lightweight, high worker limit |
  | `meta/llama-3.1-70b-instruct` | ✅ Reliable | 🟢 Good | Heavy model, lower worker limit |
  | `z-ai/glm-5.2` | ⚠️ Slow | 🟢 Good | 120s timeout needed; reserve for voice agent |
  | `deepseek-ai/deepseek-v4-flash` | ⚠️ Flaky | 🟢 Good | Edel reports intermittent failures |
  | `nvidia/llama-3.1-nemotron-nano-8b-v1` | ✅ Works | 🔴 Broken | Responds in garbled Turkish |
  | `stepfun-ai/step-3.7-flash` | ⚠️ Partial | 🟡 N/A | Returns `content: null` format |
  | `google/gemma-4-31b-it` | ❌ Timeout | — | HTTP 000/500 |
  | `mistralai/mistral-7b-instruct-v0.3` | ❌ 404 | — | Model not found |

  **Recommendation:** Use `minimaxai/minimax-m3` via NVIDIA for production cron jobs. Avoid `deepseek-ai/deepseek-v4-flash` on NVIDIA (same flakiness pattern Edel reported). Reserve `z-ai/glm-5.2` for voice agent use.

- **Hermes auxiliary systems consume the same free quota** — compression, curator, session_search, approval, MCP, skills_hub all use `opencode-zen` (`deepseek-v4-flash-free`) with `base_url: https://opencode.ai/zen/v1`. Config audit: `auxiliary.*.provider == opencode-zen`.

---

### Pitfall: Model Watchdog Script — Python String-Quote Bugs in f-strings

The `model-watchdog.py` script (at `~/.hermes/scripts/model-watchdog.py`) can crash with `NameError` due to missing string quotes in f-string interpolations. Two instances found and fixed 2026-06-10:

**Bug 1 — Line 341:**
```python
# BEFORE (NameError: name 'name' is not defined)
log(f"Cron \"{job.get(name, )}\": {model} {reason}")

# AFTER
log(f"Cron \"{job.get('name', '')}\": {model} {reason}")
```
The variable `name` was undefined — should be string literal `'name'`. Trailing comma after the default value also created a tuple.

**Bug 2 — Line 302:**
```python
# BEFORE (NameError: name 'POLLINATIONS_API_KEY' is not defined)
new_config += f"...api_key: {env.get(POLLINATIONS_API_KEY, )}..."

# AFTER
new_config += f"...api_key: {env.get('POLLINATIONS_API_KEY', '')}..."
```
Same pattern: `POLLINATIONS_API_KEY` was an undefined variable — should be string literal `'POLLINATIONS_API_KEY'`.

**Root cause pattern:** When porting `env.get("KEY", "default")` calls into f-strings, the quotes inside the f-string must be changed from `"` to `'` to avoid conflicting with the f-string delimiter. Easy to miss.

**Diagnosis:** If `model-watchdog.py` crashes silently (script exits with code 1), check the watchdog delivery — it includes stderr with the full traceback:
```bash
python3 ~/.hermes/scripts/model-watchdog.py 2>&1 | tail -20
```

**Fix:** Open the file, find the line referenced in the NameError traceback, and add quotes around the variable name:
```python
# Wrong in f-string:
{env.get(SOME_VAR, '')}
# Correct:
{env.get('SOME_VAR', '')}
```

---

## Pitfall: base_url Contamination — "Invalid model or alias" Error

### Symptom
```
RuntimeError: Error code: 400 - {'success': False, 'error': {'message': 'Invalid model or alias: "<model_name>". Must be a valid model name or alias.', 'code': 'BAD_REQUEST', 'timestamp': '...'}, 'status': 400}
```

The model name IS valid on the correct provider — but the request is being sent to the WRONG endpoint.

### Root Cause
`base_url` field in the cron job config points to a different provider's proxy. Common scenarios:

| Scenario | Model | Provider | base_url (WRONG) | Actual Destination |
|----------|-------|----------|-------------------|-------------------|
| Morning Greeting (2026-06-08) | `mimo-v2.5-free` | `opencode-zen` | `http://127.0.0.1:19999/v1` | Pollinations proxy |
| Evening Precheck (2026-06-06) | `deepseek-v4-flash-free` | `opencode-zen` | `http://127.0.0.1:19999/v1` | Pollinations proxy |

The `cronjob(action='update')` tool changes `model` and `provider` but does NOT clear `base_url`. If you switch from a Pollinations-based job to opencode-zen, the old `base_url` remains and routes requests to the wrong proxy.

### Diagnosis
1. Check the job's `base_url` in `~/.hermes/cron/jobs.json`:
```bash
python3 -c "import json; j=json.load(open('/home/ubuntu/.hermes/cron/jobs.json')); [print(f'{x[\"name\"]}: base_url={x.get(\"base_url\")}, provider={x[\"provider\"]}') for x in j['jobs'] if x.get('base_url')]"
```
2. Cross-reference with the correct base_url per provider:

| Provider | Correct base_url |
|----------|-----------------|
| `opencode-zen` | `null` (must be absent or null) |
| `custom:opencode-go` | `http://127.0.0.1:19998/v1` (proxy) |
| `custom:Pollinations` | `http://127.0.0.1:19999/v1` (UA proxy) |

### Fix
Remove the `base_url` field (or set to `null`) from the job's config in `~/.hermes/cron/jobs.json`:

```patch
- "base_url": "http://127.0.0.1:19999/v1"
+ (remove completely)
```

Use the `patch` tool directly on the JSON file — `cronjob(action='update')` won't clear `base_url`:
```python
patch(path='/home/ubuntu/.hermes/cron/jobs.json',
      old_string='"base_url": "http://127.0.0.1:19999/v1"',
      new_string='')  # also remove trailing comma if needed
```

### Prevention
After ANY provider switch via `cronjob(action='update')`, always verify `base_url`:
- **If new provider is `opencode-zen`**: base_url MUST be null/absent
- **If new provider is `custom:opencode-go`**: base_url MUST be `http://127.0.0.1:19998/v1`
- **If new provider is `custom:Pollinations`**: base_url MUST be `http://127.0.0.1:19999/v1`

Add this to the verification checklist below (item 4).

## Pitfall: base_url Contamination — Delivery Tracing

When investigating where a cron job output lands (not model errors), trace through:

```
~/.hermes/cron/jobs.json          → Check deliver + origin fields
  ↓
cron/scheduler.py:455-530         → _resolve_single_delivery_target()
  ↓ parse "telegram:<chat_id>:<thread_id>"
tools/send_message_tool.py:354    → _parse_target_ref(regex match)
  ↓ returns (chat_id, thread_id, True)
cron/scheduler.py:730-840         → _deliver_result()
  ↓ creates send_metadata={"thread_id": "2920"}
gateway/platforms/telegram.py:1843 → adapter.send(metadata=...)
  ↓ extracts thread_id
gateway/platforms/telegram.py:1878 → _metadata_thread_id()
gateway/platforms/telegram.py:633  → _thread_kwargs_for_send()
gateway/platforms/telegram.py:678  → _message_thread_id_for_send()
  ↓ returns int(2920) or None if "1"
Telegram Bot API                   → send_message(message_thread_id=...)
```

### Key Files
- `~/.hermes/cron/jobs.json` — job config (deliver, origin, model, provider)
- `~/.hermes/logs/agent.log` — delivery logs (INFO only shows `platform:chat_id`, not thread_id)
- `/data/ubuntu/hermes-agent/cron/scheduler.py` — delivery resolution + processing
- `/data/ubuntu/hermes-agent/tools/send_message_tool.py` — target parsing
- `/data/ubuntu/hermes-agent/gateway/platforms/telegram.py` — adapter, thread handling

### Key Log Pattern
The scheduler log format at INFO level is:
```
Job '<id>': delivered to <platform>:<chat_id> via live adapter
```
**Thread_id is NOT logged at INFO level.** To see it, you need DEBUG level. Check `~/.hermes/logs/agent.log` for `"delivering to"` (DEBUG) and `"thread_fallback"` or `"Thread ... not found"` (WARNING).

## Verification Checklist

### After fixing a delivery issue:
1. [ ] `deliver` field points to correct `platform:chat_id:thread_id`
2. [ ] `origin.thread_id` matches target thread (recreate job if needed)
3. [ ] Model/provider is appropriate for job weight (free vs paid)
4. [ ] `base_url` matches provider (`null` for `opencode-zen`, `:19998` for `custom:opencode-go`, `:19999` for `custom:Pollinations`)
5. [ ] `cronjob run` delivers to correct topic (manual test)
6. [ ] No truncation errors in `agent.log`
7. [ ] Scheduled runs appear in correct Telegram topic

### When "Invalid model or alias" error occurs:
1. [ ] Check `base_url` in `~/.hermes/cron/jobs.json` — does it match the provider?
2. [ ] If `opencode-zen` + non-null `base_url` → remove `base_url` via patch
3. [ ] If `custom:Pollinations` + model not in gpt-5.4-mini/gemma family → switch provider
4. [ ] Run `cronjob run` to verify fix

## References
- `references/systematic-cron-maintenance.md` — Full cron health check procedure: discover → triage → diagnose → fix → verify. Use when user asks for "cron bakımı".
- `references/bundle-delivery-case-study.md` — Full reproduction of the 2026-06-06 Bundle job delivery misroute, with code path trace and fix.
- `references/base-url-contamination-case-study.md` — `evening_precheck` Azure filter → provider switch → base_url contamination → fix. Timeline and diagnosis pattern.
- `references/mimo-v2.5-free-base-url-case-study.md` — `morning_greeting` "Invalid model" error via stale Pollinations base_url with `mimo-v2.5-free` on `opencode-zen`. Same pattern, different model.
- `references/morning-greeting-pollinations-migration.md` — Full timeline: base_url contamination → Pollinations migration → 128 tool limit → enabled_toolsets fix. Combines all three patterns in one case.
- `references/opencode-go-rate-limit-case-study.md` — 2026-06-07 Bundle Gündem 429 error → systematic migration of all 23 cron jobs to `opencode-zen` free tier. Strategy D model assignment matrix and zero-paid-jobs outcome.
