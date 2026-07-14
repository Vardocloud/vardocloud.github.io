# Deepgram Voice Agent — BYO Endpoint Rules

**Source:** https://developers.deepgram.com/docs/voice-agent-llm-models (2026-06-15)
**Tested:** 2026-06-15 with `vanitas-voice-bridge` architecture

## Key Rule: `provider.model` vs `endpoint.url`

**⚠️ Schema discovery (2026-06-15):** Deepgram API schema (`ThinkSettingsV1`) requires `provider` with BOTH `type` and `model` for ALL provider types — even with BYO endpoint. The `open_ai` provider type REJECTS BYO endpoint entirely (only managed models work). Use `groq` instead.

| Mode | `provider.type` | `provider.model` | `endpoint.url` | `prompt` | `timeout` |
|------|-----------------|-----------------|----------------|----------|-----------|
| **Managed LLM** (Deepgram provides) | `open_ai` ✅ | REQUIRED (known name) | OMIT | OK | OK |
| **BYO endpoint** (custom LLM) | **`groq`** ✅ | **REQUIRED** (valid Groq name) | REQUIRED | **OK** ✅ | **OMIT** ❌ |

**Critical:** `open_ai` provider type does NOT support BYO endpoint. Use `groq` instead — it's OpenAI-compatible and mandates endpoint.

## BYO Endpoint — Working Settings (verified 2026-06-15 via schema test)

```json
"think": {
    "provider": {
        "type": "groq",
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.8
    },
    "endpoint": {
        "url": "https://<tunnel>/v1/chat/completions",
        "headers": {"Content-Type": "application/json"}
    },
    "prompt": "You are Vanitas. Speak Turkish warmly..."
}
```

Note: `provider.model` is REQUIRED (schema validation) but the actual model is determined by your endpoint/proxy. Use any valid Groq model name (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`). `prompt` IS valid inside `think`. `timeout` is NOT in the schema — omitting it prevents parse errors.

## Error: UNPARSABLE_CLIENT_MESSAGE

This Deepgram error happens BEFORE any API call — it's a Settings JSON validation failure.

### Known causes (verified via schema test, 2026-06-15):
1. **Missing `provider.model`** — REQUIRED for all provider types per `ThinkSettingsV1Provider` schema
2. **`open_ai` + `endpoint.url`** — `open_ai` only supports managed models, rejects BYO endpoint
3. **`groq` without `provider.model`** — even with endpoint, model field is schema-required
4. **`timeout` inside `think`** — this field does NOT exist in `ThinkSettingsV1` schema
5. **`agent.language` at top level** — deprecated, use `agent.listen.provider.language` and `agent.speak.provider.language`
6. **`temperature` at `think` level** — MUST be inside `think.provider`, not at `think` level
7. **Extra/unknown fields** inside `provider` or `think` — Deepgram validates strictly
8. **Unknown model names** in managed mode — Deepgram validates against known list

## Supported `provider.type` values (BYO compatibility)

| Type | BYO Endpoint Support | Notes |
|------|---------------------|-------|
| `groq` | ✅ **WORKS** | OpenAI-compatible, endpoint REQUIRED |
| `open_ai` | ❌ REJECTS | Only managed models (gpt-4o, gpt-5-nano, etc.) |
| `google` | ✅ Docs show example | Tested with custom Google endpoint |
| `anthropic` | ? Untested | Docs say endpoint optional |
| `nvidia` | ? Untested | Docs say endpoint optional |
| `aws_bedrock` | ? Untested | Docs say endpoint REQUIRED |

## Deprecated Fields
- `agent.language` → use `agent.listen.provider.language` + `agent.speak.provider.language`
- `agent.listen.provider.model` with Flux → use `agent.listen.provider.version: "v2"`

## See Also
- [Deepgram LLM Models docs](https://developers.deepgram.com/docs/voice-agent-llm-models)
- [Deepgram Configure Voice Agent](https://developers.deepgram.com/docs/configure-voice-agent)
- `vanitas-voice-bridge` skill for working architecture
