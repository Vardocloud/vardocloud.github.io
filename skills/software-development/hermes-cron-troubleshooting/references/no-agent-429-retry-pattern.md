# 429 Rate Limit Retry Pattern for no_agent Scripts

## Problem
A no_agent cron script (Python) calls an LLM API and receives HTTP 429 (rate limit exceeded). The script exits with code 1, the job is marked `last_status: error`, and no work gets done. If the limit is transient (rolling window, per-minute rate), a retry with backoff would succeed.

## Pattern: Exponential Backoff on 429 Only

```python
import time
from openai import OpenAI

def call_with_retry(client, system_prompt, user_content, model, retries=5):
    """
    Call LLM API with exponential backoff on 429 errors.
    Non-rate-limit errors are re-raised immediately.
    """
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.7,
                max_tokens=16384,
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            error_str = str(e)
            if "429" in error_str or "rate_limit" in error_str.lower():
                if attempt < retries:
                    wait = min(2 ** attempt * 30, 600)  # 60s, 120s, 240s, 480s, 600s
                    print(f"Rate limit hit (attempt {attempt}/{retries}), waiting {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"Rate limit exhausted after {retries} attempts.")
            else:
                # Non-rate-limit error: re-raise immediately
                raise
    raise last_error
```

## Key Design Decisions

| Decision | Why |
|----------|-----|
| Backoff: 2^attempt × 30s | Ballistic: 60s → 120s → 240s → 480s → 600s (10min max). Catches both per-minute and rolling-hour limits. |
| Cap at 600s | Prevents runaway waits on daemon scripts. 10min is enough for most free tier windows. |
| Re-raise non-429 immediately | No point retrying on auth errors (401), model-not-found (404), server errors (500). |
| Print progress to stdout | no_agent scripts capture stdout for delivery; user sees what's happening. |
| `retries=5` default | 5 attempts × ~18min total max wait = reasonable for a nightly job. Reduce to 3 for time-sensitive jobs. |

## When to Use

- **no_agent scripts** that call external LLM APIs (opencode-zen, Pollinations, NVIDIA).
- **Any script** where the API is known to have transient 429 limits.
- **Nightly/batch jobs** where a 10-minute delay is acceptable.

## When NOT to Use

- Agent jobs (Hermes agent loop has its own retry).
- Time-critical jobs (morning greeting, hourly checks) — lower `retries` to 2-3.
- Non-429 errors (auth, model, format) — retry is pointless.

## Example: gunluk_sentez.py (2026-07-15)

Applied to the daily synthesis script that was failing with `FreeUsageLimitError: Rate limit exceeded` on opencode-zen:

```python
# Before: no retry, exits immediately on 429
response = client.chat.completions.create(...)

# After: 5 retries with backoff
response = call_with_retry(client, system_prompt, user_content, MODEL)
```
