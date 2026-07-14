# Vanitas Voice Agent v10.7 — Deepgram PCM + Streaming LLM (2026-06-16)

## Architecture (CURRENT v10.7)
Browser (PCM Int16, 16kHz, 4096-sample chunks per 256ms)
  -> WebSocket -> Voice Agent on port 8765 (FastAPI)
    -> Deepgram WS (whisper-large, linear16, interim_results=true, utterance_end_ms=1000)
    -> Interim transcripts sent INSTANTLY to frontend (type=interim)
    -> Final transcripts sent INSTANTLY + queued for LLM
    -> Proxy on port 8767 (vanitas_hermes_proxy.py)
      -> Strips ALL system msgs, injects REAL Vanitas prompt
      -> Hermes API on port 8642 -> Groq (llama-4-scout-17b)
    <- Bella TTS MP3 back to browser

## Architecture (Previous v10.4)
Browser (PCM Int16, 16kHz, 4096-sample chunks per 256ms)
  -> WebSocket -> Voice Agent on port 8765 (FastAPI)
    -> Deepgram WS (nova-2, linear16, interim_results=true, utterance_end_ms=1000)
    -> Utterance queue with 0.6s silence gap flush
    -> Proxy on port 8767 (vanitas_hermes_proxy.py)
      -> Strips ALL system msgs, injects REAL Vanitas prompt
      -> Hermes API on port 8642 -> openai (Pollinations)
    <- Bella TTS MP3 back to browser

## Key Parameters

### Browser (ScriptProcessorNode)
- Sample rate: 16000 Hz mono
- Buffer size: 4096 samples (256ms) — fewer WebSocket messages, less overhead
- Format: Int16 PCM (Float32 converted via `s < 0 ? s * 0x8000 : s * 0x7FFF`)
- NOT MediaRecorder — produces WebM container, incompatible with Deepgram raw encoding

### Deepgram WebSocket Connection (v10.7)
- URL: `wss://api.deepgram.com/v1/listen`
- Query: `model=whisper-large&encoding=linear16&sample_rate=16000&channels=1&interim_results=true&utterance_end_ms=1000&smart_format=true&punctuate=true`
- **Model change (2026-06-16):** `nova-2` + `language=tr` produced garbled Turkish. `whisper-large` (no language constraint) has significantly better accuracy.
- Auth: `Token {DEEPGRAM_API_KEY}` header
- `utterance_end_ms` minimum is 1000 (500 causes HTTP 400)

### Server-Side Utterance Handling (v10.7)
- **Interim transcripts:** Sent IMMEDIATELY to frontend as `{"type":"interim"}` — user sees real-time text
- **Final transcripts:** Sent IMMEDIATELY to frontend as `{"type":"transcript"}` + added to `utterance_queue`
- `delayed_flush(0.8)` — 0.8 second silence triggers LLM processing (display already happened)
- `speech_final` from Deepgram triggers immediate LLM flush
- **Streaming LLM** with `asyncio.wait_for(timeout=45)` + per-chunk stall detection (20s no chunk → abort)

### Proxy (vanitas_hermes_proxy.py, port 8767) — v10.7
- Model: `groq-llama-4-scout` (Groq LPU, via custom_provider in Hermes config)
- Non-streaming: `max_tokens=150`, streaming SSE chunks
- Still uses `httpx.AsyncHTTPTransport(retries=0)` — required on ARM64

## Pitfalls Resolved (v10.0 -> v10.7)

| Version | Problem | Fix |
|---------|---------|-----|
| v10.0-v10.2 | MediaRecorder WebM != Deepgram raw opus | AudioContext ScriptProcessor raw PCM Int16 |
| v10.3 | `utterance_end_ms=500` -> HTTP 400 | Changed to 1000 (minimum accepted) |
| v10.4 | `utterance_timer` not in nonlocal | Added to nonlocal declaration |
| v10.4 | httpx ReadTimeout on localhost POST | `AsyncHTTPTransport(retries=0)` |
| v10.4a | Overlapping LLM calls during TTS | Utterance lock pattern |
| v10.4a | Transcript not shown during response | Send transcript BEFORE buffering check |
| v10.4a | Voice agent timeout < proxy timeout | Aligned: both 45s |
| v10.4a | gemma degraded to 27s | Switched to `openai` (4-5s) |
| v10.4a | Proxy weak 4-line prompt | Upgraded to 24-line Vanitas prompt |
| **v10.7** | **Streaming LLM hung forever (no timeout)** | `asyncio.wait_for(45s)` + per-chunk 20s stall detection |
| **v10.7** | **asyncio.Lock reentrancy deadlock** | Moved recursive handle_reply OUTSIDE lock |
| **v10.7** | **Interim transcripts ignored -> display delay** | Send EVERY transcript instantly to frontend |
| **v10.7** | **Nova-2 Turkish garbled (language=tr)** | Switched to whisper-large model |
| **v10.7** | **Pollinations openai throttled 5-7s** | Switched to Groq llama-4-scout (~7.5s) |

## Utterance Lock Pattern (v10.7 FIXED)

**Problem:** Without a lock, `handle_reply()` runs concurrently when new utterances arrive during TTS playback. Two LLM calls overlap. In v10.4a, the recursive `handle_reply(full_text)` inside `async with reply_lock:` caused an **asyncio.Lock deadlock** — `asyncio.Lock` is NOT reentrant.

**Fix (v10.7 — 3-part):**

1. **`asyncio.Lock()` + `is_responding` flag — queue processing OUTSIDE lock:**
```python
reply_lock = asyncio.Lock()
is_responding = False

async def handle_reply(text):
    nonlocal is_responding, utterance_queue
    async with reply_lock:
        is_responding = True
        try:
            await _handle_reply_inner(text)  # LLM + TTS
        finally:
            is_responding = False
    # CRITICAL: process queue OUTSIDE lock to avoid reentrancy deadlock
    if utterance_queue:
        full_text = " ".join(utterance_queue).strip()
        utterance_queue = []
        if full_text:
            await handle_reply(full_text)
```

2. **`flush_utterances()` sends transcript FIRST, then checks lock:**
```python
async def flush_utterances():
    if not utterance_queue: return
    full_text = " ".join(utterance_queue).strip()
    # ALWAYS show transcript — user needs to see it
    await safe_send(json.dumps({"type": "transcript", "text": full_text}))
    if is_responding:
        return  # Buffer: keep in queue, don't call LLM
    utterance_queue = []
    await handle_reply(full_text)
```

3. **Streaming with timeout (v10.7):**
```python
async def _handle_reply_inner(text):
    full_reply = ""
    try:
        async def _stream_with_timeout():
            nonlocal full_reply
            async with httpx.AsyncClient(transport=TR, timeout=45) as c:
                async with c.stream("POST", PROXY_URL, json={...}) as r:
                    last_chunk = asyncio.get_running_loop().time()
                    async for line in r.aiter_lines():
                        # ... parse SSE ...
                        if tok:
                            full_reply += tok
                            last_chunk = asyncio.get_running_loop().time()
                        if asyncio.get_running_loop().time() - last_chunk > 20:
                            raise Exception("Stream stalled (20s no chunk)")
        await asyncio.wait_for(_stream_with_timeout(), timeout=45)
    except asyncio.TimeoutError:
        log.error("LLM timeout (45s)")
        if full_reply:  # partial response is better than nothing
            ...
```

**Key insight:** The transcript MUST reach the frontend even during response. In v10.7, EVERY transcript (interim + final) is sent INSTANTLY — no queue delay for display.

## ScriptProcessor vs MediaRecorder
| | MediaRecorder | ScriptProcessor |
|---|---|---|
| Output | WebM container | Raw PCM Int16 |
| Deepgram encoding | opus (MISMATCH) | linear16 (MATCH) |
| Chunk size | Variable | Fixed 4096 samples |
| Thread | Media thread (reliable) | Main thread (can lag) |

## Model Selection for Turkish Voice (BENCHMARKED 2026-06-16)

| Model | Provider | Latency | Turkish | Verdict |
|-------|----------|---------|---------|---------|
| **groq-llama-4-scout** | Groq | ~7.5s | ✅ Good | **USE THIS (v10.7)** — LPU fast, reliable, free tier |
| groq-instant | Groq | ~5s (est.) | ⚠️ OK | Backup for max speed — llama-3.1-8b |
| openai | Pollinations | 4-5s | ✅ Good | Was primary (v10.4a), now throttled |
| mistral | Pollinations | 15-16s | ⚠️ OK | Fallback only |
| openai-fast | Pollinations | 23-24s | ⚠️ OK | ❌ Name is misleading — SLOW |
| gemma | Pollinations | 27s | ✅ Good | ❌ Was fast (1-3s), now throttled |
| mimo-v2.5-free | opencode-zen | 5-10s | ✅ Best | Good quality, slow for real-time |
| deepseek-v4-pro | opencode-go | 30-50s | N/A | ❌ TOO SLOW (reasoning) |

**Groq integration (2026-06-16):** Added as custom_provider in Hermes config. Base URL: `https://api.groq.com/openai/v1`, API key from Bitwarden `GROQ_API_KEY`. Model aliases: `groq` (llama-4-scout), `groq-hizli` (llama-3.1-8b-instant). Proxy uses `groq-llama-4-scout` model name.

**Config pattern for adding providers (when patch tool refuses config.yaml):**
```python
import yaml
with open("config.yaml") as f: config = yaml.safe_load(f)
config["custom_providers"].insert(idx, {
    "api_key_env": "GROQ_API_KEY",
    "api_mode": "chat_completions", 
    "base_url": "https://api.groq.com/openai/v1",
    "models": {"groq-llama-4-scout": "llama-4-scout-17b-16e-instruct"},
    "name": "Groq"
})
config["model_aliases"]["groq"] = {"model": "groq-llama-4-scout", "provider": "Groq"}
# Then systemctl --user restart hermes-gateway
```

**Benchmark method:** `curl` against Hermes API (8642) or proxy (8767), measure wall-clock time.

## Hermes Config Model/Provider Consistency
Provider model lists (updated 2026-06-16):
- **Groq**: groq-llama-4-scout, groq-instant
- **Pollinations**: gemma, openai, openai-fast, openai-large, mistral, mistral-large, nova, llama, deepseek, qwen-coder
- **opencode-go**: deepseek-v4-pro, deepseek-v4-flash, glm-5, kimi-k2.5, minimax-m2.7, qwen3.7-max
- **opencode-zen**: mimo-v2.5-free, big-pickle, nemotron-3-ultra-free, deepseek-v4-flash-free, north-mini-code-free

Voice proxy overrides model per-request, so config default only affects Telegram.
