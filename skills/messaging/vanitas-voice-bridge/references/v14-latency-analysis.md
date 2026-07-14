# v14.1 Pipeline Latency Analysis

Measured 5 Temmuz 2026 on Hermes container (Docker, WSL, x86_64).

## Pipeline Components

| Stage | Technology | Latency (3sn audio) | Notes |
|-------|-----------|---------------------|-------|
| VAD silence | Browser AnalyserNode RMS | **1000ms** | Configurable via `SILENCE_MS` constant |
| STT | Groq Whisper `whisper-large-v3` | **~400ms** (1sn audio) — **~1500ms** (3sn audio) | Scales with audio duration |
| LLM | Groq `llama-3.3-70b-versatile` | **~250ms** | Streaming TTFB, total depends on response length |
| TTS | Edge TTS CLI (`edge-tts`, EmelNeural) | **~1300ms** | CLI startup + file I/O overhead |
| **Total** | (VAD+STT+LLM+TTS) | **~3500ms** (worst case: 1sn VAD+1.5sn STT+0.3sn LLM+1.3sn TTS) |

## Measurement Method

```bash
# STT (send audio, measure round-trip)
START=$(date +%s%N)
curl -s -X POST http://127.0.0.1:3005/api/stt \
  -H 'Content-Type: audio/wav' \
  --data-binary @/tmp/speech.wav > /dev/null
END=$(date +%s%N)
echo "STT: $(( (END-START)/1000000 ))ms"

# LLM (send prompt, measure first token)
# TTS (send text, measure audio return)
```

## Bottlenecks (ranked)

1. **Edge TTS** (~1300ms) — CLI spawns a Python process, loads models, writes temp file. ElevenLabs API (~1080ms) slightly faster but not transformative. Real fix: Soniox TTS or sentence streaming.
2. **STT** (400-1500ms) — Scales with audio length. Soniox WebSocket would eliminate this entirely (real-time transcription during speech).
3. **VAD** (1000ms) — Hard lower-bound for natural turn-taking. Below 700ms risks cutting users off mid-pause.

## Forward Path for ~1.5s Total Latency

| Change | Latency Saved | Cumulative |
|--------|--------------|------------|
| Soniox stt-rt-v5 (WebSocket, real-time) | ~1000ms (VAD+STT) | 1500ms |
| ElevenLabs sentence streaming TTS | ~800ms (TTF) | 700ms |
| **Target total** | | **~1.5s** |

## VAD Tuning Guide

Parameters in `index.html`:
- `SPEAK_THRESHOLD = 0.015` — RMS threshold for speech detection. Lower = more sensitive. Adjust if mic sensitivity varies.
- `SILENCE_MS = 1000` — ms of silence before triggering. 700ms for faster response, 1200ms for safer turn-taking.
- `MIN_RECORD_MS = 300` — minimum recording duration to prevent false triggers.
- VAD check interval: 200ms (every `setInterval` tick).

Audio format: `sampleRate: 16000, channelCount: 1, echoCancellation: true, noiseSuppression: true`.
