# Soniox GitHub Resources

Soniox maintains an active GitHub organization at https://github.com/soniox with **17+ public repositories** (discovered 2026-06-22). Below are the repos most relevant to Vanitas Voice integration.

## 🐍 soniox-python — Python SDK

**URL:** https://github.com/soniox/soniox-python  
**Stars:** 8 | **Forks:** 5 | **Commits:** 154  
**Last commit:** *last week* (June 2026) — actively maintained

Official Python SDK for the Soniox API. Realtime and async STT + TTS.

```bash
pip install soniox
```

### Key Features

- **Realtime STT** — `AsyncSonioxClient.realtime.stt.connect()` with `RealtimeSTTConfig`
- **Realtime TTS** — `client.realtime.tts.connect()` with `RealtimeTTSConfig`
- **REST STT** — `client.stt.transcribe_and_wait_with_tokens()`
- **REST TTS** — `client.tts.generate_to_file()`
- **Full typing** — Pydantic models for all request/response types
- **Auto-config** — Reads `SONIOX_API_KEY` from env by default

### Async STT Usage (matches our architecture)

```python
from soniox.client import AsyncSonioxClient
from soniox.types import RealtimeSTTConfig

client = AsyncSonioxClient()
config = RealtimeSTTConfig(
    model="stt-rt-v5",
    audio_format="pcm_s16le",  # matches our browser PCM
    sample_rate=16000,
    num_channels=1,
    language_hints=["tr"],
    enable_endpoint_detection=True,
    max_endpoint_delay_ms=1000,
)

async with client.realtime.stt.connect(config=config) as session:
    # Feed browser PCM chunks as they arrive
    await session.send_bytes(pcm_chunk)
    
    # Receive events with auto-assembled tokens
    async for event in session.receive_events():
        for token in event.tokens:
            if token.is_final:
                print(token.text)  # SDK handles subword concat + dedup!
```

### Async TTS Usage (potential ElevenLabs alternative)

```python
from soniox.client import AsyncSonioxClient
from soniox.types import RealtimeTTSConfig

client = AsyncSonioxClient()
config = RealtimeTTSConfig(
    stream_id="vanitas-tts",
    model="tts-rt-v1",
    language="tr",  # Turkish support?
    voice="Maya",   # Voice selection
    audio_format="wav",
)

async with client.realtime.tts.connect(config=config) as session:
    await session.send_text_chunks(["Merhaba!", "Nasılsın?"], text_end=True)
    async for chunk in session.receive_audio_chunks():
        await websocket.send(chunk)  # Forward to browser
```

**⚠️ Turkish TTS not yet verified.** The README examples use "Adrian", "Maya" (English voices). Check `list_voices()` or Soniox docs for Turkish voice support before relying on this for production.

### Known Pitfall: Python 3.13.6 SSL Regression

CPython issue #137583: Python 3.13.6 has a regression in `ssl` that causes realtime WebSocket connections to hang. The SDK detects this at import time. **Avoid Python 3.13.6** — use any other 3.10-3.13.x.

### Directory Structure

```
src/soniox/
├── client.py          # SonioxClient (sync) + AsyncSonioxClient (async)
├── types.py           # RealtimeSTTConfig, RealtimeTTSConfig, Token, etc.
├── utils.py           # render_tokens, throttle_audio, output_file_for_audio_format
└── errors.py          # SonioxRealtimeError
examples/
├── soniox_client/     # Sync examples (STT + TTS, REST + realtime)
└── async_soniox_client/ # Async examples (matches our FastAPI pattern)
```

---

## 📦 soniox-js — JavaScript/TypeScript SDK Monorepo

**URL:** https://github.com/soniox/soniox-js  
**Stars:** 4 | **Forks:** 1 | **Issues:** 3

The successor to the archived `speech-to-text-web` repo (archived 28 May 2026). Monorepo structure.

```bash
npm install @soniox/speech-to-text-web
```

### Browser SDK (SonioxClient)

```javascript
const client = new SonioxClient({ apiKey: '...' });
client.start({
  model: 'stt-rt-v5',
  languageHints: ['tr'],        // Turkish support
  onPartialResult: (result) => {
    // result.tokens — per-token is_final
  }
});
```

### Features
- Language identification
- Speaker diarization
- Context terms (rare word hints)
- Endpoint detection
- Real-time translation
- **Temporary API keys** (no key exposure on client)

### Temporary API Key Pattern

```javascript
// Key never leaves your backend
const client = new SonioxClient({
  apiKey: async () => {
    const resp = await fetch('/api/get-temp-key', { method: 'POST' });
    const { apiKey } = await resp.json();
    return apiKey;
  },
});
```

Audio is buffered in memory until the async function resolves, then sent to Soniox. No API key exposure in browser.

---

## ⚡ vercel-ai-sdk-provider — Vercel AI SDK Provider

**URL:** https://github.com/soniox/vercel-ai-sdk-provider  
**Stars:** 1 | **Commits:** 19 | **Last commit:** 4 months ago

Vercel AI SDK (`useChat`, `useAssistant` hooks) için Soniox provider'ı.

```bash
npm install @soniox/vercel-ai-sdk-provider
```

**Not a priority until Stage 1+2 are stable** and/or frontend migrates to Next.js.

---

## 🔗 langchain-soniox — LangChain Integration

**URL:** https://github.com/soniox/langchain-soniox  
**Stars:** 0 | **Commits:** 5 | **Last commit:** 4 months ago

**⚠️ NOT a speech recognition model.** This is a LangChain document loader that transcribes audio files via the Soniox STT API and loads the result as LangChain documents.

```bash
pip install langchain-soniox
```

**Use case:** Post-recording analysis pipeline — transcribe meeting/podcast audio → LangChain chain for summarization, Q&A, etc.

**Not a replacement for Groq Whisper**, which remains optimal for real-time transcription needs.

---

## 🔧 n8n-nodes-soniox — n8n Workflow Node

**URL:** https://github.com/soniox/n8n-nodes-soniox  
**Stars:** 2 | **Fork:** 1

Soniox STT/TTS for n8n automation workflows. Not relevant unless n8n is adopted.

---

## 🧪 soniox-compare — Voice AI Side-by-Side Comparison

**URL:** https://github.com/soniox/soniox-compare  
**Stars:** 25 | **Forks:** 8

Real-time voice AI comparison tool — compares Soniox against Deepgram, Whisper, etc. Useful for benchmarking.

---

## 📚 soniox_examples — Multi-Language Examples

**URL:** https://github.com/soniox/soniox_examples  
**Stars:** 37 | **Forks:** 13

Examples of using Soniox client libraries in different programming languages. 37 stars — most popular Soniox repo.

---

## Soniox Organization — Full Repo List (10 of 17 visible)

| Repo | Description | Priority for Voice |
|------|-------------|-------------------|
| `soniox-python` | Python SDK: STT + TTS ✅ | 🥇 HIGH |
| `soniox-js` | JS SDK monorepo (replaces speech-to-text-web) | 🥈 HIGH |
| `vercel-ai-sdk-provider` | Vercel AI SDK provider | 🥉 MEDIUM |
| `langchain-soniox` | LangChain integration | MEDIUM (post-recording) |
| `soniox_examples` | Multi-language examples (37 ⭐) | REFERENCE |
| `soniox-compare` | Voice AI comparison tool | REFERENCE |
| `n8n-nodes-soniox` | n8n workflow node | LOW (no n8n) |
| `speech-to-text-web` | **ARCHIVED** (28 May 2026) | USE soniox-js INSTEAD |
| `langchain-js` | LangChain JS | LOW |
| `tanstackai-adapter` | TanStack AI adapter | LOW |

---

## Cost Comparison (STT, hourly rates, June 2026)

| Provider | Streaming | Async (file) | Turkish Quality | Notes |
|----------|-----------|-------------|----------------|-------|
| **Soniox stt-rt-v5** | **$0.12/hr** | $0.10/hr | ⭐⭐⭐⭐ | Best price/quality ratio |
| Deepgram Nova-2 | $0.35/hr | — | ⭐⭐⭐⭐ | 3× more expensive |
| Groq Whisper | **Free** 🆓 | Free | ⭐⭐⭐ | Rate-limited, file-based |

**Soniox is ~⅓ the price of Deepgram** with comparable Turkish quality.

---

## Integration Notes for Vanitas Voice

**Before (v10.10):** Manual WebSocket → Soniox STT via `websockets` library. Works but:
- ~80 lines of raw WS code in `vanitas_ses.py`
- Manual token concat (subword pitfall)
- Manual dedup (cumulative buffer pitfall)
- Manual reconnect on failure
- No typed models

**SDK Approach (v11, ✅ IMPLEMENTED 2026-06-22):**
- `AsyncSonioxClient` → clean async context manager
- `RealtimeSTTConfig` → typed configuration  
- `session.receive_events()` → auto-handled tokens
- Built-in reconnect and error handling
- Optional Soniox TTS via same SDK (Turkish TTS not verified)
- `vanitas_ses.py` reduced from 862 → 838 lines (-24)
- 3 pitfall classes eliminated (token dedup, subword concat, reconnect)

**Key question:** Does Soniox TTS support Turkish? If yes, could simplify the TTS chain (currently ElevenLabs Bella). If not, keep ElevenLabs for TTS and only replace STT.

**Test plan (✅ COMPLETED 2026-06-22):**
1. ✅ `pip install soniox==2.6.0` in voice-agent-venv (system python3.11)
2. ✅ Replace `connect_soniox()` + `process_soniox()` with SDK  
3. ✅ PCM stream feeding via `session.send_bytes()` — verified compatible
4. ✅ Syntax check passed, typed models verified
5. ⏳ Latency/quality comparison vs manual approach — pending
6. ⏳ Soniox TTS Turkish support test — pending
