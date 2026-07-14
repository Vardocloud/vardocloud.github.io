# Piper TTS Integration (2026-06-24)

## Overview
Piper TTS is a fast, local neural TTS system. Runs on CPU (no GPU needed). ONNX-based, MIT license (but some voice models have different licenses).

## Installation

```bash
pip install piper-tts
```

## Turkish Models

3 Turkish voices available at HuggingFace:
`https://huggingface.co/rhasspy/piper-voices/tree/v1.0.0/tr/tr_TR/`

| Voice | Gender | Quality | Sample Rate | Params | License |
|-------|--------|---------|-------------|--------|---------|
| dfki | 🤷 Muhtemelen kadın | medium | 22.05KHz | ~15-20M | CC BY-NC-SA 4.0 |
| fettah | 🚹 Erkek | medium | 22.05KHz | ~15-20M | ? |
| fahrettin | 🚹 Erkek | medium | 22.05KHz | ~15-20M | ? |

**⚠️ dfki is CC BY-NC-SA 4.0 (non-commercial).** Cannot use in commercial products.

## Download Model

```bash
mkdir -p ~/voice-agent-venv/piper_models
cd ~/voice-agent-venv/piper_models

# dfki (female-ish, non-commercial)
curl -sL -o tr_TR-dfki-medium.onnx \
  "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/tr/tr_TR/dfki/medium/tr_TR-dfki-medium.onnx"
curl -sL -o tr_TR-dfki-medium.onnx.json \
  "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/tr/tr_TR/dfki/medium/tr_TR-dfki-medium.onnx.json"
```

## Usage (Python)

```python
from piper import PiperVoice
import wave

voice = PiperVoice.load("piper_models/tr_TR-dfki-medium.onnx")

wav_path = "/tmp/output.wav"
wav = wave.open(wav_path, "w")
wav.setnchannels(1)
wav.setsampwidth(2)
wav.setframerate(22050)

for chunk in voice.synthesize("Merhaba Edel, ben Vanitas"):
    wav.writeframes(chunk.audio_int16_bytes)

wav.close()
```

**Key API notes:**
- `voice.synthesize()` returns a **generator of AudioChunk objects**
- Each chunk has `.audio_int16_bytes` → raw PCM Int16 data
- Also available: `.audio_int16_array` (numpy), `.audio_float_array`
- Sample rate is fixed per model (22.05KHz for medium quality)

## Integration with v12

Piper can replace Edge TTS as fallback when no internet:

```python
async def text_to_speech(text: str) -> bytes:
    """TTS with Edge TTS primary, Piper fallback."""
    if internet_available:
        return await edge_tts_fallback(text)
    return await piper_tts_local(text)

async def piper_tts_local(text: str) -> bytes:
    """Synchronous but wrapped in executor."""
    loop = asyncio.get_event_loop()
    def _run():
        import io, wave
        buf = io.BytesIO()
        wav = wave.open(buf, "w")
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(22050)
        for chunk in PIPER_VOICE.synthesize(text):
            wav.writeframes(chunk.audio_int16_bytes)
        wav.close()
        return buf.getvalue()
    return await loop.run_in_executor(None, _run)
```

## Performance

- ~4.5s speech generated in <1s on CPU
- 61MB ONNX model file (medium quality)
- No internet needed after model download
- Voice is less natural than Edge TTS (espeak-based phoneme synthesis)
