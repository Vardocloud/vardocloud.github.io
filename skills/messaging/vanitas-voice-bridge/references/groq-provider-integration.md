# Groq LPU Provider Integration (2026-06-16)

## Why Groq for Voice

Groq LPU hardware provides fastest LLM inference. For voice: sub-500ms first token, consistent streaming, no throttling, excellent Turkish via llama-4-scout. Free tier with generous limits.

## Adding to Hermes

Groq API is OpenAI-compatible. Add as custom_provider in config.yaml under `custom_providers`:

```yaml
- api_key_env: GROQ_API_KEY
  api_mode: chat_completions
  base_url: https://api.groq.com/openai/v1
  models:
    groq-llama-4-scout: llama-4-scout-17b-16e-instruct
    groq-instant: llama-3.1-8b-instant
  name: Groq
```

Also add model aliases:
```yaml
model_aliases:
  groq: {model: groq-llama-4-scout, provider: Groq}
  groq-hizli: {model: groq-instant, provider: Groq}
```

Insert before Secure-Local provider (or append to end of custom_providers list). Gateway restart required after config change.

## API Key

`GROQ_API_KEY` env var injected via Bitwarden Secrets Manager. Get key from console.groq.com/keys.

## Model Selection

| Model | Speed | Turkish | Use |
|-------|-------|---------|-----|
| llama-4-scout-17b | ~7.5s total | Excellent | Primary voice |
| llama-3.1-8b-instant | Fastest | Good | Fallback |

## Proxy Usage

```python
payload = {"model": "groq-llama-4-scout", "messages": clean, "stream": stream, "max_tokens": 150}
```

Hermes Gateway resolves model name to Groq provider via custom_providers config.

## Verified Quality (2026-06-16)

Natural Turkish, warm tone, emoji-native:
- "Merhaba Edel! İyiyim, teşekkür ederim. Sen nasılsın?"
- "Test başarılı sayılır mı? Sesin ulaştı, bağlantı sağlam."

## Streaming Reliability

Groq streaming hung on 3rd consecutive request in one test. Timeout pattern handles this: 45s total + 20s per-chunk with partial recovery. See v10.7-streaming-fixes reference.
