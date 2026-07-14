# v14 Latency Analysis (5 Temmuz 2026)

## Ölçüm Yöntemi

Her pipeline aşaması ayrı ayrı curl ile ölçüldü. Sürelere network latency dahildir.

## Sonuçlar

| Aşama | Ortalama Süre | Not |
|-------|--------------|-----|
| VAD silence (konuşma sonu bekleme) | 1500ms | JavaScript setInterval 200ms, RMS threshold 0.015 |
| Deepgram Nova-2 REST STT (1sn ses) | 1094ms | REST POST → bekle → transkript dönüş |
| Groq LLM (llama-3.3-70b) | 296ms | 106ms total_time (Groq server-side) |
| Edge TTS CLI (EmelNeural) | 1298ms | edge-tts CLI başlatma + dosya yazma |
| **Toplam (konuşma bitiminden itibaren)** | **~4188ms** | |

## Darboğazlar (Sıralı)

1. **Edge TTS CLI** (1300ms) — En büyük darboğaz. Her TTS çağrısında Python CLI başlatılır, edge-tts kütüphanesi yüklenir, MP3 dosyaya yazılır, okunur. Çözüm: ElevenLabs HTTP API (~400ms, Bella sesi, sentence streaming).

2. **Deepgram REST STT** (1100ms) — REST POST ile tüm sesi gönder, Deepgram işlesin, transkript dönsün. Çözüm: Soniox stt-rt-v5 WebSocket (~200ms, gerçek zamanlı, VAD beklemesi yok).

3. **VAD silence** (1500ms) — Konuşma bitince 1.5sn sessizlik beklenir. Çözüm: WebSocket streaming STT ile VAD beklemesine gerek kalmaz.

## Optimizasyon Stratejisi

### Kısa Vade (Soniox key yokken)
- VAD threshold: 0.015 → 0.01 (daha hassas)
- Silence bekleme: 1500ms → 700ms
- Edge TTS → ElevenLabs Bella (mevcut BWS key)

### Uzun Vade (Soniox key var)
- Soniox stt-rt-v5 WebSocket STT (browser-side, @soniox/client JS SDK)
- ElevenLabs Bella TTS (sentence streaming + barge-in)
- Groq LLM (streaming, cümle cümle TTS)
- Hedef: ~900ms total latency

## Ölçüm Komutları

```bash
# Deepgram STT
time curl -s -X POST http://127.0.0.1:3005/api/stt \
  -H 'Content-Type: audio/wav' \
  --data-binary @/tmp/test_audio.wav

# Groq LLM
time curl -s -X POST http://127.0.0.1:3005/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"merhaba"}'

# Edge TTS
time curl -s -X POST http://127.0.0.1:3005/api/tts \
  -H 'Content-Type: application/json' \
  -d '{"text":"Merhaba dünya."}' -o /dev/null
```
