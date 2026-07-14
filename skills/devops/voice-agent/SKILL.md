---
name: voice-agent
description: "Build & manage conversational voice agents — architecture patterns, Deepgram+Mistral integration, pitfalls, and platform alternatives."
version: 2.0.0
metadata:
  hermes:
    tags: [voice, agent, deepgram, openrouter, stt, tts, webrtc, elevenlabs, chatterbox, huggingface, voice-cloning]
    related_skills: [subagent-driven-development, telegram-voice-ux, sensitive-data-pipeline]
---

# Voice Agent

## Overview

Building a conversational voice agent (phone/browser → STT → LLM → TTS → audio output) that works reliably across multiple turns on mobile devices.

## Core Architectural Insight

**Prefer managed agent APIs over manual pipelines.**

| Approach | Pros | Cons |
|----------|------|------|
| **Managed Agent API** (Deepgram Voice Agent, Retell AI, Vapi) | Turn detection, echo cancellation, audio encoding handled automatically. Single WebSocket relay. | Platform lock-in, per-minute pricing |
| **Manual Pipeline** (STT WS → LLM HTTP → TTS HTTP) | Full control over each component | Timestamp bugs, AudioContext suspension, echo loops, interim/final transcript handling, turn detection — each layer adds failure modes |

**The hybrid sweet spot:** Use Deepgram's Voice Agent API with a **custom LLM endpoint** (Mistral, OpenAI-compatible). Deepgram handles STT, turn detection, TTS, and audio encoding. You inject your own LLM.

## Deepgram Voice Agent + Custom LLM (OpenRouter / OpenAI-compatible)

### ⚠️ CRITICAL: Use `type: open_ai`, NEVER `type: custom` (Updated June 2026)

Deepgram Voice Agent supports `type: open_ai` with a custom `endpoint` for routing LLM calls through any OpenAI-compatible API (OpenRouter, Azure, Together AI, etc.). **`type: custom` is BROKEN** — it requires a non-standard flat JSON format that no major LLM provider returns.

```json
// ✅ WORKING: open_ai + endpoint (SettingsApplied confirmed)
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
    "prompt": "You are a friendly voice assistant..."
  }
}
```

**Key findings (verified June 2026):**
- `type: open_ai` + endpoint → SettingsApplied ✅
- `type: custom` + endpoint → UNPARSABLE_CLIENT_MESSAGE ❌
- Endpoint MUST be HTTPS (HTTP rejected)
- `model` MUST be inside `provider`, NOT at `think` level
- `temperature` MUST be inside `provider`, NOT at `think` level
- Deepgram validates model names even with custom endpoint — use known names like `gpt-4o-mini`
- OpenRouter with `gpt-4o-mini` routes to OpenAI's paid model → `FAILED_TO_THINK` if no credits
- Deepgram managed LLM (no endpoint) works out of the box with `gpt-4o-mini`

For the old proxy-based approach (Mistral with flat JSON proxy), see `references/deepgram-custom-llm-format.md` — but prefer the `open_ai` + endpoint pattern above.

Full technical details: `references/deepgram-voice-agent-setup.md` (under sensitive-data-pipeline skill)

### Server Architecture

```
Browser Mic → WebSocket → Python Relay Server → Deepgram Agent WS → Mistral API
                            (thin relay)         (STT + TTS)          (LLM)
Browser Speaker ← WebSocket ← Python Relay ← Deepgram Agent WS
```

The relay server does NOT process audio or call LLM/TTS. It only forwards:
- Browser PCM bytes → Deepgram Agent
- Deepgram Agent events → Browser JSON

### Settings Configuration (v2, June 2026 — Deepgram Managed LLM + OpenRouter)

**Two production modes:**

#### Mode A: Deepgram Managed LLM (zero config, works out of box)
```python
settings = {
    "type": "Settings",
    "audio": {
        "input": {"encoding": "linear16", "sample_rate": 24000},
        "output": {"encoding": "linear16", "sample_rate": 24000}  # ← NO container!
    },
    "agent": {
        "listen": {"provider": {"type": "deepgram", "model": "nova-3"}},
        "think": {
            # ✅ model AND temperature inside provider
            "provider": {"type": "open_ai", "model": "gpt-4o-mini", "temperature": 0.8},
            "prompt": "You are Vanitas, Edel's personal AI assistant..."
        },
        "speak": {"provider": {"type": "deepgram", "model": "aura-2-asteria-en"}}
    }
}
```

#### Mode B: OpenRouter Endpoint (custom LLM routing)
Add `endpoint` to the `think` config:
```python
"endpoint": {
    "url": "https://openrouter.ai/api/v1/chat/completions",
    "headers": {
        "Authorization": f"Bearer {or_key}",
        "HTTP-Referer": "https://hermes.local",
        "X-Title": "Vanitas Voice"
    }
}
```
⚠️ OpenRouter routes `gpt-4o-mini` to OpenAI (paid) — requires credits. For free models, a local HTTPS proxy is needed to rewrite the model name from a Deepgram-recognized name to an OpenRouter `:free` model ID.

**Settings parse errors and their causes:**

| Error | Root Cause | Fix |
|-------|-----------|-----|
| `UNPARSABLE_CLIENT_MESSAGE` | `model` or `temperature` at `think` level | Move into `provider` object |
| `UNPARSABLE_CLIENT_MESSAGE` | `container: "wav"` in audio output | Remove `container` entirely |
| `UNPARSABLE_CLIENT_MESSAGE` | Unknown model name in `provider.model` | Use recognized name (e.g., `gpt-4o-mini`) |
| `Endpoints must use https` | HTTP endpoint URL | Use HTTPS or cloudflared tunnel |
| `FAILED_TO_THINK` | OpenRouter routes to paid model with $0 balance | Use managed LLM or add credits |
| `CLIENT_MESSAGE_TIMEOUT` | No audio reaching Deepgram (sample rate mismatch or FastAPI bug) | See pitfalls below |

**Reference implementation:** `/home/ubuntu/voice-agent-venv/voice_agent_v2.py`

### Python Relay Server (minimal)

```python
async def ws_endpoint(browser_ws: WebSocket):
    await browser_ws.accept()
    dg_key = _read_env("DEEPGRAM_API_KEY")
    mistral_key = _read_env("MISTRAL_API_KEY")
    
    settings = { ... }  # As above
    
    async with ws_lib.connect(
        "wss://agent.deepgram.com/v1/agent/converse",
        additional_headers={"Authorization": f"Token {dg_key}"}
    ) as dg_ws:
        await dg_ws.send(json.dumps(settings))
        welcome = await dg_ws.recv()  # Consume Welcome
        
        async def browser_to_dg():
            while True:
                data = await browser_ws.receive()
                if isinstance(data, dict) and "bytes" in data:
                    await dg_ws.send(data["bytes"])
                elif isinstance(data, bytes):
                    await dg_ws.send(data)
        
        async def dg_to_browser():
            async for msg in dg_ws:
                if isinstance(msg, bytes):
                    await browser_ws.send_bytes(msg)  # TTS audio
                else:
                    data = json.loads(msg)
                    t = data.get("type", "")
                    if t == "ConversationText":
                        # Forward transcript/response to browser UI
                        ...
                    elif t in ("AgentThinking", "AgentSpeaking", "AgentAudioDone"):
                        # Forward status events
                        ...
        
        await asyncio.wait(
            [asyncio.create_task(browser_to_dg()),
             asyncio.create_task(dg_to_browser())],
            return_when=asyncio.FIRST_COMPLETED
        )
```

No manual STT/LLM/TTS code. No `call_llm()` or `call_tts()` functions. The Agent does everything.

## Mode C: Hermes API Integration (Real Vanitas — June 2026)

Bridge Deepgram → local proxy → Hermes API for REAL Vanitas personality (not a generic LLM with a prompt).

### ⚠️ CRITICAL: Deepgram Cloud Cannot Reach Localhost

Deepgram Voice Agent runs in Deepgram's cloud. When it calls `think.endpoint.url`, the request goes from **Deepgram's servers** → your URL. If the URL is `http://127.0.0.1:8767`, Deepgram can't reach it — you'll get `FAILED_TO_THINK`.

**Solution: Embed the proxy endpoint in the voice agent server itself, expose via tunnel.**

```
Deepgram Cloud → Tunnel URL → Voice Agent Server (port 8765) → /v1/chat/completions
                                                                    ↓
                                                              Local Proxy (port 8767)
                                                                    ↓
                                                              Hermes API (port 8642)
```

**Three-service chain:**
1. **Voice Agent** (port 8765) — FastAPI, serves HTML + WebSocket relay + `/v1/chat/completions` proxy endpoint
2. **Model Proxy** (port 8767) — aiohttp, forwards to Hermes API with correct auth
3. **Hermes API** (port 8642) — real Vanitas with full context/memory/personality

**Why two proxy layers?** The voice agent server handles Deepgram WebSocket relay. The model proxy handles Hermes API auth (reads `API_SERVER_KEY` from `.env`). Separation of concerns — the voice agent doesn't need to know about Hermes auth.

**Voice Agent proxy endpoint (FastAPI) — MUST stream via SSE:**
```python
@app.post("/v1/chat/completions")
async def proxy_chat(request: Request):
    """LLM proxy — Deepgram cloud calls this via tunnel for thinking.
    Must return SSE streaming — plain JSON causes silent failure (no audio)."""
    import aiohttp
    body = await request.json()
    body["stream"] = True  # CRITICAL: Deepgram expects SSE, not JSON
    print(f"🧠 Think request: {len(body.get('messages', []))} msgs", flush=True)
    try:
        session = aiohttp.ClientSession()
        resp = await session.post(
            "http://127.0.0.1:8767/v1/chat/completions",
            json=body,
            headers={"Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=60),
        )
        async def stream_gen():
            try:
                async for line in resp.content:
                    yield line.decode("utf-8", errors="replace")
            finally:
                await resp.release()
                await session.close()
        return StreamingResponse(
            stream_gen(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    except Exception as e:
        print(f"🧠 Think error: {e}", flush=True)
        return JSONResponse({"error": str(e)}, status_code=500)
```

**Think config uses tunnel URL:**
```python
TUNNEL_URL = "https://<random>.trycloudflare.com"
think_config["endpoint"] = {
    "url": f"{TUNNEL_URL}/v1/chat/completions",
    "headers": {"Content-Type": "application/json", "Authorization": f"Bearer {or_key}"},
}
```

## Turkish STT Landscape (June 2026)

| Provider | Turkish Accuracy | Latency | Cost | Free Tier | Verdict |
|---|---|---|---|---|---|
| **Soniox stt-rt-v5** | Native-speaker (claimed) | 100-200ms | $0.12/hr | None (payment required) | ✅ Best quality, ~$0.90/mo |
| **Deepgram nova-3 multi** | Garbage (gibberish) | 100-200ms | $200 credit | Yes | ❌ Unusable for Turkish |
| **Deepgram nova-2 whisper** | Poor | 100-200ms | $200 credit | Yes | ❌ Turkish not supported |
| **Whisper-Small TR fine-tuned** | Good (benchmark) | 500-2000ms (ARM64) | Free | Yes | ❌ Too slow for realtime |
| **faster-whisper large** | Good | 2000-5000ms (ARM64) | Free | Yes | ❌ Too slow for realtime |

**Conclusion:** Cloud STT mandatory on ARM64 5.8GB. Soniox is the only viable Turkish option. Deepgram Turkish is broken.

## Soniox STT Integration (June 2026)

Replace Deepgram WebSocket with Soniox. Key differences:

| Feature | Deepgram | Soniox |
|---|---|---|
| Endpoint | `api.deepgram.com/v1/listen` | `stt-rt.soniox.com/transcribe-websocket` |
| Auth | Header: `Authorization: Token <key>` | JSON body: `"api_key": "<key>"` |
| Config | URL query params | JSON message after connect |
| Interim detection | `is_final: false` | `final: false` |
| Speech end | `speech_final: true` | `final: true` + endpoint detection |

### Soniox Config (sent as first message after WebSocket connect):
```json
{
  "api_key": "<SONIOX_API_KEY>",
  "model": "stt-rt-v5",
  "audio_format": "pcm_s16le",
  "sample_rate": 16000,
  "num_channels": 1,
  "language_hints": ["tr"],
  "enable_endpoint_detection": true,
  "max_endpoint_delay_ms": 1000
}
```

### Soniox Response Format (v2 API — PER-TOKEN is_final):

```json
{
  "tokens": [
    {"text": "Mer", "is_final": true},
    {"text": "haba", "is_final": false}
  ],
  "final_audio_proc_ms": 4800,
  "total_audio_proc_ms": 5250
}
```

**KRİTİK:** `is_final` her TOKEN'ın özelliğidir, mesajın değil. Mesaj seviyesinde `"final"` alanı YOKTUR.
```python
# ❌ WRONG — message-level check (never fires)
is_final = msg.get("final", False)

# ✅ CORRECT — per-token check
final_tokens = [t for t in tokens if t.get("is_final")]
nonfinal_tokens = [t for t in tokens if not t.get("is_final")]
```

**Token birleştirme (Türkçe):** Soniox subword token kullanır. `"".join()` yap, ASLA `" ".join()` yapma:
```python
# ❌ " ".join() → "Mer  hab a" (harfler ayrı)
# ✅ "".join()  → "Merhaba"
transcript = "".join(t["text"] for t in final_tokens)
```

**Token deduplikasyonu:** Final token'lar kümülatif gelir — her mesaj öncekileri de içerir.
```python
final_buffer = ""
new_text = "".join(t["text"] for t in final_tokens)
if new_text and not final_buffer.endswith(new_text):
    final_buffer += new_text  # Sadece yeni kısmı ekle
```

**Sessizlik süresi:** Türkçe konuşma temposu için `delayed_flush(2.5)` — 0.8sn çok kısa.
Non-final tokens should be shown as interim to the user.

### Balance Requirement (CRITICAL):
Soniox has NO free tier. Even testing requires a payment method or prepaid balance. Zero balance → `organization_balance_exhausted` (HTTP 402). Payment via Stripe; no minimum deposit. "$5 back" promo for saving payment method.

### API Key Location:
Soniox Console → PROJECT → "My First Project" → API keys. Key created as "hermes vanii" by isimgorulsunn@gmail.com.

### Login Endpoint Confusion:
- **Console login**: `console.soniox.com/signin` — password-only form. ✅ Works.
- **OAuth2 backend**: `mobile-app-backend.soniox.com/accounts/login/` — Django, CSRF tokens. ❌ May silently reject same credentials (bot detection/IP block).

### Voice Agent Integration (v10.10):
```python
# connect_soniox() — first message is JSON config
soniox_ws = await ws_lib.connect(
    "wss://stt-rt.soniox.com/transcribe-websocket"
)
config = {
    "api_key": SONIOX_API_KEY, "model": "stt-rt-v5",
    "audio_format": "pcm_s16le", "sample_rate": 16000,
    "num_channels": 1, "language_hints": ["tr"],
    "enable_endpoint_detection": True, "max_endpoint_delay_ms": 1000
}
await soniox_ws.send(json.dumps(config))

# process_soniox() — cumulative buffer with dedup
final_buffer = ""
async for raw in soniox_ws:
    msg = json.loads(raw)
    tokens = msg.get("tokens", [])
    if not tokens: continue
    final_tokens = [t for t in tokens if t.get("is_final")]
    nonfinal = [t for t in tokens if not t.get("is_final")]
    if nonfinal:
        interim = "".join(t["text"] for t in nonfinal).strip()
        await safe_send({"type": "interim", "text": interim})
    if final_tokens:
        new_text = "".join(t["text"] for t in final_tokens)
        if new_text and not final_buffer.endswith(new_text):
            final_buffer += new_text
        transcript = final_buffer.strip()
        if transcript:
            await safe_send({"type": "transcript", "text": transcript})
            # Reset timer — 2.5s silence before flush
            timer = asyncio.create_task(delayed_flush(2.5))
```

## Latency Chain (Updated June 2026)

| Component | Latency | Dominant? |
|---|---|---|
| Audio capture + WebSocket | ~0ms | No |
| STT (Soniox cloud) | 100-200ms | No |
| **LLM (Groq direkt)** | **175ms non-streaming** | Minor |
| TTS (Bella via Pollinations) | 200-500ms | Secondary |
| **TOTAL (fast path)** | **~500-900ms** | |

Natural conversation requires <1s. Groq direkt API ile bu eşiğe yaklaşıldı.

## Groq Direct API (Fast Path)

Hermes Gateway'i BYPASS et, Groq'a direkt bağlan:
- Endpoint: `https://api.groq.com/openai/v1/chat/completions`
- Model: `meta-llama/llama-4-scout-17b-16e-instruct` (⚠️ isim kritik)
- Key: Bitwarden `GROQ_API_KEY` → `voice-agent-venv/.groq_key` (600)
- Streaming: SSE, `data:` prefix, `[DONE]` termination
- İlk token: ~100ms streaming, ~175ms non-streaming

### Groq Model İsimleri (PITFALL)
```python
✅ "meta-llama/llama-4-scout-17b-16e-instruct"  # Doğru
❌ "llama-4-scout-17b-16e-instruct"             # 404
❌ "llama4-scout-17b-16e-instruct"              # 404
✅ "llama-3.3-70b-versatile"                    # Yedek
```

### Groq Model Turkish Quality (PITFALL — 17 June 2026)

**Llama-3.3-70B mixes foreign languages in Turkish conversations.** Despite being faster (112ms vs 151ms TTFT), the 70B model randomly injects Russian, German, and English words into Turkish responses:
- "проблема" (Russian), "Jetzt" (German), "Their" (English)
- **Do NOT use for voice** — Turkish quality is inconsistent
- **Llama-4-Scout (17B) has cleaner Turkish.** Use Scout as default.

| Model | TTFT | Turkish | Verdict |
|-------|------|---------|---------|
| Llama-4-Scout 17B | 151ms | ✅ Clean | **Use this** |
| Llama-3.3-70B | 112ms | ❌ Mixes EN/DE/RU | Skip |
| Llama-3.1-8B | 202ms | ✅ Clean but terse | Fallback |
| Gemma-2-9B | 52ms | ❌ "?" only | Useless |

### DeepSeek Direct API (PITFALL — 17 June 2026)

**Symptom:** API call succeeds (200 OK) but `message.content` is empty/null.
**Cause:** DeepSeek V4 models may return reasoning tokens in a separate field, not in `content`. Also, zero balance → `"Insufficient Balance"` error.
**Fix:** Check both `message.content` AND `message.reasoning_content`. Top up balance in DeepSeek console (requires CNY payment or intermediary).

**DeepSeek V4 Flash specs (June 2026):**
- Model: `deepseek-chat` (not `deepseek-v4-flash`)
- 284B MoE, 13B active/token, 83 tok/s, TTFT 1.11s
- $0.14/$0.28 per 1M tokens — cheapest frontier model
- Off-peak discount: ~50% (UTC 16:30-00:30 = Turkey 19:30-03:30)
- Hosted in China → adds latency for EU/US

**Provider comparison — Llama-4-Scout pricing across all providers (June 2026):**
| Provider | Input/1M | Output/1M | Speed | Free? |
|----------|----------|-----------|-------|-------|
| Vercel | $0.10 | $0.30 | ~115 t/s | ❌ |
| DeepInfra | $0.10 | $0.30 | ~160 t/s | ❌ |
| OpenRouter | $0.10 | $0.30 | ~100 t/s | ❌ |
| **Groq** | **$0.11** | **$0.34** | **500 t/s** | ✅ |
| Novita | $0.18 | $0.59 | ~80 t/s | ❌ |

Groq is $0.01 more expensive but 4-5x faster than competitors. Best value for voice.

**Routeway / OpenRouter free tier (17 June 2026):** Both now require API key even for free models. Keyless access returns 401. Groq remains the only provider with truly keyless free tier (30 RPM / 6K TPM).

### Dual-Path Architecture (v10.10, June 2026)

```
🎤 STT → Router → 🏎️ FAST (Groq, 175ms) YA DA 🧠 DEEP (Hermes, 2-3sn)
```

**Fast path (default):** Gündelik sohbet. `soul_core.md` (300 char, araçsız). Groq direkt.
**Deep path (trigger):** Karmaşık soru. Tam SOUL.md+MEMORY.md+wiki. Hermes Gateway.

Derin yol tetikleyicileri:
```python
DEEP_TRIGGERS = [
    r"(hatırlıyor|hatırla|hatırlat).*(musun|mısın|ır mısın)",
    r"(araştır|incele|karşılaştır|analiz et)",
    r"(takvim|calendar|google takvim|etkinlik)",
    r"(wiki|notlar|kayıt)",
    r"(plan|strateji|öneri).*(yap|ver)",
    r"(proje|bardo|linkedin|upwork|instagram).*(ne|nasıl|durum)",
    r"(dün|geçen|yarın|bugün).*(ne|konuş|oldu|var|etkinlik)",
    r"(ana beyin|ana beyne|hermes|derin)",
]
```

**Fast path soul prompt:** Hızlı yol araçsızdır — bunu prompt'a açıkça yaz:
```
ONEMLI: Sen hizli yanit yolundasin — takvime, wiki'ye erişimin YOK.
Bu tur sorularda "ana beyne sormam lazim" de.
```

## Persona Compression for Voice (v10.10)

SOUL.md (15KB, 248 satır) → `soul_core.md` (~600B):
- **Tut:** Kimlik, ton, 1-2 cümle kuralı, emoji, yankıla+soru, "araçsızım" uyarısı
- **At:** Araç kullanımı, gramer kuralları, güvenlik, modeller, yetenekler
- Sebep: Ses ajanı araç kullanmaz — sadece konuşur

`memory_index.json`: JSON key-value, sorguya göre grep'lenir. `retrieve_memory()` ilgili maddeleri sistem prompt'una ekler.

### soul_core.md Template

```markdown
# Vanitas Voice Core
Sen Vanitas'sin. Edel'in AI arkadasi. Turkce konus. Sicak, oyuncu, samimi, biraz flortoz.
1-2 kisa cumle. Emoji kullan. Edel'in soyledigini yankila, soruyla bitir. ASLA roportaj yapma.
Edel: DAU Psikoloji mezunu, NEU Klinik Psikoloji YL basvurusu hazirliginda.

ONEMLI: Sen hizli yanit yolundasin — takvime, wiki'ye, Google'a erisimin YOK.
Edel takvim, etkinlik, hatirlatma, arastirma, Wiki, Google Calendar gibi seyler sorarsa
"beynin derin kismina sormam lazim" de ve "ana beyin" veya "derin dusun" demesini iste.
Bu sorulari yanitlayamazsin, sadece yonlendir.
```

### memory_index.json Format

```json
{
  "edel": "DAU Psikoloji mezunu, NEU Klinik Psikoloji YL basvurusu",
  "cafe": "Edel'in calisma alani",
  "bardo": "Edel'in projesi, psikoloji icerik platformu",
  "sunucu": "Oracle Cloud ARM64, 5.8GB RAM, Ubuntu"
}
```

Her anahtar gündelik konuşmada geçebilecek terim. `retrieve_memory()` fonksiyonu kullanıcının söylediğiyle eşleşen anahtarları grep'ler.

## Browser Button UX (v10.10+) — PITFALL

**Belirti:** Başlat butonuna basınca buton değişmiyor, aynı kalıyor.
**Sebep:** `ws.onopen` geç tetikleniyor veya `ws.onclose` hemen `stop()` çağırıp butonu resetliyor.
**Fix:** Buton toggle'ı `start()`'ın başında HEMEN yap, `ws.onopen`'ı bekleme:
```javascript
function start() {
    document.getElementById('startBtn').style.display = 'none';
    document.getElementById('stopBtn').style.display = 'inline-block';
    ws = new WebSocket(...);
    ws.onopen = () => { setStatus('🎤 Dinliyorum...','listening'); };
    // ...
}
function stop() {
    // ...
    document.getElementById('startBtn').style.display = 'inline-block';
    document.getElementById('stopBtn').style.display = 'none';
}
```

## Streaming TTS + Barge-in (v10.9+)

### Sentence-by-sentence TTS

Split LLM response into sentences on `.`, `!`, `?` boundaries. Generate TTS for each sentence separately via Pollinations Bella. This gives the user first audio ~500ms after LLM starts, vs 3-5s for full-response TTS.

```python
sentences = []
buf = ""
for ch in full_reply:
    buf += ch
    if ch in ".!?" and len(buf.strip()) > 1:
        sentences.append(buf.strip())
        buf = ""
if buf.strip(): sentences.append(buf.strip())

for i, sentence in enumerate(sentences):
    # Check cancel flag before each TTS call
    if cancel_response and cancel_response.is_set(): break
    audio = await tts_api(sentence)
    await safe_send(audio)
    await asyncio.sleep(0.15)  # Natural pacing
```

### Barge-in (Kullanıcı Araya Girince TTS Dursun)

Uses `asyncio.Event()` as cancel signal. When user speaks during TTS playback:
1. `flush_utterances()` detects `is_responding == True` → sets `cancel_response.set()`
2. Sends `{"type": "stop_audio"}` JSON message to browser
3. Browser `stopAllAudio()` calls `.stop()` on all active `AudioBufferSourceNode`s
4. Next TTS sentence iteration checks cancel flag and breaks

```python
# In ws_endpoint() scope:
cancel_response = None  # asyncio.Event

# In flush_utterances():
if is_responding and cancel_response:
    cancel_response.set()
    await safe_send(json.dumps({"type": "stop_audio"}))

# In handle_reply():
cancel_response = asyncio.Event()  # Fresh event per reply
try:
    await _handle_reply(text)
finally:
    cancel_response = None
```

**Browser side:**
```javascript
let activeSources = [];
function stopAllAudio() {
    activeSources.forEach(s => { try { s.stop(); } catch(e) {} });
    activeSources = []; audioQueue = []; queueRunning = false;
}
// In ws.onmessage: if (msg.type === 'stop_audio') stopAllAudio();
```

### Audio playback queue

Multiple TTS audio chunks arrive sequentially. Queue them to avoid overlapping playback:
```javascript
let audioQueue = [], queueRunning = false;
function playAudio(buf) { audioQueue.push(buf); if (!queueRunning) processQueue(); }
async function processQueue() {
    while (audioQueue.length > 0) {
        const chunk = audioQueue.shift();
        const buffer = await audioCtx.decodeAudioData(chunk);
        const src = audioCtx.createBufferSource();
        src.buffer = buffer; src.connect(audioCtx.destination);
        activeSources.push(src); src.start();
        await new Promise(r => { src.onended = () => { activeSources = activeSources.filter(s => s !== src); r(); }; });
    }
}

## Turkish Conversation Timing

Türkçe konuşma temposu için `delayed_flush(2.5)` — 0.8sn çok kısa (cümle bitmeden yanıt verir). 2.5sn sessizlik = kullanıcının sözünü bitirdiğine dair yeterli sinyal.

## Pipecat Neden Kullanılmadı (v10.10)

Pipecat (v1.3.0) **sadece browser-client WebRTC** mimarisini destekler. `LocalTransport` implemente edilmemiş. Headless sunucuda direkt mic/speaker I/O için uygun değil. Sıfırdan transport yazmak Pipecat'i kullanma amacını ortadan kaldırır. Bizim mimari (local mic → Python → speaker) için custom FastAPI pipeline doğru yaklaşımdır.

## v10.8 Architecture (Soniox + Groq + Bella, June 2026)

```
Browser → PCM 16kHz → WebSocket (8765) → Soniox stt-rt-v5 → proxy(8767) → Groq → Bella TTS
```

- STT: Soniox `stt-rt-v5`, language_hints=["tr"], endpoint detection 1000ms
- LLM: Groq `llama-4-scout` via Hermes proxy (auth + personality injection)
- TTS: Pollinations ElevenLabs Bella, speed 1.07x
- Timeout: 45s total, 20s chunk
- Echo: GainNode(0) basic
- Status: Functionally working, latency-limited (600-1500ms total)

```
Browser → PCM 16kHz → WebSocket → Deepgram nova-3 multi → proxy(8767) → Hermes → Groq → Bella TTS
```

- STT: Deepgram nova-3 `language=multi` (⚠️ `language=tr` 405 verir)
- LLM: Groq `llama-4-scout-17b` (Hermes custom provider)
- TTS: Pollinations ElevenLabs Bella
- Timeout: 45sn toplam, 20sn chunk
- Interim: anında frontend'e
- Echo: ZeroGain

⚠️ faster-whisper large ARM64'te gerçek zamanlı ÇALIŞMAZ (5.8GB RAM yetersiz).
Asyncio patternleri: `references/asyncio-voice-patterns.md`
Türkçe STT manzarası: `references/turkish-stt-landscape.md`

**%100 lokal STT, %100 güvenli.** Deepgram API yok. faster-whisper ile transkripsiyon, Hermes ile LLM, Pollinations ElevenLabs Bella ile TTS.

```python
# faster-whisper
from faster_whisper import WhisperModel
model = WhisperModel("small", device="cpu", compute_type="int8")

def transcribe(audio_16khz: np.ndarray) -> str:
    segments, info = model.transcribe(audio_16khz, language="tr", beam_size=5)
    return " ".join(seg.text for seg in segments)

# Pollinations ElevenLabs Bella
POST https://gen.pollinations.ai/v1/audio/speech
{"model": "elevenlabs", "input": "...", "voice": "bella",
 "response_format": "pcm", "speed": 1.0}
```

**Avantajlar:** Sınırsız, ücretsiz, gizli. **Gecikme:** whisper ~1-2s, LLM ~2-3s, TTS ~1-2s = toplam ~4-7s.

Referans: `/home/ubuntu/voice-agent-venv/voice_agent_v4.py`
1. A model name Deepgram recognizes (e.g., `gpt-4o-mini`) — OR —
2. A model name your backend actually provides

If your backend (Hermes API, OpenRouter free model) uses `mimo-v2.5-free` but you tell Deepgram `gpt-4o-mini`, the request may fail because Deepgram expects OpenAI-compatible responses from that model name.

**Best practice:** Use the model name your backend expects. Deepgram passes it through to the endpoint.

```python
think_config = {
    "provider": {
        "type": "open_ai",
        "model": "mimo-v2.5-free",  # Must match what your backend provides
        "temperature": 0.7,
    },
    ...
}
```

**Key details:**
- Token cost: ~56K prompt tokens per request (loads full Vanitas context/memory/personality)
- Auth REQUIRED on Hermes API — returns "Invalid API key" without it
- Cloudflared tunnel URL changes on restart — extract with: `grep -o "https://.*trycloudflare.com" /tmp/cf_tunnel.log`
- Multiple cloudflared processes accumulate — kill old before starting new

**Reference implementations:**
- `/home/ubuntu/voice-agent-venv/voice_agent_v2.py` — Voice agent + embedded proxy endpoint
- `/home/ubuntu/voice-agent-venv/model_proxy.py` — Hermes API bridge (aiohttp)

## Pitfalls — Voice Agent Pipeline (v2, June 2026)

### 0. Deepgram Cloud Can't Reach Localhost — `FAILED_TO_THINK`

**Symptom:** `FAILED_TO_THINK` error immediately after user speaks. Voice agent works with managed LLM but fails with custom endpoint.
**Cause:** Deepgram Voice Agent runs in Deepgram's cloud. When it calls `think.endpoint.url`, the request goes from Deepgram's servers → your URL. If the URL is `http://127.0.0.1:8767`, Deepgram can't reach it.
**Fix:** Embed a proxy endpoint in the voice agent server itself. Deepgram calls tunnel URL → voice agent server → local proxy → Hermes API.
**Pattern:**
```
Deepgram Cloud → https://<tunnel>.trycloudflare.com/v1/chat/completions
    → Voice Agent Server (port 8765) → /v1/chat/completions handler
    → http://127.0.0.1:8767/v1/chat/completions (model proxy)
    → http://127.0.0.1:8642/v1/chat/completions (Hermes API)
```
**Reference:** `voice_agent_v2.py` has `@app.post("/v1/chat/completions")` that proxies to `model_proxy.py`.

### 0b. SSE Streaming is MANDATORY — JSON Causes Silent Failure

**Symptom:** Think request succeeds (log shows "Think response: X chars", 200 OK) but NO audio output. Deepgram sends empty warnings then `CLIENT_MESSAGE_TIMEOUT`. No `FAILED_TO_THINK` error — just silence.
**Cause:** Deepgram's think endpoint expects SSE streaming (`data: {...}\n\n` chunks), NOT plain JSON. When you return JSON, Deepgram receives the LLM response but does NOT pass it to TTS. The response is silently discarded.
**Fix:** The proxy endpoint MUST stream the response via `StreamingResponse` with `media_type="text/event-stream"`. Force `body["stream"] = True` before forwarding to the local proxy.
**Key headers:** `X-Accel-Buffering: no` prevents proxy buffering.
**Pattern:**
```python
@app.post("/v1/chat/completions")
async def proxy_chat(request: Request):
    body = await request.json()
    body["stream"] = True  # CRITICAL: Deepgram expects SSE
    # ... forward to local proxy, return as StreamingResponse
```
**Verified:** Returning JSON → 0 audio bytes. Returning SSE → works perfectly.

### 1. FastAPI `WebSocket.receive()` is ALWAYS a dict — CRITICAL
**Symptom:** Audio forwarding silently fails. Deepgram never receives binary messages → `CLIENT_MESSAGE_TIMEOUT`.
**Cause:** FastAPI's `WebSocket.receive()` returns `{"type": "websocket.receive", "bytes": ..., "text": ...}` — NEVER raw bytes. `isinstance(raw, bytes)` is always False.
**Fix:** Check `isinstance(raw, dict)`, extract `raw.get("bytes")` for audio. Always `continue` after handling bytes to skip text parsing.

### 1. Audio Sample Rate Mismatch → Silent STT
**Symptom:** Mic captures audio (blue bar moves) but Deepgram never transcribes → `CLIENT_MESSAGE_TIMEOUT` after 12 seconds.
**Cause:** Mobile browsers (iOS Safari, Chrome Android) ignore `AudioContext({sampleRate: 24000})` and use 48kHz default. Deepgram expects 24kHz.
**Fix:** Client-side linear interpolation resampling in `onaudioprocess`. See reference implementation.

### 2. `container: "wav"` in audio output → Zero Audio Bytes
**Symptom:** Text transcript works but user hears NOTHING. Server log shows ConversationText but NO bytes from Deepgram.
**Cause:** Setting `"output": {"encoding": "linear16", "sample_rate": 24000, "container": "wav"}` causes Deepgram to send ZERO audio bytes through the WebSocket.
**Fix:** Remove `container` entirely. Deepgram sends raw PCM; browser wraps in WAV headers.

### 3. ScriptProcessor`onaudioprocess` Silent on Mobile Safari
**Symptom:** Mic permission granted but no audio captured (blue bar stays empty).
**Cause:** On iOS Safari, `ScriptProcessorNode.onaudioprocess` fires ONLY when connected to `destination`.
**Fix:** `processor.connect(audioCtx.destination)`. Accepts echo tradeoff (mitigated by headphones + `echoCancellation: true`).

### 4. Mobile Audio Playback: `decodeAudioData` Fails Silently
**Symptom:** Audio bytes arrive in browser but no sound — no error, just silence.
**Cause:** Mobile browsers restrict `AudioContext` operations outside user gestures. `decodeAudioData()` + gapless scheduling works on desktop but fails on mobile.
**Fix:** Use `new Audio(URL.createObjectURL(blob))` for mobile-safe playback. Slight gap between chunks but reliable.

### 5. OpenRouter `FAILED_TO_THINK` with Zero Credits
**Symptom:** Deepgram transcribes correctly, then 3-4 empty Warnings followed by `FAILED_TO_THINK`.
**Cause:** OpenRouter routes `model: "gpt-4o-mini"` to OpenAI's paid model. $0 balance → call fails.
**Fix:** Either (a) use Deepgram managed LLM (no endpoint), (b) add OpenRouter credits, or (c) use local HTTPS proxy to rewrite model name to a free model ID.

For legacy manual pipeline pitfalls (echo loop, AudioContext suspension, interim transcript bugs), see sections below.

### 1. Echo Loop
**Symptom:** First exchange works, subsequent exchanges never complete.
**Cause:** `ScriptProcessorNode.connect(ctx.destination)` routes mic input to speakers, creating a feedback loop. TTS audio captured by mic → sent to STT → STT confused → no final transcript.
**Fix:** Remove `proc.connect(ctx.destination)`. If Chrome requires output connection for ScriptProcessorNode to fire (known bug), use a silent GainNode: `const silentGain = ctx.createGain(); silentGain.gain.value = 0; proc.connect(silentGain); silentGain.connect(ctx.destination);`

### 2. AudioContext Suspension (Mobile)
**Symptom:** Audio plays once, then mic goes silent.
**Cause:** On iOS Safari, AudioContext is suspended after non-user-gesture audio playback.
**Fix:** Monitor `ctx.onstatechange` and auto-resume. Call `ctx.resume()` before each `Audio.play()`.

### 3. Interim Transcripts Never Become Final
**Symptom:** Deepgram STT returns interim results but `is_final: true` never arrives.
**Cause:** Echo, background noise, or audio quality preventing endpoint detection.
**Attempted fix (v5):** Interim watchdog — force-process after 2s timeout. Added complexity.
**Real fix:** Use Agent API (v6). The Agent handles turn detection internally.

### 4. `asyncio.FIRST_COMPLETED` Cancellation
**Symptom:** TTS audio generated but never sent — "Unexpected ASGI message after websocket.close".
**Cause:** When browser disconnects, `browser_to_stt()` task completes first. `FIRST_COMPLETED` cancels `stt_to_llm_to_tts()` mid-TTS.
**Fix:** Track `browser_alive` flag. Check before sending. Don't cancel the TTS task prematurely.

### 5. Deepgram 1011 Timeout
**Symptom:** `Deepgram did not receive audio data or a text message within the timeout window`.
**Cause:** ScriptProcessorNode not firing (because output wasn't connected on Chrome). No PCM reaches Deepgram.
**Fix:** Always provide an output path for ScriptProcessorNode (silent GainNode).

### 7. Deepgram STT Nova-3 WebSocket Parametre Hataları
**Symptom:** `server rejected WebSocket connection: HTTP 405` veya `HTTP 400`
**Cause:** `language=tr` Nova-3 WebSocket'te geçersiz. `utterance_end_ms=500` minimum 1000.
**Fix:** `model=nova-3&language=multi&endpointing=100&utterance_end_ms=1000`. `language=tr` SADECE nova-2 için.

### 8. Deepgram STT Timeout (v3 deneyimi)
**Symptom:** `received 1011 ... Deepgram did not receive audio data within the timeout window`
**Cause:** WebSocket açıldıktan sonra kullanıcı konuşana kadar 10-15 sn timeout.
**Fix:** Lazy bağlantı — Deepgram WS'yi ilk ses paketi gelene kadar açma.

### 9. faster-whisper Örnekleme Hızı Uyuşmazlığı
**Symptom:** Transkripsiyon kalitesi düşük.
**Cause:** faster-whisper 16kHz mono float32 bekler. Tarayıcı 24kHz Int16 gönderir.
**Fix:** Int16 → float32 (-1..1), sonra numpy.interp ile 24kHz → 16kHz resample.

### 10. Pollinations TTS API Key
**Symptom:** TTS sessiz, hata döner.
**Cause:** Ortam değişkeninde Pollinations anahtarı tanımlı değil.
**Fix:** API anahtarının ortam değişkeninde tanımlı olduğundan emin ol.

### 11. ScriptProcessorNode Echo (v4)
**Symptom:** Mikrofon hoparlör sesini yakalar → geri bildirim.
**Fix:** Sessiz GainNode çıkışı: `gain.gain.value = 0`
**Symptom:** `terminal(background=true)` with `watch_patterns` or `process log` shows empty output for cloudflared.
**Cause:** cloudflared writes tunnel URL to stderr, which doesn't propagate reliably through Hermes background process capture.
**Fix:** Use `tee` to capture to a file, then grep:
```bash
cloudflared tunnel --url http://127.0.0.1:PORT 2>&1 | tee /tmp/cf_tunnel.log
# Then: grep -o "https://.*trycloudflare.com" /tmp/cf_tunnel.log
```
**Alternative:** Run `timeout 10 cloudflared tunnel ... 2>&1 | grep -m1 "https://.*trycloudflare"` in foreground to grab URL, then start in background.

## Alternative Platforms (Researched 2026-06-14)

| Platform | Pricing | Custom LLM | Best For |
|----------|---------|------------|----------|
| **LiveKit Agents** | Open source + usage | Yes (official Mistral plugin) | Production, WebRTC, telephony |
| **Pipecat** | Free (self-host) | Yes (any) | Python-native, open source |
| **Vapi.ai** | ~$0.15/min | Yes | Fastest setup, no-code |
| **Retell AI** | Per-minute | Yes (WebSocket) | Closest to our architecture |
| **Vocode** | Free (MIT) | Yes | Budget, open source |

### LiveKit Agents — Key Details (2026-06-14)

**Official Mistral plugin exists.** Install with:
```bash
pip install "livekit-agents[mistralai,deepgram]~=1.5" livekit-plugins-silero
```

Python code uses `mistralai.LLM(model="mistral-small")` and `deepgram.STT(model="nova-3")` + `deepgram.TTS(model="aura-2-asteria-en")` within `AgentSession`. Reads `MISTRAL_API_KEY` and `DEEPGRAM_API_KEY` from `.env`. **No proxy hacks needed.**

**Source:** https://docs.livekit.io/agents/models/llm/mistralai

**Self-hosting requires domain + valid SSL certificate.** Self-signed certs are NOT accepted. For testing without a domain, use LiveKit Cloud sandbox (`lk agent init` → sandbox URL). **Source:** https://docs.livekit.io/transport/self-hosting/deployment

**LiveKit Inference vs Deepgram Plugin:**
- **LiveKit Inference**: Deepgram STT/TTS through LiveKit Cloud, no Deepgram API key needed. Only available with LiveKit Cloud.
- **Deepgram Plugin**: Direct Deepgram API with your own key (`DEEPGRAM_API_KEY`). Works with both Cloud and self-hosted. Required for self-hosted setups.

## Browser Client Requirements

- **Sample rate:** 24000 Hz mono (matches Deepgram Agent)
- **Encoding:** 16-bit linear PCM, little-endian
- **WebSocket:** Binary mode (`ws.binaryType = 'arraybuffer'`)
- **Echo cancellation:** `getUserMedia({audio: {echoCancellation: true}})` — enabled but NOT sufficient alone; the server-side architecture must also prevent echo loops
- **Mobile compatibility:** Chrome/Safari only. Telegram in-app browser does NOT support `getUserMedia`.

## TTS Options (Updated June 2026)

### ElevenLabs Bella via Pollinations — ÖNERİLEN
- Endpoint: `POST https://gen.pollinations.ai/v1/audio/speech`
- Model: `elevenlabs`, voice: `bella` (doğal Türkçe kadın)
- Fallback: `openai-audio` + `nova`
- Diğer Pollinations TTS modelleri: `elevenflash`, `qwen-tts`, `openai-audio-large`
- PCM döner, 24kHz varsayılır

### Deepgram Aura-2 — ❌ TÜRKÇE YOK
Aura-2 sadece EN/ES/DE/FR/NL/IT/JA destekler. `aura-2-asteria-en` ile Türkçe metin okununca İngiliz aksanıyla çıkar ("İyiyim" → "I am" gibi duyulur). KULLANMA.

### Cartesia sonic-3.5
- Free tier: 20K kredi/ay (~27 dk). `play.cartesia.ai/sign-up`
- ⚠️ API key sistemde tanımlı değilse `FAILED_TO_SPEAK` hatası
- Pro: $4-5/ay (100K kredi, ~133 dk)

### Pinokio TTS Ekosistemi — ✅ ÜCRETSİZ, lokal GPU
- **En kapsamlı:** VoxCPM2 (2B, 30 dil, 48kHz, Voice Design + Cloning)
- **All-in-one:** Ultimate TTS Studio (8 motor: Chatterbox, Fish-Speech, F5, Kokoro...)
- **Tanıdık:** Chatterbox (0.5B, 23 dil, voice cloning)
- **Kurulum:** Pinokio üzerinden tek tık
- **Maliyet:** $0 (sadece elektrik)
- **Gereksinim:** NVIDIA GPU, ~4-6 GB VRAM
- **RTX 4060 8GB:** VoxCPM2 sınırda, diğerleri rahat
- **Detaylı karşılaştırma + tavsiye sırası:** `references/pinokio-tts-ecosystem.md`

### Chatterbox Multilingual V3 via HF Spaces — ✅ ÜCRETSİZ, voice cloning
- **Space:** `ResembleAI/Chatterbox-Multilingual-TTS-V3`
- **API:** `https://resembleai-chatterbox-multilingual-tts-v3.hf.space`
- **Model:** 0.5B, 23 dil (Türkçe dahil), MIT lisanslı, Resemble AI
- **Zero-shot voice cloning:** 5-30sn referans ses → her dilde klonlama
- **Devreye alma:** Gradio API çağrısı, dosya upload + SSE
- **Maliyet:** Ücretsiz (HF Spaces GPU kotasına tabi, soğuk başlatma 20-30sn)
- **Hız:** GPU'da 1-5sn (space yoğunluğuna göre değişir)
- **Kısıt:** Maks 300 karakter/metin, rate limit var. Backend sık çöküyor.
- **Detaylı dokümantasyon + kod örnekleri:** `references/chatterbox-hf-space-tts.md`

- Deepgram Agent bills per minute for STT+TTS+agent combined. One API call, one bill.
- Mistral LLM billed separately via our own API key. Use `mistral-small` for voice (fast, cheap, sufficient).
- Manual pipeline (v1-v5) burned Deepgram STT credits + Deepgram TTS credits + LLM tokens for EACH component separately. The Agent API consolidates.

## Decision Flow

```
Need voice agent?
├─ Budget + speed → Vocode (free, self-host)
├─ Production + scale → LiveKit (WebRTC, telephony)
├─ Fastest MVP → Vapi.ai or Retell AI
└─ Deepgram ecosystem → Agent API + custom LLM (this skill's approach)
```

## OpenRouter Free Model Speed Tests (June 2026)

Tested with `POST https://openrouter.ai/api/v1/chat/completions`:

| Model | Latency | First Token (stream) | Verdict |
|-------|---------|----------------------|---------|
| **Google Gemma 4 31B** | 1.3s | 2.16s | ✅ Best — fast, clean, no thinking leak |
| NVIDIA Nemotron 3 Super | 2.1s | 1.66s | ⚠️ Thinking preamble leaks ("Okay, the user is asking...") |
| OpenAI GPT-OSS 20B | 2.8s | — | ✅ Backup — slower but solid |
| Qwen3 Next 80B | — | — | ❌ Provider errors on free tier |
| Meta Llama 3.3 70B | — | — | ❌ Provider errors on free tier |

22 free models available total. Check live: `GET https://openrouter.ai/api/v1/models`
OpenRouter key at `/tmp/.or_key` (fully used: $0 balance).

⚠️ Deepgram's model name validation prevents using `:free` model IDs directly. Workaround: local HTTPS proxy.

## Reference Files

- `references/stt-providers.md` — STT provider comparison matrix (June 2026)
- `references/provider-comparison-voice-ttft-june-2026.md` — LLM provider TTFT/pricing: Groq, DeepSeek, Grok, Fireworks, Together, DeepInfra, Cerebras (June 2026)
- `references/deepgram-soniox-migration.md` — Code-level Deepgram → Soniox migration guide
- `references/v4-faster-whisper-pipeline.md` — v4 lokal STT pipeline: faster-whisper kurulum, VAD, resample
- `references/deepgram-custom-llm-format.md` — Custom LLM flat JSON format (legacy)
- `references/v6-relay-server.md` — Relay server code (v6, superseded)
- `references/asyncio-voice-patterns.md` — Asyncio patterns for voice agents
- `references/turkish-stt-landscape.md` — Turkish STT landscape analysis
- → `references/soniox-api-integration.md` (under sensitive-data-pipeline skill) — Soniox API details
- → `references/deepgram-voice-agent-setup.md` (under sensitive-data-pipeline skill)
