---
name: voice-agent-webspeech
description: Browser-based voice agent using Chrome Web Speech API for STT, Hermes for LLM, and Pollinations for TTS. Complete pipeline from architecture to deployment behind token-secured Cloudflare tunnel.
---

# Voice Agent — Web Speech API Pipeline (ABANDONED — 2026-06-16)

> **⚠️ This approach is abandoned as of 2026-06-16.** Chrome's Web Speech API for Turkish had poor recognition quality, microphone clicking sounds from continuous start/stop cycling, echo loops, and high latency. After 3 iterations (v6→v7→v8), all fixes proved insufficient.
>
> **Replaced by v10:** Deepgram Nova-2 STT + MediaRecorder + ElevenLabs Bella TTS. See `vanitas-voice-bridge` skill for current architecture.
>
> This skill preserved for historical reference only.

## Why Abandoned

1. **Turkish recognition quality poor** — frequently misheard words, missed utterances entirely
2. **Microphone clicking** — `continuous: true` + `recognition.abort()` → `onend` restart cycle produced audible click each time  
3. **Echo loop** — TTS audio from speakers captured by mic, STT transcribed Vanitas's own voice
4. **Duplicate messages in UI** — `addMessage` called before guard checks
5. **Latency** — 500ms-1s per recognition cycle, unnatural flow

**Replaced by:** `voice-agent-v10` (Deepgram Nova-2 streaming + MediaRecorder opus + ElevenLabs Bella TTS). See `deepgram-voice-agent` skill for the working architecture. The v10.2 streaming proxy pattern eliminates all format issues, echo loops, and quality problems. Server code: `~/voice-agent-venv/voice_agent_v10.py`, port 8765.

## Fixes Attempted (All Insufficient — 2026-06-16)
- `recognition.abort()` instead of `stop()` → still fires `onend`
- `recognitionPaused` flag in `onend`/`onerror` → timing races with queued `onresult` callbacks
- 3-layer echo guard (substring, prefix, word overlap) → missed short echoes like "Selam" from "Selam! Ben..."
- Debounce with `isProcessing` → placed AFTER `addMessage`, causing visual duplicates in DOM
- `continuous: false` → more reliable STT but reintroduced microphone clicking
- **Root cause of echo loop (full trace):** TTS mp3 plays → speakers → mic captures → STT "Selam" → echo guard checks `"selam".includes("selam! ben iyiyim, sen..."` → FALSE → sends to server → loop. Fixed by checking REVERSE: `assistant_text.startsWith(recognized)` AND `assistant_text.includes(recognized)`.

Build a real-time Turkish voice agent where STT runs in the browser (Chrome `SpeechRecognition` API), LLM through Hermes, and TTS through Pollinations ElevenLabs Bella. Token-protected behind Cloudflare tunnel.

## Trigger
User wants to build/test/debug a browser-based voice interface, or STT latency/quality is the bottleneck for Turkish.

## Architecture (v6 — preferred)
```
Chrome SpeechRecognition (browser, lokal) → WebSocket (text) → Hermes API → Pollinations ElevenLabs Bella (mp3) → browser decodeAudioData
```

## Why Web Speech API beats all alternatives

| Approach | Turkish Quality | Latency | Cost | Privacy |
|---|---|---|---|---|
| Deepgram Voice Agent | Good | ~200ms | API $ | Audio leaves server |
| Deepgram STT WebSocket | Good | ~200ms | API $ | Timeout-prone |
| faster-whisper small (CPU) | Good | 3-32 sec | Free | Local |
| Pollinations Whisper | Terrible | ~1 sec | Polen | External |
| **Web Speech API** | **Google-quality** | **0 ms** | **Free** | **Browser-only** |

## Implementation Details

### 1. STT: Web Speech API (JavaScript — runs in browser)
```javascript
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.lang = 'tr-TR';
recognition.continuous = true;       // keeps listening after silence
recognition.interimResults = true;   // real-time partial results
recognition.onresult = (event) => {
  // event.results[i][0].transcript
  // isFinal=true → send to LLM; isFinal=false → show interim
};
recognition.onend = () => {
  // Auto-restart if connection still open
  if (ws && ws.readyState === WebSocket.OPEN) recognition.start();
};
```
- **Only works in Chrome** (and Chromium-based browsers). Safari/Firefox do NOT support.
- Interim results give real-time text preview; final result triggers Hermes call.
- The browser handles all VAD (voice activity detection) internally.

### 2. LLM: Route through the voice proxy, NOT Hermes directly
**⚠️ Hermes API requires authentication** — Authorization header mandatory. Direct calls return 401.

Use the voice proxy instead — it handles auth internally and forwards to Hermes. The proxy does NOT lose Vanitas context; it ENSURES Vanitas responds by routing through authenticated Hermes.

```python
PROXY_URL = f"http://127.0.0.1:{PROXY_PORT}/v1/chat/completions"
# NOT: HERMES_URL = f"http://127.0.0.1:{HERMES_PORT}/v1/chat/completions"  ← 401!

messages = [
    {"role": "system", "content": VANITAS_SYSTEM_PROMPT},
    *conversation_history[-10:],  # keep last 10 exchanges
]
# No auth header needed — proxy handles it
r = await c.post(PROXY_URL, json={"messages": messages, "stream": False})
```

**Architecture chain:** v6 → Proxy (has auth) → Hermes (requires auth) → Vanitas

### 3. TTS: Pollinations ElevenLabs — always use mp3 format
```python
# Primary
json={"model":"elevenlabs", "input":text, "voice":"bella", "response_format":"mp3", "speed":1.0}
# Fallback
json={"model":"qwen-tts", "input":text, "response_format":"mp3"}
```
- **Always `response_format: "mp3"`** — PCM raw bytes cause audio quality issues (voice sounds male/deep due to sample rate mismatch in manual Int16→Float32 conversion).
- Browser plays via `audioCtx.decodeAudioData(mp3Bytes)` — handles sample rate correctly.
- `elevenlabs` + `bella` is the primary combo (female Turkish voice, proven working).
- `qwen-tts` is a reliable fallback with default voice.

### 4. Security: Token auth on Cloudflare tunnel
- Add a random hex token to query string: `?token=<12-char-hex>`
- Server checks token on `/` (HTML page) and `/ws` (WebSocket) — wrong/missing token returns 403.
- Token is embedded into HTML so JS can pass it to WebSocket: `new WebSocket(.../ws?token=...)`
- Health endpoint `/health` is token-free (for monitoring).

## TTS Model Reference (Pollinations — tested 2025-06)

| Model | Voice | Result |
|---|---|---|
| `elevenlabs` | `bella` | 200, female Turkish |
| `elevenflash` | `bella` | 200, smaller file |
| `qwen-tts` | (default) | 200, large file, good fallback |
| `openai-audio` | `nova` | 400 — does not work |
| Deepgram `aura-2-asteria-en` | — | Turkish NOT supported (EN/ES/DE/FR/NL/IT/JA only) |

## Deepgram STT — Only If Web Speech API Is Unavailable

### Connection: Lazy WebSocket
Only open the Deepgram STT WebSocket when the first audio packet arrives from the browser — otherwise Deepgram times out in ~15 seconds with "did not receive audio" (error 1011).

### Working URL params (Nova-3)
```
wss://api.deepgram.com/v1/listen?encoding=linear16&sample_rate=24000&language=tr&model=nova-3&interim_results=true
```
Do NOT add `utterance_end_ms`, `no_delay`, or `endpointing` — they cause HTTP 400.

### REST API alternative
`POST https://api.deepgram.com/v1/listen?model=nova-3&language=tr` with raw audio body. Simpler than WebSocket but requires VAD on server side.

## Pitfalls

1. **STT is the bottleneck** — if STT takes >2 seconds, users close the browser before TTS plays. Web Speech API solves this (0ms).
2. **PCM audio quality** — manual Int16→Float32→AudioBuffer conversion distorts voice. Use mp3 + `decodeAudioData` instead.
3. **Hermes API requires auth** — direct calls to Hermes return 401. Always route through the voice proxy which handles `API_SERVER_KEY`.
4. **faster-whisper beam_size** — `beam_size=5` on CPU takes 32 seconds for 3 seconds of audio. `beam_size=1` improves to ~6 seconds but still too slow for real-time.
5. **Pollinations Whisper model** — marked as `whisper` in model list but produces garbage Turkish output (e.g., "Edel" → "altyazı M.K."). Do not use for Turkish.
6. **Cartesia API** — requires separate API key that was never configured. Falls back to deepgram TTS (English-only), causing "Failed to speak" errors.
7. **Web Speech API browser support** — Chrome only. Test with `!!window.SpeechRecognition` and show error if not available.
8. **Recognition click sound** — Web Speech API plays a system sound on start/stop. Keep recognition continuously open, only pause during TTS playback.
9. **🔊 ECHO LOOP (critical)** — `recognition.continuous = true` + TTS playback through speakers = microphone captures Vanitas's own voice → STT converts to text → sends back to Vanitas → infinite loop. **Symptoms:** message count escalates (2→3→5→7...) without user input, proxy log shows repeated calls, Vanitas appears to "talk to herself."

### Echo Loop Fix (3-layer defense)

**Layer 1 — Pause recognition during TTS:**
```javascript
let recognitionPaused = false;

// When TTS starts (agent_speaking event):
recognitionPaused = true;
try { recognition.stop(); } catch(e) {}

// When TTS finishes (after audio received):
setTimeout(() => {
  recognitionPaused = false;
  recognition.start();
}, 1500);  // 1500ms cooldown (not 500ms — too short)
```

**Layer 2 — Echo guard by text matching:**
```javascript
let lastAssistantText = '';

// Store Vanitas's last response
if (msg.type === 'transcript') {
  lastAssistantText = msg.content;
}

// In onresult, skip if captured text matches Vanitas's voice:
if (lastAssistantText && cleaned.includes(
    lastAssistantText.toLowerCase().substring(0, 20))) {
  console.log('🔇 Echo blocked:', cleaned);
  return;  // Don't send to server
}
```

**Layer 3 — RecognitionPaused gate in onresult:**
```javascript
recognition.onresult = (event) => {
  if (recognitionPaused) return;  // Drop ALL results during TTS
  // ... normal processing
};
```

**Why all three layers?** Layer 1 prevents most echoes. Layer 2 catches edge cases where TTS bleeds into recognition restart window. Layer 3 is the belt-and-suspenders — no STT events processed while agent is speaking.

## Files
- Implementation lives in `~/voice-agent-venv/voice_agent_v6.py` (current, Web Speech API)
- Proxy: `~/voice-agent-venv/vanitas_hermes_proxy.py` (port 8767, handles Hermes auth)
- Proxy logs: `/tmp/vanitas_proxy.log` — includes per-request message content since 2026-06-16
- v6 logs: `/tmp/voice_agent_v6.log`
- Earlier versions (v2-v5) available as `.bak` files for reference
- Service ports: v6 on 8765, proxy on 8767
- Cloudflare tunnel: proxy through WARP+ SOCKS5 to avoid IP blocks

## Debugging Echo Loops
When message count escalates without user input:
1. Check proxy log: `tail -f /tmp/vanitas_proxy.log` — look for `[user]` messages that match previous `[assistant]` text
2. Browser console: check for `🔇 Echo blocked` messages (confirms guard is working)
3. If loops persist, increase TTS cooldown from 1500ms to 2500ms
4. Verify `recognition.stop()` is called BEFORE TTS, not after
