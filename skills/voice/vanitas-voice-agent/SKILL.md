---
name: vanitas-voice-agent
description: Vanitas sesli görüşme altyapısı — STT/TTS zinciri, mimari seçenekler, debugging, ve güvenlik.
triggers:
  - voice agent
  - sesli görüşme
  - voice_agent
  - STT
  - TTS
  - deepgram
  - elevenlabs
  - faster-whisper
  - pollinations whisper
  - ses çalışmıyor
  - failed to speak
---

# Vanitas Voice Agent (DEPRECATED — absorbed by vanitas-voice-bridge)

> **⚠️ This skill describes v5 (abandoned 2026-06-16).**  
> **Current development:** v16 — Soniox Voice Bot Demo (Python FastAPI, full-duplex, Silero VAD barge-in).  
> **Authoritative skill:** `vanitas-voice-bridge` (messaging category) — covers ALL versions v2-v16.  
> **New reference:** `vanitas-voice-bridge/references/soniox-voice-bot-demo.md` — Soniox full-duplex architecture details.

## Neden v5 Terk Edildi

- **faster-whisper `small` model ARM64'te 10x+ yavaş** — 3 saniyelik ses 30 saniyede işlenemedi, timeout. `tiny` model 0.7x real-time ama Türkçe kalitesi orta.
- **Pollinations Whisper 500 hatası veriyor** — OVH upstream kaynaklı, güvenilir değil.
- **ScriptProcessorNode PCM yakalama** → 4 ayrı tarayıcı/sunucu bug'ı çıktı (buffer size, output bağlantısı, AudioContext resume, binary receive formatı).
- **Yerine v10 (Deepgram + MediaRecorder):** Daha hızlı (~200ms), daha basit, daha kaliteli Türkçe.

## Mimari Evrim (Güncel)

| v | STT | TTS | Durum |
|---|-----|-----|-------|
| **v10** | Deepgram Nova-2 REST + MediaRecorder | Bella | ✅ **PRODUCTION** |
| v9 | faster-whisper-tiny + VAD + PCM | Bella | ❌ Abandoned |
| v6-v8 | Chrome Web Speech API | Bella | ❌ Abandoned |
| v5 | faster-whisper small | Bella | ❌ Abandoned |
| v2 | Deepgram Voice Agent (managed) | Aura-2 | 🔄 Fallback |

Tüm güncel mimari, pitfall'lar, başlatma komutları → `vanitas-voice-bridge` skill'i. Bu skill sadece tarihsel referans için korunuyor.

## Tarihsel Referans (Korunuyor)

Aşağıdaki bölümler v5 dönemine ait, sadece referans amaçlı. Güncel bilgi için `vanitas-voice-bridge` skill'ini yükle.

### Tarayıcı Ses Pipeline'ı (v5, ScriptProcessor)
```javascript
const audioCtx = new AudioContext({sampleRate: 24000});
const source = audioCtx.createMediaStreamSource(stream);
const processor = audioCtx.createScriptProcessor(4096, 1, 1);
const ratio = audioCtx.sampleRate / 24000;

processor.onaudioprocess = (e) => {
  const input = e.inputBuffer.getChannelData(0);
  const outLen = Math.floor(input.length / ratio);
  const int16 = new Int16Array(outLen);
  for (let i = 0; i < outLen; i++) {
    int16[i] = Math.max(-32768, Math.min(32767, input[Math.floor(i*ratio)] * 32767));
  }
  ws.send(int16.buffer);
};
source.connect(processor);
processor.connect(audioCtx.destination);
```

WebSocket bağlantısı:
```javascript
ws = new WebSocket(protocol + '//' + location.host + '/ws?token=' + VOICE_TOKEN);
```

## Pitfalls: Deepgram (artık kullanılmıyor)

- `aura-2-asteria-en`: **Türkçe desteklemez**, İngiliz aksanıyla okur
- Fazla query parametresi (`utterance_end_ms`, `endpointing`, `no_delay`) → HTTP 400
- Minimum çalışan parametre: `encoding=linear16&sample_rate=24000&language=tr&model=nova-3&interim_results=true`
- **Timeout**: Bağlantı açıldıktan sonra 10-15sn ses gelmezse 1011 internal error
- **Sample rate uyuşmazlığı**: Tarayıcı ile Deepgram farklı hızda kaydedebilir → otomatik resample gerekir
- Deepgram Voice Agent API: her mesaj yeni LLM session → Vanitas hafızası çalışmaz
- Cartesia TTS: API key sistemde tanımlı değilse 401

## Pitfalls: Pollinations

- API key process başlatılırken env'de olmalı
- Whisper için multipart/form-data ile WAV gönderilmeli
- `universal-3-pro` listede var ama 401 (ayrı auth katmanı)
- TTS fallback her zaman tanımlı olmalı (ElevenLabs kota/rate-limit)

## Pitfalls: Tarayıcı

- ScriptProcessorNode hoparlöre de bağlı → echo olabilir (gain node ile kıs)
- `getUserMedia` HTTPS ister (localhost ve Cloudflare tunnel'da OK)
- `AudioContext.sampleRate` ile `getUserMedia` sampleRate'i farklı olabilir → `ratio` ile düzelt
- AudioContext oluştururken `{sampleRate: 24000}` ver — tarayıcı desteklemezse kendi değerini kullanır

## Servis Yönetimi

v5 kaynak dosyası: `~/voice-agent-venv/voice_agent_v5.py`, port: 8765
Log: `/tmp/voice_agent_v5.log`
Tunnel: `cloudflared tunnel --url http://127.0.0.1:8765 --no-autoupdate`
Proxy: `vanitas_hermes_proxy.py`, port 8767

### Debugging sırası
1. `tail -30 /tmp/voice_agent_v5.log`
2. `curl localhost:8765/health`
3. `curl localhost:8767/health`
4. `curl localhost:8642/health`
5. Tarayıcı konsolu → PCM gönderiliyor mu?

## Bağımlılıklar (venv)
```
fastapi, uvicorn, httpx, numpy, websockets, faster-whisper, ctranslate2
```

## Mimari Evrim (referans)

| v | STT | TTS | Neden Değişti |
|---|-----|-----|---------------|
| v2 | Deepgram Agent | Aura-2 EN | TR aksan kötü, hafızasız |
| v3 | Deepgram WS | Bella | Timeout + format sorunları |
| v4 | faster-whisper | Bella | CPU ağır, model 9sn |
| v5 | faster-whisper | Bella | **AKTİF** — Pollinations Whisper TR'de kötü |
