# Silent Session Diagnosis — "Konuşuyorum ama cevap yok" — 18 Tem 2026

## Symptom
User clicks "Konuşmayı Başlat", talks into microphone, but gets no response. UI shows "Bağlandı, konuşabilirsin" but nothing happens.

## Key Distinction: Silent vs Echo Loop

- **Echo loop:** VAD triggers 10+ times/minute (TTS feedback). Log shows `User speech start detected - cancelling LLM generation` repeatedly.
- **Silent session:** VAD triggers 0 times. STT produces 0 tokens. Session JSON: `status: "silent"`, `vad_events: {speech_starts: 0}`.

## Diagnosis Procedure

### Step 1: Check Latest Session JSON
```bash
ls -lt /tmp/vanitas-test-logs/ | head -5
cat /tmp/vanitas-test-logs/<latest_session_id>/session.json | python3 -m json.tool
```

### Step 2: Analyze mic.wav Peak/RMS
```python
import wave, struct, math
w = wave.open('/tmp/vanitas-test-logs/<sid>/mic.wav', 'r')
frames = w.readframes(w.getnframes())
w.close()
samples = struct.unpack(f'<{len(frames)//2}h', frames)
peak = max(abs(s) for s in samples)
rms = math.sqrt(sum(s*s for s in samples)/len(samples))
print(f'peak={peak}/32768 ({peak/32768*100:.2f}%), rms={rms:.1f}')
```

- Normal: peak 1000-5000+ (3-15%), rms 100+
- Silent: peak <200 (<0.6%), rms <10

### Step 3: Server-Side Isolation Test
Send edge-tts Turkish PCM directly to ws://127.0.0.1:8765. If server responds → frontend is the problem.

### Step 4: Root Causes (18 Tem 2026)

| # | Root Cause | Fix |
|---|-----------|-----|
| 1 | AudioContext 48kHz + manual downsample → peak 0.43% | `new AudioContext({ sampleRate: 16000 })` |
| 2 | noiseSuppression/autoGainControl true on mobile | Set false (only Firefox: true) |
| 3 | Cloudflare tunnel corrupts binary WebSocket frames | Use Tailscale Funnel |
| 4 | MetricsMessage AttributeError → session crash 1005 | Add @property to MetricsMessage |