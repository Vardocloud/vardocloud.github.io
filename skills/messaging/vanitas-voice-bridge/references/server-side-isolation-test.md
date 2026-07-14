# Server-Side Isolation Test — Full-Duplex Pipeline Verification

## Purpose

When full-duplex "hiç cevap vermiyor" (no response at all), this test isolates the server pipeline
from the browser frontend. It sends a real Turkish speech PCM file directly to the Python WebSocket
server, bypassing the browser, the Node.js proxy, and all frontend audio capture code.

**If this test passes (transcription + LLM response + TTS audio received), the server is proven working.**
The problem is then 100% in the browser's audio capture (ScriptProcessor, AudioContext, getUserMedia).

## Prerequisites

```bash
pip install edge-tts websockets
# ffmpeg must be installed
```

## Step 1: Generate Turkish speech test file

```bash
python3 -c "
import asyncio, edge_tts
async def main():
    text = 'Merhaba Vanitas, nasılsın bugün?'
    communicate = edge_tts.Communicate(text, 'tr-TR-EmelNeural')
    await communicate.save('/tmp/test_speech.mp3')
asyncio.run(main())
"

# Convert to 16kHz mono PCM s16le
ffmpeg -y -i /tmp/test_speech.mp3 -acodec pcm_s16le -ac 1 -ar 16000 -f s16le /tmp/test_speech.pcm
```

## Step 2: Send PCM through Python WebSocket

```python
#!/usr/bin/env python3
"""Test full-duplex STT with real Turkish speech PCM."""
import asyncio, websockets, time

async def test():
    url = "ws://127.0.0.1:8765?language=tr&voice=Maya"
    
    async with websockets.connect(url) as ws:
        # Read PCM
        with open('/tmp/test_speech.pcm', 'rb') as f:
            pcm = f.read()
        print(f"Loaded {len(pcm)} bytes PCM")
        
        # Wait for session_start
        msg = await ws.recv()
        print(f"<- {msg[:80]}")
        
        # Stream audio in chunks
        chunk_size = 3200  # 100ms at 16kHz
        for i in range(0, len(pcm), chunk_size):
            await ws.send(pcm[i:i+chunk_size])
            await asyncio.sleep(0.05)
        
        # Trailing silence for VAD end detection
        for _ in range(10):
            await ws.send(b'\x00\x00' * 1600)
            await asyncio.sleep(0.2)
        
        # Collect responses
        start = time.time()
        while time.time() - start < 15:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
                if isinstance(msg, bytes):
                    print(f"<- BIN {len(msg)}b (TTS audio)")
                else:
                    print(f"<- TEXT: {msg[:300]}")
            except asyncio.TimeoutError:
                await ws.send(b'\x00\x00' * 1600)

asyncio.run(test())
```

## Expected Output (SUCCESS)

```
<- {"type": "session_start"}
<- {"type": "user_speech_start"}
<- {"type": "transcription", "final_text": "", "non_final_text": "Mer"}
<- {"type": "transcription", ..., "non_final_text": "Merhaba Vanitas, nasılsın bugün?"}
<- {"type": "user_speech_end"}
<- {"type": "transcription", "final_text": "Merhaba Vanitas, nasılsın bugün?", ...}
<- {"type": "llm_response", "text": "İyi misin canım? ..."}
<- BIN 16384b (TTS audio)
<- BIN 12288b (TTS audio)
...
```

If you see `transcription` with growing Turkish text, `llm_response` with a reply, and TTS audio chunks → **server pipeline is PERFECT.**

## Expected Output (FAILURE — server problem)

```
<- {"type": "session_start"}
<- {"type": "user_speech_start"}
<- {"type": "user_speech_end"}
(t/o)
(t/o)
...
```

No `transcription` messages at all → **STT is not producing tokens.** Check Soniox API key, STT model name, network connectivity.

## Common Failure Patterns

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| No `transcription` at all | STT `_receive_task_handler` crashed silently | Check `stt.py` — `content.get("tokens")` not `content["tokens"]` |
| `transcription` with empty text | STT receives audio but doesn't understand | Wrong audio format? Check 16kHz mono PCM s16le |
| `transcription` works, no `llm_response` | LLM not triggered | Check `llm.py` — needs `UserSpeechEndMessage` or `TranscriptionEndpointMessage` |
| `llm_response` works, no BIN audio | TTS API key missing | Check `SONIOX_API_KEY_TTS` in env/.env |
| Binary TTS chunks but too small (<100 bytes) | LLM generated very short text | Prompt issue or Groq returned placeholder |
