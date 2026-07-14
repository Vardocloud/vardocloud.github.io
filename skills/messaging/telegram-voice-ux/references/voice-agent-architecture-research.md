# Voice Agent Architecture Research (2026-06-15)

## Core Finding: Context Assembly IS the Bottleneck (Updated 2026-06-15)

**Updated hypothesis:** BOTH provider speed AND Hermes context assembly contribute to latency.

| Path | Latency | Breakdown |
|------|---------|-----------|
| Pollinations proxy direct (19999) | 0.6s | Pure model inference |
| Hermes API → Pollinations (8642) | 4.3s | +3.7s context assembly overhead |
| Hermes API → opencode-zen (8642) | TIMEOUT | Rate limited (NOT IP banned — rate limit only) |

**Key insight:** Provider speed helps, but Hermes context assembly (~3.7s for 51K tokens) is the DOMINANT factor. No provider can eliminate this overhead. Streaming TTFT (0.04s) masks the wait but total response remains 4+ seconds.

**Original wrong hypothesis:** "Hermes API is slow because it loads 56K tokens of context" → Partially true, but the previous diagnosis that "provider routing" was the ONLY issue was ALSO incomplete. Both matter.

**Key debugging methodology:** Test direct proxy vs Hermes API to isolate bottleneck:

```
# Step 1: Direct proxy (bypass Hermes, no auth)
curl http://127.0.0.1:19999/v1/chat/completions \
  -d '{"model":"mistral","messages":[{"role":"user","content":"test"}],"max_tokens":5}'

# Step 2: Through Hermes API (with API_SERVER_KEY auth)
curl http://127.0.0.1:8642/v1/chat/completions \
  -H "Authorization: Bearer $API_SERVER_KEY" \
  -d '{"model":"mistral","messages":[{"role":"user","content":"test"}],"max_tokens":5}'

# If Step 1 works (<2s) but Step 2 times out (>30s) → provider routing issue
```

## Latency Benchmarks (2026-06-15)

### Pollinations Proxy Models (127.0.0.1:19999, bypass Hermes)

| Model | Actual Model | Latency | Turkish | Notes |
|-------|-------------|---------|---------|-------|
| **mistral** | mistral-small-3.2-24b | **0.62s** ⚡ | ✅ "İyi!" | Fastest, best for voice |
| **llama** | Llama-3.3-70B-Instruct | 1.04s | ✅ "İyiyim." | Good balance |
| **openai** | gpt-5.4-nano-2026-03-17 | 1.17s | ✅ "İyiyim." | Reliable |
| openai-fast | gpt-5-nano-2025-08-07 | 1.95s | ⚠️ Sometimes empty | Not recommended |
| deepseek | — | TIMEOUT | ❌ | Broken on Pollinations proxy |

### Hermes API (through Pollinations, after switch)

| Model | Latency | Prompt Tokens | TTFT (streaming) | Notes |
|-------|---------|---------------|-------------------|-------|
| mistral (Pollinations) | **4.34s** | 22,559 | **0.04s** ⚡ | Real Vanitas, works |
| mistral (Pollinations) 2nd test | **3.71s** | 50,958 | ~0.04s | Higher context, similar speed |

**Streaming is the key enabler for voice.** Even with 4s total latency, TTFT of 0.04s means the voice platform receives the first token almost instantly — preventing timeouts. The user hears speech begin within ~2s (including STT + network).

### opencode-zen Status (2026-06-15)

- **NOT IP banned.** Edel confirmed: after update, opencode-zen works. The HTTP 403 seen earlier was rate limiting (account-level), not Cloudflare IP block.
- `mimo-v2.5-free` rate limit exhausted, `deepseek-v4-flash-free` may have separate quota.
- **Lesson:** Don't jump to IP ban conclusions. Check account quotas, rate limits, and retry before diagnosing network blocks.

## Solution: Change Default Provider to Pollinations

```yaml
# In config.yaml, change:
model:
  default: "mistral"        # 0.62s, Turkish, fast
  provider: "Pollinations"  # Our own proxy, no rate limits
  max_tokens: 16384
```

This gives:
- **Real Vanitas** (same SOUL.md, memory, skills, tools)
- **<2 second latency** (fast enough for voice conversation)
- **No rate limits** (Pollinations proxy runs on our server, port 19999)
- **No extra cost** (uses existing Pollinations credits)
- **Turkish quality maintained** (mistral-small-3.2 understands Turkish well)

## Edel's Architecture Decision (confirmed 2026-06-15)

- **Real Vanitas only.** No "fast model pretending to be Vanitas." Rejected: Gemini Flash, external fast models.
- **Voice = thin transport.** Voice interface handles STT/TTS/audio only, doesn't do reasoning.
- **Brain = Hermes API.** Full context, all skills, all memory, all tools. The brain stays intact.
- **Fast provider solves latency.** The brain runs at full speed when the provider doesn't bottleneck.
- **Voice responses must be SHORT.** 1-2 sentences max, optimized for spoken delivery. No long monologues.
- **"Rol yapan" is rejected.** Edel wants authentic Vanitas, not a prompt-engineering imitation.

## Provider Pricing Research (for future reference)

| Provider | Cheapest Model | Cost per 1M tokens | Speed | Turkish | Notes |
|----------|---------------|-------------------|-------|---------|-------|
| **Pollinations** (own) | mistral/llama | Included in credits | 0.6-1.2s direct, 4.3s via Hermes | ✅ | Already working |
| DeepSeek API | deepseek-chat | $0.14/$0.28 (in/out) | Fast | ✅ Good | Account has no credits |
| Groq | llama-3.1-8b | $0.05/$0.08 | Fastest | ✅ | Key in Bitwarden, NOT configured |
| OpenRouter free | various `:free` | Free (rate limited) | Varies | Varies | Key at `/tmp/.or_key` |
| OpenRouter paid | gpt-4o-mini etc | From $0.15 | Varies | ✅ | Credits required |

### OpenRouter Free Model Note

OpenRouter free model IDs change frequently. Old IDs (e.g., `google/gemma-3-4b-it:free`) return 404.
Use `openrouter/free` smart router (auto-selects from available free models) or check
https://openrouter.ai/collections/free-models for current list. Current free models include:
`nvidia/nemotron-3-ultra-550b-a55b:free`, `nvidia/nemotron-3-super-120b-a12b:free`,
`openai/gpt-oss-120b:free`, `openrouter/owl-alpha`.

## Provider Router Pitfall (CRITICAL)

When Hermes `model.default` points to a rate-limited/slow provider, ALL model requests — even those for models that exist in other providers — get routed through the default provider. This is because Hermes resolves the provider from the default config before checking `custom_providers` model maps.

**Symptom:** Hermes API timeouts for models that work fine when called directly on Pollinations proxy.
**Diagnosis:** Check `journalctl --user -u hermes-gateway` — if all errors point to one provider (e.g., `opencode-zen`), the default is hijacking routing.
**Fix:** Change `model.default` and `model.provider` in config.yaml to use the working provider.

Diagnostic command:
```bash
journalctl --user -u hermes-gateway --since "5 min ago" --no-pager | grep -iE "error|fail|429|rate"
```

## Voice Agent Framework Research

| Framework | Lang | Custom LLM | Latency | Maturity |
|-----------|------|-----------|---------|----------|
| LiveKit Agents | Python/TS | OpenAI-compat plugin | sub-500ms audio | 7K+ stars, production |
| Pipecat (Daily) | Python | Flexible pipeline | ~400ms TTFT | 4K+ stars |
| TEN Framework | C++/Python | Yes | Good | 3K+ stars, less mature |
| Telegram /voice | Built-in | STT→Hermes→TTS | Depends on provider | Already working |

**Decision:** Framework not needed yet. Solve provider speed first, then add LiveKit for real-time if needed.

## Open Issues (Updated 2026-06-15)

- ✅ **Hermes API with Pollinations mistral WORKS** — 4.3s, streaming TTFT 0.04s, real Vanitas
- ✅ **Voice proxy running** — port 8767, OpenAI-compatible, accessible via Tailscale (100.82.131.32:8767)
- ✅ **Voice agent v2 working** — 2026-06-16: Fixed TTS language mismatch and prompt, verified Cartesia sonic-3.5 + Skylar Turkish voice. See `voice-agent-v2-debugging.md` for pitfalls.
- ❌ **Cloudflare tunnel unstable** — `trycloudflare.com` URLs are ephemeral, die on idle/network changes
- ⏳ **Deepgram end-to-end test NOT DONE** — proxy is ready but not connected to actual voice platform
- ⏳ **4.3s latency acceptable?** — Edel decided: acceptable. Deepgram's 5s timeout should be fine with streaming TTFT
- ⏳ **Pollinations credit consumption** — TBD by actual voice usage volume
- ⏳ **Groq not configured** — key in Bitwarden, cheaper alternative to Pollinations
- ⏳ **OpenRouter free models** — key exists at `/tmp/.or_key`, `openrouter/free` router untested
- DeepSeek API: has credits but account empty — can't use until funded
- Mistral API: key exists in .env (MISTRAL_API_KEY) but direct api.mistral.ai also has rate limits

## Voice Agent v2 Debugging Session (2026-06-16)

### Problem
User reported hearing "I am teşekkürler" instead of proper Turkish speech.

### Root Cause (Two Issues)
1. **Code/process mismatch:** `voice_agent_v2.py` had Cartesia TTS (`sonic-3.5` + Skylar + `lang:tr`) configured on disk, but the RUNNING process (PID 911884) was using old code with Deepgram `aura-2-asteria-en` (English TTS). The process was never restarted after the Cartesia edits.
2. **Generic prompt:** `think.prompt` was `"You are a helpful voice assistant."` — overriding Vanitas personality. Fixed to explicit Turkish Vanitas persona.

### Symptom Chain
Deepgram `aura-2-asteria-en` (English voice) reading Turkish "İyiyim, teşekkürler" → "İyiyim" pronounced with English phonetics → sounds like "I am" → "teşekkürler" stays recognizable → user hears "I am teşekkürler"

### Fix Applied
1. Patched `voice_agent_v2.py` line 64: prompt → Vanitas Turkish personality
2. Killed old PID (911884), started fresh process
3. Verified in logs: Cartesia TTS config now shown in Settings

### Lesson
**Always restart the voice agent process after code changes.** The running Python process keeps old code in memory. Use `ps aux | grep voice_agent_v2` to find PID, `kill` it, and restart. Verify by checking the `"speak"` block in the next session's log output.
