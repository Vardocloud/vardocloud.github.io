# AudioWorklet Migration — 13 Temmuz 2026

## Neden AudioWorklet?

| Özellik | ScriptProcessorNode (eski) | AudioWorklet (yeni) |
|---------|---------------------------|---------------------|
| İş parçacığı | Ana thread (UI ile yarışır) | Ayrı audio thread |
| Durum | **Deprecated** (2014'ten beri) | **Modern standart** |
| iOS Safari | Güvenilmez, bazen tetiklenmez | iOS 14.5+ stabil |
| Performans | Yüksek ses basıncında glitch | Zaman-kesin garantili |
| Gecikme | 2 render quantum (zorunlu) | 1 quantum (daha düşük) |

## Mimari

```
Ana Thread                   AudioWorklet Thread
───────────                  ──────────────────
createMediaStreamSource ──→ PCMCaptureProcessor.process()
    │                              │
    │                         Float32 alır
    │                         ↓ downsample (→16kHz)
    │                         ↓ Float32 → PCM s16le
    │                         ↓
    │                    port.postMessage(buffer, [buffer])
    │                              │
    │◄────────────────────────────┘
    │
    handlePcmData(pcmBuffer)
    │  ├─ Level meter güncelle
    │  └─ ws.send(pcmBuffer) → Sunucu
```

## Kod Yapısı

### 1. Worklet Kodu (string → Blob URL)

```javascript
const WORKLET_CODE = `
'use strict';
class PCMCaptureProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._inputRate = sampleRate;
    this._ratio = sampleRate / 16000;
  }
  process(inputs, outputs, params) {
    const input = inputs[0];
    if (!input || !input[0] || !input[0].length) return true;
    const samples = input[0];
    // Downsample → 16kHz
    let out;
    if (this._inputRate === 16000) {
      out = samples;
    } else {
      const newLen = Math.floor(samples.length / this._ratio);
      out = new Float32Array(newLen);
      for (let i = 0; i < newLen; i++)
        out[i] = samples[Math.min(Math.round(i * this._ratio), samples.length - 1)];
    }
    // Float32 → PCM s16le
    const pcm = new Int16Array(out.length);
    for (let i = 0; i < out.length; i++) {
      const s = Math.max(-1, Math.min(1, out[i]));
      pcm[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    // Zero-copy transfer
    this.port.postMessage(pcm.buffer, [pcm.buffer]);
    return true;
  }
}
registerProcessor('pcm-capture-processor', PCMCaptureProcessor);
`;
```

### 2. Main Thread — AudioWorklet Başlatma

```javascript
async function startMicCapture() {
  // ... getUserMedia ...

  // TRY AudioWorklet first
  if (audioCtx.audioWorklet) {
    try {
      const blob = new Blob([WORKLET_CODE], {type: 'application/javascript'});
      const blobUrl = URL.createObjectURL(blob);
      await audioCtx.audioWorklet.addModule(blobUrl);
      URL.revokeObjectURL(blobUrl);

      const workletNode = new AudioWorkletNode(audioCtx, 'pcm-capture-processor');
      workletNode.port.onmessage = (e) => handlePcmData(e.data);

      source.connect(workletNode);

      // Echo önleme: GainNode(0) ile sessiz çıkış
      const silentGain = audioCtx.createGain();
      silentGain.gain.value = 0;
      workletNode.connect(silentGain);
      silentGain.connect(audioCtx.destination);

      captureNode = workletNode;
      captureMethod = '⚡ AudioWorklet';
      return;
    } catch (e) {
      console.warn('AudioWorklet not supported, falling back:', e);
    }
  }

  // FALLBACK: ScriptProcessorNode
  // ... createScriptProcessor kodu ...
}
```

## Önemli Noktalar

1. **Blob URL:** Worklet kodu inline string olarak tanımlanır, `Blob` + `URL.createObjectURL` ile yüklenir. Ayrı `.js` dosyası gerekmez.

2. **Transferable postMessage:** `port.postMessage(pcm.buffer, [pcm.buffer])` — buffer'ı kopyalamaz, ownership'ı transfer eder. Zero-copy!

3. **captureNode değişkeni:** Hem AudioWorkletNode hem de ScriptProcessorNode için ortak referans. `stopMicCapture()` ikisini de `disconnect()` eder.

4. **GainNode(0):** AudioWorkletNode'un da output bağlantısına ihtiyacı vardır (audio graph'ın bir parçası olmalı). GainNode(0) ile sessiz çıkış echo'yu önler.

5. **sampleRate:** `AudioWorkletGlobalScope`'daki `sampleRate` değişkeni sayesinde worklet, browser'ın native sample rate'ini bilir ve doğru downsampling yapabilir. `constructor()`'da `this._inputRate = sampleRate` ile saklanır.

## Fallback Senaryoları

| Durum | Oluşma Sebebi | Sonuç |
|-------|---------------|-------|
| `audioCtx.audioWorklet` undefined | Çok eski tarayıcı (Safari <14.5, Chrome <66) | ScriptProcessor fallback |
| `addModule()` hatası | CSP blokluyor, blob URL izni yok | ScriptProcessor fallback |
| `AudioWorkletNode()` hatası | Nadir, bellek/izin | ScriptProcessor fallback |
| Worklet çalışır ama port mesaj gelmez | Hatalı process() dönüşü (`return true` unutulursa) | Console uyarısı, ScriptProcessor'a düşüş yok (bir sonraki session'da) |

## Test

1. Tarayıcı konsolunda log kontrolü:
   - `[Mic] ✅ AudioWorklet aktif` → AudioWorklet kullanılıyor
   - `AudioWorklet desteklenmiyor, ScriptProcessor'a düşülüyor` → Fallback aktif

2. `captureBadge` elementi gösterir:
   - `⚡ AudioWorklet` → Modern, ayrı thread
   - `🔄 ScriptProcessor (fallback)` → Deprecated API

3. Sunucu tarafı testi için `server-side-isolation-test.md` kullanılır.

## Gelecek

- **AudioWorklet + SharedArrayBuffer** ile daha da düşük gecikme (ileride)
- **WASM işleme** — worklet içinde Silero VAD çalıştırmak (teorik)
- **Worker → Worklet port bridge** ile voiceprint doğrulama
