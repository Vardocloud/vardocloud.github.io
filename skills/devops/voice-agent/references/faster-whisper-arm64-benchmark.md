# Faster-Whisper ARM64 Benchmark

Oracle Cloud A1 (Ampere Altra, 4 vCPU, 5.8GB RAM), Python 3.12.

## Model Speed Test (3s audio, language=tr, beam_size=5)

| Model | Load Time | Transcribe 3s | Ratio | Usable? |
|-------|-----------|---------------|-------|---------|
| tiny | 1.1s | 2.0s | 0.7x | ✅ Fast |
| base | 4.8s* | 3.2s | 1.1x | ✅ OK |
| small | ~1s | 30s+ | 10x+ | ❌ NO |

*base first-load downloads ~140MB from HF Hub. Subsequent loads are fast (<2s).

## Model Size & Memory

| Model | Disk | RAM (peak) |
|-------|------|------------|
| tiny | ~150MB | ~400MB |
| base | ~290MB | ~500MB |
| small | ~950MB | ~1.5GB+ |

## Recommendation

Use `tiny` for real-time voice agents on ARM64. Quality is good enough for Turkish conversation.
If budget allows, Deepgram Nova-2 offers sub-second latency with better quality at $0.0059/min ($200 free credit).

## Testing Command

```python
import time, numpy as np
from faster_whisper import WhisperModel

audio = np.zeros(16000 * duration_seconds, dtype=np.float32)
model = WhisperModel("tiny", device="cpu", compute_type="auto")
t0 = time.time()
segments, info = model.transcribe(audio, language="tr", beam_size=5)
elapsed = time.time() - t0
ratio = elapsed / duration_seconds
print(f"Ratio: {ratio:.1f}x {'✅' if ratio < 1.5 else '❌'}")
```
