# Voiceprint Hybrid Architecture — Node.js + Python Microservice

**Created:** 1 July 2026
**Context:** v13.1 Node.js server + Python MFCC voiceprint service

## Architecture

```
Browser (PCM Int16 via AudioContext ScriptProcessor)
  → POST /api/voiceprint/verify (Node.js proxy, port 3005)
    → POST /verify (Python FastAPI, port 5050)
      → numpy MFCC extraction → cosine similarity
        ← {"is_edel": true/false, "confidence": 0.95}
  → Browser UI: "👤 Edel %95" badge
```

## Components

### 1. Python FastAPI Microservice (`voiceprint_service.py`)
- **Port:** 5050, binds 127.0.0.1
- **Endpoints:** `GET /health`, `POST /verify`, `POST /enroll`
- **Dependencies:** numpy, scipy, fastapi, uvicorn
- **MFCC:** 20-dim mean vector, Hamming window, 40 mel filters, 80-7600Hz band
- **Threshold:** cosine similarity > 0.82 = Edel
- **Files:** `edel_voiceprint.npy` (20-dim float64), `edel_voiceprint.json` (metadata)

### 2. Node.js Proxy (`server.mjs`)
- **Routes:** `POST /api/voiceprint/verify` → forward raw PCM bytes to Python `/verify`
- **Routes:** `POST /api/voiceprint/enroll` → forward raw PCM bytes to Python `/enroll`
- **CORS:** `Access-Control-Allow-Origin: *`

### 3. Browser PCM Capture (`public/index.html`)
- **AudioContext** with ScriptProcessorNode (2048 buffer, 16kHz sample rate)
- Float32 → Int16 conversion, 5-second rolling buffer (~40 chunks)
- On VAD trigger: flatten PCM buffer → POST to `/api/voiceprint/verify`
- **Fire-and-forget:** voiceprint does NOT block LLM call (runs in parallel)

## Enrollment

### From Telegram voice messages:
```bash
ffmpeg -i ~/.hermes/audio_cache/audio_XXXX.ogg -ar 16000 -ac 1 -sample_fmt s16 /tmp/edel.wav -y
python3 voiceprint_service.py  # Start service
# Then send PCM via curl:
python3 -c "
import sys, numpy as np
# Load WAV, extract PCM
from scipy.io import wavfile
sr, data = wavfile.read('/tmp/edel.wav')
if data.dtype != np.int16: data = (data * 32767).astype(np.int16)
sys.stdout.buffer.write(data.tobytes())
" | curl -s -X POST --data-binary @- http://127.0.0.1:5050/enroll --max-time 5
```

### Minimum duration: 3 seconds (48,000 samples @ 16kHz)
### Incremental: Weighted average — send more audio to refine.

## Pitfalls

- **Fire-and-forget:** Voiceprint verify asenkron çalışır (`.then()`). Eğer LLM'i bloke ederse toplam gecikme artar.
- **Çakışan getUserMedia:** SpeechRecognition + PCM capture aynı anda çalışmazsa PCM capture sessizce başarısız olur → voiceprint badge görünmez ama konuşma akışı devam eder.
- **Kısa konuşmalar:** <0.5s PCM'de voiceprint `null` döner (inconclusive).
- **Edel profili:** Mevcut `edel_voiceprint.npy` eski enrollment. Kalite artırmak için 2-3 farklı gün/ortamda kayıt ekle.
