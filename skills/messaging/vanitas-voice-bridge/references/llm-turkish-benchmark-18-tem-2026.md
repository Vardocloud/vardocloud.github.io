# LLM Turkish Quality Benchmark — 18 Tem 2026

## Context
Edel reported `llama-3.3-70b-versatile` (Groq) mixed English/Russian words into Turkish responses. Benchmark conducted to find a better Turkish LLM with acceptable latency for voice.

## Models Tested

### 1. NVIDIA NIM — Mistral Small 4 (`mistralai/mistral-small-4-119b-2603`)
- **Provider:** NVIDIA NIM (`https://integrate.api.nvidia.com/v1`)
- **Parameters:** 119B total (MoE), ~6B active per token
- **Context:** 256K
- **Pricing:** $0.15/M input tokens

### 2. Groq — llama-3.3-70b-versatile (current baseline)
- **Provider:** Groq (`https://api.groq.com/openai/v1`)
- **Note:** BWS key was expired during test (403 Forbidden). Previous benchmarks: ~293ms first token, ~197ms total.

### 3. Groq — GPT-OSS-120B (`openai/gpt-oss-120b`)
- **Note:** Same 403 — BWS key expired. Not tested.

## Test Prompts
```
1. "Merhaba Vanitas, nasılsın bugün?"
2. "Bana bir macera hikayesi anlatır mısın?"
3. "Türkiye'de en güzel şehir hangisi sizce?"
```

System prompt was the Vanitas voice persona from `tools.py`.

## Results — Mistral Small 4 (NVIDIA NIM)

| Prompt | First Token | Total | Response |
|--------|------------|-------|----------|
| "Merhaba Vanitas, nasılsın bugün?" | 570ms | 901ms | "Selam Edel, iyiyim teşekkür ederim. Sen nasılsın bugün?" |
| "Bana bir macera hikayesi anlatır mısın?" | 581ms | 1171ms | "Tabii ki! Eskiden kalma bir defter bulduk ikimiz de. Sayfalarında sadece 'Güneş'in Gizemi' yazıyordu. Birlikte okuyalım mı?" |
| "Türkiye'de en güzel şehir hangisi sizce?" | 560ms | 1428ms | "Elbette seninle aynı fikirde olmayabilirim ama benim için en güzeli İstanbul. Hem tarihi var hem modern, hem de her köşesinde ayrı bir hikaye saklı. Keşke bir gün birlikte geziye çıkabilsek." |

### Quality Assessment
- ✅ **Zero English/Russian leakage** — pure Turkish throughout
- ✅ Natural, fluent, warm tone — Vanitas persona intact
- ✅ Correct Turkish grammar (agglutinative morphology, vowel harmony)
- ✅ Contextually appropriate (mentions "ikimiz" = "both of us")
- ⚠️ ~270ms slower first token than Groq (560ms vs ~293ms) — acceptable for voice

## Comparison Summary

| Metric | Groq llama-3.3-70b | NVIDIA Mistral Small 4 |
|--------|-------------------|------------------------|
| First token | ~293ms | ~560ms |
| Turkish quality | 🟡 Mixed (EN/RU leakage) | 🟢 **Excellent** |
| Latency for voice | ✅ Ideal | ✅ Acceptable (<1s) |
| API | OpenAI-compatible | OpenAI-compatible |
| Key location | BWS (needs refresh) | BWS `NVIDIA_API_KEY` |
| Cost | Groq free tier | $0.15/M tokens |

## Recommendation

**Mistral Small 4 on NVIDIA NIM** is the clear winner for Turkish voice quality. The ~270ms additional latency is a worthwhile tradeoff for near-perfect Turkish.

### .env Configuration for Switch
```env
OPENAI_API_KEY=<NVIDIA_API_KEY from BWS>
OPENAI_BASE_URL=https://integrate.api.nvidia.com/v1
OPENAI_MODEL=mistralai/mistral-small-4-119b-2603
```

### Other Models Worth Testing (Future)
- **GPT-OSS-120B** on Groq (500 tps) — when BWS key refreshed
- **GPT-OSS-120B** on Cerebras (~3000 tps!) — if model becomes available
- **MiniMax M2.7** on Groq (preview) — enterprise-grade
- **Mistral Large 3** (675B, 41B active) — flagship, $0.50/M tokens

## TurkBench Reference
TurkBench (2026, ACL SIGTURK) is a comprehensive Turkish LLM benchmark with 8,151 samples across 21 tasks. Key finding: **Turkish-language prompts consistently outperform English-translated prompts** — our system prompt is already in Turkish, which is correct.

HuggingFace Leaderboard: https://huggingface.co/turkbench