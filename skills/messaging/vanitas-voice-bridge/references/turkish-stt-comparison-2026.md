# Turkish STT Accuracy & Cost Comparison (June 2026)

**Compiled:** June 16, 2026
**Context:** Vanitas voice bridge Turkish STT evaluation — Deepgram accuracy insufficient, exploring alternatives.
**Key finding:** ElevenLabs Scribe has the best Turkish accuracy (3.8% WER) but costs $0.39/hr. Soniox claims "native-speaker" at $0.12/hr. No free streaming option has good Turkish.

## Free Tier Availability

| Provider | Free Tier | Streaming | Turkish Quality |
|----------|-----------|-----------|-----------------|
| Deepgram | $200 credits (new signup, no CC) | ✅ WebSocket | ⚠️ Poor (9.9% WER FLEURS) |
| Azure Speech | 5 hours/month | ✅ WebSocket | ✅ Good |
| Google Cloud STT | 60 min/month | ✅ gRPC | ✅ Good |
| Groq Whisper | Free tier (rate-limited) | ❌ REST only | ✅ 88.7% (Whisper Large V3) |
| Vosk | Open source (local) | ✅ WebSocket | ❓ Unknown |
| ElevenLabs Scribe | Pay-as-you-go only | ✅ Realtime API | 🏆 3.8% WER |
| Soniox | Pay-as-you-go only | ✅ WebSocket | 🏆 "Native-speaker" |
| Local faster-whisper | Free (local CPU) | ⚠️ Possible via repo | ❌ ARM64 too slow |

## Turkish WER Benchmarks (FLEURS)

| Model | WER | Source |
|-------|-----|--------|
| ElevenLabs Scribe v1 | **3.8%** | elevenlabs.io/speech-to-text/turkish |
| Gemini Flash 2 | 5.1% | Same source |
| Whisper Large v3 | 7.5% | Same source |
| Deepgram Nova-2 | 9.9% | Same source |

## Streaming STT Cost (Turkish-capable, real-time)

| Provider | Model | Per Hour | 30min/day Monthly | Turkish WER |
|----------|-------|----------|-------------------|-------------|
| **Soniox** | STT v5 | **$0.12** | ~$1.80 | "Native" |
| **Deepgram** | Nova-3 streaming | $0.34 | ~$5.10 | ~9.9%? |
| **ElevenLabs** | Scribe Realtime | **$0.39** | ~$5.85 | **3.8%** 🏆 |
| OpenAI | gpt-4o-mini-transcribe | $0.18 | ~$2.70 | Good |
| Azure | Speech Standard | $0.96 | ~$14.40 | Good |
| Google Cloud | Chirp 2 | $0.29 | ~$4.32 | Good |

*30min/day = ~15 hours/month of actual speech (assuming 50% speaking time in conversation)*

## Decision Matrix

| Priority | Best Choice | Why |
|----------|------------|-----|
| **Free** | Deepgram ($200 credits) | Only free streaming option, but Turkish accuracy is poor |
| **Cheapest** | Soniox ($1.80/mo) | Lowest per-hour rate with Turkish-native claim |
| **Best Turkish** | ElevenLabs Scribe (3.8% WER) | Industry-leading accuracy, realtime API available |
| **Local/Offline** | Vosk Turkish model | Open source, runs on ARM64, accuracy unknown |

## What We Actually Tried

| Solution | Status | Why Failed/Abandoned |
|----------|--------|---------------------|
| Deepgram Nova-2 + language=tr | ❌ | Poor Turkish accuracy |
| Deepgram Nova-3 + language=multi | ❌ | Still poor Turkish (this session) |
| Deepgram Nova-3 + language=tr | ❌ | HTTP 405 on WebSocket |
| Deepgram whisper-large | ❌ | REST-only, no WebSocket streaming |
| Local faster-whisper large | ❌ | ARM64 CPU too slow |
| Local faster-whisper small | ❌ | Still too slow on ARM64 |
| Groq Whisper (REST) | ❌ | No streaming support |
