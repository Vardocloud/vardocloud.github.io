# Gapless Browser Audio Playback for Voice Agents

## Problem
Streaming TTS audio chunks arrive over WebSocket. Playing each chunk as a separate `<audio>` element causes audible gaps (stuttering). On mobile, `new Audio()` and `decodeAudioData()` both fail silently due to autoplay restrictions.

## Root Cause
1. Each `<audio>` element has setup latency: create → decode → start. Cumulative gaps destroy listening.
2. `new Audio().play()` blocked by mobile autoplay on iOS Safari and Chrome Android.
3. `AudioContext.decodeAudioData()` also fails silently on mobile — promise never resolves, no audio.

## Solution: AudioContext.createBuffer() + setInterval + Chunk Merging (Mobile-Verified June 2026)

**DO NOT use `decodeAudioData()` on mobile** — it silently fails. Use `createBuffer()` + manual PCM→Float32.

### Core Pattern
```javascript
let audioCtx = null, nextPlayTime = 0;
let audioChunks = [];  // queue of Int16Array PCM chunks
let playbackTimer = null;

function scheduleAudioPlayback() {
  if (!audioCtx || audioChunks.length === 0) return;
  if (playbackTimer) return;
  
  playbackTimer = setInterval(() => {
    if (audioChunks.length === 0) { clearInterval(playbackTimer); playbackTimer = null; return; }
    
    // MERGE all pending chunks
    let total = 0;
    for (const c of audioChunks) total += c.length;
    const merged = new Int16Array(total);
    let off = 0;
    while (audioChunks.length) { merged.set(audioChunks.shift(), off); off += audioChunks[0]?.length || 0; }
    
    const buf = audioCtx.createBuffer(1, merged.length, 24000);
    const ch = buf.getChannelData(0);
    for (let i = 0; i < merged.length; i++) ch[i] = merged[i] / 32768.0;
    
    const src = audioCtx.createBufferSource();
    src.buffer = buf;
    src.connect(audioCtx.destination);
    const t = Math.max(audioCtx.currentTime, nextPlayTime);
    src.start(t);
    nextPlayTime = t + buf.duration;
  }, 50);
}
```

### Why This Works
- `createBuffer()` is synchronous — no async decoding, no mobile autoplay issues
- Chunk merging eliminates crackling (Deepgram sends ~960B = 20ms chunks at 24kHz)
- `source.start(scheduledTime)` on audio clock, not JS event loop
- `setInterval` at 50ms batches chunks for smooth playback
- `sourceNode.connect(audioCtx.destination)` piggybacks on AudioContext from user gesture

## WAV Header Creation (linear16 PCM → WAV Blob)
```javascript
function createWav(pcm, sampleRate) {
  const bitsPerSample = 16, numChannels = 1;
  const byteRate = sampleRate * numChannels * bitsPerSample / 8;
  const blockAlign = numChannels * bitsPerSample / 8;
  const dataSize = pcm.length * blockAlign;
  const buf = new ArrayBuffer(44 + dataSize);
  const v = new DataView(buf);
  v.setUint32(0, 0x52494646, false); v.setUint32(4, 36 + dataSize, true);
  v.setUint32(8, 0x57415645, false);
  v.setUint32(12, 0x666d7420, false); v.setUint32(16, 16, true);
  v.setUint16(20, 1, true); v.setUint16(22, numChannels, true);
  v.setUint32(24, sampleRate, true); v.setUint32(28, byteRate, true);
  v.setUint16(32, blockAlign, true); v.setUint16(34, bitsPerSample, true);
  v.setUint32(36, 0x64617461, false); v.setUint32(40, dataSize, true);
  for (let i = 0; i < pcm.length; i++) v.setInt16(44 + i * 2, pcm[i], true);
  return new Blob([buf], { type: 'audio/wav' });
}
```

## Pitfalls (Mobile-Only, June 2026)
- **`decodeAudioData()` silently fails on iOS Safari** — use `createBuffer()` + manual Float32 conversion
- **`new Audio(url).play()` blocked by autoplay** — no error, just silence
- **`container: "wav"` in Deepgram output**: ZERO audio bytes sent. Remove `container`, use raw PCM.
- **Deepgram chunk size**: ~960B = 20ms at 24kHz. Too small individually — merge them.
- **ScriptProcessor**: Must connect to `audioCtx.destination` on Safari or `onaudioprocess` never fires
- **Sample rate mismatch**: Mobile defaults to 48kHz, Deepgram expects 24kHz. Client-side resample needed.

## Implementation Reference
- Full code: `/home/ubuntu/voice-agent-venv/voice_agent_v2.py` (TEST_PAGE_HTML section)
- Uses `createBuffer()` + `setInterval(50ms)` + chunk merging + `nextPlayTime` scheduling
- Verified iOS Safari + Chrome Android: smooth, gapless TTS playback
