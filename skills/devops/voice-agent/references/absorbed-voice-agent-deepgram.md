---
name: voice-agent-deepgram
title: Deepgram Voice Agent Pipeline
description: >-
  Deepgram Voice Agent API ile gerçek zamanlı sesli konuşma ajanı kurulumu.
  STT (Nova-3) → BYO LLM (DeepSeek) → TTS (Aura-2/ElevenLabs) zinciri,
  FastAPI WebSocket sunucusu, ve tarayıcı tabanlı HTML arayüz.
trigger: >-
  User asks to set up a voice agent, real-time conversation AI, Deepgram
  integration, voice-to-voice pipeline, or "sesli asistan kur".
---
# Deepgram Voice Agent Pipeline

## Architecture — Two Approaches

### Approach A: Browser Direct WebSocket (PREFERRED)

Browser connects DIRECTLY to Deepgram, no server relay. Lower latency, simpler.

```
Browser (mic) → WebSocket → Deepgram Voice Agent API
Browser (speaker) ← WebSocket ← Deepgram (audio bytes)
Server (FastAPI) → /api/config → returns API keys (Tailscale/VPN only)
```

**Why this is preferred:** No extra hop for audio, no relay server bottleneck, browser handles all audio directly.

### Approach B: Server-Side WebSocket Relay (Legacy)

```
Browser → WebSocket → FastAPI Sunucu → Deepgram
                                              ├── STT: Nova-3
                                              ├── LLM: DeepSeek (BYO)
                                              └── TTS: Aura-2
Browser ← WebSocket ← FastAPI Sunucu ← Deepgram
```

Use only when browser cannot handle direct WebSocket (e.g., complex auth proxies).

## Prerequisites

- Deepgram API key (Bitwarden: `DEEPGRAM_API_KEY`, UUID: `b28b5872-...`)
- DeepSeek API key (Bitwarden: `DEEPSEEK_API_KEY`, UUID: `a0d813d6-...`)
- Python venv: `deepgram-sdk`, `fastapi`, `uvicorn` (websockets only for relay)
- Cloudflared binary (`/usr/local/bin/cloudflared`) — HTTPS tunnel for browser mic

## Browser WebSocket Auth — CRITICAL

**Browser `WebSocket` API DOES NOT support custom HTTP headers.**

Deepgram expects `Authorization: Token <API_KEY>`. This DOES NOT work from browser JS.

**Solution: `Sec-WebSocket-Protocol` header**

```js
// ✅ CORRECT — Deepgram interprets this as auth
const ws = new WebSocket('wss://agent.deepgram.com/v1/agent/converse', ['token', apiKey]);
// ❌ WRONG — no custom headers in browser WebSocket
// const ws = new WebSocket(url); ws.setHeader('Authorization', ...); // doesn't exist
```

This sends `Sec-WebSocket-Protocol: token, {apiKey}` in the handshake. Deepgram interprets `token` subprotocol as `Token` auth.

**After connection**, send Settings as the FIRST message (JSON string).

## WebSocket Settings Format

Deepgram Voice Agent endpoint: `wss://agent.deepgram.com/v1/agent/converse`

```json
{
  "type": "Settings",
  "audio": {
    "input": {"encoding": "linear16", "sample_rate": 24000},
    "output": {"encoding": "linear16", "sample_rate": 24000, "container": "wav"}
  },
  "agent": {
    "listen": {"provider": {"type": "deepgram", "model": "nova-3"}},
    "think": {
      "provider": {"type": "open_ai", "model": "deepseek-chat"},
      "endpoint": {
        "url": "https://api.deepseek.com/v1/chat/completions",
        "headers": {
          "Authorization": "Bearer <DEEPSEEK_KEY>",
          "Content-Type": "application/json"
        }
      },
      "prompt": "<SYSTEM_PROMPT>"
    },
    "speak": {"provider": {"type": "deepgram", "model": "aura-2-athena-en"}}
  }
}
```

## TTS Options

| Provider | Type | Model | Turkish | Notes |
|---|---|---|---|---|
| Deepgram Aura-2 | `deepgram` | `aura-2-athena-en` | ❌ English only | Built-in, no extra key |
| ElevenLabs | `eleven_labs` | `eleven_multilingual_v2` | ✅ Needs `voice_id` | `voice_id` ZORUNLU |

ElevenLabs Turkish için `language: "tr"` + geçerli bir `voice_id` gerekir.
`voice_id` olmadan Deepgram `INVALID_SETTINGS` hatası döner.
ElevenLabs API'den ses listesini çek (`GET /v1/voices`), boş dönüyorsa
hesapta ses klonlanmamıştır — önce ElevenLabs konsolundan ses oluşturulmalı.

## CRITICAL: HTTPS Requirement

**Tarayıcılar `getUserMedia()` (mikrofon) için HTTPS veya localhost ZORUNLU kılar.**

HTTP (`http://<ip>:8765`) üzerinden erişilen sayfada mikrofon çalışmaz —
buton tıklansa bile sessizce başarısız olur, kullanıcı "hiçbir şey olmuyor" der.

### Çözüm: Cloudflared Quick Tunnel

Sunucu başladıktan sonra cloudflared ile instant HTTPS tüneli aç:

1. Sunucuyu başlat (örn. port 8765)
2. Cloudflared tünel: log çıktısından `https://<random>.trycloudflare.com` URL'sini al
3. Kullanıcıya bu HTTPS URL'sini ver — mikrofon çalışır

Tünel URL'si her başlatmada değişir (geçici). Kalıcı çözüm için nginx +
Let's Encrypt veya Tailscale Serve kullanılabilir.

## API Key Erişimi

Deepgram ve DeepSeek anahtarları Bitwarden Secrets Manager'da saklanır.

- `bws` binary yolu: `/home/ubuntu/.hermes/bin/bws`
- `BWS_ACCESS_TOKEN` ortam değişkeni gerekli
- `.env` dosyasında `DEEPGRAM_API_KEY` ve `DEEPSEEK_API_KEY` tanımlı olmalı
- `bws secret list` ile tüm anahtarları listele, `key` alanına göre filtrele

## Verification Steps

1. REST API test: `GET https://api.deepgram.com/v1/projects` → HTTP 200
2. WebSocket test: Connect → send Settings → expect `SettingsApplied` mesajı
3. Server health: `GET /health` → `{"status":"ok"}`
4. Browser test: Cloudflared URL'yi aç → butona bas → mikrofon izni → konuş

## Browser JavaScript: Audio Capture

### ✅ USE MediaRecorder (Modern)

`createScriptProcessor()` Chrome'da deprecated — WebSocket hemen kopar (code 1006).
MediaRecorder ile `audio/webm;codecs=opus` formatında her 250ms'de bir blob gönder.
Tarayıcı JS'de her zaman try/catch ile hataları yakala ve Türkçe göster.

→ Full code and patterns: `references/browser-js-patterns.md`

## API Key Erişimi (Sistem Servisleri)

Sistem servislerinde veya background process'lerde `os.environ` her zaman
çalışmaz. `.env` dosyasından doğrudan okuma yapan bir fallback fonksiyonu
eklenmeli. `pathlib.Path.home() / ".hermes" / ".env"` yolundan
`KEY=VALUE` satırlarını parse eder. Bu sayede `source .env` gerekmez
ve API anahtarları process environment'ında görünmez.

## Common Pitfalls

- **Browser WebSocket auth fails (401)**: No custom headers in browser. Use `new WebSocket(url, ['token', apiKey])`.
- **ScriptProcessorNode çökmesi (code 1006)**: Chrome deprecated. Kullanılıyorsa WebSocket onopen → anında onclose. MediaRecorder ile değiştir.
- **Cloudflared idle timeout (~8s)**: Ses akışı yoksa tünel WebSocket'i kapatır. MediaRecorder sürekli chunk göndermeli. Uzun konuşmalar için Tailscale IP kullan.
- **`source .env` subprocess'te çalışmaz**: `os.environ.get()` boş dönüyorsa `_read_env()` pattern kullan (dosyadan doğrudan oku).
- **`uvicorn.run()` unutulur**: FastAPI app tanımlanır ama `if __name__ == "__main__": uvicorn.run(app, ...)` eksik olur. Sunucu sessizce exit 0 yapar, hiç port açmaz.
- **Port çakışması (Errno 98)**: `fuser -k <PORT>/tcp` ile temizle, `ss -tlnp` ile doğrula.
- **ElevenLabs `voice_id` ZORUNLU**: `eleven_labs` provider ile `INVALID_SETTINGS` → `voice_id` eksik. ElevenLabs hesabında ses yoksa konsoldan oluştur.
- **HTTP'de mikrofon çalışmaz**: Tarayıcı getUserMedia() HTTPS veya localhost ister. Cloudflared tunnel zorunlu.
- **Aura-2 sadece İngilizce**: Türkçe metni yabancı aksanla okur. Doğal Türkçe için ElevenLabs + geçerli voice_id.
- **`bws` PATH'te yok**: Tam yol `/home/ubuntu/.hermes/bin/bws`. `bws secret list` → key adıyla filtrele → UUID ile `bws secret get`.
- **`bws secret get` UUID ister**: Önce `bws secret list` ile ID'yi bul: `bws secret list | python3 -c "... filter by key ..."`, sonra `bws secret get <UUID>`.
