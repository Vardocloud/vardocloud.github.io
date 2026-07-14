# Colab GPU Bridge Setup Guide

## Overview

Connect Hermes server to Google Colab's T4 GPU for Whisper transcription.

**Why:** Local CPU is slow; Colab T4 is fast and free (user already uses it).

## Architecture

```
HERMES SERVER (Ubuntu)          GOOGLE COLAB (User's Browser)
     │                                   │
     │  POST /transcribe                 │
     │  ├── audio file                   │
     │  │                               │
     │  │                         Faster-Whisper Large-v3
     │  │                         T4 GPU (~1-2s per chunk)
     │  │                               │
     │  ◄── JSON: {text, segments}      │
     │                                   │
     └───────── Ngrok Tunnel ────────────┘
           (https://random.ngrok.io)
```

## Colab Notebook Setup (User Does This)

### Step 1: Install Dependencies

```python
!pip -q install fastapi uvicorn faster-whisper pyngrok python-multipart
```

### Step 2: Start Server (Run This Cell)

```python
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
from pyngrok import ngrok
import tempfile
import os

# Setup ngrok
ngrok.set_auth_token("YOUR_NGROK_AUTHTOKEN")
tunnel = ngrok.connect(8000)
public_url = tunnel.public_url
print(f"🚀 Server URL: {public_url}")
print(f"📝 POST to: {public_url}/transcribe")
print(f"📝 Health check: {public_url}/ping")

# Load Whisper model (T4 GPU)
from faster_whisper import WhisperModel
print("Loading Whisper Large-v3 on T4...")
model = WhisperModel("large-v3", device="cuda", compute_type="float16")
print("Model ready!")

# FastAPI app
app = FastAPI()

@app.get("/ping")
async def ping():
    return {"status": "ok", "time": time.time()}

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    # Transcribe
    segments, info = model.transcribe(
        tmp_path,
        language="tr",
        beam_size=5,
        vad_filter=True
    )
    
    # Cleanup
    os.unlink(tmp_path)
    
    # Return result
    return JSONResponse({
        "text": " ".join([s.text for s in segments]),
        "language": info.language,
        "segments": [{"start": s.start, "end": s.end, "text": s.text} for s in segments]
    })

# Start server
uvicorn.run(app, port=8000, log_level="info")
```

### Step 3: Keep Cell Running

- **DON'T close the browser tab** — Colab idles when tab is closed
- **Keep laptop awake** or use [Colab Keep Alive](https://github.com/W是一/ColabAlive) tricks
- If disconnected: reconnect and re-run cell (new ngrok URL each time)

## Server-side Client (Python)

### transcribe-client.py

```python
import requests
import os
import time

class ColabTranscriber:
    def __init__(self, colab_url):
        self.url = colab_url.rstrip('/')
        self.transcribe_url = f"{self.url}/transcribe"
        self.ping_url = f"{self.url}/ping"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'meet-bot/1.0'
        })
    
    def health_check(self, timeout=5):
        """Check if Colab is still connected"""
        try:
            r = self.session.get(self.ping_url, timeout=timeout)
            return r.status_code == 200
        except:
            return False
    
    def transcribe(self, audio_path, timeout=30):
        """Send audio file, return transcript"""
        if not self.health_check():
            print("[COLAB] Connection lost, skipping...")
            return None
        
        try:
            with open(audio_path, 'rb') as f:
                r = self.session.post(
                    self.transcribe_url,
                    files={'file': f},
                    timeout=timeout
                )
            
            if r.status_code == 200:
                return r.json()
            else:
                print(f"[COLAB] Error {r.status_code}: {r.text}")
                return None
        except Exception as e:
            print(f"[COLAB] Exception: {e}")
            return None

# Usage
colab = ColabTranscriber("https://abc123.ngrok.io")
result = colab.transcribe("/tmp/chunk.wav")
if result:
    print(result['text'])
```

## Troubleshooting

### Colab Disconnects (15 min idle)

**Symptom:** `health_check()` returns False

**Solution:** 
- Re-run notebook cell
- Get new ngrok URL
- Update server config

### Ngrok URL Changes

**Every reconnection = new URL**

Workarounds:
1. Use ngrok paid plan (fixed subdomain)
2. Store URL in shared location (Telegram bot message, Google Doc)
3. Manual update before each meeting

### Memory Issues

Colab T4 has 16GB VRAM. Whisper Large-v3 fits comfortably.

If OOM:
```python
model = WhisperModel("large-v3", device="cuda", compute_type="int8")
```

## Alternative: Groq API (Limited)

| Metric | Value |
|--------|-------|
| Free tier | 8.5 hours/month |
| Per meeting (1hr) | 1 hour |
| Per week (5 meetings) | 5 hours |
| Needed | ~20 hours/month |

**Verdict:** Insufficient.

## Alternative: Local Whisper CPU

If Colab unavailable, fallback to:

```python
model = WhisperModel("medium", device="cpu", compute_type="int8")
# Slower but works without internet
```

## Ngrok Setup

1. Sign up at https://ngrok.com
2. Get authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
3. Use free tier (1 concurrent tunnel, 3 connections/hour)

Free tier limitations:
- URL changes every reconnect
- 3-hour session limit
- Sufficient for most meetings