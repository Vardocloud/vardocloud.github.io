# Voice Agent Error Reference

## 2026-06-16 — Echo Loop & 401 Auth

### Hermes 401 Unauthorized (v6)
**Symptom:** Every LLM request returns HTTP 401.
**Root cause:** v6 called Hermes API directly without auth header. Hermes requires authentication.
**Fix:** Route through voice proxy which handles auth internally. See SKILL.md section "LLM" for architecture.

### Echo Loop (v6-v8)
**Symptom:** Message count escalates (2→3→5→7...) without user input. Vanitas "talks to herself."
**Root cause:** Web Speech API continuous mode captures TTS audio from speakers → STT → sent as new utterance.
**Full trace:** TTS mp3 plays → speakers → mic captures → STT "Selam" → echo guard checks `"selam".includes("selam! ben iyiyim, sen..."` → FALSE → sends to server → loop.
**Fix:** Check REVERSE match: `assistant_text.startsWith(recognized)` AND `assistant_text.includes(recognized)`. Plus 3-layer defense: abort during TTS, recognitionPaused flag, text-matching guard.

### Voice Quality (v6)
**Fix:** Always use mp3 format for TTS, not raw PCM. Browser handles decode correctly.

### Duplicate Messages in UI (v7-v8)
**Symptom:** Same user message appears 2-3 times in transcript.
**Root cause:** `addMessage('user', final)` called BEFORE debounce check. `onresult` fires twice → two DOM nodes created, though only one utterance sent.
**Fix:** Move ALL guard checks (echo, debounce, pause) BEFORE `addMessage`. Guards must run before any DOM changes.

### ScriptProcessorNode Silent Failure (v9)
**Symptom:** WebSocket connects, mic permission granted, zero audio frames flow. `onaudioprocess` never fires.
**Root cause:** ScriptProcessorNode MUST be connected to audio destination for the callback to execute. Connecting only to source is insufficient.
**Fix:** `processor.connect(gainNode); gainNode.gain.value = 0; gainNode.connect(ctx.destination);` — gain=0 prevents feedback.

### FastAPI Binary WebSocket Receive (v9)
**Symptom:** Audio chunks arrive at server but `isinstance(raw, bytes)` returns False. All audio silently dropped.
**Root cause:** Starlette's `ws.receive()` wraps binary in dict: `{"type": "websocket.receive", "bytes": b"..."}`.
**Fix:** Handle `raw.get("bytes")` before the `isinstance(raw, bytes)` check.

### Deepgram REST 400 "corrupt data" (v10-v10.1)
**Symptom:** Deepgram API returns 400: "failed to process audio: corrupt or unsupported data"
**Root cause:** MediaRecorder's webm chunks, when concatenated, do NOT form a valid standalone webm file. The EBML header is only in the first chunk, and cluster boundaries may be misaligned.
**Fix:** Use Deepgram WebSocket streaming API with `encoding=opus` — raw opus frames pass through without format conversion.

### webrtcvad Import Error (v9, Python 3.12+)
**Symptom:** `ModuleNotFoundError: No module named 'pkg_resources'` when importing webrtcvad.
**Root cause:** webrtcvad 2.0.10 imports `pkg_resources` which was removed from setuptools 67+.
**Fix:** Patch the installed webrtcvad.py to remove the pkg_resources import and hardcode version.

### faster-whisper ARM64 Performance (v9)
**Symptom:** `faster-whisper small` model takes 30+ seconds for 3 seconds of audio on ARM64 CPU.
**Root cause:** `small` model is too heavy for ARM64 CPU with `int8` quantization.
**Fix:** Use `tiny` model only (0.7x real-time, ~2s for 3s audio). `base` works at 1.1x. `small` and above = unusable.

---

## 2025-06-16 — Earlier Errors

### Deepgram: "Failed to speak"
Cartesia API key missing. Aura-2 TTS English-only.

### Deepgram STT: 400 / 1011
Extra query params cause 400. Lazy WebSocket connect needed to avoid timeout.

### faster-whisper: 32-second latency
beam_size=5 on CPU. beam_size=1 → ~6s. Still too slow for real-time.

### Pollinations Whisper: garbage Turkish
"Edel" → "altyazı M.K." — unusable for Turkish.

### TTS format: male/deep voice
Raw PCM conversion distorts. Use mp3 format instead.

## TTS Reference

| Model | Voice | Status | Notes |
|---|---|---|---|
| elevenlabs | bella | Working | Female Turkish, primary, use mp3 |
| elevenflash | bella | Working | Smaller, faster |
| qwen-tts | default | Working | Reliable fallback |
| openai-audio | nova | Broken | 400 error |
| Deepgram Aura-2 | — | Broken | No Turkish support |
