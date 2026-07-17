---
name: voice-agent-infrastructure
description: "Real-time AI voice agent setup — Deepgram Voice Agent, model proxy, SSE streaming, cloudflared tunnels. Covers configuration pitfalls and architecture patterns."
category: devops
tags: [voice, deepgram, websocket, SSE, cloudflared]
---

# Voice Agent Infrastructure

Build and debug real-time AI voice agents backed by LLM APIs.

## Architecture

```
Browser/Phone → Cloudflared Tunnel → Voice Agent Server (:8765)
                                         │
                                    POST /v1/chat/completions (SSE)
                                         │
                                    Model Proxy (:8767)
                                         │
                                    LLM Backend (Hermes API / OpenRouter)
```

## Services

| Service | Port | Role |
|---|---|---|
| `voice_agent_v2.py` | 8765 | Deepgram Voice Agent + SSE proxy endpoint |
| `model_proxy.py` | 8767 | Routes to LLM backend |
| `cloudflared` | dynamic | Public HTTPS tunnel for Deepgram cloud |

## Deepgram Voice Agent Critical Configuration

### Provider Settings (CRITICAL — wrong placement causes silent failures)

**Managed LLM (Deepgram provides the model):**
`model` and `temperature` MUST be inside the `provider` object:
```python
"think": {
    "provider": {
        "type": "open_ai",
        "model": "gpt-4o-mini",        # ← INSIDE provider (managed LLM)
        "temperature": 0.7,           # ← INSIDE provider
    },
    "timeout": 15000,
    "prompt": "System prompt text...",
}
```

**BYO Endpoint (custom LLM endpoint):**
`provider.model` MUST be OMITTED when `endpoint.url` is set. Including both causes `UNPARSABLE_CLIENT_MESSAGE`.
```python
"think": {
    "provider": {
        "type": "open_ai",
        "temperature": 0.7,           # ← OK (inside provider)
        # "model": "..."              # ← OMIT when using endpoint!
    },
    "endpoint": {
        "url": f"{TUNNEL_URL}/v1/chat/completions",
        "headers": {"Content-Type": "application/json"},
    },
    "timeout": 15000,
    "prompt": "System prompt text...",
}
```

**PITFALL:** Putting `model` at the `think` level (not inside `provider`) causes `UNPARSABLE_CLIENT_MESSAGE`. **PITFALL:** Including `provider.model` alongside `endpoint.url` (BYO mode) also causes `UNPARSABLE_CLIENT_MESSAGE` — Deepgram validates model names against its known list and rejects custom models in BYO mode.

### Think Endpoint Requirements

1. **MUST be a publicly accessible URL** — Deepgram Voice Agent runs in the cloud, cannot reach `localhost`
2. **MUST return SSE streaming** (`text/event-stream`) — JSON responses cause silent TTS failure (no audio output)
3. **MUST NOT include non-standard SSE events** — `event:` lines and tool events (`data: {"tool": ...}`) break Deepgram's parser
4. **MUST respect timeout** — Deepgram times out after ~5s for streaming; use `"timeout": 15000` in think_config

### TTS Model Constraint

Deepgram TTS models (e.g., `aura-2-helena-en`) are **English-only**. Non-English text is silently dropped — no audio, no error message.

**Workaround:** Force English-only responses via system prompt. For multilingual voice, use a different TTS provider (ElevenLabs, etc.).

## Model Proxy Design

### SSE Filtering (when backend emits tool events)

Some backends emit non-standard SSE data lines that break Deepgram:

```
data: {"tool": "skill_view", "label": "...", "status": "running"}
data: {"choices": [{"delta": {"content": "..."}}]}  ← Real content
```

Filter in proxy:
```python
if '"tool"' in decoded or '"toolCallId"' in decoded:
    continue  # Skip tool events
if decoded.startswith("event:"):
    continue  # Skip event lines
```

### OpenRouter Model Selection

**Use non-reasoning models.** Reasoning models put text in `delta.reasoning` not `delta.content`, causing empty TTS output.

Free non-reasoning models: `google/gemma-4-31b-it:free`, `meta-llama/llama-3.1-8b-instruct:free`
**DO NOT USE:** `nvidia/nemotron-3-super-120b-a12b:free` (reasoning model)

## LLM Backend for Voice: Groq (Recommended — June 2026)

**Groq LPU inference provides sub-second first-token latency** — the fastest option for real-time voice chat. Free tier is generous (30 req/min for some models).

### Groq via Hermes Gateway (Custom Provider)

Add Groq as a `custom_provider` in Hermes config, then the model proxy uses Hermes as normal — Hermes routes to Groq:

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

**Recommended model for voice:** `groq-llama-4-scout` (llama-4-scout-17b) — fast, good multilingual (Turkish works well), balanced quality. `groq-instant` (llama-3.1-8b) for maximum speed.

**Key:** `GROQ_API_KEY` must be in `.env` or Bitwarden. Groq API key is free at console.groq.com.

### Latency Comparison (June 2026)

| Backend | First Token | Total (short reply) | Verdict |
|---------|------------|---------------------|---------|
| **Groq llama-4-scout** | <500ms | ~2s | ✅ Best for voice |
| Pollinations `openai` | 5-7s | 8-10s | ❌ Too slow |
| OpenRouter gemma-4 | 1.3s | ~4s | ⚠️ Viable |
| Hermes+Pollinations chain | 6-9s | 10-15s | ❌ Too slow |

**Decision:** Use Groq for voice chat. Keep Hermes API for text conversations where context/memory matters more than latency.

### Previous Limitation (Now Resolved)

Hermes API used to be too slow for voice because it loaded ~50K tokens and routed through Pollinations (6-9s). With Groq as the provider, Hermes Gateway adds negligible overhead — the bottleneck was always Pollinations, not Hermes.

See `references/groq-provider-setup.md` for the full integration recipe.

## Cloudflared Tunnel

```bash
cloudflared tunnel --url http://127.0.0.1:8765
```

URLs change each restart. Update `TUNNEL_URL` in the voice agent after each restart.

## Known Issues

1. **Pollinations LLM is too slow for voice** (5-7s first token). Use Groq via Hermes custom provider instead — see LLM Backend section.
2. OpenRouter free models require crafted system prompt to simulate personality
3. Cloudflared quick tunnel URLs rotate on restart — capture with `grep -o "https://.*trycloudflare.com" /tmp/cf_tunnel.log`
4. Deepgram TTS is English-only — requires English-only prompt engineering or external TTS (ElevenLabs Bella via Pollinations)
5. Model proxy sometimes needs restart after gateway restart (port conflict)
6. **Deepgram STT Turkish = broken** — transcribes Turkish as Scandinavian/Germanic. Use Soniox instead.
7. **Pipecat v1.3.0**: Installed but not fully integrated. PipelineWorker.run(WorkerParams) API; FastAPIWebsocketTransport(websocket=ws) per-connection.
8. **Redaction write_file corruption**: Patterns like API_KEY=* in scripts get mangled. Use terminal heredoc to write scripts with credential references.

## Service Directory

`/home/ubuntu/voice-agent-venv/`
- `voice_agent_v10_8.py` — Soniox STT + Groq proxy + Bella TTS (working, June 2026)
- `voice_agent_v11_pipecat.py` — Pipecat pipeline (partially integrated)
- `vanitas_hermes_proxy.py` — Vanitas personality proxy (port 8767)
- `model_proxy.py` — aiohttp proxy to LLM backend

## Soniox STT (Production — June 2026)

Deepgram Turkish STT fails (transcribes as Scandinavian). **Soniox is the production STT.**

- **Account:** isimgorulsunn@gmail.com, org "herms", $3 balance (Stripe, no minimum)
- **API key:** `~/.hermes/soniox_api_key.txt` (600)
- **Model:** `stt-rt-v5` — 60 languages, Turkish ✅
- **WebSocket:** `wss://stt-rt.soniox.com/transcribe-websocket`
- **REST:** `https://api.soniox.com/v1`

### Login PITFALL
Soniox has TWO login pages. Automated login ONLY works at `console.soniox.com/signin` (email→password, two-step). The OAuth2 backend at `mobile-app-backend.soniox.com/accounts/login/` rejects automated credentials even when correct. VNC+xdotool is the reliable fallback for console access.

### WebSocket Config
```json
{"api_key":"...","model":"stt-rt-v5","audio_format":"pcm_s16le","sample_rate":16000,"num_channels":1,"language_hints":["tr"],"enable_endpoint_detection":true,"max_endpoint_delay_ms":1000}
```
