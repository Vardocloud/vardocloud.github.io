# Groq Provider Setup for Voice Chat

## Prerequisites

- `GROQ_API_KEY` in Bitwarden or `.env` (free at console.groq.com)
- Hermes Agent with Bitwarden Secrets Manager enabled (auto-loads key)

## Add Groq as Custom Provider

Groq is added to `custom_providers` in Hermes `config.yaml`:

```yaml
custom_providers:
  - api_key_env: GROQ_API_KEY
    api_mode: chat_completions
    base_url: https://api.groq.com/openai/v1
    models:
      groq-llama-4-scout: llama-4-scout-17b-16e-instruct
      groq-instant: llama-3.1-8b-instant
    name: Groq
```

**Insert before Secure-Local** provider to keep ordering clean.

Also add model aliases for convenience:

```yaml
model_aliases:
  groq:
    model: groq-llama-4-scout
    provider: Groq
  groq-hizli:
    model: groq-instant
    provider: Groq
```

## Update Model Proxy

In the model proxy (`vanitas_hermes_proxy.py` or equivalent), change the model:

```python
# Before (slow — Pollinations)
payload = {"model": "openai", "messages": clean, "stream": stream, "max_tokens": 100}

# After (fast — Groq)
payload = {"model": "groq-llama-4-scout", "messages": clean, "stream": stream, "max_tokens": 150}
```

## Restart & Verify

```bash
systemctl --user restart hermes-gateway
pkill -f "vanitas_hermes_proxy.py"
# Restart proxy (background)
cd /home/ubuntu/voice-agent-venv && ./bin/python vanitas_hermes_proxy.py &

# Test
curl -s -X POST http://127.0.0.1:8767/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Merhaba nasilsin"}],"stream":false}'
```

## Groq Models for Voice

| Model ID | Hermes Name | Speed | Turkish | Best For |
|----------|-------------|-------|---------|----------|
| `llama-4-scout-17b-16e-instruct` | `groq-llama-4-scout` | ⚡⚡⚡ | ✅ Good | Default voice |
| `llama-3.1-8b-instant` | `groq-instant` | ⚡⚡⚡⚡ | ✅ Decent | Max speed |
| `llama-3.3-70b-versatile` | (add if needed) | ⚡⚡ | ✅ Best | Quality over speed |

## Why Groq Over Pollinations for Voice

- **Pollinations**: Free shared proxy, 5-7s first token, throttled on consecutive requests
- **Groq**: LPU hardware inference, <500ms first token, free tier 30 req/min
- **The Hermes Gateway itself is NOT the bottleneck** — the LLM backend is
