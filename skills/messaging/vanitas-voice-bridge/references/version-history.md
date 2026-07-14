# Version History (Archive)

## v14 — Groq Whisper STT (5 Tem 2026)
- STT: Groq Whisper `whisper-large-v3` (~400ms)
- TTS: Edge TTS (EmelNeural) + ElevenLabs Bella (Pollinations proxy)
- Architecture: HTTP REST (no full-duplex)
- Replaced: Deepgram Nova-2 REST (v10)
- Latency: ~3500ms total (VAD+STT+LLM+TTS)
- **Full details:** `references/v14-latency-analysis.md`
- **Watchdog:** `references/voice-watchdog-system.md`

## v15 — SonioxClient JS SDK (5 Tem 2026)
- Bridge to Soniox via JavaScript SDK
- esbuild bundle + Groq LLM + Edge TTS
- Short-lived: immediately superseded by v16

## v10 — Deepgram Nova-2 REST + MediaRecorder (16 Haz 2026)
- **PRODUCTION** öncesi son half-duplex versiyon
- STT: Deepgram Nova-2 REST (MediaRecorder webm/opus)
- TTS: ElevenLabs Bella (Pollinations proxy)
- Port: 8765 (Python FastAPI)
- Terk edilme sebebi: Deepgram REST polling → WebSocket full-duplex ihtiyacı

## v9 — faster-whisper-tiny + VAD + PCM
- ARM64'te tiny model 0.7x real-time (small 10x+ → unusable)
- 4 browser bug: ScriptProcessorNode, AudioContext resume, binary format, output bağlantısı
- webrtcvad 2.0.10 broken pkg_resources → `__version__` hardcode

## v6-v8 — Chrome Web Speech API
- Kötü Türkçe, tıklama sesleri, echo loop
- Web Speech API sınırlamaları

## v5 — Pollinations Whisper
- OVH upstream → 500 Internal Server Error, güvenilmez
- faster-whisper small ARM64'te 10x+ yavaş → timeout

## v2 — Deepgram Voice Agent (managed)
- Aura-2 TTS İngiliz aksanıyla Türkçe okur
- Her mesaj yeni LLM session → Vanitas hafızası çalışmaz
