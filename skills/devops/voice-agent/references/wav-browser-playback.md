# Browser WAV Audio Playback

Deepgram Voice Agent returns PCM audio in WAV container (`encoding: linear16`, `container: wav`).
The browser must construct a proper WAV header before playback because the raw bytes from Deepgram
are linear16 PCM without RIFF wrapper.

## WAV Header Construction (JavaScript)

```javascript
function makeWav(pcmBytes) {
  var wav = new ArrayBuffer(44 + pcmBytes.length);
  var v = new DataView(wav);

  // RIFF chunk
  var write = function(pos, str) {
    for (var i = 0; i < str.length; i++) v.setUint8(pos + i, str.charCodeAt(i));
  };
  write(0, 'RIFF');
  v.setUint32(4, 36 + pcmBytes.length, true);  // file size - 8
  write(8, 'WAVE');

  // fmt chunk
  write(12, 'fmt ');
  v.setUint32(16, 16, true);   // chunk size
  v.setUint16(20, 1, true);    // PCM format
  v.setUint16(22, 1, true);    // mono
  v.setUint32(24, 24000, true); // sample rate
  v.setUint32(28, 48000, true); // byte rate (sampleRate * channels * bitsPerSample/8)
  v.setUint16(32, 2, true);    // block align
  v.setUint16(34, 16, true);   // bits per sample

  // data chunk
  write(36, 'data');
  v.setUint32(40, pcmBytes.length, true);

  // Copy PCM
  new Uint8Array(wav, 44).set(new Uint8Array(pcmBytes));

  return new Blob([wav], {type: 'audio/wav'});
}

// Usage in WebSocket handler:
ws.onmessage = function(e) {
  if (e.data instanceof Blob) {
    e.data.arrayBuffer().then(function(buf) {
      var blob = makeWav(new Uint8Array(buf));
      var audio = new Audio(URL.createObjectURL(blob));
      audio.play().catch(function(err) { console.log('Audio blocked:', err); });
    });
  }
};
```

## Mobile Autoplay Policy

Mobile browsers block `audio.play()` unless triggered by user gesture. Mitigation:
1. Always `.catch()` the play promise
2. On first user click (the "Start" button), create and immediately pause a silent AudioContext to "unlock" audio
3. Show a warning if autoplay was blocked, instructing user to tap the page

## Verified Audio Format

- Input (upload): linear16 PCM, 24000Hz, mono, raw bytes (no header)
- Output (download): linear16 PCM, 24000Hz, mono, WAV container
- Bit depth: 16-bit signed integer, little-endian
