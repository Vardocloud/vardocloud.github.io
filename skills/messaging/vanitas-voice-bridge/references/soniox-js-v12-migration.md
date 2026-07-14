# v12 Soniox JS SDK Migration (2026-06-23)

## Mimari Değişimi

**v11 (önceki):**
```
Browser → ScriptProcessor PCM (120 satır) → WebSocket binary → Server → Soniox SDK (STT) → LLM → TTS (ElevenLabs)
```

**v12 (yeni):**
```
Browser → SonioxClient SDK (40 satır) → Soniox API (direkt STT!) → transcript → WebSocket text → Server → LLM → TTS (Edge TTS)
```

## Kazanımlar

- ~300 satır server-side STT kodu kalktı (voiceprint, speaker tracking, silence timer, Soniox SDK backend)
- ~80 satır browser-side PCM kodu kalktı (ScriptProcessor/AudioWorklet)
- WebSocket binary trafiği → text-only (daha hafif, daha güvenilir)
- TTS ücretsiz (Edge TTS, Pollinations bakiyesi bitmişti)
- Aylık maliyet ~$7.50 → ~$1.80

## Yeni Bileşenler

### 1. Temporary API Key Endpoint (`/tmp-key`)
- `POST /tmp-key` → Soniox `create_temporary_api_key()` döndürür
- `usage_type: "transcribe_websocket"`, `expires_in_seconds: 300`
- Browser her session'da yeni key alır (key asla browser'da kalmaz)
- Python SDK method: `create_temporary_api_key()` (snake_case, `_api_` infix ile)

### 2. WebSocket Text-Only Protokol
- `{"type": "transcript", "text": "..."}` — Browser Soniox'tan gelen transcript'i server'a iletir
- `{"type": "flush", "text": "..."}` — Endpoint event'inde LLM'e gönder
- `{"type": "assistant", "text": "..."}` — LLM yanıtı
- Audio binary → MP3 chunk (Edge TTS)

### 3. Edge TTS
- `edge_tts.Communicate(text, "tr-TR-EmelNeural")`
- `pip install edge-tts` (önceden yüklü)
- MP3 çıktı, browser `decodeAudioData` ile decode eder
- Tempfile pattern: `NamedTemporaryFile(delete=False)` → `save()` → oku → `unlink()`

## Debugging Sırası (v12)

1. `curl http://127.0.0.1:8765/health` — voice agent ayakta mı?
2. `curl -X POST http://127.0.0.1:8765/tmp-key` — temporary key dönüyor mu?
3. Python websockets test script'i (`/tmp/test_v12_full.py`) — transcript → flush → assistant → audio döngüsü
4. Tarayıcı: Cloudflare tunnel URL + `?token=2fcff74bacf5`

## Bilinen Hatalar

- `memory_index.json` string listesi, dict listesi değil → `retrieve_memory()` type check yapmalı
- `AsyncSonioxClient(api_key=...)` zorunlu, boş çağrılmaz
- Pollinations bakiyesi 0.0065 pollen → TTS çalışmaz, Edge TTS kullan
