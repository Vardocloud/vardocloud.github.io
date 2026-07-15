# Hermes Provider Health Reference

Quick-reference for testing and choosing between Hermes LLM providers.

## Provider Matrix

| Provider | Type | Health | Base URL | API Key Env | Notes |
|----------|------|--------|----------|-------------|-------|
| `opencode-zen` | Free | ✅ Functional | `https://opencode.ai/zen/v1` | `OPENCODE_ZEN_API_KEY` (optional) | Shared daily rate limit across ALL consumers |
| `custom:opencode-go` | Paid proxy | ✅ Reliable | `http://127.0.0.1:19998/v1` | `OPENCODE_GO_API_KEY` (auto-injected) | Proxy runs since container start |
| `NVIDIA` | Free NIM | ❌ Unreliable | `https://integrate.api.nvidia.com/v1` | `NVIDIA_API_KEY` | Frequent timeouts despite listed models |
| `Groq` | Free | ❌ Key invalid | `https://api.groq.com/openai/v1` | `GROQ_API_KEY` | HTTP 403 — key expired |
| `custom:Zenmux` | Paid | ✅ Limited | `https://zenmux.ai/api/v1` | `ZENMUX_API_KEY` | Only vision & web_extract |

## Auxiliary Systems Using opencode-zen

All of these consume the same free daily quota via `opencode-zen` → `deepseek-v4-flash-free`:
- compression, curator, session_search, approval
- MCP, skills_hub, profile_describer
- title_generation, triage_specifier

Every Hermes round-trip burns 5-15 free-tier calls through these subsystems.

## Free Tier Rate Limit

- **Type:** Daily cumulative quota (requests + tokens)
- **Resets:** ~midnight UTC
- **Shared across:** ALL opencode-zen calls (cron + auxiliary)
- **Symptom:** `HTTP 429 FreeUsageLimitError`
- **Pattern:** Early jobs succeed, late jobs (23:00+) fail
- **Load:** ~4-8 cron calls + ~20-50 auxiliary calls/day from normal usage

## Model Availability

### opencode-zen free models
- `deepseek-v4-flash-free` — best for general tasks
- `nemotron-3-ultra-free` — strong reasoning
- `mimo-v2.5-free` — lightweight
- `hy3-free` — experimental
- `north-mini-code-free` — code-focused

### opencode-go proxy (port 19998, paid)
- `deepseek-v4-flash` — most reliable, Turkish support
- `deepseek-v4-pro` — strong reasoning
- `qwen3.7-max` — strongest general
- `qwen3.7-plus` — Turkish-friendly
- `glm-5.1` — analysis/reasoning
- `kimi-k2.6` — long context
- `minimax-m3` — balanced

### NVIDIA (do not use for production)
Tested 2026-07-15: all models (GLM-5.2, Gemma 4, Nemotron Ultra, Step 3.7) timeout despite appearing in API model list. GLM-5.2 succeeded once then failed. Unreliable.
