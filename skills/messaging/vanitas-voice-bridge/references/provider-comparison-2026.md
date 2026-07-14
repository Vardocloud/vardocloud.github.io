# Voice Provider Comparison — June 2026

Data collected 2026-06-17 from official pricing pages, Artificial Analysis, TokenMix, InfraBase, and direct API testing.

## Llama-4-Scout — Same Model, Different Providers

| Provider | Input/1M | Output/1M | Speed (t/s) | Free Tier | Notes |
|----------|----------|-----------|------------|-----------|-------|
| **Groq** | $0.11 | $0.34 | **500** | ✅ 30 RPM | LPU hardware, fastest |
| Vercel | $0.10 | $0.30 | ~115 | ❌ | |
| DeepInfra | $0.10 | $0.30 | ~160 | ❌ | |
| OpenRouter | $0.10 | $0.30 | ~100 | ❌ | Adds 5% markup |
| Novita | $0.18 | $0.59 | ~80 | ❌ | |

**Verdict:** Groq charges $0.01-0.04 more but delivers 4-5x faster inference. Worth it for voice.

## Voice-Suitable Fast Models (≤1.5s TTFT)

| Provider | Model | TTFT | Speed | Input/1M | Output/1M | Free? | Turkish |
|----------|-------|------|-------|----------|-----------|-------|---------|
| **Groq** | Llama-4-Scout 17B | **151ms** | 500 t/s | $0.11 | $0.34 | ✅ | ✅ Clean |
| Groq | Llama-3.1-8B | ~100ms | 840 t/s | $0.05 | $0.08 | ✅ | ⚠️ Basic |
| Groq | Llama-3.3-70B | ~700ms | 394 t/s | $0.59 | $0.79 | ✅ | ❌ Mixes RU/DE/EN |
| Groq | GPT-OSS-120B | ~700ms | 500 t/s | $0.15 | $0.60 | ✅ | Untested |
| **DeepSeek** | V4 Flash | **1.11s** | 83 t/s | $0.14 | $0.28 | ❌ | Untested |
| DeepSeek | V4 Pro | ~1.9s | 40 t/s | $1.74 | $3.48 | ❌ | Reasoning |
| Grok/xAI | 4.1 Fast | ~800ms? | ? | $0.20 | $0.50 | ⚠️ $175 credit | Untested |
| DeepInfra | Llama-4-Scout | ~700ms | 160 t/s | $0.08 | $0.30 | ❌ | |
| DeepInfra | Llama-4-Maverick | ~800ms | ? | $0.15 | $0.60 | ❌ | |
| Fireworks | DeepSeek V3 | ~1.2s | ~80 t/s | $0.45 | $1.10 | ❌ | |

## Free Tier Reality Check (Tested 2026-06-17)

| Provider | Status | Details |
|----------|--------|---------|
| **Groq** | ✅ Working | 30 RPM, 6K TPM, 14,400 req/day, no credit card |
| OpenRouter | ❌ 401 | Free models now require API key |
| Routeway | ❌ 401 | Free models now require API key |
| ZenMux | ❌ 403 | API key valid but 0 credits = access denied |
| DeepSeek | ❌ Balance | API key exists but "Insufficient Balance" |
| StepFun | ❌ 401 | API key required |

## Groq Free Tier Limits (April 2026)

- 30 requests/min per model
- 6,000 tokens/min (bottleneck for long prompts)
- 14,400 requests/day
- Organization-level (multiple keys don't bypass)
- All models available, no credit card needed

## Why Groq Wins for Turkish Voice

1. **LPU hardware** — custom silicon optimized for inference, 4-12x faster than GPU providers
2. **Llama-4-Scout** — consistently clean Turkish, no code-switching (unlike Llama-3.3-70B)
3. **Generous free tier** — sufficient for personal voice assistant usage
4. **OpenAI-compatible API** — drop-in replacement, zero migration cost
5. **Streaming SSE** — first token in 151ms, perfect for voice UX

## Price-Performance Winner

**DeepSeek V4 Flash** is theoretically the cheapest at $0.14/$0.28 (83 t/s, 1.11s TTFT) but:
- Hosted in China → latency to Turkey/Europe
- No free tier → requires top-up
- Turkish quality untested
- API key present but balance is 0

**Groq Llama-4-Scout** is the proven choice:
- 151ms TTFT (7x faster than DeepSeek)
- Free tier with no friction
- Verified clean Turkish
- Already integrated and working
