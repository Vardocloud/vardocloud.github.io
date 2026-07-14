# Groq Direct API for Voice (June 2026)

## Speed Test Results (ARM64 Oracle Cloud, Istanbul)

| Model | Status | First Token | Total |
|-------|--------|-------------|-------|
| `meta-llama/llama-4-scout-17b-16e-instruct` | ✅ 200 OK | ~100ms | ~175ms |
| `llama-4-scout-17b-16e-instruct` | ❌ 404 | — | — |
| `llama4-scout-17b-16e-instruct` | ❌ 404 | — | — |
| `llama-3.3-70b-versatile` | ✅ 200 OK | — | ~171ms |
| `mixtral-8x7b-32768` | ❌ 400 | — | — (deprecated) |

## Endpoint
```
POST https://api.groq.com/openai/v1/chat/completions
Authorization: Bearer gsk_...
Content-Type: application/json
```

## Streaming Format
Standard SSE: `data: {"choices":[{"delta":{"content":"token"}}]}\n\n`
Termination: `data: [DONE]`

## API Key
- Source: Bitwarden Secrets Manager → `GROQ_API_KEY`
- Local: `voice-agent-venv/.groq_key` (chmod 600)
- Retrieved via: `bws secret list <PROJECT_ID> | python3 -c "..." `

## Alternatives Tested (Slower)
| API | Model | First Token |
|-----|-------|-------------|
| Pollinations :19999 | gemma | ~1500ms |
| OpenCode Go :19998 | deepseek-v4-flash | ~9580ms |
| DeepSeek direkt | deepseek-chat | 618ms (boş döndü) |
| Hermes Gateway :8642 | deepseek-v4-pro | ~2-3sn |

## Conclusion
Groq direkt API is the ONLY viable fast path for voice. All proxies add 500ms+ overhead.
