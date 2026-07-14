# v14 Architecture — MediaRecorder + VAD + Deepgram Nova-2 STT

> **Tarih:** 5 Temmuz 2026
> **Durum:** ✅ PRODUCTION (CURRENT)
> **Önceki:** v13.1 (Web Speech API, abandoned due to Chrome origin restrictions)

## Stack

| Layer | Teknoloji | Detay |
|-------|-----------|-------|
| **Frontend** | Vanilla HTML/JS | `index.html` — MediaRecorder + AnalyserNode VAD |
| **STT** | Deepgram Nova-2 | `POST /api/stt` → Deepgram REST API (Türkçe) |
| **LLM** | Groq llama-3.3-70b | `POST /api/chat` → SSE streaming |
| **TTS** | Edge TTS | `edge-tts` CLI → tr-TR-EmelNeural |
| **Voiceprint** | MFCC (numpy+scipy) | `voiceprint_service.py` (port 5050) |
| **Tunnel** | Cloudflare Quick Tunnel | `cloudflared tunnel --url http://127.0.0.1:3005` |
| **Server** | Node.js HTTP | `server.mjs` (port 3005) |

## Data Flow

```
Kullanıcı konuşuyor
  → MediaRecorder (WebM/Opus, 100ms chunks)
    → AnalyserNode VAD (RMS threshold 0.015, 200ms interval)
      → 1.5sn sessizlik = VAD trigger
        → MediaRecorder.stop()
          → Blob oluştur
            → POST /api/stt (Content-Type: audio/webm)
              → [server.mjs] Deepgram Nova-2 API çağrısı
                → Transkript JSON döndür
                  → processWithLLM(transcript)
                    ├─ Heartbeat komutu mu? → /api/heartbeat → TTS
                    └─ Normal sohbet → Groq (streaming) → TTS
```

## Backend API (server.mjs)

### POST /api/stt
- **Input:** Raw audio body (WebM/Opus binary)
- **Content-Type:** `audio/webm`
- **Output:** `{ "transcript": "...", "confidence": 0.99 }`
- **Deepgram:** Nova-2 model, Türkçe, noktalama aktif
- **Gereken API Key:** `DEEPGRAM_API_KEY` (BWS'de saklanır)
- **Hata durumu:** Minimum 100 byte kontrolü, çok kısa sesler reddedilir

### POST /api/chat (değişmedi)
Groq llama-3.3-70b-versatile, SSE streaming.
System prompt: "Sen Vanitas'sin - Edel'in yapay zeka asistani."

### POST /api/tts (değişmedi)
Edge TTS CLI (`edge-tts`), tr-TR-EmelNeural, MP3 output.

### POST /api/heartbeat (değişmedi)
Sesli supervisor — task durumu sorgulama.

## Frontend (index.html)

### VAD (Voice Activity Detection)
- **AnalyserNode** ile RMS hesaplama (fftSize=256)
- **Threshold:** 0.015 (konuşma başlangıcı)
- **Silence timeout:** 1500ms sessizlik = kaydı durdur
- **Min record:** 500ms (çok kısa kayıtları atla)
- **Check interval:** 200ms

### MediaRecorder
- **MIME:** `audio/webm;codecs=opus` (fallback: `audio/webm`)
- **Timeslice:** 100ms (ondataavailable sıklığı)
- **Auto-restart:** Her TTS sonrası otomatik yeniden başlar

### Voiceprint (fire-and-forget)
- ScriptProcessorNode ile PCM capture (16kHz, Int16)
- Her LLM çağrısı öncesi /api/voiceprint/verify çağrılır
- LLM'i bloke etmez (async, await'siz)

### TTS Playback
- `new Audio(url)` ile oynatma (autoplay kilidi için AudioContext)
- Web Audio API fallback (decodeAudioData + BufferSource)
- `finishTts()` → VAD reset + auto-restart

## Kalıcılık & Servis Yönetimi

### Watchdog Script (`voice_watchdog.sh`)
- **Zamanlama:** Her 2 dakikada bir (no-agent cron)
- **Job ID:** `41d2e0671bd6`
- **Kontrol:** Voice Agent (port 3005), Voiceprint (port 5050), Cloudflare Tunnel
- **Çıktı:** Sadece değişiklik varsa Telegram'a mesaj (sessiz watchdog)
- **Tunnel URL:** `~/.hermes/data/voice_tunnel_url.txt`

### Startup Script (`voice_startup.sh`)
- **Çağrıldığı yer:** `~/.profile` (login shell)
- **Sıra:** Voice Agent → Voiceprint → Cloudflare Tunnel
- **Koruma:** `VOICE_STARTED` env var ile tekrar çalışması engellenir

### Tunnel
- **Tür:** Cloudflare Quick Tunnel (trycloudflare.com)
- **Uyarı:** URL her restart'ta değişir, uptime garantisi yok
- **Otomatik başlatma:** Watchdog (2dk içinde) + Startup script

## Derived Requirements (v13 → v14 Migration)

1. Chrome Web Speech API `trycloudflare.com` domain'inde çalışmıyor
2. Deepgram API key BWS'de mevcut (`DEEPGRAM_API_KEY`)
3. MediaRecorder + AnalyserNode VAD her HTTPS domain'de çalışır
4. Deepgram Nova-2 Türkçe kalitesi Web Speech API'den iyidir
5. Voiceprint + Heartbeat etkilenmez (sadece STT katmanı değişti)
