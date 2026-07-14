# Bundle Cron Job — Delivery Debugging Case Study

**Dates:** 2026-06-06 (initial fix) through 2026-06-07 (root cause discovered)
**Symptom:** Bundle Gündem İşleme cron job output appearing in general chat (thread 1) instead of 📰Haberler topic (thread 2920).

## Environment
- Hermes Agent running on Oracle Cloud ARM64 (Ubuntu 22.04)
- Telegram group: "Edel & Vanitas" (-1003917030255)
- Topics: 🔒(12) 🧠APA(13) 💼LinkedIn(14) 📧Gmail(15) 🎯Op(16) 📚Öğrenme(17) 🎭Bardo(18) 📰Haberler(2920) 📅Günlük(1223)
- Hermes source: `/data/ubuntu/hermes-agent/`

## Phase 1 (2026-06-06): Job Recreation → Assumed Fixed

### Original (broken) job config
```json
{
  "job_id": "4cb28605521c",
  "name": "Bundle Gündem İşleme",
  "deliver": "telegram:-1003917030255:2920",
  "origin": {"thread_id": "1"},
  "model": "deepseek-v4-flash",
  "provider": "custom:opencode-go",
  "schedule": "15 6,10,16 * * *"
}
```

### Observed logs — no thread_id in any delivery log entry
```
2026-06-06 06:03:55 INFO Job '4cb28605521c': delivered to telegram:-1003917030255 via live adapter
2026-06-06 10:10:07 INFO Job '4cb28605521c': delivered to telegram:-1003917030255 via live adapter
2026-06-06 17:29:05 INFO Job '4cb28605521c': delivered to telegram:-1003917030255 via live adapter
```

### Secondary issue: Truncation
The 10:10 run used `opencode-zen` (free model) due to load-redistribution. Bundle's heavy prompt exceeded free tier output token limits:
```
RuntimeError: Response remained truncated after 3 continuation attempts
```

### Phase 1 Solution
1. Deleted job `4cb28605521c`
2. Recreated as `93582f1545d2` from thread 2920 → `origin.thread_id` = `"2920"`
3. Kept `deliver: "telegram:-1003917030255:2920"`
4. Kept `model: deepseek-v4-flash` + `provider: custom:opencode-go` (paid)
5. Updated prompt to use `nlm` CLI for NotebookLM archiving (MCP auth unreliable)
6. **Assumed fixed** — manual trigger confirmed delivery

## Phase 2 (2026-06-07): Defense-in-Depth FAILED — Root Cause Identified

### What Happened
User reported: Job output still going to general chat. Last message in Haberler topic was from 16:09 (previous day) — Bundle output at 01:47 and 02:31 never appeared there.

Despite `origin.thread_id == deliver.thread_id`, the **silent thread_fallback** in telegram.py still triggered.

### Root Cause: Silent Thread Fallback in Telegram Adapter
Location: `/data/ubuntu/hermes-agent/gateway/platforms/telegram.py`, lines 1977-2007

```python
if _is_thread_not_found_error(send_err) and effective_thread_id is not None:
    if not retried_thread_not_found:
        retried_thread_not_found = True
        continue  # retry once with same thread_id
    # Second failure: silently drop message_thread_id
    logger.warning("Thread %s not found in %s, retrying without message_thread_id", ...)
    used_thread_fallback = True
    effective_thread_id = None
    thread_kwargs = {"message_thread_id": None}
    continue
```

This triggers when Telegram API returns "thread not found" — can happen due to:
- Transient network hiccup during API call
- Telegram forum reindexing
- Rate limiting disguised as 404
- Bot session state mismatch between scheduler and live adapter

Two consecutive failures → adapter silently drops `message_thread_id` → general chat delivery.

### Verification That Thread 2920 IS Accessible
Manual `send_message(target="telegram:-1003917030255:2920")` succeeded (message_id: 3998). The thread exists and the bot has access. The issue is in the cron auto-delivery path only.

### Phase 2 Solution: `send_message` Bypass Pattern
Modified the job prompt to use `send_message` tool directly, completely bypassing the scheduler's auto-delivery chain:

```markdown
5. İşin bitince send_message tool'unu kullanarak sonucu ŞU hedefe gönder: 
   target="telegram:-1003917030255:2920"
```

**Why this works:**
- `send_message` creates a fresh adapter session — no stale state
- Does NOT go through `_deliver_result()` → `adapter.send(metadata=...)` path
- No `thread_fallback` mechanism in the send_message tool path
- If thread truly doesn't exist, fails HARD with visible error instead of silent misroute

## Code Path Comparison

### Auto-Delivery Path (has silent fallback)
```
_resolve_single_delivery_target() → returns {"chat_id": "...", "thread_id": "2920"}
_deliver_result() → adapter.send(chat_id, text, metadata={"thread_id": "2920"})
  └─ telegram.py:send() → ⚠️ FALLBACK: thread not found ×2 → drops message_thread_id
```

### send_message Tool Path (no fallback)
```
send_message() tool → _parse_target_ref("telegram:chat:thread") → adapter.send(thread_id=2920)
  └─ ✅ Works or hard-fails — no silent fallback
```

## Key Takeaway
The `origin.thread_id == deliver.thread_id` alignment is NOT sufficient protection. For critical deliveries, use the `send_message` bypass pattern in the job prompt.
