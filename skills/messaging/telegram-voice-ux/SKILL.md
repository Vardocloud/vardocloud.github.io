---
name: telegram-voice-ux
version: 0.3.0
title: Telegram Voice UX (Hermes)
description: 'How to reliably get Hermes to return voice replies on Telegram using /voice modes, and how to debug when the UI doesn’t show expected voice bubbles.'
author: 'Vanitas (Edel)'
pinned: false
tags: [telegram, voice, tts, stt, elevenlabs, troubleshooting]
---

# Telegram Voice UX (Hermes)

## Goal
Make Telegram voice conversations feel natural: when the user sends **voice messages**, Hermes should respond with **voice messages** (Telegram voice bubbles), not only text.

## Relevant Hermes commands
- `/voice on` — voice reply to **voice messages only**
- `/voice off` — text-only replies (default)
- `/voice tts` — **auto-TTS all replies** (not ideal for “real chat” feel)
- `/voice status` — show current voice mode

## When to use
Use this skill whenever:
- The user prefers realistic chat flow: *user sends voice → assistant replies voice*
- The user complains that voice was generated but didn’t show as a voice bubble, or previous voice tests didn’t appear correctly.

## Core interaction pattern (realistic flow)
1. Ensure voice mode is set to **/voice on**.
2. Always test by sending a **short voice message** (1–2 sentences).
3. Validate that Hermes responds with a **Telegram voice bubble** (not just a text “read-out” preview).
4. If the assistant is replying to a voice message with text only, gently suggest `/voice on` rather than leaving the user to guess.
5. If voice bubble appears and is “birebir okunuyor” (same content), keep the setting; no need to switch to `/voice tts`.

## Debugging checklist: “Voice generated but chat shows text / nothing”
1. **Confirm mode**
   - Run `/voice status`.
   - If mode is not `voice-only`, switch accordingly (prefer `/voice on` for realism).
2. **Verify the trigger**
   - In `voice-only` mode, a *text* message from the user may produce **text** replies.
   - The user must send a **voice message** to trigger voice output.
3. **Telegram UI discrepancy**
   - If Hermes reports/produces a TTS audio internally but earlier messages didn’t show as voice bubbles, assume **Telegram rendering/UI timing or message-type formatting** differences.
   - Repeat with a single short voice test and re-check.
4. **Only if necessary**
   - Use `/voice tts` temporarily to force voice output for all replies if debugging proves the voice pipeline works but trigger mapping is off.
   - After confirmation, switch back to `/voice on` to preserve the natural chat UX.

## Pitfalls
- **Voice mode is per-chat, not per-user.** `/voice on` set in a DM (chat_id=6306976553) does NOT apply to a group chat (chat_id=-1003917030255). The `gateway_voice_mode.json` stores `platform:chat_id` keys. Always check which chat the user is in before assuming voice mode is active. To enable voice mode in a group, run `/voice on` inside that group.
- **Don't keep `/voice tts` as the default** when the goal is realism; it yields less "human chat" behavior (assistant speaks even when user wrote text).
- Voice-mode commands differ by surface (CLI vs messaging). Always use the messaging ones (`/voice ...`) inside Telegram.
- **Provider routing trap:** Hermes `model.default` provider overrides model-specific routing. If default is a rate-limited provider (e.g., opencode-zen), ALL models timeout even if they exist in other providers (e.g., Pollinations). Fix: change `model.provider` to the working provider. See `references/voice-agent-architecture-research.md`.
- **Voice responses must be short:** Long monologues kill voice UX. Enforce 1-2 sentence responses in voice mode — the full reasoning happens in the brain, only the conclusion reaches voice.
- **Do NOT jump to IP ban conclusions:** Cloudflare tunnel failures, HTTP errors, and timeouts have many causes (protocol mismatch, rate limiting, QUIC issues, config). IP ban is only ONE possibility. Check logs systematically before diagnosing. See `references/debugging-anti-patterns.md`.
- **Search session history FIRST:** Before debugging a recurring problem (voice agent, provider issues), use `session_search` to recall past attempts. Avoid repeating the same failed approaches. This session's voice debugging wasted time re-discovering known issues from June 14.
- **Cloudflare tunnel security:** Public `trycloudflare.com` URLs are accessible to anyone who knows the URL. Protect with token auth: FastAPI query param `?token=SECRET` on both GET `/` and WS `/ws`. Token embedded in HTML → injected into WebSocket URL. Without token: 403 Forbidden. Code pattern in v5/v6: `VOICE_TOKEN` env var, `index(token=...)` check, WS `query_params` check. See `references/cloudflare-tunnel-token-auth.md`.
- **Deepgram API key invalidation (2026-06-16):** Our Deepgram API key started returning `INVALID_AUTH` on REST API calls (`POST /v1/listen`). WebSocket `wss://api.deepgram.com/v1/listen` also failed with `400 Bad Request` and `1011 internal error` (timeout waiting for audio). **UPDATE 2026-06-16 later:** Key WORKS with WebSocket streaming using `encoding=linear16` — the `400`/`1011` errors were caused by format mismatch (WebM container sent as raw opus), not key invalidation. Always verify key with `websockets.connect()` test using correct encoding before assuming revoked. REST API still returns `INVALID_AUTH` → use WebSocket streaming only.
- **Web Speech API (DEPRECATED — do NOT use for new work):** v6-v8 used Chrome's `SpeechRecognition` API. ABANDONED June 16 due to: (a) microphone start/stop causes system clicking sounds, (b) Chrome's Turkish STT quality is mediocre, (c) `continuous` mode causes echo loops. Current winner is v9 (faster-whisper-tiny + webrtcvad VAD). Full evolution: `references/voice-agent-v8-echo-stt.md` and `references/voice-agent-v9-whisper-vad.md`.
- **faster-whisper model selection on ARM64:** `tiny` = 0.7x real-time (use this), `base` = 1.1x (better quality), `small` = 30s+ timeout (DO NOT USE). `compute_type='int8'` doesn't help enough on ARM64 — use `auto`.
- **httpx connection pooling timeout (CRITICAL):** `httpx.AsyncClient()` default transport hangs indefinitely on POST requests to localhost on ARM64 Oracle Cloud. Fix: ALWAYS use `transport=httpx.AsyncHTTPTransport(retries=0)`. Affects ALL venvs — voice-agent-venv, hermes venv. Symptom: `httpx.ReadTimeout` despite `curl` working instantly. See `references/httpx-transport-fix.md`.
- **MediaRecorder WebM ≠ Deepgram raw opus:** Browser `MediaRecorder` with `audio/webm;codecs=opus` produces **WebM container** chunks (EBML header + opus data + framing). Deepgram `encoding=opus` expects **raw opus frames**. Mismatch → `400 Bad Request: corrupt or unsupported data`. Fix: either (a) use `AudioContext` + `ScriptProcessor` to capture raw PCM Int16 → `encoding=linear16`, or (b) extract raw opus from WebM on server. Option (a) confirmed working with Deepgram Nova-2.
- **Deepgram utterance_end_ms minimum:** Setting `utterance_end_ms=500` causes `HTTP 400 Bad Request` on WebSocket connect. Minimum accepted value is `1000` (1 second). Range per docs: 1-20000ms but implementation rejects sub-1000.
- **ScriptProcessor buffer size tradeoff (PCM mode):** `1024` samples (64ms @ 16kHz) = too many WebSocket messages, overhead causes delays. `4096` samples (256ms) = fewer messages, more reliable transmission. MUST be power of 2.
- **Turkish voice model selection:** Hermes `/v1/chat/completions` routes all model names to Mistral (mediocre Turkish). Pollinations direct (port 19999) supports `gemma` (best natural Turkish tested), `gpt-5.4-mini` (good), `openai`/Mistral (OK but inconsistent), `glm` (broken — outputs internal reasoning). Model availability on Pollinations is intermittent — test with small payload before committing.
- **Voice agent personality injection:** The proxy (`vanitas_hermes_proxy.py`, port 8767) MUST inject the REAL Vanitas context (SOUL.md personality + MEMORY.md facts + USER.md profile). Old proxy used a generic 3-line prompt → robotic responses. New approach: strip ALL system messages from voice agent, inject ONE comprehensive system prompt sourced from the real Vanitas files. This is what makes the voice agent feel like the REAL Vanitas, not a mimic. The prompt should include: personality traits (warm, curious, playful, flirty), conversation rules (echo → one question → listen, never interview), Edel's personal context (DAÜ, NEU, LinkedIn, privacy preferences), and the key rule: \"Sen\" not \"Siz\", natural Turkish, emoji allowed.
- **Python nonlocal scope trap:** Nested `async def` functions inside `ws_endpoint` that assign to outer-scope variables (e.g., `utterance_timer`) MUST declare them in their `nonlocal` statement. Forgetting causes `cannot access local variable 'X' where it is not associated with a value` when the variable is read before assignment. The variable appears assigned in the function body, making Python treat it as local, but a read-before-assign path exists through async code flow.
- **asyncio.Lock deadlock (CRITICAL):** Calling `await handle_reply(full_text)` recursively INSIDE `async with reply_lock:` causes deadlock because `asyncio.Lock` is NOT reentrant. Fix: move queued utterance processing OUTSIDE the lock's `finally` block. The queue processing (`if utterance_queue: full_text = ...; await handle_reply(full_text)`) must happen AFTER the `async with` block exits. This allows the next `handle_reply` call to acquire the lock normally.
- **Transcript display during buffering (UI bug):** When `is_responding=True` and new utterances arrive, `flush_utterances()` MUST still send `{"type":"transcript",...}` to frontend BEFORE returning. Otherwise user sees no transcription and thinks "Türkçe anlamadı" when Deepgram actually transcribed correctly. Just skip the LLM call, not the UI update.
- **Timeout chain alignment:** Every hop in the voice pipeline must have timeout > the downstream hop. Wrong: voice agent 20s → proxy 35s → Hermes (voice agent times out first with 500). Right: voice agent 45s → proxy 45s → Hermes. Rule: set each layer's timeout to >= the next layer's timeout.
- **Pollinations consecutive-request throttling:** Requests get PROGRESSIVELY slower: #1=5s, #2=13s, #3=20s for same model. First request after idle is always fastest. This is server-side throttling, not fixable client-side. Mitigation: keep conversations short, prefer the first-response speed.
- **Model speed ≠ model name:** `openai-fast` was the SLOWEST at 23.6s. `openai` was the FASTEST at 4.5s. Always benchmark actual response times — never trust model names. Test with `curl` against Hermes API directly: `for m in openai openai-fast mistral; do time curl ... -d '{"model":"$m",...}'; done`.
- **Cloudflare tunnel URL lifecycle:** `trycloudflare.com` URLs are ephemeral — they expire after ~24 hours or when the tunnel process restarts. Always verify the current URL with `curl -s -o /dev/null -w "%{http_code}" <url>?token=...` before giving to the user. The tunnel process logs the URL on startup. Check with `ps aux | grep cloudflared | grep 8765` and `cat /tmp/cf_8765_v5.log` for the current URL.
- **Voice model latency hierarchy (Turkish) — BENCHMARKED 2026-06-16:** `openai` (Pollinations) = 4-5s, best speed/quality balance ✅. `mistral` (Pollinations) = 15-16s, OK Turkish. `openai-fast` (Pollinations) = 23-24s ⚠️ SLOW despite name. `gemma` (Pollinations) = 27s ❌ DO NOT USE for voice (was fast but now throttled). `mimo-v2.5-free` (opencode-zen) = 5-10s, best Turkish but moderate latency. Rule: USE `openai` for voice. NEVER use reasoning models (deepseek-v4-pro, kimi-k2-thinking) for voice — they "think" for 30+ seconds. **Always benchmark before committing to a model** — names are misleading and performance changes over time. Test with: `for m in openai openai-fast mistral gemma; do time curl -s ... -d '{"model":"$m","messages":[{"role":"user","content":"Selam"}],"max_tokens":30}'; done`.
- **Hermes config model/provider consistency:** When changing `model.default` in config.yaml, `model.provider` MUST be updated to a provider that actually hosts that model. Mismatch → Hermes API returns `502 Bad Gateway`. Pollinations hosts: `gemma`, `openai`, `openai-fast`, `openai-large`, `mistral`, `mistral-large`, `nova`, `llama`. Opencode-go hosts: `deepseek-v4-pro`, `deepseek-v4-flash`, `glm-5`, `kimi-k2.5`, `minimax-m2.7`. Opencode-zen hosts: `mimo-v2.5-free`, `big-pickle`, `nemotron-3-ultra-free`. The voice proxy overrides model per-request, so config default only affects Telegram sessions.
- **Feature-limited models (DO NOT request for chat):** `gemini-flash-lite-3.1` is configured as an AUXILIARY model only (vision, web_extract, compression, approval). It is NOT available as a general-purpose chat model via Hermes API. Do not attempt to route chat requests through it — use Pollinations or opencode-zen providers instead.
- **AssemblyAI Universal-3-Pro — Türkçe yok:** This model supports only 6 languages (English, Spanish, German, French, Portuguese, Italian). Turkish is NOT supported. Do not attempt to use it for Turkish voice transcription regardless of Pollinations model listing.
- **Deepgram Nova-2 Turkish accuracy issue (2026-06-16):** `model=nova-2&language=tr` produced garbled Turkish transcriptions (e.g., "Sesim nasıl, net geliyor mu baba?" → "Sesim ismini net etiket geliyor ya baba"). Root cause: `language=tr` constraint combined with Nova-2's training data produces artifacts in casual spoken Turkish. **CORRECTION 2026-06-16 later:** `whisper-large` does NOT work with Deepgram WebSocket streaming — returns `HTTP 405`. The actual fix for better Turkish is `model=nova-3&language=multi` (confirmed connected successfully). Nova-3 multilingual mode with `language=multi` enables code-switching including Turkish. Also add `endpointing=100` for multilingual mode per Deepgram docs.
- **Interim transcripts MUST be forwarded (UI responsiveness bug):** When `interim_results=true` is set but only `is_final` transcripts are forwarded to frontend, the user sees NO real-time text. Fix: send EVERY transcript (both interim and final) immediately to frontend. Use `{"type":"interim"}` for partial results, `{"type":"transcript"}` for finals. This eliminates the perceived "anında yazmıyor" problem.
- **Voice agent dual-service architecture:** Two services required — (1) Voice agent on port 8765 (browser-facing, WebSocket, STT), (2) Proxy on port 8767 (LLM/TTS backend). Both must be running. CF tunnel points to 8765. Voice agent calls proxy at `http://127.0.0.1:8767/v1/chat/completions`. Proxy handles model routing and personality injection.
- **webrtcvad pkg_resources bug:** webrtcvad 2.0.10 imports `pkg_resources` which doesn't exist in setuptools 67+. Fix: replace `pkg_resources.get_distribution('webrtcvad').version` with `"2.0.10"` and remove the import.
- **Pollinations Whisper (DO NOT USE):** `/v1/audio/transcriptions` returns HTTP 500 from upstream (ovh.net). Unreliable — use local faster-whisper instead.
- **Streaming LLM timeout (CRITICAL for Groq):** `aiter_lines()` hangs indefinitely if the upstream stream stalls. Fix with double timeout: (1) `asyncio.wait_for(_stream_with_timeout(), timeout=45)` for total response, (2) per-chunk 20s timeout inside the loop using `asyncio.get_event_loop().time()`. On timeout, use partial response if available instead of discarding everything. This prevents the "sessizce kilitlenme" behavior where the user hears nothing and the agent never recovers.
- **Groq custom provider setup (Hermes):** Add to `custom_providers` in `config.yaml`: `{api_key_env: GROQ_API_KEY, api_mode: chat_completions, base_url: https://api.groq.com/openai/v1, models: {groq-llama-4-scout: llama-4-scout-17b-16e-instruct, groq-instant: llama-3.1-8b-instant}, name: Groq}`. Add model aliases for convenience: `{groq: {model: groq-llama-4-scout, provider: Groq}}`. Groq LPU hardware provides ~7.5s total response with streaming SSE chunks. API key from Bitwarden `GROQ_API_KEY`. Note: Groq STT (Whisper) is REST-only, not streaming — use for batch transcription only, not real-time voice.
- **Browser AudioContext resilience:** `new AudioContext({sampleRate: 16000})` fails on some browsers. Fix: try with 16kHz first, fall back to `new AudioContext()` without constraints. Similarly, `getUserMedia` constraints should use `{ideal: 1}` instead of `channelCount: 1` and omit `sampleRate` — let the browser pick the best available config. Add `console.log('AudioContext sampleRate:', audioCtx.sampleRate)` for debugging.
- **ZeroGain echo prevention:** `processor.connect(audioCtx.destination)` creates echo loop. Fix: `const zeroGain = audioCtx.createGain(); zeroGain.gain.value = 0; processor.connect(zeroGain); zeroGain.connect(audioCtx.destination)`. This keeps the audio graph alive (ScriptProcessor needs active destination) while silencing speaker output. Browser `echoCancellation: true` handles physical echo separately.
- **Soniox — Turkish-native STT+TTS alternative:** Cloud API with "native-speaker accuracy" for Turkish. Real-time WebSocket streaming, barge-in via Silero VAD, open-source voice bot demo at `github.com/soniox/soniox_examples` (`apps/soniox-voice-bot-demo/`). Pricing: STT ~$0.12/hr, TTS ~$0.70/hr. Architecture: Python server + React frontend, modular (STT/LLM/TTS processors). Stack: `Browser PCM → Soniox STT → LLM (Groq/any) → Soniox TTS`. Significantly better Turkish accuracy than Deepgram. Consider migrating from Deepgram if Turkish quality remains inconsistent.
- **STT model trial history:** See `references/stt-model-trial-log.md` for the full Deepgram model trial log (nova-2, nova-3, whisper-large — what worked and what didn't).
- **DOM guard ordering (JS):** All guards (debounce, echo, recognitionPaused) must run BEFORE `addMessage()` / DOM manipulation. Otherwise duplicate `onresult` callbacks create visual duplicates even when the utterance is correctly blocked.

## Verification
- After setting `/voice on`, send a short voice message like: "Test tamam."
- Confirm the assistant response arrives as a **voice bubble** and the spoken content matches the intended transcript.

## Reference Files
- `references/telegram-native-voice-pipeline.md` — Full Telegram native voice processing pipeline: handler registration, caching, STT flow, auto-TTS logic, voice mode persistence, config, and debugging steps. Use this when debugging "voice message not arriving" or "no voice reply" issues in Telegram chats.

## STT Provider Decision Matrix (from v4/v5/v6/v8/v9 evolution)

**Never repeat the STT journey — use this table:**

| Scenario | Provider | Why |
|----------|----------|-----|
| Real-time voice (Chrome) | faster-whisper `tiny` + webrtcvad VAD (v9) | 0.7x real-time, good Turkish, no clicking, 400MB RAM |
| Real-time voice (non-Chrome) | faster-whisper `tiny` + webrtcvad VAD | Same server, browser-independent PCM capture |
| Better quality, slower | faster-whisper `base` | 1.1x real-time, better accuracy |
| Offline/batch transcription | faster-whisper `small`/`medium` | Accuracy over speed |
| Deepgram key works | Deepgram WS `nova-3` + `language=multi` + `endpointing=100` (`wss://...?model=nova-3&language=multi&...`) | 1-3s, Turkish via multilingual code-switching, PCM capture required |
| **NEVER for Turkish** | Pollinations Whisper (`/v1/audio/transcriptions`) | Returns HTTP 500, unreliable |
| **DEPRECATED — DO NOT USE** | Web Speech API (browser `SpeechRecognition`) | Poor Turkish, clicking sounds, echo loops |

**Why Web Speech API was abandoned (v6→v9):**
- Microphone start/stop cycles produce system audio clicks
- Chrome's Turkish STT quality is mediocre — misses words, slow
- `continuous` mode unstable: `true` = echo loops, `false` = slow start/stop
- Browser-dependent: Chrome only, Firefox unsupported

**Why faster-whisper tiny won:**
- 0.7x real-time on ARM64 — faster than speech
- Good enough Turkish for conversation
- No clicking (mic opens once, stays open with VAD)
- No echo loop risk (raw PCM, no browser STT feedback)
- Server-side = any browser works

**Why faster-whisper small failed:**
- 30+ seconds for 3s audio on ARM64 CPU
- `compute_type='int8'` doesn't help enough on ARM64
- Model loading: 9 seconds on startup

## Voice Agent Version History

- **v2:** Deepgram Voice Agent API (black box). Works but English TTS only ("I am teşekkürler"). Code: `voice_agent_v2.py`
- **v3:** Custom pipeline (Deepgram STT WS + Hermes + Bella). Deepgram WS broke (400→1011→INVALID_AUTH). Code: `voice_agent_v3.py` (dead)
- **v4:** Local faster-whisper STT. Too slow (32s). Code: `voice_agent_v4.py` (dead)
- **v5:** Pollinations Whisper STT. Bad Turkish. Code: `voice_agent_v5.py` (dead)
- **v9 (CURRENT):** faster-whisper-tiny + webrtcvad VAD. Best Turkish quality, no clicking. Code: `voice_agent_v9.py` ✅
  - Port 8765, log at `/tmp/voice_agent_v9.log`
  - Architecture: `Browser PCM → WS → VAD → Whisper tiny → Proxy(8767) → Hermes → Bella`
  - Whisper model: `tiny` (0.7x real-time, ~400MB RAM). `small` unusable on ARM64 (30s+ timeout).
  - VAD: webrtcvad mode 3, 16kHz, 30ms frames, 1s silence timeout
  - No echo loops — audio capture is raw PCM, no STT feedback path in browser
  - Full architecture and pitfalls: `references/voice-agent-v9-whisper-vad.md`

- **v10-v10.2 (Deepgram REST/WebM):** Attempted Deepgram Nova-2 with MediaRecorder WebM. **FAILED** — MediaRecorder `audio/webm;codecs=opus` produces WebM container, Deepgram expects raw opus → `400 corrupt data`. Multiple iterations (REST file upload, REST chunked, WebSocket streaming) all hit same format mismatch.

- **v10.3 (DEEPGRAM PCM FIX):** First working Deepgram approach. AudioContext + ScriptProcessor → raw PCM Int16 → Deepgram WS `encoding=linear16`. Confirmed: Deepgram accepts linear16, transcribes Turkish well. But had latency issues (13s delay) and Python `nonlocal` bug.

- **v10.4 (Deepgram production base):** Production Deepgram voice agent on port 8765. Key features:
  - PCM streaming (4096 sample buffer, 256ms chunks)
  - Deepgram Nova-2: `encoding=linear16&sample_rate=16000&interim_results=true&utterance_end_ms=1000`
  - Utterance queuing: 0.6s silence gap flushes to LLM
  - Utterance lock pattern: `asyncio.Lock()` + `is_responding` flag prevents overlapping LLM calls
  - Proxy v2.1 (port 8767): Strips incoming system msgs, injects comprehensive 24-line Vanitas prompt with examples
  - Model: `openai` on Pollinations via Hermes API (8642) — fastest at 4-5s (was `gemma` at 1-3s but degraded to 27s)
  - Timeouts: voice agent 45s, proxy 45s non-stream / 60s stream (aligned to prevent 500 chain)
  - httpx transport fix: `AsyncHTTPTransport(retries=0)` required on ARM64
  - Code: `voice_agent_v10_4.py` + `vanitas_hermes_proxy.py`
  - Architecture: `Browser PCM → WS(8765) → Deepgram WS → Proxy(8767) → Hermes(8642) → openai → Bella TTS`

- **v10.7 (CURRENT — streaming LLM + Groq + critical fixes):** v10.4 base with streaming LLM and six critical fixes. Code: `voice_agent_v10_7.py`.
  - **Streaming LLM:** `stream=True` to proxy, SSE chunk parsing, `asyncio.wait_for` with 45s total + 20s per-chunk timeout — prevents silent hangs
  - **Deadlock fix:** `handle_reply()` recursive call moved OUTSIDE `async with reply_lock` — `asyncio.Lock` is NOT reentrant
  - **Interim transcripts:** EVERY transcript (interim + final) sent instantly to frontend via `{"type":"interim"}` and `{"type":"transcript"}` — no more 0.6s display delay
  - **STT model:** `nova-2` + `language=tr` (garbled Turkish) → `whisper-large` (HTTP 405) → **`nova-3` + `language=multi` + `endpointing=100`** ✅ (confirmed connected, Turkish via code-switching)
  - **LLM model:** `openai` (Pollinations, 5-7s, throttled) replaced with **`groq-llama-4-scout`** (Groq LPU, ~7.5s total, 64 SSE chunks, more reliable)
  - **Groq provider:** Added as custom_provider in Hermes config (`api.groq.com/openai/v1`, models `groq-llama-4-scout` and `groq-instant`), API key from Bitwarden `GROQ_API_KEY`. Added model aliases `groq` and `groq-hizli`.
  - **Browser resilience:** AudioContext fallback (16kHz → default), relaxed getUserMedia constraints (`ideal` not exact), ZeroGain echo prevention
  - Architecture: `Browser PCM → WS(8765) → Deepgram WS (nova-3+multi) → Proxy(8767) → Hermes(8642) → Groq → Bella TTS`
  - **⚠️ Turkish accuracy still suboptimal** with Deepgram nova-3+multi — Soniox identified as superior alternative. Full STT provider comparison in `references/turkish-stt-provider-landscape.md`.

- **v6-v8 (DEPRECATED):** Web Speech API STT. ABANDONED due to poor Turkish quality, clicking sounds, echo loops.
  - **Why deprecated:** Chrome's Turkish STT is mediocre; start/stop cycles produce system audio pops; `continuous` mode causes echo loops and instability.
  - v8 echo loop prevention learnings preserved in `references/voice-agent-v8-echo-stt.md` (guard ordering still applies to any browser STT)
  - **401 fix preserved:** Must route through proxy (8767), never direct Hermes (8642)

## Voice Agent Architecture Research
See `references/voice-agent-architecture-research.md` for deep-dive: LiveKit vs Pipecat vs TEN, LLM latency analysis, model comparison for Turkish voice, and why Deepgram failed with our backend. Key decision: voice interface = thin transport, real agent brain behind it.

## MEDIA File Sending
See `references/media-file-sending.md` for Telegram dosya gönderme rehberi (izinli dizinler, format desteği, debugging).
