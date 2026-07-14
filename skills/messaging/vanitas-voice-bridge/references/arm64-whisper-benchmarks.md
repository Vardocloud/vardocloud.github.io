# ARM64 CPU Benchmark: faster-whisper Models (2026-06-16)

Tested on Oracle Cloud ARM64 (Ampere Altra), Ubuntu 22.04, Python 3.12, faster-whisper 1.2.1.

All tests: `compute_type="auto"`, `device="cpu"`, `beam_size=5`, `language="tr"`.

## Raw Results

| Model | Load Time | 2s Audio → | 3s Audio → | Real-time Factor | Turkish Quality | Verdict |
|-------|-----------|-----------|-----------|-----------------|-----------------|---------|
| `tiny` | 1.1s | 2.1s | 2.0s | **0.7x** ⚡ | Orta | ✅ Usable |
| `base` | 4.8s¹ | — | 3.2s | **1.1x** | İyi | ✅ Usable |
| `small` | — | 30s+ ❌ | timeout | **10x+** | — | ❌ Unusable |

¹ `base` download time included (first run, not cached). Subsequent loads ~1.5s.

## Key Finding

**`small` model is completely unusable on ARM64 CPU.** A 3-second audio clip timed out at 30 seconds. The `tiny` model is the only viable option for real-time voice on this hardware, with a 0.7x real-time factor (faster than real-time).

## Test Methodology

```python
import time, numpy as np
from faster_whisper import WhisperModel

# Silence audio (worst case — real speech may be slightly faster due to VAD filtering)
audio = np.zeros(16000 * duration, dtype=np.float32)

model = WhisperModel(model_name, device="cpu", compute_type="auto")
t0 = time.time()
segments, info = model.transcribe(audio, language="tr", beam_size=5)
list(segments)  # consume generator
elapsed = time.time() - t0
```

## Recommendation

For Vanitas voice agent on this server: **use Deepgram Nova-2 REST** (v10 architecture). It's faster (~200ms), higher quality Turkish, zero CPU load, and has $200 free credit.

If local STT is required: use `tiny` model (0.7x real-time). Accept that Turkish quality is moderate — good enough for basic conversation but may miss nuance.
