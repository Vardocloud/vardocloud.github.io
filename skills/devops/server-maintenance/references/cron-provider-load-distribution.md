# Cron Job Provider Load Distribution

## Problem

Too many cron jobs using the same provider proxy (e.g., `opencode-go` on port 19998) cause:
- **Truncation errors**: `RuntimeError: Response remained truncated after 3 continuation attempts`
- **Timeouts**: Jobs hanging, no output
- **Spike collisions**: 5 jobs firing at the same minute (e.g., 09:00)

## Diagnosis

```bash
# Count jobs per provider
python3 -c "
import json
with open('/home/ubuntu/.hermes/cron/jobs.json') as f:
    jobs = json.load(f)
from collections import Counter
provs = Counter(j.get('model',{}).get('provider','unknown') for j in jobs)
for p,c in provs.most_common(): print(f'{c:3d} jobs → {p}')
"
```

## Solution Pattern

### 1. Classify jobs by priority

| Priority | Provider | Model | For |
|----------|----------|-------|-----|
| Critical | `custom:opencode-go` | `deepseek-v4-flash` | Kanban, Tam Güvenlik, IG Analiz |
| Routine | `opencode-zen` | `deepseek-v4-flash-free` | Gmail, Skool, LinkedIn, Sentez, APA, Yarı Güvenlik |
| Simple (no tools) | `custom:Pollinations` | `gemma` / `gpt-5.4-mini` | yardimci, yazar |

### 2. Migrate routine jobs to free tier

```python
# Example: migrate all non-critical jobs from opencode-go to opencode-zen
for job in jobs:
    provider = job.get('model', {}).get('provider', '')
    model = job.get('model', {}).get('model', '')
    if 'opencode-go' in provider and model == 'deepseek-v4-flash':
        name = job.get('name', '')
        if name not in ['Tam Güvenlik', 'IG Analiz']:  # keep critical
            job['model']['provider'] = 'opencode-zen'
            job['model']['model'] = 'deepseek-v4-flash-free'
```

### 3. Stagger schedules

After migration, ensure minimum 15-minute spacing:
```python
from datetime import datetime, timedelta
import re

def parse_cron_minute(schedule):
    """Extract minute from cron expression"""
    parts = schedule.split()
    if len(parts) >= 1 and parts[0].isdigit():
        return int(parts[0])
    return 0

# Sort by current minute, reassign with 15-min gaps
jobs_sorted = sorted(migrated_jobs, key=lambda j: parse_cron_minute(j['schedule']))
for i, job in enumerate(jobs_sorted):
    new_minute = (i * 15) % 60
    old_schedule = job['schedule']
    parts = old_schedule.split()
    parts[0] = str(new_minute)
    job['schedule'] = ' '.join(parts)
```

### 4. Verify distribution

```bash
# Check peak concurrency per hour
python3 -c "
import json
with open('jobs.json') as f:
    jobs = json.load(f)
# Group by hour
from collections import Counter
hours = Counter()
for j in jobs:
    s = j.get('schedule','')
    parts = s.split()
    if len(parts) >= 2 and parts[1].isdigit():
        hours[int(parts[1])] += 1
for h in sorted(hours):
    print(f'{h:02d}:00 → {hours[h]} jobs')
"
```

## Root Cause

OpenCode Go proxy (port 19998) is single-threaded. Each request holds the connection for the full LLM generation (up to 60s). Multiple concurrent requests queue up → some timeout → truncation errors.

**Not a task limit issue** — the proxy simply can't handle 5+ concurrent generations.

**BONUS ROOT CAUSE (6 Haz 2026):** Free model output token limits. `deepseek-v4-flash-free` (opencode-zen) has ~2000 output token limit. Heavy jobs like **Bundle** (15+ article deep-read → wiki updates → NotebookLM archive) exceed this. Symptom: partial output delivered, then truncation error. Other free-tier jobs work fine — only the heavy one fails. Fix: keep heavy output jobs on paid `opencode-go` + `deepseek-v4-flash`.

## Output Complexity Check (Before Migration)

When migrating a job to free tier, verify it won't exceed the free model's output limit:

```bash
# Check last successful run's output length (proxy)
grep -o '"content":"[^"]*"' ~/.hermes/cron/jobs.json | wc -c
```

Jobs producing >2000 output tokens should stay on paid tier. Bundle is the canonical example — 15+ articles × analysis × wiki × NotebookLM = ~4000+ output tokens.

## Prevention

- Max 3-4 cron jobs on `opencode-go` at any given hour
- Free tier jobs → `opencode-zen` (cost: 0 TL)
- New cron job → check peak hour load before scheduling
