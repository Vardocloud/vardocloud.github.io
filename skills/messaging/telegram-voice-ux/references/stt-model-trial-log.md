# STT Model Trial Log — Turkish Voice Agent

**Date:** 2026-06-16  
**Context:** Deepgram WebSocket streaming voice agent (v10.7)  
**Goal:** Find STT model with accurate Turkish transcription and real-time streaming support

## Models Tested

| # | Model | Parameters | Result | Root Cause |
|---|-------|-----------|--------|------------|
| 1 | `nova-2` + `language=tr` | `wss://...?model=nova-2&language=tr&...` | ⚠️ Connected but garbled Turkish | `language=tr` constraint causes artifacts in casual Turkish |
| 2 | `whisper-large` | `wss://...?model=whisper-large&...` | ❌ HTTP 405 | Whisper NOT available on Deepgram WebSocket streaming |
| 3 | `nova-3` + `language=tr` | `wss://...?model=nova-3&language=tr&...` | ❌ HTTP 405 | nova-3 WebSocket needs `language=multi`, not `tr` |
| 4 | `nova-3` (no language) | `wss://...?model=nova-3&...` | ✅ Connected, accuracy suboptimal | Auto-detection not optimized for Turkish |
| 5 | `nova-3` + `language=multi` | `wss://...?model=nova-3&language=multi&endpointing=100&...` | ✅ Connected, accuracy still problematic | Multilingual mode includes Turkish but not native-level |

## Key Takeaways

1. Whisper models only on Deepgram REST `/v1/listen` — NOT WebSocket streaming
2. nova-3 with `language=multi` is best Deepgram option for Turkish streaming
3. Soniox identified as superior: native Turkish accuracy, open-source demo
4. Working URL format: `wss://api.deepgram.com/v1/listen?model=nova-3&language=multi&endpointing=100&encoding=linear16&sample_rate=16000&channels=1&interim_results=true&utterance_end_ms=1000`

## Groq Whisper STT (REST only)

`whisper-large-v3-turbo` ($0.04/hr) and `whisper-large-v3` ($0.111/hr) via `/v1/audio/transcriptions`. No streaming — not suitable for real-time voice agents.
