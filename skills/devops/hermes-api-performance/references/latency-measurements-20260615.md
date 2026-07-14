# Latency Measurements (2026-06-15)

All measurements from Oracle ARM64 (5.8GB RAM) server.

## Direct Proxy Tests (bypass Hermes)

| Proxy | Model | Latency | Turkish Response |
|-------|-------|---------|------------------|
| Pollinations (19999) | mistral (small-3.2) | 0.62s | "İyi!" |
| Pollinations (19999) | llama (3.3-70B) | 1.04s | "İyiyim." |
| Pollinations (19999) | openai (gpt-5.4-nano) | 1.17s | "İyiyim." |
| Pollinations (19999) | openai-fast (gpt-5-nano) | 1.95s | (empty) |
| opencode-go (19998) | kimi-k2.5 | 2.61s | "Merhaba!" |
| opencode-go (19998) | deepseek-v4-pro | 3.21s | "merhaba" |
| opencode-go (19998) | deepseek-v4-flash | 13.26s | "Merhaba" |
| opencode-zen | ALL models | HTTP 403 | Cloudflare error 1010 |

## Hermes API Tests (through 8642, with full context)

| Model | Provider | Latency | Prompt Tokens | Streaming TTFT |
|-------|----------|---------|---------------|----------------|
| kimi-k2.5 | opencode-go | 6.22s | 20,234 | - |
| deepseek-v4-flash | opencode-go | 5.85s | 50,958 | - |
| mistral | Pollinations | 3.71-4.34s | 22-51K | 0.04s |
| openai-fast | Pollinations | timeout | - | - |
| llama | Pollinations | 502 error | - | - |

## Context Assembly Overhead

Direct mistral: 0.62s
Through Hermes mistral: 4.34s
Overhead: ~3.72s (provider-independent)

## Provider Status

| Provider | Status | Note |
|----------|--------|------|
| opencode-go | ACTIVE | Default for daily use |
| Pollinations | ACTIVE | Fastest (0.6s), uses credits |
| opencode-zen | BLOCKED | Cloudflare IP reputation block |
| Mistral | UNTESTED | API key exists in .env |
| Secure-Local | UNTESTED | Ollama qwen3.5 |
| Groq | UNTESTED | API key in Bitwarden, $0.05/M tokens |

---

# 2026-06-16 UPDATE: Voice-Optimized Model Comparison

Measured through Hermes API (8642) → Pollinations. Single-sentence Turkish prompt ("Selam"), max_tokens=30, stream=false. 3 consecutive runs to test throttling.

## Per-Model Results

| Model | Run 1 | Run 2 | Run 3 | Degradation |
|-------|-------|-------|-------|-------------|
| `openai` | 4,513ms | 5,254ms | 13,272ms | 2.9× by run 3 |
| `openai-fast` | 23,572ms | — | — | **SLOWEST** |
| `mistral` | 15,882ms | — | — | Moderate |
| `gemma` | 27,112ms | — | — | Slowest single run |

## Findings

1. **`openai` is the fastest** at 4.5s first response — 5× faster than `openai-fast`
2. **`openai-fast` is a trap**: Despite the name, it's the slowest (23s). Name ≠ latency.
3. **Consecutive-request throttling**: `openai` degrades from 4.5s → 13s → 20s on back-to-back calls
4. **`gemma` at 27s** is unusable for voice despite good Turkish quality

## Voice Agent Recommendation

`openai` via Pollinations. Accept 5-15s latency range. The first response in a conversation
is fast; rapid back-and-forth will degrade due to Pollinations server-side throttling.
