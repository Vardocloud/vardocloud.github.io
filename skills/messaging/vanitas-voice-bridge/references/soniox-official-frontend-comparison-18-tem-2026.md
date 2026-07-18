# Soniox Official Frontend Comparison — 18 Tem 2026

## Kaynak

Soniox resmi voice bot demo frontend: `https://github.com/soniox/soniox_examples/tree/master/apps/soniox-voice-bot-demo/frontend`

`/src/hooks/useMicrophone.ts` — ana ses yakalama hook'u. React/TypeScript.

## Karşılaştırma

| Ozellik | Soniox Official | Bizim v16 (eski) | Bizim v17 (18 Tem 2026) |
|---------|----------------|------------------|------------------------|
| AudioContext | `new AudioContext({ sampleRate: 16000 })` | `new AudioContext()` (48000Hz) | `new AudioContext({ sampleRate: 16000 })` |
| Downsample | **Yok** AC 16kHz | AudioWorklet nearest-neighbor | **Yok** |
| Capture | ScriptProcessor 512 samples | AudioWorklet + SP fallback | ScriptProcessor 4096 |
| Echo onleme | `echoCancellation: true` + isSpeaking | `echoCancellation: true` + GainNode(0) | `echoCancellation: true` + isSpeaking |
| `processor.connect` | `audioCtx.destination` direkt | `GainNode(0).connect(destination)` | `micCtx.destination` direkt |
| noiseSuppression | Sadece Firefox | Hep acik | Sadece Firefox |
| autoGainControl | Sadece Firefox | Hep acik | Sadece Firefox |
| Playback context | Ayni AC | Ayni AC | Ayri 24kHz AC |

## Kritik Dersler

### 1. AudioContext sampleRate = Anahtar
Soniox resmi `new AudioContext({ sampleRate: 16000 })` kullanir. Tarayici hardware-level resample yapar. Bizim v16 48000Hz'de calisip nearest-neighbor downsample yapiyordu her 3 ornekten 1'ini alarak enerjiyi 1/3'e dusuruyordu. Peak 0.4% (normal 3-15%).

### 2. GainNode(0) Gereksiz
Soniox resmi kullanmaz. `processor.connect(audioCtx.destination)` + `echoCancellation: true` yeterli. GainNode(0) echo cozum gibi gorunuyordu ama asil sorun downsample'di.

### 3. NS + AGC = Mobil Katil
Soniox: `noiseSuppression: isFirefox`. Bizim v16: her zaman acik. Mobil tarayicilarda ses seviyesini neredeyse sifira dusuruyor.

## Soniox Official Frontend Code (useMicrophone.ts)

```typescript
const TARGET_SAMPLE_RATE = 16000;
const CHUNK_SIZE = 512;

const stream = await navigator.mediaDevices.getUserMedia({
  audio: {
    sampleRate: TARGET_SAMPLE_RATE,
    channelCount: 1,
    echoCancellation: true,
    noiseSuppression: isFirefox,
    autoGainControl: isFirefox,
  },
});

const audioContext = new AudioContext({ sampleRate: TARGET_SAMPLE_RATE });
const source = audioContext.createMediaStreamSource(stream);
const processor = audioContext.createScriptProcessor(CHUNK_SIZE, 1, 1);

processor.onaudioprocess = (event) => {
  const channelData = event.inputBuffer.getChannelData(0);
  const int16Data = new Int16Array(channelData.length);
  for (let i = 0; i < channelData.length; i++) {
    const sample = Math.max(-1, Math.min(1, channelData[i]));
    int16Data[i] = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
  }
  onData(int16Data.buffer);
};

source.connect(processor);
processor.connect(audioContext.destination);
```