# Voice Agent LLM Provider Comparison — June 2026

**Kritik metrik:** TTFT (Time To First Token) — sesli konuşmada <500ms hedef.

## Primary Candidates

| Provider | Model | TTFT | Tok/s | $/1M In | $/1M Out | Free Tier | Turkish |
|----------|-------|------|-------|---------|----------|-----------|---------|
| **Groq** | Llama-4-Scout 17B | **151ms** | 594 | $0.11 | $0.34 | ✅ 30 RPM | ✅ Clean |
| Groq | Llama-3.3-70B | ~600ms | 394 | $0.59 | $0.79 | ✅ 30 RPM | ⚠️ Mixes langs |
| Groq | GPT-OSS-120B | ~700ms | 500 | $0.15 | $0.60 | ✅ 30 RPM | ? |
| Groq | Llama-3.1-8B | ~100ms | 840 | $0.05 | $0.08 | ✅ 30 RPM | ? |
| **DeepSeek** | V4 Flash 284B MoE | **1.11s** | 83 | **$0.14** | **$0.28** | ❌ Needs $ | ? (China) |
| DeepSeek | V4 Pro 1.6T | ~1.9s | 40 | $1.74 | $3.48 | ❌ | ? |
| DeepInfra | Llama-4-Scout | ~700ms | ~160 | $0.08 | $0.30 | ❌ | ? |
| DeepInfra | Llama-4-Maverick 17Bx128E | ~800ms | ? | $0.15 | $0.60 | ❌ | ? |
| **xAI Grok** | 4.1 Fast | ~800ms? | ? | $0.20 | $0.50 | $175 credit | ? |
| xAI Grok | 4.3 | ~1s? | ? | $1.25 | $2.50 | $175 credit | ? |
| Fireworks | DeepSeek V3 | ~1.2s | ~80 | $0.45 | $1.10 | ❌ | ? |
| Together AI | Llama-4-Scout | ~800ms | ~80 | $0.59 | $0.79 | ❌ | ? |
| Together AI | Llama-4-Maverick | ~900ms | ? | $1.10 | $1.40 | ❌ | ? |
| Cerebras | Llama-4-Scout | ~200ms? | 1500 | $0.65 | $0.85 | ❌ Sub | ? |

## Verified Speeds (Tested June 17, 2026)

| Provider | Model | Test | Result | Notes |
|----------|-------|------|--------|-------|
| Groq Direct | Llama-4-Scout | Streaming TTFT | **151ms** | Free tier, key from Bitwarden |
| Groq Direct | Llama-3.3-70B | Streaming TTFT | 112ms | FAST but mixes Russian/German/English with Turkish |
| Groq Direct | Llama-3.1-8B | Non-streaming | 202ms | Lowercase, cut-off |
| Pollinations | Gemma (via proxy) | Streaming TTFT | 1500ms | Proxy overhead too high |
| OpenCode Go | DeepSeek V4 Flash | Streaming TTFT | 9580ms | Proxy overhead kills performance |
| DeepSeek Direct | deepseek-chat | Non-streaming | 742ms | Empty content (balance=0) |
| OpenRouter | Gemini Flash Lite | Non-streaming | 309ms | Returns "?" (empty/useless) |
| ZenMux | All models | — | 403 | 0 credits |
| StepFun | step-1-flash | — | 401 | Needs key |

## Provider Notes

### Groq (current choice)
- Custom LPU hardware — **fastest TTFT by far**
- Free tier: 30 RPM, 6K TPM, 14,400 req/day per model
- Developer tier: 10x limits, 25% token discount
- Model: `meta-llama/llama-4-scout-17b-16e-instruct` (⚠️ exact name critical)
- ❌ No GPT/Claude/Gemini — open-source only
- ❌ Fine-tuning not available

### DeepSeek V4 Flash
- **Best price-performance** in the industry
- 284B MoE, 13B active per token
- 83 tok/s, 1.11s TTFT (measured)
- $0.14/$0.28 per 1M — 12.4× cheaper than V4 Pro
- Off-peak: 50% discount (UTC 16:30-00:30 = TR 19:30-03:30)
- Cache hits: 90% discount ($0.014/1M)
- ❌ Hosted in China — adds latency
- ❌ Free tier only 10K tokens/min
- ❌ Turkish quality untested

### xAI Grok
- **$175/month free credits** via data-sharing program
- 2M context window (largest in industry)
- Grok 4.1 Fast: $0.20/$0.50 — cheapest "reasoning-capable" from major US provider
- Grok 4.3: production sweet spot at $1.25/$2.50
- ❌ Speed not benchmarked — AI Analysis data not available
- ❌ Turkish quality completely unknown

## Decision Matrix for Vanitas Voice

| Priority | Winner | Why |
|----------|--------|-----|
| **Speed** | Groq | 151ms TTFT, LPU hardware |
| **Cost ($0 budget)** | Groq Free | 14,400 req/day, no credit card |
| **Cost (paid)** | DeepSeek V4 Flash | $0.14/$0.28 — 4× cheaper than Groq paid |
| **Turkish quality** | Groq Llama-4-Scout | Tested, clean, no foreign language mixing |
| **Smartest model** | DeepSeek V4 Flash | 284B MoE, 79% SWE-bench |
| **Free credits** | xAI Grok | $175/month promotional |
| **Overall (current)** | **Groq Free** | Only option with free tier + proven Turkish |

## Groq Model Naming Pitfall

```python
✅ "meta-llama/llama-4-scout-17b-16e-instruct"  # Correct
❌ "llama-4-scout-17b-16e-instruct"             # 404
❌ "llama4-scout-17b-16e-instruct"              # 404
✅ "llama-3.3-70b-versatile"                    # Backup
✅ "llama-3.1-8b-instant"                       # Cheapest/fastest
```

## Groq Free Tier Limits (June 2026)

| Limit | Value | Notes |
|-------|-------|-------|
| Requests/min | 30 | Per model, org-level |
| Tokens/min | 6,000 | Real bottleneck for long prompts |
| Requests/day | 14,400 | ~500/hr sustained |
| Credit card | No | Truly free |

## Sources
- Artificial Analysis (June 2026): Groq TTFT 0.6-0.87s across catalog
- TokenMix (April 2026): Groq pricing, free tier limits
- TokenPricing.dev (June 2026): DeepSeek V4 Flash $0.14/$0.28
- Infrabase.ai (March 2026): Provider comparison, DeepInfra $0.039/$0.19
- TokenTab.dev (June 2026): DeepInfra all 67 models, Llama-4-Scout $0.08/$0.30
- GMI Cloud (May 2026): Reliability + speed leaderboard
- Şükrü Yusuf Kaya (2026): Turkish-language provider analysis
- Rogue Marketing (June 2026): Grok API pricing, $175 free credits
- DeepSeekSR1.com: V4 Flash specs, 83 tok/s, 1.11s TTFT
