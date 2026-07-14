---
name: hermes-api-performance
description: "Hermes API latency diagnostics — provider comparison, context overhead measurement, voice agent feasibility testing"
version: 1.0.0
metadata:
  hermes:
    tags: [hermes, api, latency, performance, provider, voice]
    category: devops
---

# Hermes API Performance Diagnostics

Latency measurement and provider comparison for Hermes API.

## Core Finding

Hermes API response time varies significantly by provider:
- **Groq LPU (BEST for voice):** ~7.5s total via Hermes custom_provider. llama-4-scout-17b. Fast streaming, excellent Turkish. No throttling observed.
- **Pollinations:** 5-20s, throttles on consecutive requests. `openai` model ~4.5s first call, degrades to ~20s by 3rd-4th call.
- **opencode-go (deepseek):** 2-3s for flash models, 20-50s for reasoning models.

Context assembly overhead (3-4s) is provider-independent. Streaming masks this: first token arrives while context is still loading.

## Diagnostic Pattern

```
1. Test provider DIRECTLY (bypass Hermes) → baseline inference speed
2. Test SAME model THROUGH Hermes API → context-added total
3. Difference = context assembly overhead
4. If difference is large → problem is context size, not provider
```

### Test Commands

Direct proxy test uses local proxy port. Hermes API test uses the gateway port with API key from env.

Streaming TTFT (time-to-first-token) is a better metric than total response time for voice applications. Measure with `stream: true`.

## Provider Switching

To switch default model and provider:

```
hermes config set model.default <model_name>
hermes config set model.provider <provider_name>
systemctl --user restart hermes-gateway
```

Always restart gateway after config changes. Verify with a test request.

### Adding Custom Providers (e.g., Groq)

Hermes config.yaml `custom_providers` supports OpenAI-compatible APIs:

```yaml
custom_providers:
  - api_key_env: GROQ_API_KEY
    api_mode: chat_completions
    base_url: https://api.groq.com/openai/v1
    models:
      groq-llama-4-scout: llama-4-scout-17b-16e-instruct
    name: Groq
```

Also add model aliases for shorthand: `groq: {model: groq-llama-4-scout, provider: Groq}`.

After adding, restart gateway. Model is immediately available via `/v1/chat/completions` with `model: groq-llama-4-scout`.

## Voice Agent Feasibility

For real-time voice (sub-2 second total response), Hermes API with full context is not suitable. The constraint triangle:

- **Fast** (under 2 seconds)
- **Full context** (memory, tools, skills)
- **Full capability** (server access, file operations)

Only two can coexist. Pick based on use case:
- Voice conversation → sacrifice full context (use light endpoint or external fast model)
- Deep work → accept 4-6 second response (use full Hermes API)
- Quick chat → external fast model with personality prompt

## Pitfalls

- **Don't diagnose without measuring:** HTTP 403 can be IP ban OR rate-limit. Check error body for code before concluding.
- **HTTP 502 from Hermes:** Provider routing failure. Verify model name exists in provider's model list.
- **Timeout:** Provider may be down. Test direct proxy connection first.
- **Streaming TTFT misleading:** TTFT measures time from when provider receives request, not from user submission. Context assembly still happens before streaming begins.
- **Provider change requires restart:** Config changes don't take effect until gateway restart.
- **`openai-fast` misnomer (2026-06-16):** Despite its name, `openai-fast` is the SLOWEST model on Pollinations (23s). `openai` (standard) is 5× faster at 4.5s. Do not select models by name — always measure.
- **Pollinations consecutive-request throttling (2026-06-16):** First call after idle: ~5s. By the 3rd-4th consecutive call: ~20s. This is server-side rate limiting, not a client bug. For voice agents, this means the first response is fast but rapid back-and-forth degrades. Mitigation: accept the latency range or switch provider.
- **Timeout chain alignment (2026-06-16):** In multi-hop architectures (voice agent → proxy → Hermes), upstream timeout MUST exceed downstream timeout + buffer. Rule: `T_upstream ≥ T_downstream + 5s`.

## Prompt Caching Diagnostics

### DeepSeek Cache Behavior (VERIFIED Jul 2026)

DeepSeek prompt caching uses automatic prefix matching from token 0:

- **Cache hit discount:** ~90% (hit tokens ~$0.014/M vs miss ~$0.14/M)
- **Critical constraint:** ANY byte change in the prompt prefix invalidates the entire cache. A single changing character at position 0 → 0% cache hit rate.
- **Stable prefix → ~70% cache hit** achievable in steady-state sessions.
- **Verify:** Check `prompt_cache_hit_tokens` and `prompt_cache_miss_tokens` in API response `usage` object.

### Test Methodology

Test directly against the provider proxy endpoint (bypass gateway):

```python
import json, time, urllib.request

STABLE = "You are a test assistant. Answer briefly."
payload1 = {"model": "...", "messages": [
    {"role": "system", "content": STABLE},
    {"role": "user", "content": "question A"}
], "max_tokens": 50}
payload2 = payload1.copy()
payload2["messages"][1]["content"] = "question B"

# First call: cache miss. Second call: should show cache hit.
for p in [payload1, payload2]:
    req = urllib.request.Request(URL, data=json.dumps(p).encode(), headers={"Content-Type": "application/json"})
    data = json.loads(urllib.request.urlopen(req, timeout=60).read())
    hit = data["usage"].get("prompt_cache_hit_tokens", 0)
    miss = data["usage"].get("prompt_cache_miss_tokens", 0)
    print(f"hit={hit} miss={miss} ratio={hit/(hit+miss)*100:.0f}%")
```

### Optimization Strategies

1. **Stable prefix first:** All invariant context (persona, core rules, permanent memory) must appear at the very start of the prompt. Variable content (timestamps, session metadata, conversation history) should come AFTER the stable block.
2. **Memory ordering by volatility:** Place confirmed/permanent entries first, error logs and frequently-updated entries last. When volatile entries change, the stable prefix cache survives.
3. **Mid-session stability:** Don't change core system content mid-conversation. Tool changes require `/reset` for this reason — Hermes enforces this to preserve caching.
4. **Provider TTL:** Config `prompt_caching.cache_ttl` (default 5min) controls how long cached prefixes persist.

Full test scripts and raw data: `references/prompt-caching-deepseek.md`

If variable content (timestamps, dynamic metadata) appears BEFORE the stable system prompt, prompt caching is effectively disabled — every request becomes a cache miss. If cache hit rate is consistently 0%, check whether dynamic content precedes the stable prefix in the prompt assembly order.
