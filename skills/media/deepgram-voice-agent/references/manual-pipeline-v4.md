# Manual Pipeline v4 — faster-whisper (Lokal STT) + Hermes + ElevenLabs Bella (2026-06-16)

**Final working architecture.** Deepgram TAMAMEN devre dışı. STT %100 lokal (faster-whisper small).
Hiçbir dış STT API'sine bağımlılık yok. Gizlilik, hız, maliyet — hepsi avantaj.

## Mimari

```
Browser (ScriptProcessorNode, 24kHz PCM) → WS → voice_agent_v4 (8765)
                                                   ├── VAD (enerji tabanlı)
                                                   ├── faster-whisper small (lokal, 16kHz)
                                                   ├── Proxy (8767) → Hermes API (8642) → Vanitas
                                                   └── Pollinations TTS (ElevenLabs Bella, 24kHz PCM)
```

## Neden faster-whisper?

Deepgram STT ile yaşanan sorunlar (2026-06-16):
- `HTTP 400` — parametre uyumsuzluğu (`utterance_end_ms`, `no_delay`, `endpointing`)
- `1011 internal error` — timeout (bağlantı açıldı ama ses gelmedi)
- Ses formatı uyuşmazlığı (tarayıcı sample rate ≠ 24000)
- Nova-3 modeli tutarsız davranış

**Çözüm:** faster-whisper small model. Tek seferlik ~500MB indirme. Sonrası sınırsız, ücretsiz, %100 lokal.

## faster-whisper Kurulum

```bash
pip install faster-whisper numpy
```

Model ilk kullanımda otomatik iner (~9sn, HuggingFace cache):
```python
from faster_whisper import WhisperModel
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")
```

## VAD (Voice Activity Detection) — Enerji Tabanlı

```python
class VAD:
    def __init__(self, sample_rate=24000, threshold=0.015, silence_ms=600, min_utterance_ms=300):
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.silence_samples = int(silence_ms * sample_rate / 1000)
        self.min_utterance_samples = int(min_utterance_ms * sample_rate / 1000)
        self.buffer = []       # Float32 samples
        self.silence_count = 0
        self.is_speaking = False
        self.utterance_samples = 0

    def add_samples(self, samples: np.ndarray):
        """Float32 samples (-1..1) → (utterance_array | None, is_speaking)"""
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

**Parametreler:**
- `threshold=0.015`: Konuşma enerji eşiği. Sessiz ortamda düşür (0.01), gürültülüde yükselt (0.03).
- `silence_ms=600`: Cümle sonu için sessizlik süresi. Türkçe için 500-700ms ideal.
- `min_utterance_ms=300`: "Hıhı" gibi kısa sesleri filtreler.

## PCM → faster-whisper Transkripsiyon

```python
import numpy as np

WHISPER_SAMPLE_RATE = 16000

def resample_audio(samples: np.ndarray, src_rate: int, dst_rate: int) -> np.ndarray:
    """Linear interpolasyon ile yeniden örnekle"""
    if src_rate == dst_rate:
        return samples
    duration = len(samples) / src_rate
    target_len = int(duration * dst_rate)
    indices = np.linspace(0, len(samples) - 1, target_len)
    return np.interp(indices, np.arange(len(samples)), samples)

async def transcribe_audio(audio_float32: np.ndarray) -> str:
    audio_16k = resample_audio(audio_float32, 24000, 16000)
    loop = asyncio.get_event_loop()
    segments, info = await loop.run_in_executor(
        None,
        lambda: whisper_model.transcribe(audio_16k, language="tr", beam_size=5)
    )
    return " ".join(seg.text for seg in segments).strip()
```

**Gecikme:** ~1-3sn (small model, CPU, ARM64). Cümle uzunluğuna bağlı.

## Browser PCM — Sample Rate Uyuşmazlığı Çözümü

Tarayıcı `getUserMedia({sampleRate: 24000})` isteğini HER ZAMAN karşılamaz.
Gerçek sample rate'i `audioCtx.sampleRate`'ten oku, yeniden örnekle:

```javascript
const actualRate = audioCtx.sampleRate;      // Örn: 44100, 48000
const targetRate = 24000;
const ratio = actualRate / targetRate;

processor.onaudioprocess = (e) => {
    const input = e.inputBuffer.getChannelData(0);
    let outLen = Math.floor(input.length / ratio);
    const int16 = new Int16Array(outLen);
    for (let i = 0; i < outLen; i++) {
        const srcIdx = Math.floor(i * ratio);
        int16[i] = Math.max(-32768, Math.min(32767, input[srcIdx] * 32767));
    }
    ws.send(int16.buffer);
};
```

## Tam Entegrasyon: Ana Döngü

```python
async def handle_vanitas_session(browser_ws):
    vad = VAD(sample_rate=24000)
    conversation = []
    was_speaking = False

    while True:
        raw = await browser_ws.receive()
        # ... parse bytes ...
        int16_data = np.frombuffer(data, dtype=np.int16)
        float32_data = int16_data.astype(np.float32) / 32768.0

        utterance, is_speaking = vad.add_samples(float32_data)

        if is_speaking and not was_speaking:
            await browser_ws.send_text(json.dumps({"type": "user_speaking"}))
        was_speaking = is_speaking

        if utterance is not None:
            text = await transcribe_audio(utterance)
            if text:
                # LLM → TTS (arka planda, semaphore ile)
                asyncio.create_task(process_utterance(text))
```

## TTS — Pollinations ElevenLabs Bella

Deepgram Aura-2 Türkçe desteklemez. Cartesia API key yoksa **birincil tercih:**

```python
async def tts_speak(text: str) -> bytes:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://gen.pollinations.ai/v1/audio/speech",
            headers={"Authorization": f"Bearer {POLLINATIONS_API_KEY}"},
            json={"model": "elevenlabs", "input": text, "voice": "bella",
                  "response_format": "pcm", "speed": 1.0},
        )
        if resp.status_code == 200:
            return resp.content
        # Fallback: openai-audio
        resp2 = await client.post(..., json={"model": "openai-audio", "voice": "nova", ...})
        return resp2.content
```

## v3 (Deepgram) vs v4 (faster-whisper) Karşılaştırması

| Özellik | v3 (Deepgram STT) | v4 (faster-whisper) |
|---------|-------------------|---------------------|
| STT | Deepgram API (nova-3) | faster-whisper small (lokal) |
| Gizlilik | Ses Deepgram'a gider | %100 lokal |
| Ücret | API kotası | Sınırsız, ücretsiz |
| Gecikme | ~200ms | ~1-3sn |
| Bağımlılık | İnternet + API key | Sadece CPU |
| Hata modları | 400, 1011, timeout... | Model hatası (nadir) |
| Debug | Kapalı kutu | Her adım loglanabilir |

**Karar:** Her zaman v4 (faster-whisper) ile başla. Gecikme kritikse ve internet varsa v3'e geç.
