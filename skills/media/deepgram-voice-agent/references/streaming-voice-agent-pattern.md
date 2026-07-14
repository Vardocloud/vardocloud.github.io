# Streaming Voice Agent Pattern (v10.6, 2026-06-16)

Natural conversation voice agent: speculative LLM + sentence-level TTS + audio interruption.

## Architecture

```
Browser Mic (16kHz PCM)
  → WebSocket → Python Server (8765)
    → Deepgram STT (interim + final)
      ├─ interim: speculative LLM warmup
      └─ final: process reply (use warmed result)
    → Hermes Proxy (8767, stream=True)
      → Hermes Gateway (8642) → Pollinations openai
    ← SSE stream tokens
  ← sentence-by-sentence TTS (ElevenLabs Bella)
  ← browser plays audio, stops on user interruption
```

## Key Patterns

### 1. Speculative LLM
Start LLM call with Deepgram INTERIM results before speech_final arrives:
```python
if transcript and not is_final and len(transcript) > 15:
    speculative_task = asyncio.create_task(llm_stream(transcript))
```
If final matches, use warmed result. Saves 1-3 seconds.

### 2. Sentence-Level TTS
Split LLM response by sentence boundary and TTS each immediately:
```python
sentences = re.split(r'(?<=[.!?…])\s+', full_response)
for s in sentences:
    audio = await tts(s)
    await safe_send(audio)  # Send to browser immediately
```
User hears first sentence while LLM generates the rest.

### 3. Audio Interruption
When user speaks during TTS playback:
- Server sends `{"type": "interrupt"}` → browser stops audio
- Server cancels current LLM stream
- New speech processed immediately

### 4. Zero Client-Side Delay
Process on `speech_final` only — no additional silence timer. Deepgram's `utterance_end_ms=1000` is sufficient.

## Critical System Prompt
For voice, single-sentence responses are critical for speed:
```
KRITIK KURAL: TEK CUMLE cevap ver. En fazla 15 kelime.
```

## Model Selection
Pollinations benchmark (2026-06-16):
- `openai`: 4.5s first request ✅ (use this)
- `openai-fast`: 23.6s ❌ (misleading name)
- `gemma`: 27s ❌
- `mistral`: 15.8s ⚠️

## Env Var Handling
When writing agent source files, use `terminal` Python heredoc to avoid file corruption:
```bash
python3 << 'PYEOF'
code = '''...'''
with open("file.py", "w") as f: f.write(code)
PYEOF
```

## Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| AudioContext 24kHz vs Deepgram 16kHz | Garbled transcriptions ("Beyin", "Susam?") | Both at 16000Hz |
| `utterance_end_ms` < 1000 | HTTP 400 from Deepgram | Use 1000ms minimum |
| Missing `nonlocal` before variable use | UnboundLocalError | `nonlocal var` at function top |
| `finally` block accesses uninitialized task | Crash on early return | Initialize `task = None`, guard with `if task:` |
| `openai-fast` model | 23s responses | Use plain `openai` |
| Progressive Pollinations throttling | 2nd+ requests 3-5x slower | Accept first-response speed as baseline |
