# Custom Voice Pipeline v3 — Architecture & Reference

> **Created:** 2026-06-16  
> **Service:** `/home/ubuntu/voice-agent-venv/voice_agent_v3.py` (template in `templates/voice_agent_v3.py`)  
> **Log:** `/tmp/voice_agent_v3.log`  
> **Port:** 8765 (browser WebSocket)  
> **Status:** ✅ Working — Deepgram STT + Hermes LLM + ElevenLabs Bella TTS

## Architecture

v3 **bypasses Deepgram Voice Agent API entirely**. Instead it chains three independent services:

```
Browser (phone/desktop) → Cloudflare Tunnel → voice_agent_v3.py (:8765)
                                                    ├── Deepgram STT Streaming WS
                                                    │   (nova-3, language=tr, 24kHz PCM)
                                                    ├── Hermes Proxy (:8767) → Hermes API (:8642)
                                                    │   (Gerçek Vanitas, hafızalı)
                                                    └── Pollinations TTS (HTTP)
                                                        (elevenlabs/bella, PCM output)
```

### v2 vs v3 Comparison

| Component | v2 (Deepgram Agent) | v3 (Custom Pipeline) |
|-----------|---------------------|---------------------|
| STT | Deepgram Agent (black box) | Deepgram STT WS (direct) |
| LLM | Deepgram routes to proxy | Proxy → Hermes directly |
| TTS | Deepgram Aura-2 (EN only) | ElevenLabs Bella (TR natural) |
| Conversation | Deepgram internal context | Proxy session (last 10 msgs) |
| Fault isolation | All-or-nothing | Each component debugged separately |

## Key Learnings

### 1. Deepgram Aura-2 TTS: NO Turkish Support
Deepgram's Aura-2 TTS models support: EN, ES, DE, FR, NL, IT, JA. **Turkish is NOT available.** Using `aura-2-asteria-en` for Turkish produces garbled output ("İyiyim" → "I am"). This is NOT fixable — use an alternative TTS.

### 2. Pollinations TTS — The Best Alternative

**Available TTS models** (from `GET /v1/models`):
- `elevenlabs` — ElevenLabs v3, multilingual, natural Turkish
- `elevenflash` — ElevenLabs Flash, faster/cheaper
- `openai-audio` — OpenAI TTS (alloy, echo, fable, nova, onyx, shimmer)
- `openai-audio-large` — OpenAI TTS large
- `qwen-tts` — Qwen TTS
- `qwen-tts-instruct` — Qwen TTS with instruction following

**Endpoint:** `POST https://gen.pollinations.ai/v1/audio/speech`
**Auth:** `Authorization: Bearer <POLLINATIONS_API_KEY>`

**Working Turkish config (tested 2026-06-16):**
```json
{
  "model": "elevenlabs",
  "input": "Merhaba, nasılsın?",
  "voice": "bella",
  "response_format": "pcm",
  "speed": 1.0
}
```

Response: raw 16-bit PCM audio at sample rate matching input (24kHz).

**Fallback chain** (if ElevenLabs fails):
```json
{
  "model": "openai-audio",
  "input": "text",
  "voice": "nova",
  "response_format": "pcm"
}
```

### 3. Deepgram STT Streaming WebSocket (NOT Agent API)

**URL:** `wss://api.deepgram.com/v1/listen`
**Auth:** `Authorization: Token <DEEPGRAM_API_KEY>` header

**Parameters for Turkish:**
```
encoding=linear16&sample_rate=24000&language=tr&model=nova-3&interim_results=true&utterance_end_ms=700&no_delay=true&endpointing=500
```

**Key events:**
- `SpeechStarted` — user began speaking
- `UtteranceEnd` — user finished speaking → trigger LLM call
- `Results` with `is_final: true` → final transcript
- `Results` with `is_final: false` → interim transcript (for UI display)

**Audio format:** 16-bit signed integer PCM, mono, 24kHz (matching browser output)

### 4. Browser PCM Streaming (ScriptProcessorNode)

**Issue:** MediaRecorder API does not reliably produce raw PCM; `audio/webm;codecs=pcm` unsupported in most browsers.

**Solution:** Use `AudioContext.createScriptProcessor()` (deprecated but universally supported):

```javascript
const audioCtx = new AudioContext({sampleRate: 24000});
const source = audioCtx.createMediaStreamSource(stream);
const processor = audioCtx.createScriptProcessor(4096, 1, 1);

processor.onaudioprocess = (e) => {
  const input = e.inputBuffer.getChannelData(0); // Float32Array
  const int16 = new Int16Array(input.length);
  for (let i = 0; i < input.length; i++) {
    int16[i] = Math.max(-32768, Math.min(32767, input[i] * 32767));
  }
  ws.send(int16.buffer);
};

source.connect(processor);
processor.connect(audioCtx.destination); // Echo back — remove for production
```

**⚠️ Pitfall:** `processor.connect(audioCtx.destination)` creates speaker echo. In production, omit this connection if echo cancellation isn't perfect.

### 5. Session Conversation Context

To maintain conversation flow across multiple utterances, the proxy accumulates messages:

```python
conversation = []  # [(role, content), ...]

async def get_vanitas_reply(text):
    conversation.append({"role": "user", "content": text})
    recent = conversation[-10:]  # Keep last 10 exchanges
    response = await client.post(PROXY_URL, json={
        "model": "mistral",
        "messages": recent,
        "stream": False,
    })
    reply = response.json()["choices"][0]["message"]["content"]
    conversation.append({"role": "assistant", "content": reply})
    return reply
```

This gives **memory within a single browser session**. Cross-session memory relies on Hermes's own USER.md/MEMORY.md injection.

### 6. Cartesia TTS — Free Tier Available

**Pricing (2026-06):**
- Free: $0/mo, 20K credits (~27 min Sonic-3.5), 1 agent slot
- Pro: $4/mo, 100K credits (~133 min), instant voice cloning
- Startup: $37/mo, 1.25M credits, pro voice cloning

**Key:** We do NOT have a Cartesia API key. Previous code referenced Cartesia but no key was ever configured — it fell back to Deepgram's Aura-2 internally.

### 7. Voice Agent Process Management (Same for v2 and v3)

After ANY code change, the running process keeps old code — MUST restart:
```bash
pkill -f voice_agent_v3.py
sleep 1
cd /home/ubuntu/voice-agent-venv && ./bin/python voice_agent_v3.py 2>&1 | tee /tmp/voice_agent_v3.log &
```

Check what's actually running:
```bash
grep 'Stack:' /tmp/voice_agent_v3.log
curl -s http://localhost:8765/health
```

## Quick Health Check
```bash
# v3 running?
curl -s http://localhost:8765/health

# Tunnel active?
ps aux | grep "cloudflared.*8765" | grep -v grep

# Latest session
grep 'Session ended' /tmp/voice_agent_v3.log | tail -3

# STT working?
grep '\[user\]' /tmp/voice_agent_v3.log | tail -3

# TTS working?
grep 'Audio sent' /tmp/voice_agent_v3.log | tail -3
```

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| "I am teşekkürler" | English TTS model (Aura-2) | Use ElevenLabs Bella (v3) |
| "Failed to speak" | Missing/broken TTS API key | Check Pollinations key; fallback to openai-audio |
| No transcript | Deepgram STT not hearing | Check browser mic permissions; verify PCM format |
| Delayed response | Hermes LLM latency | Reduce context window or use mistral model |
| Conversation amnesia | Session context lost | Verify conversation list isn't being reset |
| Echo/doubled audio | ScriptProcessor connected to destination | Remove `processor.connect(audioCtx.destination)` |
