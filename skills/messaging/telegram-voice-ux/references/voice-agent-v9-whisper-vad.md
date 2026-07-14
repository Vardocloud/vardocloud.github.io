# Voice Agent v9 — faster-whisper + webrtcvad (CURRENT)

## Architecture
Browser PCM → WebSocket → VAD (webrtcvad) → faster-whisper-tiny → Proxy (8767) → Hermes → Bella TTS

## Why v9 replaced v6-v8
v6-v8 used Chrome's Web Speech API for STT:
- **Clicking sounds**: `recognition.start()`/`stop()`/`abort()` cycles produced system audio pops
- **Poor Turkish quality**: Chrome's built-in Turkish STT is mediocre, missed words
- **Unreliable continuous mode**: `continuous: true` caused echo loops; `continuous: false` caused slow start/stop cycles
- **Echo loop**: TTS audio → microphone → STT → new utterance → infinite loop

v9 uses server-side faster-whisper-tiny:
- **No clicking**: Microphone opens ONCE, stays open. VAD handles silence/activity.
- **Better Turkish**: Whisper tiny > Chrome STT for Turkish
- **No echo loop**: Audio capture is PCM-only, no STT feedback path in browser

## Model Selection (ARM64 CPU)
| Model | 3s audio | Ratio | RAM | Verdict |
|-------|---------|-------|-----|---------|
| `tiny` | 2.0s | 0.7x | ~400MB | ✅ Real-time |
| `base` | 3.2s | 1.1x | ~500MB | ✅ Near real-time |
| `small` | 30s+ | 10x+ | ~1GB | ❌ Unusable |

**Default: `tiny`** — fast enough for conversation, good enough Turkish for voice agent.

## VAD Configuration
- Library: webrtcvad 2.0.10
- Mode: 3 (most aggressive — best for clean speech in quiet environments)
- Frame size: 30ms (480 samples at 16kHz, 960 bytes at 16-bit)
- Silence timeout: 1.0s (speech → silence gap → end utterance)
- Max utterance: 15s (safety cap)
- Min utterance: 0.3s (ignore clicks/pops)

## webrtcvad pkg_resources Bug
webrtcvad 2.0.10 imports `pkg_resources` which was removed in setuptools 67+. Fix:
```python
# In webrtcvad.py, replace:
import pkg_resources
__version__ = pkg_resources.get_distribution('webrtcvad').version
# With:
__version__ = "2.0.10"
```

## Browser Audio Capture
- Separate AudioContext for capture (16kHz) and playback (24kHz)
- **ScriptProcessorNode buffer: 512 samples (32ms at 16kHz)** — MUST be power of 2 (256, 512, 1024, ...). 480 throws `Failed to execute 'createScriptProcessor': buffer size must be power of two between 256 and 16384`.
- Float32 → Int16 conversion before WebSocket: `new Int16Array(512)` fixed size, `(input[i] || 0) * 32767` with clamp
- Do NOT connect processor to destination (prevents feedback)
- `echoCancellation: true, noiseSuppression: true, autoGainControl: true`

## Browser-Server Frame Size Mismatch (Critical)
Browser sends 512-sample (32ms) chunks. webrtcvad requires 480-sample (30ms) frames. Server resolves this with a **vad_buffer accumulation pattern**:
```python
vad_buffer = bytearray()
VAD_FRAME = 480 * 2  # 960 bytes

# On each WS binary message:
vad_buffer.extend(raw)
while len(vad_buffer) >= VAD_FRAME:
    frame = vad_buffer[:VAD_FRAME]
    vad_buffer = vad_buffer[VAD_FRAME:]
    is_voice = vad.is_speech(bytes(frame), SAMPLE_RATE)
    # ... process frame for speech/silence ...
```
This handles any incoming chunk size — the server accumulates and re-frames to 30ms. Remaining bytes carry over to next WS message.

## Pollinations Whisper (DO NOT USE)
`POST https://gen.pollinations.ai/v1/audio/transcriptions` returns HTTP 500 INTERNAL_ERROR from upstream (ovh.net). Unreliable — do not attempt.

## Echo Loop Prevention (v6-v8 learnings, applies to any browser STT)
1. Guards (debounce, echo, pause) must run BEFORE `addMessage()` — otherwise duplicate messages appear in DOM
2. `recognitionPaused` must be set on utterance send, not on `agent_speaking` response
3. 3-layer echo guard: substring match, prefix match, word overlap >50%
4. After TTS: 1500ms cooldown before restarting recognition
5. `continuous: false` is more reliable than `continuous: true` for Turkish

## Code Location
- `/home/ubuntu/voice-agent-venv/voice_agent_v9.py` — current version
- `/tmp/voice_agent_v9.log` — runtime log
- Port 8765, cloudflare tunnel `belts-midi-snake-austin.trycloudflare.com`
- Token auth: `?token=2fcff74bacf5` (both HTTP and WS)
