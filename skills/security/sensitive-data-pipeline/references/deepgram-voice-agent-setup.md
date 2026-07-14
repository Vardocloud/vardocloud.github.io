# Deepgram Voice Agent API — Complete Reference

## Architecture
Browser mic → WS → Your server (relay or direct) → Deepgram Voice Agent API
→ wss://api.deepgram.com/v1/agent/converse (US) or wss://api.eu.deepgram.com/v1/agent/converse (EU)
→ STT + LLM + TTS in a SINGLE WebSocket — no external LLM server needed

## LLM Provider Types (CRITICAL — the root of all bugs)

Deepgram Voice Agent supports 6+1 provider types for `agent.think.provider`:

| Type | Format | Endpoint Support | Notes |
|------|--------|-----------------|-------|
| `open_ai` | OpenAI Chat Completions (nested JSON) | YES — `endpoint.url` + `endpoint.headers` | ✅ **Use this for OpenRouter, Azure, any OpenAI-compatible API** |
| `anthropic` | Anthropic Messages | YES | Claude models |
| `google` | Gemini API | YES | Gemini models |
| `nvidia` | NVIDIA API | YES | Nemotron models |
| `groq` | Groq API | YES | Groq models |
| `aws_bedrock` | AWS Bedrock | YES | |
| `custom` | **Flat JSON ONLY** (`ConversationText`) | YES | ❌ **AVOID — requires non-standard format** |

### The `custom` Type Trap (June 2026)
- **`type: custom` requires FLAT JSON**: `{"type": "ConversationText", "role": "assistant", "content": "..."}`
- OpenAI-compatible APIs return NESTED format: `{"choices": [{"message": {"role": "assistant", "content": "..."}}]}`
- Deepgram's `custom` parser REJECTS nested JSON → "Error parsing client message" / "Check the agent.think field against the API spec"
- A proxy that reformats nested→flat AND streams SSE MIGHT work, but is fragile
- **Solution: Use `type: open_ai` instead** — it NATIVELY handles OpenAI format, and accepts a custom `endpoint`
- Source: [GitHub Discussion #1034](https://github.com/orgs/deepgram/discussions/1034)

### Working Pattern: open_ai + Custom Endpoint (TESTED & VERIFIED June 2026)

**⚠️ CRITICAL — Two fields MUST be inside `provider`, NOT at `think` level.** Putting `model` or `temperature` at the `think` level causes `Error parsing client message. Check the agent.think field against the API spec.` — these two bugs caused hours of debugging.

```json
{
  "think": {
    "provider": {
      "type": "open_ai",
      "model": "gpt-4o-mini",
      "temperature": 0.8
    },
    "endpoint": {
      "url": "https://openrouter.ai/api/v1/chat/completions",
      "headers": {
        "Authorization": "Bearer <KEY>",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://hermes.local",
        "X-Title": "Vanitas"
      }
    },
    "prompt": "You are a friendly voice assistant. Keep responses 1-3 sentences."
  }
}
```

**Valid fields at `think` level:** `provider`, `endpoint`, `prompt`, `functions`, `context_length` — NOT `model` or `temperature`.
**Valid fields inside `provider`:** `type`, `model`, `temperature`, `reasoning_mode`, `version`.

**Verified behavior:** This Settings JSON was accepted by Deepgram (SettingsApplied received). The model name `gpt-4o-mini` passes validation because it's in Deepgram's known list.

**Model name constraint:** Deepgram validates the model name even when using a custom endpoint. Unknown names (like `google/gemma-4-31b-it:free`) cause `UNPARSABLE_CLIENT_MESSAGE`. You MUST use a recognized model name in the provider. The endpoint receives whatever model name Deepgram sends — if Deepgram sends `gpt-4o-mini`, that's what OpenRouter routes.

**HTTPS endpoint required:** Endpoints MUST use `https://` or `wss://`. HTTP endpoints (including `http://127.0.0.1:8766/...`) are REJECTED with: `Endpoints must use https or wss. Invalid endpoint: http://...`

## OpenRouter Integration (Free Models)
- OpenRouter key: `/tmp/.or_key` (sk-or-v1-... format, 600 perms)
- Free models available: 22 (June 2026) — check live via `GET https://openrouter.ai/api/v1/models`
- Best free models for voice: `nvidia/nemotron-3-super-120b-a12b:free` (1M ctx), `qwen/qwen3-next-80b-a3b-instruct:free`, `meta-llama/llama-3.3-70b-instruct:free`
- REQUIRED headers for OpenRouter: `HTTP-Referer` + `X-Title` (OpenRouter blocks without them)
- Model IDs MUST include `:free` suffix for free tier access

## Deepgram Voice Agent vs LiveKit Agents — Different Products

| | Deepgram Voice Agent | LiveKit Agents |
|---|---|---|
| Architecture | Single WS: STT+LLM+TTS in Deepgram's runtime | Framework: compose separate STT/LLM/TTS/VAD plugins |
| LLM flexibility | provider types (above) + endpoint | Plugin system (mistralai, openai, deepgram, etc.) |
| Mistral integration | Via `type: open_ai` + custom endpoint | Native plugin: `livekit.plugins.mistralai` |
| Self-host cost | Only API key (no server needed) | Needs LiveKit server (self-host or Cloud) |
| WebRTC transport | No (raw WS) | Yes (built-in) |
| VAD/interruption | Built-in | Built-in via silero.VAD |
| When to use | Simpler, one WS connection, no extra infra | Full WebRTC, mobile-optimized, production-grade |

## Server Setup (Python SDK)
```bash
pip install deepgram-sdk requests
export DEEPGRAM_API_KEY="***"
```
- SDK: `DeepgramClient` → `client.agent.v1.connect()` → `connection.send_settings(settings)`
- Settings: `AgentV1Settings` with audio input/output, agent (listen/think/speak), greeting
- Full reference: https://developers.deepgram.com/docs/build-a-voice-agent-python

## Audio Playback (Browser)

See the "Browser audio playback — working approach" section under Pitfalls below for the tested gapless AudioContext scheduling technique.

## OpenRouter Free Model Speed Tests (June 2026)

Tested with `POST https://openrouter.ai/api/v1/chat/completions` (non-streaming unless noted):

| Model | Latency | First Token | Verdict |
|-------|---------|-------------|---------|
| **Google Gemma 4 31B** | 1.3s | 2.16s (stream) | ✅ Best choice — fast, clean responses, no thinking leak |
| NVIDIA Nemotron 3 Super | 2.1s | 1.66s (stream) | ⚠️ Thinking preamble leaks into response ("Okay, the user is asking...") |
| OpenAI GPT-OSS 20B | 2.8s | — | ✅ Backup — slower but solid |
| Qwen3 Next 80B | — | — | ❌ Provider errors on free tier |
| Meta Llama 3.3 70B | — | — | ❌ Provider errors on free tier |

**Recommendation:** Gemma 4 31B (`google/gemma-4-31b-it:free`) for voice. BUT note the model name constraint — Deepgram won't accept this name in provider. Workaround TBD (local HTTPS proxy to rewrite model name).

## Pitfalls (updated June 2026)

### Audio sample rate mismatch — silent STT failure (NEW)
- **Deepgram expects exactly the sample rate specified in Settings** (typically 24000Hz)
- Mobile browsers (Safari, Chrome Android) often IGNORE `AudioContext({sampleRate: 24000})` and use 48kHz default
- `getUserMedia({audio: {sampleRate: 24000}})` is also ignored on mobile — browsers don't support custom mic sample rates
- When the browser sends 48kHz PCM but Deepgram expects 24kHz, STT SILENTLY FAILS — no transcription, no error
- Deepgram times out after ~12 seconds with `CLIENT_MESSAGE_TIMEOUT` because the garbled audio can't be decoded
- **Diagnostic:** Log `audioCtx.sampleRate` in JS console. If ≠ 24000, resampling is required
- **Fix:** Client-side linear interpolation resampling in `onaudioprocess`:
  ```javascript
  const actualRate = audioCtx.sampleRate;
  const TARGET_RATE = 24000;
  const needsResample = actualRate !== TARGET_RATE;
  
  if (needsResample) {
    const ratio = actualRate / TARGET_RATE;
    const outLen = Math.floor(inLen / ratio);
    const samples = new Float32Array(outLen);
    for (let i = 0; i < outLen; i++) {
      const srcIdx = i * ratio;
      const srcFloor = Math.floor(srcIdx);
      const srcCeil = Math.min(srcFloor + 1, inLen - 1);
      const frac = srcIdx - srcFloor;
      samples[i] = input[srcFloor] * (1 - frac) + input[srcCeil] * frac;
    }
  }
  ```
- Verified working: iPhone Safari 48kHz → 24kHz resampling produced successful STT ("Homeowner." transcribed)

### OpenRouter "Failed to think" when using paid model name with zero credits (NEW)
- When Deepgram sends `model: "gpt-4o-mini"` to OpenRouter endpoint, OpenRouter routes to OpenAI's gpt-4o-mini
- If the OpenRouter key has **$0 balance**, this call FAILS with `Failed to think. Please check your agent.think settings.`
- The error appears as 3-4 empty `Warning` messages followed by the terminal `Error`
- **Two solutions:**
  1. **Use Deepgram's managed LLM** — remove `endpoint` entirely, Deepgram uses their own OpenAI subscription
  2. **Add OpenRouter credits** — minimum $5 deposit enables paid model routing
- For truly free models, a local HTTPS proxy (via cloudflared) can intercept and rewrite the model name from a Deepgram-recognized name to an OpenRouter `:free` model ID

### Deepgram managed LLM vs custom endpoint tradeoffs
- **Managed (no endpoint):** Deepgram bills your account for STT + LLM + TTS. Works out of the box. Tested: greeting "Hey! I'm Vanitas. What's up?" received.
- **Custom endpoint:** You control the LLM. Requires HTTPS endpoint. Model name must pass Deepgram validation. OpenRouter routing may cost money depending on model name sent. Settings format is finicky (temperature/model inside provider).

### FastAPI WebSocket `receive()` is ALWAYS a dict, never raw bytes (NEW — silent audio failure)
- **FastAPI's `WebSocket.receive()` returns `{"type": "websocket.receive", "bytes": ..., "text": ...}`**
- `isinstance(raw, bytes)` is **ALWAYS False** — the audio PCM data is at `raw["bytes"]`
- This causes ALL audio forwarding to silently fail: Deepgram never receives binary messages → `CLIENT_MESSAGE_TIMEOUT`
- **Fix:** Check `isinstance(raw, dict)` first, extract `raw.get("bytes")` for audio, `raw.get("text")` for text
- This bug also causes `NameError` because code falls through to text parsing where `msg` is undefined
- **Always `continue` after handling bytes** to skip text parsing branch entirely

### ScriptProcessor `onaudioprocess` silent on mobile Safari (NEW)
- On **iOS Safari** and some Android browsers, `ScriptProcessorNode.onaudioprocess` fires ONLY when connected to `audioCtx.destination`
- If not connected, the event never fires → no audio captured → `CLIENT_MESSAGE_TIMEOUT` even though mic permission is granted
- **Fix:** Connect processor to destination (`processor.connect(audioCtx.destination)`) for Safari compatibility
- **Echo tradeoff:** This creates a mic→speaker feedback loop. Mitigations:
  - User wears headphones/earbuds
  - `echoCancellation: true` in `getUserMedia` (helps but not perfect)
  - Use a `GainNode` with zero gain as intermediate node (untested on Safari)
- Diagnostic: add a blue level bar in HTML that fills when `onaudioprocess` fires — user can verify mic capture independently of network

### Model & temperature MUST be inside provider (two bugs, same error)
- Both `model` and `temperature` MUST be inside `provider` object, NOT at `think` level
- Wrong: `{"think": {"provider": {"type": "open_ai"}, "model": "gpt-4o-mini", "temperature": 0.8}}` ❌
- Correct: `{"think": {"provider": {"type": "open_ai", "model": "gpt-4o-mini", "temperature": 0.8}}}` ✅
- Error message for both: `Error parsing client message. Check the agent.think field against the API spec.`
- Validated through isolation tests: `{"temperature": 0.8}` alone at think level triggers UNPARSABLE_CLIENT_MESSAGE
- Valid `think`-level fields: `provider`, `endpoint`, `prompt`, `functions`, `context_length`
- Valid `provider`-level fields: `type`, `model`, `temperature`, `reasoning_mode`, `version`

### HTTPS endpoint requirement (NEW)
- Endpoints MUST use `https://` or `wss://`. HTTP (including localhost proxies) is REJECTED
- Error: `Endpoints must use https or wss. Invalid endpoint: http://127.0.0.1:8766/...`
- For local proxies, use cloudflared to get HTTPS (`cloudflared tunnel --url http://127.0.0.1:PORT`)

### Model name validation (NEW)
- Deepgram validates model names in provider even when using custom endpoint
- Unknown names (OpenRouter free IDs, custom model strings) are REJECTED
- Must use a recognized model name (e.g., `gpt-4o-mini`, `gpt-5-nano`)
- The endpoint receives whatever model name Deepgram sends — if Deepgram sends `gpt-4o-mini` through OpenRouter, OpenRouter routes to OpenAI's gpt-4o-mini (paid)
- For truly free models, a middleware proxy is needed to rewrite the model name in transit

### Browser audio playback — working approach (June 2026, tested iOS Safari)

**DO NOT use `container: "wav"`** in audio output settings. This causes Deepgram to send ZERO audio bytes (confirmed by server logs — no `bytes` type messages received from Deepgram WS). Use raw PCM output instead: `"output": {"encoding": "linear16", "sample_rate": 24000}`.

**DO NOT use `new Audio(blobUrl)`** on mobile. This SILENTLY FAILS on iOS Safari and Chrome Android due to autoplay restrictions. No error, just no sound.

**USE AudioContext `createBufferSource()` with chunk merging** — piggybacks on the AudioContext resumed during user gesture (Start button press). Critical sub-techniques:

1. **Chunk merging**: Deepgram sends ~960-byte chunks (20ms at 24kHz). Scheduling each individually creates 30ms gaps between 20ms chunks → crackling. Merge ALL pending chunks into one buffer before scheduling:
```javascript
// Merge queued chunks for smooth playback
let totalSamples = 0;
for (const c of audioChunks) totalSamples += c.length;
const merged = new Int16Array(totalSamples);
let offset = 0;
while (audioChunks.length > 0) {
  merged.set(audioChunks.shift(), offset);
  offset += audioChunks.shift().length;
}
```

2. **Gapless scheduling**: Track `nextPlayTime` to avoid overlaps:
```javascript
const startTime = Math.max(audioCtx.currentTime, nextPlayTime);
sourceNode.start(startTime);
nextPlayTime = startTime + audioBuffer.duration;
```

3. **Output connection**: `sourceNode.connect(audioCtx.destination)` — uses the already-resumed AudioContext (no autoplay block).

**PCM conversion**: Int16Array samples → Float32 `[-1.0, 1.0]` via `sample / 32768.0`.
- Setting `"output": {"encoding": "linear16", "sample_rate": 24000, "container": "wav"}` caused Deepgram to send **zero audio bytes** to the relay server
- Server logs showed text events (ConversationText, AgentStartedSpeaking) but `isinstance(raw_msg, bytes)` was NEVER True
- Users heard nothing — only text responses appeared
- **Fix:** Remove `container` entirely, use only `"output": {"encoding": "linear16", "sample_rate": 24000}`
- Deepgram sends raw PCM when no container is specified, which the browser wraps in WAV client-side
- This is the OPPOSITE of the documented behavior — the `container` field description is misleading

### FastAPI `WebSocket.receive()` NEVER returns raw bytes (NEW — 3+ hours of debugging)
- **FastAPI's `WebSocket.receive()` returns `{"type": "websocket.receive", "bytes": ..., "text": ...}`** — ALWAYS a dict
- `isinstance(raw, bytes)` is **ALWAYS False** regardless of what the client sent
- Audio PCM lives at `raw["bytes"]`, text at `raw["text"]`
- Code that checks `isinstance(raw, bytes)` silently drops ALL binary audio — Deepgram never receives it → `CLIENT_MESSAGE_TIMEOUT`
- Additionally, when bytes are handled but `continue` is missing, code falls through to `msg.get("type")` where `msg` is undefined → `NameError` → loop breaks → only first chunk sent
- **Fix pattern:**
  ```python
  raw = await browser_ws.receive()
  if isinstance(raw, dict):
      if "bytes" in raw:  # audio data
          await dg_ws.send(raw["bytes"])
          continue  # CRITICAL: skip text parsing!
      if "text" in raw:   # JSON message
          msg = json.loads(raw["text"])
  ```
### Balance check: use console.deepgram.com (REST endpoint may return empty)
### `custom` provider type = flat JSON only. Use `open_ai` with endpoint for any OpenAI-compatible API
### OpenRouter free models are rate-limited. Test voice latency <2s before committing
### Deepgram WS endpoint moved: `wss://agent.deepgram.com` → `wss://api.deepgram.com/v1/agent/converse` (Dec 2025)

## Reference Implementation
Working server: `/home/ubuntu/voice-agent-venv/voice_agent_v2.py`
- FastAPI + WebSocket relay between browser and Deepgram Voice Agent
- OpenRouter endpoint integration for LLM with `type: open_ai`
- Gapless browser audio playback via AudioContext scheduling
- HTML test page with microphone capture (24kHz linear16 PCM)
- Tunnel via `cloudflared tunnel --url http://127.0.0.1:8765` for HTTPS access
