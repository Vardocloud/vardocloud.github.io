# VAD Implementation — Web Speech API Continuous Listening

**Date:** 2026-07-01  
**Context:** Vanitas v13.1 — push-to-talk rejection, natural conversation flow  

## Architecture

Web Speech API (`SpeechRecognition`) with `continuous: true` + `interimResults: true` provides a built-in VAD-like experience:

```javascript
const recognition = new SpeechRecognition();
recognition.continuous = true;     // Keep listening after each utterance
recognition.interimResults = true; // Show text while user speaks
recognition.lang = 'tr-TR';
```

## VAD Flow (No External Library)

| Step | What Happens |
|------|-------------|
| 1 | User clicks "Konuşmayı Başlat" (required browser gesture) |
| 2 | `recognition.start()` → microphone opens, status: "Dinliyorum" |
| 3 | User speaks → `onresult` fires → interim + final transcripts accumulate |
| 4 | On each final result → reset 1.2s silence timer |
| 5 | Timer expires (user stopped speaking) → `processWithLLM(transcript)` |
| 6 | LLM responds → TTS plays via AudioContext |
| 7 | TTS ends → `recognition.start()` again → back to step 2 |

## Silence Timer (1.2s)

```javascript
let silenceTimer = null;
// In onresult:
if (final) {
  if (silenceTimer) clearTimeout(silenceTimer);
  silenceTimer = setTimeout(() => {
    if (transcript.trim() && !isProcessing && !isSpeaking) {
      processWithLLM(transcript);
    }
  }, 1200); // 1.2s — good balance for Turkish speech
}
```

**Why 1.2s?** Turkish natural speech has longer pauses between thoughts than English. 0.6s cuts off mid-sentence. 1.2s is short enough to feel responsive but long enough for natural pauses.

## Auto-Restart on Error (Critical)

Mobile browsers frequently drop SpeechRecognition due to:
- Network changes (tunnel instability)
- Audio focus loss (notification sounds, calls)
- Resource constraints (battery saver, background tab)

```javascript
recognition.onerror = function(event) {
  if (event.error === 'no-speech') return; // Normal silence
  if (event.error === 'aborted') return;   // Intentional stop
  if (event.error !== 'not-allowed' && autoRestart) {
    setTimeout(startRecognition, 1500); // Restart after 1.5s
  }
};

recognition.onend = function() {
  if (autoRestart && !isSpeaking && !isProcessing) {
    setTimeout(startRecognition, 800); // Restart after 0.8s
  }
};
```

## Echo Prevention

During TTS playback, recognition must be paused to prevent the microphone from capturing the speaker output:

```javascript
async function processWithLLM(text) {
  pauseRecognition(); // Stop listening
  // ... LLM + TTS ...
  // On TTS end:
  resumeRecognition();
}
```

## Known Limitations

| Issue | Impact | Workaround |
|-------|--------|------------|
| `continuous: true` mobile battery drain | +15-20% | Accept for now |
| No speaker diarization | Can't distinguish speakers | Voiceprint microservice (separate) |
| Max 1-minute recognition sessions (some browsers) | Auto-restart handles this | Already implemented |
| Background tab throttling | 30s-60s silence then auto-restart | Already implemented |
| Two getUserMedia calls (STT + PCM) | Second call may fail | Voiceprint is fire-and-forget |

## Files

- `~/vanitas-web/public/index.html` — Full implementation (~450 lines)
- `~/vanitas-web/server.mjs` — Backend API (chat, TTS, voiceprint proxy)
- `~/vanitas-web/voiceprint_service.py` — Python MFCC verification service
