# Soniox Official Frontend Comparison — 18 Tem 2026

## Source
Soniox's official `useMicrophone.ts` from `soniox-voice-bot-demo/frontend/src/hooks/` on GitHub.

## Critical Differences (Official vs Our v16 Code)

| Feature | Soniox Official | Our v16 (Broken) | Our v17 (Fixed) |
|---------|----------------|-------------------|-----------------|
| **AudioContext** | `new AudioContext({ sampleRate: 16000 })` | Native rate (48000Hz) | `new AudioContext({ sampleRate: 16000 })` ✅ |
| **Downsample** | **None** — browser does it | Manual nearest-neighbor (Float32 → 16kHz) | **None** ✅ |
| **Chunk size** | 512 (32ms) | 4096 (256ms) | 4096 (kept — VAD processes at 512 internally) |
| **GainNode(0)** | **None** — `processor.connect(audioCtx.destination)` | Yes (echo prevention) | **None** — `echoCancellation: true` in getUserMedia ✅ |
| **noiseSuppression** | Only Firefox | Always true | Only Firefox ✅ |
| **autoGainControl** | Only Firefox | Always true | Only Firefox ✅ |

## Root Cause of Silent Sessions (v16)

AudioContext at native rate (48000Hz) + manual nearest-neighbor downsample:
1. Browser gives Float32 samples at 48000Hz
2. Our code picks every 3rd sample (`Math.round(i * ratio)`)
3. This naive decimation loses amplitude — peak drops to **0.43%** (normal: 3-15%)
4. Soniox STT receives PCM but can't recognize speech (too quiet)
5. VAD never triggers (speech_starts = 0)

## The Fix (v17)

```javascript
// Create AudioContext DIRECTLY at 16kHz — no downsample needed
micCtx = new AudioContext({ sampleRate: 16000 });

// getUserMedia — minimal constraints
micStream = await navigator.mediaDevices.getUserMedia({
  audio: {
    sampleRate: 16000,
    channelCount: 1,
    echoCancellation: true,
    noiseSuppression: isFirefox,  // only Firefox
    autoGainControl: isFirefox,    // only Firefox
  }
});

// ScriptProcessor — direct, no GainNode
const source = micCtx.createMediaStreamSource(micStream);
const processor = micCtx.createScriptProcessor(4096, 1, 1);

processor.onaudioprocess = (event) => {
  const channelData = event.inputBuffer.getChannelData(0);
  // Float32 → Int16 — NO downgrade, AudioContext is already 16kHz
  const int16Data = new Int16Array(channelData.length);
  for (let i = 0; i < channelData.length; i++) {
    const sample = Math.max(-1, Math.min(1, channelData[i]));
    int16Data[i] = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
  }
  handlePcmData(int16Data.buffer);
};

source.connect(processor);
processor.connect(micCtx.destination);  // direct — no GainNode(0)
```

## Separate Playback Context

TTS audio at 24kHz needs its own AudioContext to avoid sample rate conflicts:

```javascript
playCtx = new AudioContext({ sampleRate: 24000 });
```

This separation prevents the mic context from being forced to 24kHz (which would break the 16kHz assumption).

## Verification

After the fix, server-side isolation test confirmed:
- Browser sends 8192-byte binary PCM chunks
- STT transcribes "Ses deneme 1-2" correctly
- LLM generates response (293ms first token)
- TTS produces 159,744 bytes of audio
- Full pipeline: STT → LLM → TTS all working

## Why noiseSuppression/autoGainControl Kill Mobile Audio

These browser-provided DSP filters are designed for phone calls, not voice agents:
- `noiseSuppression: true` — aggressively suppresses anything below a certain energy threshold. On mobile, the mic is further from the mouth, so speech energy is lower → suppressed.
- `autoGainControl: true` — tries to normalize loudness, but on mobile it can overshoot and reduce gain to near-zero during quiet speech.
- Firefox handles these differently (more conservative), so keeping them on for Firefox is OK.
- Chrome/Safari mobile: **disable both**. `echoCancellation: true` stays (prevents TTS feedback loop).