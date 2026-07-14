# Turkish STT Landscape (Haziran 2026)

## Test Edilenler

| Provider | Model | Streaming | Türkçe Doğruluk | Ücret | Sonuç |
|----------|-------|-----------|-----------------|-------|-------|
| Deepgram | nova-2 language=tr | ✅ WebSocket | Kötü | Bedava | ❌ Anlamıyor |
| Deepgram | nova-3 language=multi | ✅ WebSocket | Orta-düşük | Bedava | ⚠️ Testte |
| faster-whisper | large-v3 (CPU) | ❌ | %88 (kaynak: OpenAI) | Bedava | ❌ ARM64'te çok yavaş |
| Groq Whisper | large-v3-turbo | ❌ REST | %88 | $0.04/saat | ❌ Streaming yok |
| Soniox | native Turkish | ✅ WebSocket | İddia: native | $0.12/saat | ✅ En iyi f/p |
| ElevenLabs | Scribe v2 Realtime | ✅ WebSocket | %3.8 WER | $0.39/saat | 🏆 En doğru |
| Azure Speech | neural | ✅ WebSocket | İyi | 5 saat/ay bedava | Kart ister |
| Google Cloud | latest_long | ✅ gRPC | İyi | 60 dk/ay bedava | Kart ister |

## Vosk (Dolandırıcılık Riski)

- small-tr-0.3: 35MB, WER "TBD", GitHub'da "yetersiz" denmiş
- Big model: "e-posta ile ulaşın" — güvenilir değil
- **Kullanma.**

## Henüz Test Edilmeyen

- **whisper.cpp** ARM64: C++ optimize, real-time streaming örneği var (stream.wasm). ARM64 perf bilinmiyor.
- **whisper-streaming-websocket** (GitHub: soufiiyane): faster-whisper + VAD + VAC + WebSocket. ARM64'te test gerek.

## Deepgram nova-3 Doğru Parametreler

```
wss://api.deepgram.com/v1/listen?model=nova-3&language=multi&smart_format=true&punctuate=true&encoding=linear16&sample_rate=16000&channels=1&interim_results=true&utterance_end_ms=1000&endpointing=100
```

- `language=tr` → 405 (nova-3 WebSocket'te geçersiz)
- `language=multi` → çalışır
- `endpointing=100` → çokdilli için önerilir
