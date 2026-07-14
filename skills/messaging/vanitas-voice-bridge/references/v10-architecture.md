# v10 Deepgram REST Architecture — Design Decisions (2026-06-16)

## Why v10 Replaced v9

v9 (local whisper + VAD + raw PCM) abandoned after one session. Root causes:

1. **ARM64 too slow:** `small` model 30s+. `tiny` 0.7x real-time but Turkish quality poor.
2. **PCM complexity:** 4 bugs found in one session (ScriptProcessor output path, buffer size power-of-2, WebSocket binary dict unpacking, AudioContext suspended state).
3. **VAD sensitivity:** webrtcvad mode 3 needs real speech, not test tones.
4. **Silence timeout:** Must flush on disconnect. Easily missed.

## v10 Design Choices

### MediaRecorder (not ScriptProcessor)
- Produces browser-native webm/opus — no PCM conversion
- `ondataavailable` fires reliably, no audio graph hacks
- No sample rate negotiation drama
- Chunks sent directly as ArrayBuffer over WebSocket

### Deepgram REST (not WebSocket streaming)
- Simpler: POST accumulated webm, get JSON back
- No second WebSocket connection to manage
- Silence detection: if no chunks for 1.5s, flush
- 200-500ms REST latency negligible vs LLM+TTS time

### Silence-Based Flushing (not VAD)
- Silence detection: "has browser stopped sending?"
- Works because MediaRecorder only fires when there's audio
- Background `silence_monitor` coroutine checks every 500ms

## Session Memory
v10 keeps last 8 messages in conversation list. Each utterance adds to context. Full Hermes session memory still works via proxy forwarding.

## Deepgram API

### Nova-2 vs Nova-3
- `nova-2`: Better for Turkish. More stable, better non-English accuracy.
- `nova-3`: Newer, Turkish not yet validated.

### Query Parameters
```
language=tr&model=nova-2&smart_format=true&punctuate=true
```

### Response
```json
{"results": {"channels": [{"alternatives": [{"transcript": "...", "confidence": 0.98}]}]}}
```

## Error Recovery

### API Errors
- 400: Corrupt audio — check Content-Type and webm validity
- 401: Check API key env var
- 500: Retry once after 1s (transient)

### WebSocket Disconnect
- Handler calls `flush_audio()` — buffered audio processed before session ends
- Background monitor cancelled in `finally`

### LLM/TTS Failures
- Hermes errors → `{"type": "error"}` to browser
- TTS: Bella primary, Qwen fallback
- Browser shows red status
