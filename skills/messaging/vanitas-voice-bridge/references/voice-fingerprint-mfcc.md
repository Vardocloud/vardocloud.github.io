# Voice Fingerprint — MFCC-Based Speaker Verification (No PyTorch)

**Created:** 17 June 2026
**Context:** Vanitas Ses voice agent — Edel vs stranger identification

## Why MFCC Instead of Resemblyzer

Resemblyzer requires PyTorch (~800MB), too heavy for ARM64 5.8GB server.
Custom MFCC pipeline uses only `numpy` + `scipy` (~10MB), runs in <5ms per utterance.

## Architecture

```
Browser mic → PCM int16 (16kHz) → Server WS
  ├→ Soniox WS (STT + diarization)
  └→ utterance_audio bytearray (buffered for voiceprint)

On utterance flush:
  int16 bytes → float32 numpy → MFCC extraction → mean MFCC vector
  → cosine similarity vs edel_voiceprint.npy → is_edel (True/False/None)
```

## MFCC Extraction Pipeline

1. Pre-emphasis: `audio[1:] - 0.97 * audio[:-1]`
2. Frame: 512 samples (32ms), hop 160 (10ms), Hamming window
3. FFT → magnitude spectrum
4. Mel filterbank: 40 filters, 80Hz–7600Hz
5. Log + DCT type 2 → 20 MFCC coefficients
6. Liftering: `1 + 11 * sin(π * k / 22)`
7. Mean across frames → 20-dim voiceprint

## Enrollment

```bash
cd /home/ubuntu/voice-agent-venv
./bin/python3 voiceprint_enroll.py edel_ses.wav
# → edel_voiceprint.npy (20-dim float64)
```

Requirements: 30+ seconds of Edel speaking naturally, 16kHz mono WAV.
Quality score: inverse of within-speaker MFCC variance (higher = cleaner enrollment).

## Verification

```python
def verify_voiceprint(pcm_bytes: bytes) -> bool | None:
    vp = np.load("edel_voiceprint.npy")
    audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    if len(audio) < 8000:  # < 0.5s
        return None  # inconclusive
    mfcc_mean = _extract_mfcc_mean(audio)
    sim = np.dot(vp, mfcc_mean) / (norm(vp) * norm(mfcc_mean) + 1e-10)
    return sim > 0.82  # threshold
```

Threshold 0.82 was chosen empirically — balances false positives vs false negatives.

## Custom Prompt Context (18 June 2026)

A textarea above the start button lets Edel type context instructions. This gets passed via `?prompt=` query parameter on WebSocket connect. In `_handle_reply()`, every user message gets prefixed:

```python
# In ws_endpoint:
custom_prompt = ws.query_params.get("prompt", "")
# In _handle_reply:
if custom_prompt:
    msg_content = f"[BAĞLAM: {custom_prompt}] {text}"
```

The LLM sees the context before every message, shaping its behavior. Example: "Şu an arkadaşımla oturuyorum, ortamda müzik var, geyik muhabbeti yapıyoruz. Sakin ve espirili ol..."

## Incremental Enrollment (18 June 2026)

Voiceprint can be built incrementally with `--add` flag:

```bash
# First enrollment (creates edel_voiceprint.npy + edel_voiceprint.json)
./bin/python3 voiceprint_enroll.py edel_1.wav

# Add more samples later (weighted average)
./bin/python3 voiceprint_enroll.py --add edel_2.wav
./bin/python3 voiceprint_enroll.py --add edel_3.wav
```

The `edel_voiceprint.json` metadata tracks total frame count for weighted averaging:

```python
# Weighted average formula:
total_count = old_count + new_count
combined_vp = (old_vp * old_count + new_vp * new_count) / total_count
```

## Enrolling from Telegram Voice Cache

Existing Telegram voice messages (.ogg in `~/.hermes/audio_cache/`) can be used:
```bash
cd /home/ubuntu/voice-agent-venv
ffmpeg -i ~/.hermes/audio_cache/audio_XXXX.ogg -ar 16000 -ac 1 -sample_fmt s16 /tmp/edel.wav -y
./bin/python3 voiceprint_enroll.py /tmp/edel.wav
```

Best practice: 2-3 samples from different days/moods → combine with `--add` for robust coverage. Target 5000+ total MFCC frames.

## Pitfalls

- **Mixed audio:** Speaker change flush buffers may contain both speakers' audio → verification unreliable. Mitigation: clear `utterance_audio` immediately after flush.
- **Short utterances:** <0.5s audio returns `None` (inconclusive) → keeps previous `last_utterance_is_edel` value.
- **Enrollment quality:** Background noise, distance from mic, room acoustics all affect MFCC quality. Re-enroll in the actual usage environment.
- **ARM64 scipy:** `pip install scipy` may need `libopenblas-dev`. On Oracle ARM64: `apt install libopenblas-dev` first.
