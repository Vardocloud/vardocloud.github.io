# Speaker-Based Voice Setup — Echo Cancellation & Natural Desktop Conversation

**Date:** 2026-06-16 | **Session:** v10.4→v10.6 voice agent iterations

## Problem

Vanitas voice bridge must work WITHOUT headphones — Edel wants natural desk conversation with speakers. The default setup produces an echo/feedback loop where TTS audio plays through speakers, gets picked up by the microphone, and gets re-transcribed by Deepgram as garbage ("san san san", "ses sesi sim sim sim").

## Root Causes (3-Layer)

### 1. Mic Monitoring (Direct Feedback Loop)
```javascript
processor.connect(audioCtx.destination);
```
This line connects the microphone input DIRECTLY to the speakers. The microphone signal is played back with ~10ms delay (ScriptProcessor buffer), creating immediate acoustic feedback.

**Fix:** Remove the line entirely. ScriptProcessorNode fires `onaudioprocess` based on INPUT connection, not output. `source.connect(processor)` is sufficient.

### 2. TTS Echo (Indirect Feedback Loop)
When TTS plays through speakers:
1. Speaker audio travels through air → microphone
2. Microphone captures TTS + user's voice
3. Deepgram transcribes the mix → gets garbled text ("san san san")
4. Speculative LLM fires with garbage text → wastes resources
5. LLM generates response to garbage → more TTS → cycle repeats

The browser's `echoCancellation: true` in `getUserMedia` is NOT sufficient for this. It works best with headphones; on speakers, the acoustic path is too complex for basic AEC.

### 3. Multiple Browser Tabs (Zombie Sessions)
User refreshes page → old WebSocket stays open → old Deepgram connection waits for audio that never comes → timeout. 3-5 simultaneous zombie sessions observed in logs.

## Solutions Implemented (v10.6)

### Solution 1: Remove Mic Monitoring
```javascript
// BEFORE (v10.4-v10.5):
source.connect(processor);
processor.connect(audioCtx.destination);  // ❌ FEEDBACK

// AFTER (v10.6+):
source.connect(processor);
/* mic monitoring disabled to prevent echo loop */
```

### Solution 2: Gate Mic During TTS Playback
```javascript
processor.onaudioprocess = (e) => {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  if (playing || audioQueue.length) return;  // 🛑 Don't send during TTS
  // Energy gate — skip silence
  let energy = 0;
  for (let i = 0; i < input.length; i++) {
    energy += input[i] * input[i];
  }
  if (energy < input.length * 0.0001) return;  // Silence threshold
  // ... send audio
};
```

This effectively makes the conversation **half-duplex during TTS** — microphone is muted while Vanitas is speaking. User CANNOT interrupt (barge-in), which is the tradeoff for echo-free operation.

### Solution 3: Session Deduplication
```python
_active_sessions = {}

@app.websocket("/ws")
async def ws_endpoint(ws):
    client_ip = ws.client.host
    old_sid = _active_sessions.pop(client_ip, None)
    if old_sid:
        log.info(f"Closing duplicate session {old_sid}")
    sid = uuid.uuid4().hex[:8]
    _active_sessions[client_ip] = sid
    # ... finally: _active_sessions.pop(client_ip, None)
```

### Solution 4: Audio Queuing (Frontend)
TTS audio chunks arrive asynchronously. Without queuing, they play simultaneously (overlapping speech).

```javascript
let audioQueue = [], playing = false;

function playAudio(buf) {
  audioQueue.push(buf);
  playNext();
}

function playNext() {
  if (playing || !audioQueue.length) return;
  playing = true;
  const buf = audioQueue.shift();
  // ... decode and play
  src.onended = () => {
    playing = false;
    setTimeout(playNext, 150);  // 150ms gap between sentences
  };
}
```

## What Does NOT Work (Tested & Rejected)

| Approach | Result | Why |
|----------|--------|-----|
| `echoCancellation: true` alone | Echo persists | Browser AEC needs headphones; insufficient for speakers |
| `noiseSuppression: true` alone | No effect | Doesn't address echo, only ambient noise |
| Lowering TTS volume | Helps but not enough | User can't hear Vanitas properly |
| `utterance_end_ms < 1000` | HTTP 400 from Deepgram | Minimum is 1000ms for Nova-2 |

## Future: True Full-Duplex with Barge-In

For true natural conversation (both can speak simultaneously, user can interrupt):
1. **Acoustic Echo Cancellation (AEC)** — needs reference signal loopback
2. **AudioWorklet** instead of ScriptProcessor — lower latency, better AEC integration
3. **Server-side VAD on raw audio** — detect user speech energy vs TTS energy
4. **Streaming cancellation** — when user speaks during TTS, cancel remaining TTS and switch to listening

Current half-duplex approach (mute during TTS) is a pragmatic tradeoff that works NOW.
