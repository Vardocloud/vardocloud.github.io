# Kokoro TTS Setup Reference

## Dependency Chain

Kokoro TTS (82M params, open-source) has a non-obvious dependency tree:

```
kokoro → misaki → spacy → phonemizer → espeakng_loader
                → espeakng_loader (phonemizer's espeak backend)
```

### Install Command (complete)

```bash
pip install kokoro soundfile misaki spacy phonemizer espeakng_loader
```

### What Each Package Does

| Package | Size | Role |
|---------|------|------|
| `kokoro` | 32KB (code) | Main TTS engine. 82M param model downloaded separately on first load |
| `soundfile` | ~2MB | Audio file I/O (WAV writing) |
| `misaki` | 3.6MB | Grapheme-to-phoneme: splits English text into pronounceable segments |
| `spacy` | ~50MB+ | NLP pipeline that misaki depends on for tokenization |
| `phonemizer` | ~300KB | Text-to-phoneme conversion, dispatches to espeak-ng |
| `espeakng_loader` | 10MB | **Bundled** `libespeak-ng.so` + `espeak-ng-data` — ships a fully working espeak-ng with no system-level install needed |

### Why this matters

`espeakng_loader` is a wheel-package that includes a statically-linked espeak-ng binary and its voice data. It's the only way to get phoneme generation working on systems **without root/sudo** (WSL, Docker containers, restricted environments). Without it, `misaki/espeak.py` fails with `ModuleNotFoundError: No module named 'espeakng_loader'`.

### Model Download

On first `KPipeline(lang_code='a')`, Kokoro downloads the Hexgrad/Kokoro-82M model from HuggingFace Hub:

```
Repo: hexgrad/Kokoro-82M (~300MB)
Cache: ~/.cache/huggingface/hub/models--hexgrad--Kokoro-82M/
```

Warning on first load:
```
WARNING: Defaulting repo_id to hexgrad/Kokoro-82M. Pass repo_id='hexgrad/Kokoro-82M' to suppress this warning.
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
```

Both warnings are harmless for basic usage.

### Torch Warnings (Harmless)

```
UserWarning: dropout option adds dropout after all but last recurrent layer...
FutureWarning: torch.nn.utils.weight_norm is deprecated...
```

These are Kokoro-82M model architecture warnings from PyTorch. They do not affect output quality.

### Santa Voice

Voice name is `'Santa'` — warm, slightly older male storyteller quality in English. Speed 0.95-1.0 recommended for narration.

```python
from kokoro import KPipeline
import soundfile as sf
import numpy as np

pipeline = KPipeline(lang_code='a')
generator = pipeline(text, voice='Santa', speed=0.95)

all_audio = []
for gs, ps, audio in generator:
    all_audio.append(audio)

combined = np.concatenate(all_audio)
sf.write("output.wav", combined, 24000)  # 24kHz sample rate
duration = len(combined) / 24000
print(f"Generated {duration:.1f}s of audio")
```

### Troubleshooting

| Symptom | Likely Fix |
|---------|------------|
| `No module named 'espeakng_loader'` | `pip install espeakng_loader` |
| `No module named 'phonemizer'` | `pip install phonemizer` |
| `No module named 'spacy'` | `pip install spacy` |
| `espeak-ng: command not found` | Normal — not needed; `espeakng_loader` provides the library directly |
| Model download hangs/timeout | First download is ~300MB, run with `background=true` and `timeout=300` |
