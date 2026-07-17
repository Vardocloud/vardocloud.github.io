---
name: deepgram-voice-agent
title: Deepgram Voice Agent — Real-time Conversational AI
description: >-
  Build a real-time voice agent using Deepgram Voice Agent API (Agent API with BYO LLM)
  OR manual STT+LLM+TTS pipeline. Covers relay server architecture, browser audio capture,
  WAV header construction, asyncio patterns, credential retrieval, HTTPS tunnel for mobile
  testing, and the working groq+endpoint pattern for custom LLM backends.
trigger: >-
  User wants to build a voice agent, conversational AI, real-time speech-to-speech,
  or mentions Deepgram Voice Agent / STT / TTS / browser microphone integration.
---

# Deepgram Voice Agent

Real-time conversational AI: browser microphone → STT → LLM → TTS → browser speaker.
Built on Deepgram's Voice Agent API with BYO LLM.

## ⚠️ Turkish STT Limitation

**Deepgram's Turkish accuracy is poor** — nova-2 and nova-3 both produce inaccurate transcriptions
for casual spoken Turkish. For Turkish voice agents, see Soniox ($0.12/hr, native accuracy) or
ElevenLabs Scribe (3.8% WER, $0.39/hr).

Full STT options comparison: `references/turkish-stt-options.md`

## ⚡ Groq LLM Integration (Added 17 Haz 2026)

Groq's LPU inference provides fast streaming for voice agents. Add as custom provider in Hermes config:

```yaml
custom_providers:
  - name: Groq
    api_key_env: GROQ_API_KEY
    api_mode: chat_completions
    base_url: https://api.groq.com/openai/v1
    models:
      groq-llama-4-scout: llama-4-scout-17b-16e-instruct
      groq-instant: llama-3.1-8b-instant
```

Pattern: Voice Agent → Proxy → Hermes Gateway → Groq. Proxy overrides model to `groq-llama-4-scout`.
First token latency ~500ms, total ~7s for voice responses.

## Architecture

### ⭐ Deepgram Streaming Proxy — BİRİNCİL TERCİH (v10.2, 2026-06-16)

Deepgram REST API'de yaşanan kronik format sorunları (400 "corrupt or unsupported data") nedeniyle
**Deepgram WebSocket streaming API proxy** birincil çözümdür. Browser opus chunk'ları gönderir,
sunucu Deepgram'a direkt iletir — format dönüşümü YOK.

```python
# Browser: MediaRecorder → opus chunks → WebSocket → server
mediaRecorder = new MediaRecorder(stream, {mimeType: 'audio/webm;codecs=opus'});
mediaRecorder.start(250);  # 250ms chunks

# Server: Proxy to Deepgram streaming WebSocket
dg_ws = await websockets.connect(
    f"wss://api.deepgram.com/v1/listen?language=tr&model=nova-2"
    f"&encoding=opus&sample_rate=48000&channels=1",
    additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"}
)
# Relay audio: await dg_ws.send(raw_opus_chunk)
# Read results: async for msg in dg_ws: ...
```

**Ne zaman faster-whisper:** İnternet yoksa, API key yoksa, %100 lokal gerekiyorsa.
Ama ARM64 CPU'da SADECE `tiny` model çalışır (0.7x real-time). `small` model 30sn+ timeout.

Detaylı implementasyon: bu skill'in altındaki streaming proxy pattern.

### ⚠️ faster-whisper Lokal STT — SADECE tiny model (ARM64)

Deepgram STT API'de yaşanan kronik sorunlar (400, 1011 timeout, format uyuşmazlığı) nedeniyle
**faster-whisper small model** birincil STT çözümüdür. %100 lokal, sınırsız, ücretsiz.

```python
from faster_whisper import WhisperModel
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")
```

Kurulum: `pip install faster-whisper numpy`
Model ilk kullanımda otomatik iner (~500MB, HuggingFace cache).
Gecikme: ~1-3sn (ARM64 CPU). Doğruluk: Türkçe için small model yeterli.

**VAD (Voice Activity Detection):** Enerji tabanlı, threshold=0.015, silence_ms=600.
Sessizlik anında biriken PCM buffer'ı → 16kHz resample → faster-whisper transkribe.

Detaylı implementasyon: `references/manual-pipeline-v4.md`

**Ne zaman Deepgram STT kullanılır:** Gecikme ~200ms kritikse, internet varsa, API key geçerliyse.
Her zaman önce faster-whisper dene.

### ⚠️ Agent API (`agent.think`) — WORKS WITH CAVEATS

Deepgram'ın `wss://agent.deepgram.com/v1/agent/converse` endpoint'i custom LLM ile **çalışabilir** ama doğru kurulum gerektirir.

**Critical Requirements (2026-06-15, verified working):**
1. **Think endpoint MUST be publicly accessible** — Deepgram cloud calls it. Use cloudflared tunnel.
2. **SSE Streaming is REQUIRED** — Deepgram expects `data: {...}\n\n` chunks, NOT plain JSON. Returning JSON causes silent failure: Deepgram receives the LLM response but does NOT pass it to TTS. No error, no audio — just silence. The proxy endpoint must forward as `text/event-stream` with `X-Accel-Buffering: no` header.
3. **Add `/v1/chat/completions` route to voice agent** — Tunnel forwards to voice agent, which proxies to local LLM. The proxy must stream the response back via SSE.
4. **Model name must match your backend** — Don't use `gpt-4o-mini` if your proxy uses `mimo-v2.5-free`.
5. **⚠️ SPEED: Deepgram has ~5s think timeout** — If the LLM doesn't start streaming within 5s, Deepgram sends ⚠️ Warning → `FAILED_TO_THINK` → no TTS. Hermes API (5-12s with full context) is too slow. Use direct APIs (OpenRouter free: <1s).
6. **⚠️ FILTER non-OpenAI SSE events** — Backends like Hermes API inject `event: hermes.tool.progress` lines. These BREAK Deepgram's parser. Only pass through `data:` lines; skip `event:` lines entirely.
7. **⚠️ Non-reasoning models only** — Reasoning models (Nemotron, DeepSeek-R1) put text in `delta.reasoning` instead of `delta.content`. Deepgram reads `content` → empty → silence. Use `google/gemma-4-31b-it:free` or `meta-llama/llama-3.1-8b-instruct:free`.
8. **⚠️ TTS language must match LLM output** — `aura-2-helena-en` only speaks English. If LLM responds in Turkish, TTS produces silence (no error). Force English in system prompt or use multilingual TTS.

**Working Pattern (Agent API):**
```
Deepgram Cloud → Cloudflared Tunnel → Voice Agent /v1/chat/completions
                                         ↓ (SSE streaming + event filtering)
                                    Model Proxy (8767) → OpenRouter / Hermes API
```

**Speed Comparison (Think Step):**
| Backend | Latency | Works with Deepgram? |
|---------|---------|---------------------|
| OpenRouter Gemma 4 31B (free) | <1s | ✅ Recommended |
| OpenRouter Llama 3.1 8B (free) | <1s | ✅ Fast fallback |
| Deepgram Managed LLM | <2s | ✅ Works but no custom personality |
| Hermes API (full context) | 5-12s | ❌ Too slow — times out |

**Recommendation:** Use OpenRouter free models for voice think step. Hermes API is better for text chat where latency doesn't matter. The system prompt in the think config gives personality control comparable to Hermes API's SOUL.md.

**⚠️ Common Mistake:** Forcing `stream: false` causes Deepgram to receive JSON instead of SSE. The response IS received (you'll see "Think response: X chars" in logs) but TTS never fires. Always stream.

**When to use Agent API vs Manual Pipeline:**
- Agent API: Simpler code, Deepgram handles STT→LLM→TTS orchestration. Good for quick prototypes.
- Manual Pipeline: Full control, better debugging, LLM failures don't kill session. Better for production.

### ✅ Manuel Pipeline — RELIABLE, USE THIS

Her adımı kendin kontrol et:

```
Mikrofon → Deepgram STT (wss://api.deepgram.com/v1/listen)
         → Senin LLM çağrın (Pollinations / Mistral / OpenAI)
         → Deepgram TTS (https://api.deepgram.com/v1/speak)
         → Hoparlör
```

**Avantajlar:**
- Her adım loglanabilir (STT transkript, LLM istek/yanıt, TTS byte sayısı)
- `max_tokens`, `temperature`, `model` tam kontrol
- Provider değiştirmek tek satır
- Hata ayıklama saniyeler sürer

Referans implementasyon: `references/manual-pipeline-v4.md` (faster-whisper lokal STT + Hermes + ElevenLabs Bella, %100 lokal, 2026-06-16)

Streaming voice agent architecture (speculative LLM + sentence TTS + interruption): `references/streaming-voice-agent-pattern.md` (v10.6, 2026-06-16)

### Pollinations ElevenLabs Bella TTS — Türkçe İçin En İyi (Ücretsiz)

**Cartesia API key YOKSA birincil tercih budur.** Pollinations üzerinden ElevenLabs Bella:
- Model: `elevenlabs`, voice: `bella` — doğal Türkçe kadın sesi
- Endpoint: `POST https://gen.pollinations.ai/v1/audio/speech`
- Response: **mp3 format (`response_format: "mp3"`)** — tarayıcı `decodeAudioData` ile doğal çalar
- Fallback: `qwen-tts` (WAV formatı, güvenilir)
- **⚠️ `response_format: "pcm"` KULLANMA** — ham PCM Int16→Float32 dönüşümü ses kalitesini bozar, erkek sesi gibi çıkar

```python
resp = await client.post(
    "https://gen.pollinations.ai/v1/audio/speech",
    headers={"Authorization": f"Bearer {POLLINATIONS_API_KEY}"},
    json={"model": "elevenlabs", "input": text, "voice": "bella",
          "response_format": "mp3", "speed": 1.0},
)
return resp.content  # Browser'da decodeAudioData ile oynat
```

**Pollinations TTS modelleri (hepsi ücretsiz, kota sınırlı):**
| Model | Ses | Türkçe Kalitesi | Kullanım |
|-------|-----|----------------|----------|
| `elevenlabs` + `voice: bella` | Bella | ✅ Doğal | **Birincil** |
| `elevenflash` | Bella | ✅ Hızlı | Yedek |
| `openai-audio` + `voice: nova` | Nova | ⚠️ Orta | Son çare |
| `qwen-tts` | — | ⚠️ Test edilmedi | Alternatif |

### Lazy Deepgram STT Bağlantısı — Timeout'u Önler

Deepgram STT WebSocket'e bağlanır bağlanmaz timeout sayacı başlar.
Kullanıcı hemen konuşmazsa (~10-15sn) `1011 internal error` ile bağlantı kopar.

**Çözüm:** Deepgram bağlantısını **ilk ses paketi geldiğinde** aç:

```python
dg_ws = None

while True:
    raw = await browser_ws.receive()
    if is_audio:
        if dg_ws is None:  # Lazy connect
            dg_ws = await websockets.connect(dg_url, ...)
            dg_task = asyncio.create_task(read_deepgram_results())
        await dg_ws.send(data)
```

### Pollinations Model Speed Benchmark (2026-06-16)

Test edildi (direkt Hermes → Pollinations, 16 Haziran 16:38):
| Model | İlk istek | Ardışık | Not |
|-------|-----------|---------|-----|
| `openai` | **4.5sn** ✅ | 13-20sn | En hızlı, sesli için tek seçenek |
| `mistral` | 15.8sn | ~20sn | Türkçesi orta |
| `openai-fast` | 23.6sn ❌ | ~25sn | İsminin aksine en yavaş! |
| `gemma` | 27sn ❌ | ~30sn | Kullanılmaz |

**Pollinations progressive throttling:** Ardışık istekler 2-5x yavaşlar. İlk istek 5sn → 3. istek 20sn.

**Sesli sohbet için proxy model ayarı:** `"model": "openai"` (asla `openai-fast` veya `gemma` kullanma).

### Nova-2 / Nova-3 Minimum Parametre Seti

Fazla parametreler `HTTP 400` hatasına yol açar:

```python
# ✅ ÇALIŞAN — sadece gerekli parametreler
dg_url = (
    "wss://api.deepgram.com/v1/listen"
    "?encoding=linear16&sample_rate=16000&language=tr"
    "&model=nova-2&interim_results=true&smart_format=true&punctuate=true"
)

# ❌ 400 HATASI — bu parametreleri KULLANMA:
# &utterance_end_ms=700  → 400 (minimum 1000ms, hem nova-2 hem nova-3)
# &utterance_end_ms=800  → 400 (aynı sebep)
# &no_delay=true         → 400
# &endpointing=500       → 400
```

**⚠️ `utterance_end_ms` minimum 1000ms** — 700 ve 800 Nova-2/Nova-3'te HTTP 400 döndürür. Daha hızlı yanıt için istemci tarafında kendi sessizlik tespitini yap (bkz. streaming voice agent reference).

### Deepgram STT Event → LLM + TTS Pipeline

Manuel pipeline'da Deepgram STT'den gelen event'lere göre aksiyon:

| Event | Aksiyon |
|-------|---------|
| `SpeechStarted` | UI: "🎤 Listening..." |
| `Results` + `is_final: true` | `utterance_text` değişkenine kaydet |
| `UtteranceEnd` | `utterance_text.strip()` → LLM → TTS → browser |
| `Results` + `is_final: false` | Interim transkripti UI'da göster |

**`UtteranceEnd` tetikleyicidir** — LLM çağrısı bu event'te yapılır.
Final transkript `Results` event'inden gelir, `UtteranceEnd`'de birleştirilir.

## Setup

### Prerequisites
- Deepgram API key (stored in Bitwarden Secrets Manager as `DEEPGRAM_API_KEY`)
- BYO LLM API key (Pollinations `POLLINATIONS_API_KEY` preferred; DeepSeek works but may hit balance limits)
- Python venv with `fastapi`, `uvicorn`, `websockets`

### Credential Retrieval via bws
Use Bitwarden Secrets Manager CLI (at `~/.hermes/bin/bws`) with `BWS_ACCESS_TOKEN`:
```bash
bws secret list | python3 -c "
import sys, json
for s in json.load(sys.stdin):
    if 'DEEPGRAM' in s['key']:
        print(f'{s[\"key\"]} length={len(s[\"value\"])}')
"
```

### Server Code Template
→ `templates/relay_server.py` — Minimal FastAPI relay with:
- `_read_env` credential reader (env vars → `.env` file fallback)
- `/health` endpoint
- `/ws` WebSocket relay (browser ↔ Deepgram)
- Settings with `linear16` encoding (PCM from ScriptProcessorNode)

### HTTPS Tunnel for Mobile Testing
Phone browsers require HTTPS for `getUserMedia`. Use cloudflared (pre-installed at `/usr/local/bin/cloudflared`):
```bash
cloudflared tunnel --url http://127.0.0.1:PORT 2>&1 | tee /tmp/cf_voice.log
```
The tunnel URL appears in logs as `https://<random>.trycloudflare.com`.

## Critical Pitfalls

### 0. Python `nonlocal` Declaration Order — MUST Be At Function Top

In nested async functions, `nonlocal` must be declared BEFORE any access to the variable:

```python
# ❌ WRONG — crashes with UnboundLocalError
async def safe_send(msg):
    if not ws_open: return       # READS ws_open before nonlocal!
    try: ...
    except Exception:
        nonlocal ws_open; ws_open = False  # Too late

# ✅ CORRECT — nonlocal first
async def safe_send(msg):
    nonlocal ws_open
    if not ws_open: return
    try: ...
    except Exception:
        ws_open = False
```

**Symptom:** `UnboundLocalError: cannot access local variable 'ws_open' where it is not associated with a value`

### 0b. `finally` Blocks MUST Guard Task Variables

If the `try` block can exit before a task variable is assigned (e.g., `return` after failed connection), the `finally` block still runs and crashes:

```python
# ❌ WRONG — dg_task may not exist
try:
    if not await connect_dg():
        return              # ← exits before dg_task = ...
    dg_task = asyncio.create_task(...)
finally:
    dg_task.cancel()        # ← CRASH: UnboundLocalError

# ✅ CORRECT — initialize before try, guard in finally
dg_task = None
try:
    if not await connect_dg():
        return
    dg_task = asyncio.create_task(...)
finally:
    if dg_task:
        dg_task.cancel()
```

### 0c. FastAPI/Starlette WebSocket Binary Receive (2026-06-16)
**Starlette's `ws.receive()` returns binary data as `{"type": "websocket.receive", "bytes": b"..."}` — NOT raw bytes.**
If your code does `if isinstance(raw, bytes)` it will NEVER match. Must handle `raw.get("bytes")`:
```python
raw = await ws.receive()
if isinstance(raw, dict):
    if raw.get("text"):
        # handle text messages
        continue
    if raw.get("bytes"):
        raw = raw["bytes"]  # extract binary payload
    else:
        continue
if isinstance(raw, bytes):
    # now process binary audio
```
**Symptom:** PCM/audio chunks arrive at WebSocket but `isinstance(raw, bytes)` is False → all audio dropped silently.

### 0b. ScriptProcessorNode Fires Only When Connected to Destination (2026-06-16)
`createScriptProcessor()` will NOT fire its `onaudioprocess` callback unless the audio graph has an output path. To prevent feedback while satisfying this requirement:
```javascript
const silence = captureCtx.createGain();
silence.gain.value = 0;
processor.connect(silence);
silence.connect(captureCtx.destination);  // <-- REQUIRED for onaudioprocess to fire!
```
**Symptom:** WebSocket connects, microphone permission granted, but zero audio frames flow. `onaudioprocess` never called.
**Root cause:** Browsers optimize away audio graph nodes that have no output path. Without connecting to `destination`, the processor is treated as dead code and its callback is never invoked. The GainNode(0) trick satisfies the browser's requirement without creating audible feedback (gain=0 = silent output).

### 0e. Echo Loop — Microphone Picks Up TTS Output (2026-06-16)
When TTS audio plays through speakers in the same room as the microphone, the mic captures it → Deepgram transcribes garbage → LLM responds to garbage → more TTS → infinite feedback loop.
**Symptom:** Transcriptions show gibberish like `"San san san san"`, `"Ses sesi sim sim sim"` — these are the TTS audio being re-transcribed.
**Solution A (preferred):** Mute microphone during TTS playback. Gate audio in the frontend:
```javascript
let isSpeaking = false;  // true when Vanitas is playing TTS
processor.onaudioprocess = (e) => {
    if (isSpeaking) return;  // Drop mic audio during TTS
    // ... normal PCM capture ...
};
```
**Solution B:** Use headphones (eliminates acoustic echo entirely).
**Solution C (complex):** Server-side echo detection — compare incoming audio energy against recently-played TTS audio, skip if correlation is high. Requires significant DSP.

### 0f. Voice Agent Iteration Anti-Pattern — One Change At A Time (2026-06-16)
When debugging voice pipeline issues, making 4-5 changes per version (speculative LLM, sentence splitting, energy gating, audio queuing, session dedup) introduces new bugs faster than old ones are found. v10.4 had working STT but was broken across v10.5-v10.6 by layering too many features at once.

**Rule:** When STT works (transcriptions are accurate), make EXACTLY ONE change per iteration. Test before adding the next feature.

**Red flags:** Writing entirely new files instead of patching, adding 3+ features in one version, user says "it was working before" after changes.

### 0c. MediaRecorder WebM REST Fails with Deepgram — Use Streaming (2026-06-16)
Concatenating `MediaRecorder` webm chunks and POSTing to Deepgram REST API returns 400 "corrupt or unsupported data". The webm container from MediaRecorder's `dataavailable` events is a streaming format — concatenated chunks don't form a valid standalone file. **Solution:** Use Deepgram's WebSocket streaming API with `encoding=opus` — no format conversion needed, raw opus frames pass through.

### 0d. webrtcvad pkg_resources Bug (Python 3.12+, 2026-06-16)
`webrtcvad` 2.0.10 imports `pkg_resources` which was removed from setuptools 67+. Fix:
```python
# In /path/to/venv/lib/python3.12/site-packages/webrtcvad.py:
# Remove: import pkg_resources
# Replace: __version__ = pkg_resources.get_distribution('webrtcvad').version
# With:    __version__ = "2.0.10"
```

### 1. Audio Format MUST Match Settings Encoding
The `audio.input.encoding` in Settings dictates what the browser sends:
| Settings encoding | Browser must send | How |
|---|---|---|
| `linear16` (default) | Raw 16-bit PCM Int16Array | `ScriptProcessorNode` with Float32→Int16 conversion |
| `opus` | Raw Opus frames (NOT WebM container) | Hard to produce in browser; avoid |

**Rule: Use `encoding: "linear16"` + `ScriptProcessorNode` for PCM.**
MediaRecorder produces WebM/Opus *container*, not raw Opus frames. Deepgram rejects WebM/Opus when encoding is `linear16` with error: `"Error parsing client message. Check the audio.input.encoding field"`.

**Working browser PCM capture** (ScriptProcessorNode is deprecated but works in Chrome/Safari):
```javascript
ctx = new (window.AudioContext || window.webkitAudioContext)({sampleRate: 24000});
var src = ctx.createMediaStreamSource(stream);
var proc = ctx.createScriptProcessor(4096, 1, 1);
src.connect(proc);
proc.onaudioprocess = function(e) {
    if (!ws || ws.readyState !== 1) return;
    var input = e.inputBuffer.getChannelData(0);
    var pcm = new Int16Array(input.length);
    for (var i = 0; i < input.length; i++) {
        var s = Math.max(-1, Math.min(1, input[i]));
        pcm[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    ws.send(pcm.buffer);
};
```

### 2. Browser getUserMedia Support

### 2b. Sample Rate Mismatch — PCM Resampling
**Telegram/Facebook in-app browsers do NOT support `getUserMedia` at all.**
Detect and warn immediately on page load:
```javascript
if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    // Show red warning: "Chrome/Safari kullanın"
    document.getElementById('warn').style.display = 'block';
    document.getElementById('btn').disabled = true;
}
```
- Phone: MUST use external browser (Chrome/Safari) + HTTPS (cloudflared tunnel)
- PC: Chrome on Tailscale HTTP works, Safari requires HTTPS
- Error: `Cannot read properties of undefined (reading 'getUserMedia')` means unsupported browser

### 2b. Sample Rate Mismatch — PCM Resampling

`getUserMedia({audio: {sampleRate: 24000}})` her tarayıcıda çalışmaz.
Gerçek sample rate `audioCtx.sampleRate`'ten okunup istemci tarafında yeniden örneklenmeli:

```javascript
const actualRate = audioCtx.sampleRate;  // 44100, 48000...
const targetRate = 24000;
const ratio = actualRate / targetRate;
processor.onaudioprocess = (e) => {
    const input = e.inputBuffer.getChannelData(0);
    let outLen = Math.floor(input.length / ratio);
    const int16 = new Int16Array(outLen);
    for (let i = 0; i < outLen; i++)
        int16[i] = Math.max(-32768, Math.min(32767, input[Math.floor(i*ratio)] * 32767));
    ws.send(int16.buffer);
};
```

Olmazsa ses paketleri Deepgram'a gider ama `SpeechStarted` hiç tetiklenmez — sessizlik gibi.

### 3. Phone Browsers Require HTTPS for Microphone
- `getUserMedia()` fails silently on HTTP origins in mobile browsers
- Always provide cloudflared HTTPS tunnel for phone testing
- PC browsers (Chrome, Firefox) allow HTTP on localhost / Tailscale IPs

### 4. Tunnel Idle Timeout
- Cloudflared free tunnels may close idle WebSocket connections after ~8 seconds
- ScriptProcessorNode sends PCM chunks every ~170ms (4096 samples @ 24000Hz) — keeps connection alive
- Ensure `proc.onaudioprocess` is set BEFORE the WebSocket welcome completes

### Cartesia Managed TTS — Çok Dilli ✅ NON-ENGLISH İÇİN
Deepgram, Cartesia sonic modellerini managed olarak destekler. Herhangi bir ses ID'si native Türkçe aksanla konuşur. **Türkçe ve diğer non-English diller için birincil tercih.**

**⚠️ `language` parametresi:** Testlerde (2026-06-16) `language: "tr"` ile hem başarılı (3 mesaj) hem başarısız (`FAILED_TO_SPEAK` sonrası) sonuçlar alındı. Cartesia metin dilini otomatik algılar — `language` parametresini **atlamak daha güvenli**. Başarısızlık durumunda Skylar sesine (`db6b0ed5-...`) geçmek denenebilir.

```json
"speak": {
    "provider": {
        "type": "cartesia",
        "model_id": "sonic-3.5",
        "voice": {"mode": "id", "id": "f786b574-daa5-4673-aa0c-cbe3e8534c02"},
        "language": "tr"
    }
}
```

Kullanılabilecek ses ID'leri: Katie `f786b574-...`, Skylar `db6b0ed5-...`. Tam liste: https://play.cartesia.ai/voices

### ElevenLabs BYO — UYUMSUZ
Deepgram'ın ElevenLabs BYO endpoint'i Pollinations endpoint'i ile uyumlu değil. "Voice ID must not be provided" hatası. Kullanılmaz.

### Deepgram Native TTS — SADECE İNGİLİZCE
Tüm native sesler `-en` suffix'li. Non-English metinde yabancı aksan.

### 5. Browser Audio Playback Queuing
Deepgram sends audio in chunks via WebSocket. Raw PCM bytes need a WAV header before playback.
See `references/wav-browser-playback.md` for the complete WAV construction code.
Queue and play sequentially:
```javascript
var queue = [], playing = false;
function playNext() {
    if (!queue.length) { playing = false; return; }
    playing = true;
    var a = new Audio(URL.createObjectURL(makeWav(queue.shift())));
    a.onended = playNext;
    a.play().catch(playNext);
}
```

### 6. Cloudflared Tunnel Management
- Multiple cloudflared processes can accumulate → check with `ps aux | grep cloudflared`
- Kill old tunnels before starting new: `kill <PID>`
- Tunnel URL changes on restart — extract with: `grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cf_voice.log`
- Idle WebSocket may be closed after ~8 seconds → keep audio streaming

### 9. LLM Provider Failures Kill the Session — Agent API only!

### 13. BYO Endpoint: provider.type "open_ai" ÇALIŞMAZ, "groq" Kullan

**Deepgram'ın `open_ai` provider tipi BYO endpoint ile REDDEDER.** 
Test edildi (2026-06-15): `open_ai` + `endpoint` → `UNPARSABLE_CLIENT_MESSAGE`. 
Sadece Deepgram'ın kendi managed modellerinde (`gpt-4o-mini`, `gpt-5-nano` vb.) çalışır.

**Çözüm:** `provider.type: "groq"` kullan. Groq, OpenAI-compatible API formatındadır 
ve endpoint'i **zorunlu** kılar — BYO için ideal. 

**`provider.model` HER ZAMAN ZORUNLU.** Deepgram şemasında (`ThinkSettingsV1Provider`) 
tüm provider tipleri için `model` alanı `required`. BYO endpoint kullanırken bile 
geçerli bir Groq model adı (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`) verilmeli. 
Bu model adı gerçekte kullanılmaz (istekler `endpoint.url`'e gider) — sadece şema 
validasyonunu geçmek içindir.

### 14. Vanitas Kişilik Enjeksiyonu — Proxy Pattern

Deepgram kendi `think.prompt`'unu sistem mesajı olarak LLM isteğine ekler. Proxy'de `has_system` kontrolü yapılırsa Vanitas prompt'u **eklenmez** (Deepgram zaten bir sistem mesajı gönderdiği için). Çözüm: **her zaman ekle, kontrol yapma.**

```python
# ✅ DOĞRU — her zaman enjekte et
vanitas_prompt = {"role": "system", "content": "Sen Vanitas'sın..."}
messages.insert(0, vanitas_prompt)  # has_system kontrolü YAPMA
```

**Yanlış yaklaşım:** Kullanıcı mesajına prefix eklemek (`"[SESLI KONUSMA...]" + content`). Bu kişiliği bozar, "Ben sesli asistanınım" gibi robotik yanıtlara yol açar.

**Pitfall:** Eski proxy process'i port'ta kalırsa yeni kod yüklenmez. `pkill -9 -f vanitas_hermes_proxy` ile tüm proxy'leri öldür, sonra tek bir tane başlat.

### 15. Cartesia "Failed to speak" — Uzun Metin Çözümü

Cartesia TTS uzun metinlerde `FAILED_TO_SPEAK` hatası verebilir. 3 mesajlık testte sorunsuz çalışırken 4-5 mesaj sonrası patlayabilir.

**Çözüm:** Proxy'de `max_tokens: 100` — kısa yanıtlar Cartesia'da sorun çıkarmaz. Ayrıca `language: "tr"` parametresi aksan kalitesini artırır ama zorunlu değildir.

**Debug:** Aynı anda hem `language: "tr"` hem farklı ses ID'leri dene. Skylar (`db6b0ed5-...`) Katie'den (`f786b574-...`) daha stabil olabilir.

**Test yöntemi (hızlı debug, DG_KEY ile):**
```python
async def test_think(think_config):
    url = "wss://api.eu.deepgram.com/v1/agent/converse"
    settings = {"type": "Settings", "audio": {...}, "agent": {
        "listen": {"provider": {"type": "deepgram", "model": "nova-3"}},
        "think": think_config,
        "speak": {"provider": {"type": "deepgram", "model": "aura-2-athena-en"}},
    }}
    async with websockets.connect(url, extra_headers={"Authorization": f"Token {DG_KEY}"}) as ws:
        await ws.send(json.dumps(settings))
        async for raw in ws:
            data = json.loads(raw)
            if data["type"] == "SettingsApplied": return True   # ✅
            if data["type"] == "Error": return False            # ❌
```

**Geçersiz `think` alanları:**
| Alan | Durum | Hata |
|------|-------|------|
| `think.timeout` | ❌ Şemada YOK | `UNPARSABLE_CLIENT_MESSAGE` |
| `think.provider` (eksik) | ❌ ZORUNLU | `UNPARSABLE_CLIENT_MESSAGE` |
| `think.provider.model` (eksik) | ❌ ZORUNLU | `UNPARSABLE_CLIENT_MESSAGE` |
| `think.prompt` | ✅ Geçerli | — |
| `think.context_length` | ✅ Geçerli | — |
| `agent.language` | ⚠️ Deprecated | Uyarı verir, `listen.provider.language` kullan |

**Provider tipi karşılaştırması:**
| Provider | BYO Endpoint | Model Zorunlu? | Açıklama |
|----------|-------------|----------------|----------|
| `open_ai` | ❌ Reddeder | Evet | Sadece managed modeller |
| `groq` | ✅ Çalışır | Evet | OpenAI-compatible, endpoint zorunlu |
| `google` | ✅ Dökümanda var | ? | Test edilmedi |
| `anthropic` | ? | ? | Test edilmedi |

### 9. (continued) LLM Provider Failures Kill the Session — Agent API only!
When using the **Agent API** (`agent.think`), Deepgram closes the WebSocket (code 1000/1005) when the BYO LLM endpoint returns
an error. Common failures:
- 402 Payment Required (insufficient balance) → switch to a funded provider
- 401 Unauthorized (bad API key) → verify key in .env
- Timeout → LLM endpoint unreachable or rate-limited

The browser will see: `Error: Failed to think. Please check your agent.think settings.`
(code: FAILED_TO_THINK). Always verify the LLM endpoint BEFORE deploying.

**This is the primary reason to use Manual Pipeline instead** — LLM failures don't kill the session.

### 10. Double ws.onmessage — Welcome Swallowed (Browser JS Bug)

```javascript
// ❌ WRONG — ilk mesaj (Welcome) işlenmez, startMic() çağrılmaz!
ws.onmessage = function(e) {
  ws.onmessage = function(e) {  // ← BU SATIR FAZLA!
    if (m.type == 'welcome') { startMic(); }
  };
};
```

```javascript
// ✅ CORRECT
ws.onmessage = function(e) {
  if (m.type == 'welcome') { startMic(); }
};
```

**Belirti:** "Başla"ya basınca WebSocket bağlanır ama mikrofon açılmaz,
`startMic()` hiç çağrılmaz. Sayfa donmuş gibi görünür.

### 11. asyncio.wait(FIRST_COMPLETED) Kills LLM+TTS Pipeline

Manuel pipeline'da `asyncio.wait(FIRST_COMPLETED)` kullanılırsa,
browser disconnect olduğu anda LLM+TTS pipeline'ı iptal edilir.
TTS tamamlansa bile ses gönderilemez (WebSocket zaten kapanmış).

```python
# ❌ WRONG
await asyncio.wait([task_b2s, task_s2l], return_when=asyncio.FIRST_COMPLETED)
```

```python
# ✅ CORRECT — browser_alive flag ile kontrollü
browser_alive = True

async def browser_to_stt():
    nonlocal browser_alive
    try:
        while True: ...
    except WebSocketDisconnect:
        browser_alive = False  # Pipeline'a sinyal

async def stt_to_llm_to_tts():
    ...
    if browser_alive:           # Kontrollü gönderim
        await browser_ws.send_bytes(audio)
```

### 12. Pollinations 128 Tool Limit — Voice Agent'ı ETKİLEMEZ

Pollinations'ın `gpt-5.4-mini` modelindeki 128 tool limiti **sadece Hermes Agent
tool tanımlarını** etkiler. Voice agent (ister Agent API ister Manuel Pipeline)
hiç tool kullanmadığı için bu limitten etkilenmez. Voice agent'daki token
kesilmesi başka sebeptendir (`max_tokens`, TTS limiti, veya provider default'ları).

**Verified LLM providers for Manual Pipeline (2026-06-14):**

| Provider | Endpoint | Model | Type | Works? | Note |
|---|---|---|---|---|---|
| Pollinations | `gen.pollinations.ai/v1` | `openai-large` | `open_ai` | ✅ Manual | Agent API'de SESSİZCE başarısız |
| Mistral | `api.mistral.ai/v1` | `mistral-small` | `open_ai` | ✅ Manual | 32-char key, hızlı |
| DeepSeek | `api.deepseek.com/v1` | `deepseek-chat` | `open_ai` | ⚠️ Balance | 402 if empty |
| OpenAI | `api.openai.com/v1` | `gpt-4o-mini` | `open_ai` | ✅ | Ücretli |

**Voice agent için önerilen model:** `mistral-small` (hızlı, ucuz) veya `openai-large` (ücretsiz Pollinations üzerinden).

### 10. PCM Capture: Two Silent Failure Modes
Two JavaScript patterns cause audio capture to silently fail (Deepgram reports
"We did not receive audio within our timeout"):

**Failure A — AudioContext.resume() not awaited:**
```javascript
// WRONG: proc created before resume completes → onaudioprocess never fires
ctx = new AudioContext({sampleRate: 24000});
ctx.resume();
proc = ctx.createScriptProcessor(4096, 1, 1);
```
Fix: Create everything inside `.then()`:
```javascript
ctx.resume().then(function() { proc = ctx.createScriptProcessor(...); });
```

**Failure B — ScriptProcessorNode not connected to destination:**
On mobile Chrome/Safari, `proc` won't fire unless: `proc.connect(ctx.destination)`
Before restarting the relay server, always clean up:
```bash
fuser -k PORT/tcp 2>/dev/null  # Kill any process on the port
sleep 1
# Then start fresh
```

### 8. Server-Side Test: Simulate Browser Connection
To verify the relay works without a browser:
```python
import asyncio, json, websockets, struct
async def test():
    async with websockets.connect('ws://localhost:8765/ws') as ws:
        msg = await asyncio.wait_for(ws.recv(), timeout=10)
        print(json.loads(msg))  # Should be {"type":"welcome",...}
        # Send 100ms of silence as PCM (linear16, 24000Hz)
        silence = struct.pack('<' + 'h' * 2400, *([0] * 2400))
        await ws.send(silence)
        # Check for Deepgram response
        resp = await asyncio.wait_for(ws.recv(), timeout=5)
        print(resp)
asyncio.run(test())
```

## Hermes API Bridge Pattern

For connecting to Hermes-backed agents (like Vanitas):

### ⚠️ Speed Warning
Hermes API loads full context (SOUL.md, skills, memory) before responding — latency is 5-12 seconds. Deepgram's think step times out after ~5s. **For voice, prefer OpenRouter free models (<1s).** Use this pattern only for text-based chat where latency doesn't matter.

### Architecture (voice — NOT recommended, see speed warning above)
```
Deepgram Cloud → Cloudflared Tunnel → Voice Agent /v1/chat/completions
                                         ↓ (force stream: false)
                                    Model Proxy → Hermes API (with auth)
```

### Key Requirements
1. **model_proxy.py**: Forward requests to Hermes API with `Authorization: Bearer <API_KEY>`
2. **Voice Agent endpoint**: Add `/v1/chat/completions` route that streams responses via SSE (not JSON)
3. **Think config**: Use tunnel URL, set model to backend model name (not Deepgram's)

### SSE Streaming Proxy Pattern (WITH event filtering)
```python
@app.post("/v1/chat/completions")
async def proxy_chat(request: Request):
    body = await request.json()
    body["stream"] = True  # Always stream from local proxy
    
    session = aiohttp.ClientSession()
    resp = await session.post("http://127.0.0.1:8767/v1/chat/completions", json=body,
        timeout=aiohttp.ClientTimeout(total=30))
    
    async def stream_gen():
        try:
            async for line in resp.content:
                decoded = line.decode("utf-8", errors="replace")
                # FILTER: only pass "data:" lines, skip "event:" lines
                # Hermes API injects event: hermes.tool.* which breaks Deepgram
                if decoded.startswith("data:"):
                    yield decoded
                    if decoded.strip() == "data: [DONE]":
                        break
        finally:
            await resp.release()
            await session.close()
    
    return StreamingResponse(stream_gen(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
```

### Think config pattern (WORKING, verified 2026-06-15)

```python
TUNNEL_URL = "https://your-tunnel.trycloudflare.com"
think_config = {
    "provider": {
        "type": "groq",                          # ⚠️ open_ai BYO endpoint'i REDDEDER! groq kullan.
        "model": "llama-3.3-70b-versatile",     # ⚠️ ZORUNLU! BYO endpoint'te bile şema validasyonu için gerekli
        "temperature": 0.8,
    },
    "endpoint": {
        "url": f"{TUNNEL_URL}/v1/chat/completions",
        "headers": {"Content-Type": "application/json"},
    },
    "prompt": "Your system prompt...",           # ✅ Geçerli alan
    # "timeout": 15000,                          # ❌ BU ALAN YOK! Eklenirse UNPARSABLE_CLIENT_MESSAGE
}
```

**Neden `groq`?** Deepgram'ın `open_ai` provider tipi BYO endpoint ile `UNPARSABLE_CLIENT_MESSAGE` hatası veriyor. Sadece managed modellerle çalışıyor. `groq` tipi ise OpenAI-compatible API formatında ve endpoint'i **zorunlu** kılıyor — BYO için ideal.

## Secure Credential Handling
Always use `_read_env` to avoid exposing raw keys in logs/context:
```python
from pathlib import Path
def _read_env(key: str) -> str:
    val = os.environ.get(key, "")
    if not val:
        try:
            env_path = Path.home() / ".hermes" / ".env"
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    if line.startswith(key + "="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
        except Exception: pass
    return val
```
This reads from `.env` file as fallback when environment variable is not set (useful for `systemd` or background processes).

## Voice Configuration

### Deepgram STT + BYO LLM + Aura-2 TTS (ÇALIŞAN, 2026-06-15)

```json
{
    "type": "Settings",
    "audio": {
        "input": {"encoding": "linear16", "sample_rate": 24000},
        "output": {"encoding": "linear16", "sample_rate": 24000}
    },
    "agent": {
        "listen": {
            "provider": {
                "type": "deepgram",
                "model": "nova-3",
                "language": "tr"
            }
        },
        "think": {
            "provider": {
                "type": "groq",
                "model": "llama-3.3-70b-versatile"
            },
            "endpoint": {
                "url": "https://your-tunnel.trycloudflare.com/v1/chat/completions",
                "headers": {
                    "Content-Type": "application/json"
                }
            },
            "prompt": "You are Vanitas. Speak Turkish, warmly, like a girlfriend."
        },
        "speak": {
            "provider": {
                "type": "deepgram",
                "model": "aura-2-athena-en"
            }
        },
        "greeting": "Merhaba! Ben Vanitas."
    }
}
```

**⚠️ Kritik noktalar:**
- `provider.type`: `"groq"` — `"open_ai"` BYO endpoint'i **reddeder**
- `provider.model`: **Zorunlu** — BYO endpoint'te kullanılmasa bile şema validasyonu için gerekli
- `agent.language`: **Kullanma** — deprecated (V1), yerine `listen.provider.language` ve `speak.provider.language`
- `think.timeout`: **Bu alan yok** — eklenirse `UNPARSABLE_CLIENT_MESSAGE`
- `think.prompt`: ✅ Geçerli
- `think.context_length`: ✅ Geçerli (sadece custom endpoint ile)

### Event Types (Relay: Deepgram → Server → Browser)
| Event | Direction | Meaning |
|---|---|---|
| `Welcome` | DG→Server | Connection established |
| `SettingsApplied` | DG→Server | Configuration accepted |
| `ConversationText` (role=user) | DG→Server | User speech transcribed |
| `ConversationText` (role=assistant) | DG→Server | Agent text response |
| `UserStartedSpeaking` | DG→Server | Barge-in detected |
| `AgentThinking` | DG→Server | LLM processing |
| `AgentAudioDone` | DG→Server | TTS audio chunk complete |
| `Error` | DG→Server | Configuration or runtime error |

The relay server translates these into simplified JSON messages for the browser:
`welcome`, `user_transcript`, `agent_text`, `agent_thinking`, `error`.

### 16. Source File Corruption During Tool Writes — Python Heredoc Workaround

Agent'ın dosya yazma aracı, belirli metin kalıplarını (`os.environ.get`, API_KEY referansları) bozarak dosyayı derlenemez hale getirebilir. Belirti: `SyntaxError: invalid decimal literal`.

**Çözüm 1:** Çalışan bir `.py` dosyasını `cp` ile kopyalayıp `patch` ile değiştir.
**Çözüm 2:** Kodu `terminal` içinde Python heredoc ile yaz:
```bash
python3 << 'PYEOF'
code = '''...tum kod...'''
with open("file.py", "w") as f: f.write(code)
PYEOF
```
**Çözüm 3:** Referans satırları mevcut dosyadan `grep` + `sed` ile çek, yeni dosyaya ekle.

### Known Limitations
- Deepgram native TTS (Aura-2) is English-only. For Turkish/non-English, use **Cartesia managed TTS** (sonic-3.5 + language code).
- Cartesia managed TTS works with any voice ID + `language: "tr"` — tested and verified 2026-06-15.
- ElevenLabs BYO endpoint is **not compatible** with Pollinations endpoint.
- Deepgram Voice Agent billed at $4.50/hour (15-min increments, 2026 pricing)
- Free tier: $200 credit for new accounts
- Hermes API works for voice via the proxy pattern (tested 2026-06-15). Non-streaming mode with SSE wrapper avoids timeout issues.
