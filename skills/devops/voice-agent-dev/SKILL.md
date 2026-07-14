---
name: voice-agent-dev
description: "Deepgram Voice Agent development pattern — custom LLM endpoint (Mistral), browser audio fixes, Settings pitfalls"
version: 1.0.0
metadata:
  hermes:
    tags: [voice, deepgram, mistral, webrtc, audio, stt, tts]
    category: devops
---

# Voice Agent Development

Build a browser-based voice assistant using Deepgram Voice Agent API with custom LLM (Mistral).

## Architecture (preferred): Deepgram Agent API

Use `wss://agent.deepgram.com/v1/agent/converse` — Deepgram handles turn detection, endpointing, and audio routing. We provide Settings for STT, LLM, TTS.

```
Browser mic → Server WebSocket relay → Deepgram Agent → Custom LLM endpoint (Mistral)
                                              ↓
Browser speaker ← Server WebSocket relay ← Deepgram TTS ← LLM response
```

### Settings for Custom LLM (Proxy Pattern — REQUIRED)

**⚠️ Direct Mistral endpoint will FAIL** — Deepgram ignores OpenAI nested format. A local proxy is required. See `voice-agent` skill for complete working Settings.

**Working proxy Settings (schema-verified 2026-06-15):**
```json
{
  "type": "Settings",
  "audio": {
    "input": {"encoding": "linear16", "sample_rate": 24000},
    "output": {"encoding": "linear16", "sample_rate": 24000, "container": "wav"}
  },
  "agent": {
    "listen": {"provider": {"type": "deepgram", "model": "nova-3", "language": "en"}},
    "think": {
      "provider": {"type": "groq", "model": "llama-3.3-70b-versatile", "temperature": 0.8},
      "endpoint": {
        "url": "http://127.0.0.1:8766/v1/chat/completions",
        "headers": {"Content-Type": "application/json"}
      }
    },
    "speak": {"provider": {"type": "deepgram", "model": "aura-2-athena-en"}}
  }
}
```

**Key differences from earlier incorrect assumptions:**
- `provider.type`: MUST be `"groq"` — `"open_ai"` REJECTS BYO endpoint (only managed models). Groq is OpenAI-compatible.
- `provider.model`: **REQUIRED** even with BYO endpoint. Schema mandates `model` for all provider types. Use valid Groq model name.
- `provider.temperature`: MUST be inside `provider`, not at `think` level
- `endpoint.url`: Points to LOCAL PROXY (127.0.0.1:8766)
- **No `Authorization` header** in endpoint — proxy adds it (keeps keys off Deepgram's servers)

### CRITICAL: Settings JSON Pitfalls

1. **DO NOT put `temperature` at `think` level** — it MUST be inside `think.provider`. `"think": {"temperature": 0.8}` → `UNPARSABLE_CLIENT_MESSAGE`. Correct: `"think": {"provider": {"type": "open_ai", "model": "gpt-4o-mini", "temperature": 0.8}}`.
2. **DO NOT use unknown model names** (e.g., `mistral-small`) — Deepgram validates `provider.model` against its known list. Unknown names cause parse error BEFORE any API call. **For BYO endpoints, `provider.model` is REQUIRED** — use a valid name from the provider's list (e.g., `llama-3.3-70b-versatile` for groq). The endpoint/proxy determines the actual model; the model name is just for schema validation. For Deepgram-managed LLMs, use a recognized name (`gpt-4o-mini`, `gpt-4o`). **`open_ai` provider type does NOT support BYO endpoint** — use `groq` instead.
3. **DO NOT put `max_tokens` inside `agent.think.provider`** — extra fields cause `UNPARSABLE_CLIENT_MESSAGE`.
4. **Provider type** must be one Deepgram supports: `open_ai`, `anthropic`, `google`, `groq`, `nvidia`, `aws_bedrock`.
5. **Response format depends on provider type** — When using `type: "open_ai"`, Deepgram expects standard OpenAI format (`choices[].message.content`). The flat JSON format (`{"type": "ConversationText", ...}`) is for the manual pipeline, NOT the Agent API.
6. **Streaming (SSE) is REQUIRED** — plain JSON response won't work. Endpoint must stream `data: {...}\n\n` chunks. Returning JSON causes silent failure: Deepgram receives the response but does NOT pass it to TTS. No error, no audio — just silence.
7. **Proxy pattern is MANDATORY** for custom LLMs — see `voice-agent` skill for working Settings with proxy.
8. **`agent.language` is deprecated** — use `agent.listen.provider.language` and `agent.speak.provider.language` instead. Top-level `agent.language` may cause Settings parse errors in newer Deepgram API versions.

**Source:** [GitHub Discussion #1034](https://github.com/orgs/deepgram/discussions/1034), Deepgram Voice Agent docs: https://developers.deepgram.com/docs/voice-agent-llm-models

## Alternative: Manual Pipeline (not recommended)

Browser → Server → Deepgram STT → LLM → Deepgram TTS → Browser

Pitfalls with manual approach:
- Turn detection unreliable (interim results never become final)
- Echo loop from mic→speaker
- AudioContext suspension on mobile
- ScriptProcessorNode not firing in Chrome

Only use if Agent API is not viable.

## Browser Audio Fixes

### Chrome ScriptProcessorNode Fix
Chrome requires the ScriptProcessorNode to have an output connection to fire. Use a silent GainNode:

```javascript
var silentGain = ctx.createGain();
silentGain.gain.value = 0;
proc.connect(silentGain);
silentGain.connect(ctx.destination);
```

**NEVER** do `proc.connect(ctx.destination)` directly — creates echo loop (mic feeds back to speakers).

### Mobile AudioContext Auto-Resume
```javascript
ctx.onstatechange = function() {
  if (ctx.state === 'suspended') { ctx.resume(); }
};
```

Before playing audio: `if (ctx && ctx.state === 'suspended') { ctx.resume(); }`

## STT Parameter Tuning

For Deepgram STT listen endpoint:
- `endpointing=300` — 300ms silence triggers end of utterance
- `utterance_end_ms=1000` — explicit utterance end timeout
- `interim_results=true` — enable interim results (recommended with timeout fallback)
- `language=en` — set explicitly

## Write_file Tool Bug

The `write_file` tool's syntax checker incorrectly flags valid Python strings with mixed quotes:
```python
line.strip('"').strip("'")  # ❌ flagged as SyntaxError
```

Workaround: Use `chr(34)` and `chr(39)` instead:
```python
val.replace(chr(34), "").replace(chr(39), "")  # ✅ works
```
Or write files via `terminal cat > file << 'EOF'`.

## Debugging

- Server logs: `/tmp/voice_agent.log` (configured in server code)
- Check `tail -f /tmp/voice_agent.log` during testing
- Key log events: "STT final", "LLM", "TTS", "Agent error"
- Deepgram error "did not receive audio data within timeout" = ScriptProcessorNode not firing
- Deepgram error "UNPARSABLE_CLIENT_MESSAGE" = Settings JSON parse error
