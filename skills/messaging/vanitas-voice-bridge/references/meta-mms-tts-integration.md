# Meta MMS-TTS Turkish Integration

**Model:** `facebook/mms-tts-tur`  
**Framework:** 🤗 Transformers (VITS-based)  
**Size:** 36.3M params, ~277MB download  
**License:** CC-BY-NC 4.0 (non-commercial)  
**Sample rate:** 16kHz (model output)  
**Source:** Meta AI's Massively Multilingual Speech project (arXiv 2305.13516)

## Setup

```bash
pip install transformers torch scipy
```

## Usage

### Import (transformers ≥5.x uyarısı)
⚠️ transformers v5.x `VitsModel` import yolunu değiştirdi. `from transformers import VitsModel` asılır (v5.12.1+) çünkü top-level modül tüm model sınıflarını enumerate etmeye çalışır. Doğrudan model yolunu kullan:

```python
from transformers.models.vits import VitsModel  # ✅ v5.x-safe
from transformers import AutoTokenizer
import torch, scipy.io.wavfile

model = VitsModel.from_pretrained("facebook/mms-tts-tur")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-tur")

text = "Merhaba Edel, ben Vanitas. Bugün nasilsin?"
inputs = tokenizer(text, return_tensors="pt")

with torch.no_grad():
    output = model(**inputs).waveform

scipy.io.wavfile.write("/tmp/output.wav", 
    rate=model.config.sampling_rate,
    data=output[0].numpy())
```

**İlk yükleme:** ~10-30s (277MB model indirilir). Cache ısındıktan sonra `local_files_only=True` ile tekrar çalıştır:
```python
model = VitsModel.from_pretrained("facebook/mms-tts-tur", local_files_only=True)
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-tur", local_files_only=True)
```

### Voice Activity Detection (VAD) + Silence Detection

This approach was abandoned but the lessons remain valuable:
- **Silence frames extend speech_buffer** in the \"grace period\" (within SILENCE_TIMEOUT). This is by design — brief pauses in natural speech shouldn't split utterances.
- **Must flush on disconnect.** If client disconnects mid-speech, accumulated audio is lost unless `except WebSocketDisconnect` handler calls `flush_speech()`.
- **Test with real speech patterns.** Pure sine waves or white noise don't match human speech formants. VAD mode 3 (most aggressive) works best for clean speech.
- **Session summary logging is essential for debugging:** `Session ended (VAD total:X, speech:Y, silence:Z)` helps diagnose VAD sensitivity issues.

### Web Speech API (v6-v8 — Abandoned Approach)
- **`continuous: true` causes rapid start/stop cycles** → microphone clicking sounds. Avoid for natural conversation.
- **`recognition.abort()` vs `recognition.stop()`:** `abort()` is synchronous but `onend` still fires and triggers auto-restart. Must guard with `recognitionPaused` flag.
- **Echo loop from TTS → mic → STT:** 3-layer guard needed: (1) `recognitionPaused` flag during TTS, (2) substring/startsWith match, (3) word overlap >50%.
- **`addMessage` must come AFTER guards** — otherwise duplicate visual messages appear when `onresult` fires twice.

### Hermes Auth (v6-v9)
- **Direct Hermes API calls (8642) return 401 without auth.** Always route through `vanitas_hermes_proxy.py` (8767) which reads `API_SERVER_KEY` from env.
- **Voice agent prompt should NOT duplicate Vanitas personality.** The proxy and/or Hermes inject the system prompt. Competing prompts cause identity conflicts.

### Deepgram (v2)
- **Cartesia 401 — no API key (2026-06-16):** Code had Cartesia configured but no `CARTESIA_API_KEY` in `.env` or system.
- **Edel's prompt rule:** Voice agent `think.prompt` MUST be empty. Hermes handles personality.
- **`getUserMedia` requires HTTPS** — Browsers block microphone access on plain HTTP (non-localhost).
- **BYO endpoint requires `provider.model`** — must be `groq` type with valid model name.
- **`open_ai` provider rejects BYO endpoint** — only managed models work. Use `groq` instead.
- **`think.timeout` NOT in schema** — omit it.
- Cloudflared tunnel URLs change on restart — must update TUNNEL_URL.

### Deepgram Voice Agent API Errors (Schema-Verified, 2026-06-15)

**⚠️ CRITICAL (schema-verified 2026-06-15, updated 2026-06-16):**
1. **`provider.model` is REQUIRED** even with BYO endpoint. The `ThinkSettingsV1Provider` schema mandates `model` for ALL provider types.
2. **`open_ai` provider type REJECTS BYO endpoint** — only managed models work. Use **`groq`** instead (OpenAI-compatible, endpoint mandatory).
3. **`prompt` IS valid** inside `think` per schema. **`timeout` is NOT** in the schema — omit it.
4. Use a valid Groq model name (`llama-3.3-70b-versatile`) for schema validation; your endpoint determines the actual model.
5. **For Turkish TTS, use Cartesia** via Deepgram managed integration. Deepgram native Aura voices are English-only and speak Turkish with a foreign accent. Cartesia Sonic 3.5 supports 42 languages including Turkish at native quality.
6. **Do NOT set `language` on Cartesia** — it auto-detects language from text. Explicit `language: \"tr\"` causes `FAILED_TO_SPEAKE` after 3 warnings.

## Performance

- **First load:** ~10-30s (download 277MB model)
- **Subsequent loads:** Instant (cached in `~/.cache/huggingface/`)
- **Inference:** ~1-2s per sentence (CPU, 16kHz output)
- **RAM:** ~800MB during inference
- **GPU:** Not required but supported (pass `device="cuda"`)

## Voice Characteristics

- **Type:** Single speaker, non-clonable
- **Gender:** Neutral (neither clearly male nor female)
- **Style:** Flat, documentary-style narration
- **Quality:** Good intelligibility, slightly robotic (VITS artifact)
- **Language:** Turkish-only (per-language checkpoint)

## Integration Test Results (2026-07-01)

Test script used (CPU, no GPU):

```python
import torch
import scipy.io.wavfile
from transformers.models.vits import VitsModel
from transformers import AutoTokenizer
import time

model_name = "facebook/mms-tts-tur"
print(f"Loading {model_name}...")
start = time.time()
model = VitsModel.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
print(f"Loaded in {time.time()-start:.1f}s")

text = "Merhaba, ben Vanitas. Sesli asistanınızım."
inputs = tokenizer(text, return_tensors="pt")

start = time.time()
with torch.no_grad():
    output = model(**inputs).waveform
gen_time = time.time() - start
audio_len = output.shape[-1] / model.config.sampling_rate
print(f"Generated {audio_len:.1f}s audio in {gen_time:.1f}s ({gen_time/audio_len:.1f}x real-time)")

output_path = "/tmp/vanitas_mms_test.wav"
scipy.io.wavfile.write(output_path, rate=model.config.sampling_rate, data=output[0].numpy())
print(f"Saved to {output_path}")
```

**Results:**
- Load time (cached): ~<1s
- Generation: 11.6s for ~8s text, CPU-only (no GPU)
- RTF: ~1.45x real-time on CPU
- Output: 16kHz WAV

**Edel's assessment (2026-07-01):** "Karadenizli müteahhit gibi kötü. kız ses yok mu?" — Voice is flat, neutral-to-deep, no female voice option. Single speaker model, no voice selection or cloning possible.

**Verdict: ❌ ELENDI.** Not suitable for Vanitas. No female voice, flat prosody, single speaker. Do not re-offer.

## Limitations

| Limitation | Impact |
|------------|--------|
| CC-BY-NC 4.0 | Non-commercial use only |
| Single speaker | No voice selection or cloning |
| 16kHz output | Lower than Edge TTS (24kHz) or Piper (22kHz) |
| No streaming | Full utterance processed at once |
| No emotion/pitch control | Flat prosody |
| No female voice option | Single neutral speaker |

## Benchmark (vs alternatives)

| Metric | Meta MMS-TTS | Edge TTS | Piper dfki |
|--------|-------------|----------|------------|
| Model size | 277MB | Cloud API | 61MB |
| Speed (5s text) | ~1.5s CPU | ~0.8s API | ~0.3s CPU |
| Quality | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Internet req? | ❌ No | ✅ Yes | ❌ No |
| Cost | 🆓 Free | 🆓 Free | 🆓 Free |
| Female voice? | ❌ No | ✅ Yes (EmelNeural) | ✅ Yes (dfki) |

## Known Issues

- **Transformers v5.x import hang** — `from transformers import VitsModel` hangs indefinitely on v5.12.1+. Use `from transformers.models.vits import VitsModel` instead. The top-level transformers import enumerates all model classes which causes the hang.
- Transformers `from_pretrained` may timeout on slow connections (use background download)
- `scipy.io.wavfile.write` expects numpy array, not torch tensor (use `.numpy()`)
- Model returns `waveform` as shape `(1, samples)` → index `[0]` before saving
- Cannot convert to higher sample rate — model outputs 16kHz only
