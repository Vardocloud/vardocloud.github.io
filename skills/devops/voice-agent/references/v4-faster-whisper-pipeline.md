# v4 Pipeline: faster-whisper (lokal) + Hermes + Pollinations Bella

## Mimari

```
Tarayıcı (PCM Int16 24kHz) → WebSocket → VAD → faster-whisper (16kHz) → Hermes API → Pollinations TTS → PCM → Tarayıcı
```

## faster-whisper Kurulum

```bash
pip install faster-whisper numpy
```

```python
from faster_whisper import WhisperModel
model = WhisperModel("small", device="cpu", compute_type="int8")
```

Model boyutları: tiny (150MB), small (500MB), medium (1.5GB), large-v3 (3GB). CPU'da int8 ile çalışır.

## Ses Dönüşümü (24kHz Int16 → 16kHz float32)

```python
import numpy as np

def pcm_to_whisper(int16_data: bytes, src_rate=24000, dst_rate=16000) -> np.ndarray:
    """Tarayıcıdan gelen Int16 PCM'i faster-whisper için float32 16kHz'e çevir"""
    samples = np.frombuffer(int16_data, dtype=np.int16).astype(np.float32) / 32768.0
    if src_rate == dst_rate:
        return samples
    duration = len(samples) / src_rate
    target_len = int(duration * dst_rate)
    indices = np.linspace(0, len(samples) - 1, target_len)
    return np.interp(indices, np.arange(len(samples)), samples)
```

## VAD (Voice Activity Detection)

```python
class VAD:
    def __init__(self, sample_rate=24000, threshold=0.015, silence_ms=600, min_utterance_ms=300):
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.silence_samples = int(silence_ms * sample_rate / 1000)
        self.min_utterance_samples = int(min_utterance_ms * sample_rate / 1000)
        self.buffer = []
        self.silence_count = 0
        self.is_speaking = False
        self.utterance_samples = 0
    
    def add_samples(self, samples: np.ndarray):
        """Returns (utterance_array or None, is_speaking)"""
        self.buffer.append(samples)
        energy = np.sqrt(np.mean(samples ** 2))
        
        if energy > self.threshold:
            self.is_speaking = True
            self.silence_count = 0
            self.utterance_samples += len(samples)
        elif self.is_speaking:
            self.silence_count += len(samples)
        
        if self.is_speaking and self.silence_count >= self.silence_samples:
            utterance = np.concatenate(self.buffer)
            self.buffer = []
            self.is_speaking = False
            self.silence_count = 0
            if self.utterance_samples >= self.min_utterance_samples:
                self.utterance_samples = 0
                return utterance, False
            self.utterance_samples = 0
        
        return None, self.is_speaking
```

## Pollinations TTS (ElevenLabs Bella)

```python
async def tts_speak(text: str) -> bytes:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://gen.pollinations.ai/v1/audio/speech",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "elevenlabs", "input": text, "voice": "bella",
                  "response_format": "pcm", "speed": 1.0},
        )
        if resp.status_code == 200:
            return resp.content
        # Fallback: openai-audio + nova
        resp2 = await client.post(
            "https://gen.pollinations.ai/v1/audio/speech",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "openai-audio", "input": text, "voice": "nova",
                  "response_format": "pcm"},
        )
        return resp2.content
```

## Tarayıcı PCM Oynatma

```javascript
async function playPCM(buffer) {
  const int16 = new Int16Array(buffer);
  const float32 = new Float32Array(int16.length);
  for (let i = 0; i < int16.length; i++) float32[i] = int16[i] / 32768.0;
  
  const audioBuffer = audioCtx.createBuffer(1, float32.length, 24000);
  audioBuffer.getChannelData(0).set(float32);
  
  const source = audioCtx.createBufferSource();
  source.buffer = audioBuffer;
  source.connect(audioCtx.destination);
  source.start(0);
}
```

## Referans Kod

- `/home/ubuntu/voice-agent-venv/voice_agent_v4.py` — Tam implementasyon
- `/home/ubuntu/voice-agent-venv/voice_agent_v3.py.bak` — v3 (Deepgram STT, başarısız)
- `/home/ubuntu/voice-agent-venv/voice_agent_v2.py.bak` — v2 (Deepgram Agent API)

## Sürüm Karşılaştırması

| Sürüm | STT | TTS | LLM | Durum |
|-------|-----|-----|-----|-------|
| v2 | Deepgram Agent | Deepgram Aura-2 | Deepgram/OpenRouter | ❌ İngilizce aksan |
| v3 | Deepgram STT WS | ElevenLabs Bella | Hermes | ❌ Timeout/parametre |
| v4 | faster-whisper | ElevenLabs Bella | Hermes | ✅ %100 lokal STT |
