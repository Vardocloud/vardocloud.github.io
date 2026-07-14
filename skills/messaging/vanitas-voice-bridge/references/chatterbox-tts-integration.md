# Chatterbox TTS Integration (Resemble AI)

**Model:** Chatterbox Multilingual V3  
**Framework:** 🤗 Transformers + custom decoder  
**Size:** 500M params  
**License:** MIT  
**Languages:** 23 (Arabic, Danish, German, Greek, English, Spanish, Finnish, French, Hebrew, Hindi, Hungarian, Indonesian, Italian, Japanese, Korean, Dutch, Polish, Portuguese, Romanian, Russian, Swedish, Turkish, Chinese)  
**Source:** https://github.com/resemble-ai/chatterbox  
**HF Hub:** https://huggingface.co/ResembleAI/chatterbox  
**Stars:** 25.2k ⭐ | **Forks:** 3.4k  
**Latest release:** v0.1.2 (Jun 13, 2025) / V3 checkpoint (Jun 10, 2026)

## Architecture Overview

Chatterbox is a family of TTS models by Resemble AI:
- **Chatterbox Multilingual V3** (500M) — Recommended for Turkish. 23 languages, zero-shot voice cloning, accent preservation across languages.
- **Chatterbox-Turbo** (350M) — English-only, low-latency (~200ms), paralinguistic tags (`[laugh]`, `[cough]`). **Not suitable for Turkish.**
- **Single Language Pack** (500M each) — Dedicated finetunes for Chinese, Latam Spanish, Brazilian Portuguese, Spain Spanish, Portuguese, Hindi.

## Setup

### Installation
```bash
pip install chatterbox-tts
```

⚠️ `pip install chatterbox` (without `-tts`) FAILS — package is named `chatterbox-tts` on PyPI.

### Dependencies Installed
- torch 2.6.0
- torchaudio 2.6.0
- transformers 5.2.0
- gradio 6.8.0
- diffusers 0.29.0
- librosa 0.11.0
- huggingface-hub 1.21.0
- soundfile, soxr, einops, conformer, safetokens, etc.

Total install size: ~3-4GB (mostly torch + CUDA libs even on CPU)

### First Run
```python
import torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

device = "cpu"  # or "cuda" / "mps"
model = ChatterboxMultilingualTTS.from_pretrained(device=device)

text = "Merhaba, ben Vanitas."
wav = model.generate(text, language_id="tr")
ta.save("/tmp/output.wav", wav, model.sr)
```

First load downloads the model checkpoint from Hugging Face (~500MB). Cached at `~/.cache/huggingface/` after first run.

## Turkish Language Support

### Language ID
Use `language_id="tr"` in `model.generate()`. Available language codes: `ar`, `da`, `de`, `el`, `en`, `es`, `fi`, `fr`, `he`, `hi`, `hu`, `id`, `it`, `ja`, `ko`, `nl`, `pl`, `pt`, `ro`, `ru`, `sv`, `tr`, `zh`.

### Voice Cloning (Zero-Shot)
Chatterbox can clone a voice from a reference audio and speak in any supported language:

```python
wav = model.generate(
    text="Ben Vanitas, sizinle tanıştığıma memnun oldum.",
    language_id="tr",
    audio_prompt_path="/path/to/reference.wav"  # 5-30sn temiz ses kaydı
)
```

**⚠️ IMPORTANT:** En iyi sonuç için referans ses HEDEF DİLDE olmalı. Yabancı bir sesi (örn. İngiliz) alıp Türkçe konuşturunca, kaynak sesin aksanı Türkçe'ye taşınır (accent preservation). Türkçe referans sesle çok daha doğal sonuç alınır.

### V3 Improvements Over V2
- ✅ Improved speaker similarity (accent preservation across languages)
- ✅ Reduced hallucinations (unwanted continuation, repetition)
- ✅ More natural, conversational speech
- ✅ More consistent multilingual output

## Performance

### System Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 4GB | 8GB+ |
| GPU | — | NVIDIA CUDA / Apple MPS |
| Disk | 2GB free | 5GB free (models + deps) |
| Python | 3.10 | 3.11 |

### CPU Inference Speed (Tested 27 Haz 2026)
Tested on Intel i7-12650H (16 cores, 7.6GB RAM, no GPU):

| Metric | Result |
|--------|--------|
| Model load (first time) | ~30-60s (includes HF download, ~500MB) |
| Generation (10 kelime) | **89 saniye** (1000 token üzerinden 96 token'da EOS) |
| RAM usage | ~4-6GB |
| Per-token speed | ~2.3 it/s (CPU) |

**⚠️ CPU'da gerçek zamanlı kullanım için çok yavaş (89sn).** GPU şart.

### GPU Inference Speed (Estimated)
| GPU | Expected Latency |
|----|-----------------|
| NVIDIA T4 (Replicate) | ~1-3s |
| NVIDIA A100/H100 | ~0.5-1s |
| Apple MPS | ~2-5s |
| CPU (tested 27 Haz) | ❌ 89s — unusable |

### Bulut/API Seçenekleri

#### 🆓 HuggingFace Spaces API (ÜCRETSİZ — ÖNERİLEN)
Chatterbox Multilingual V3 Space'i **tamamen ücretsiz** kullanılabilir. GPU'da çalışır, hızlıdır.

- **Space URL:** https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS-V3
- **Gradio API:** `https://resembleai-chatterbox-multilingual-tts-v3.hf.space/gradio_api/call/`
- **Ücret:** 🆓 **Sıfır** — HF Spaces ücretsiz tier'da çalışır (rate limit var)
- **Hız:** GPU'da ~1-5sn (CPU'ya gerek yok, Space'in kendi GPU'su var)
- **API key:** Gerekmez — herkese açık Gradio API
- **Rate limit:** HF Spaces standart kısıtlamaları geçerlidir

##### Kullanım (Python — requests)
```python
import requests, json

base = "https://resembleai-chatterbox-multilingual-tts-v3.hf.space"

# 1. Önce dil değiştir (default referans sesini güncelle)
r = requests.post(base + "/gradio_api/call/on_language_change", json={
    "data": ["tr", None, "Merhaba test"]
})
event_id = r.json()["event_id"]
r = requests.get(f"{base}/gradio_api/call/on_language_change/{event_id}", timeout=60)
# data'dan referans ses objesini al
import re
data_match = re.search(r"data: (\[.*\])", r.text, re.DOTALL)
ref_audio = json.loads(data_match.group(1))[0]

# 2. TTS üret
tts_payload = {
    "data": [
        "Merhaba, ben Vanitas. Sizinle konuşmak çok güzel.",
        ref_audio,  # referans ses objesi (None da dene)
        "tr",
        0.5,   # exaggeration
        0.8,   # temperature
        42,    # seed
        0.5    # cfg_weight
    ]
}
r = requests.post(base + "/gradio_api/call/generate_tts_audio", json=tts_payload)
event_id = r.json()["event_id"]
r = requests.get(f"{base}/gradio_api/call/generate_tts_audio/{event_id}", timeout=120)
# SSE'den audio URL'yi bul
audio_match = re.search(r'"url":\s*"([^"]+)"', r.text)
audio_url = audio_match.group(1)
# İndir
audio_data = requests.get(audio_url).content
with open("output.wav", "wb") as f:
    f.write(audio_data)
```

##### Voice Cloning
`ref_audio` parametresine kendi ses dosyanı (`path` + `meta._type: "gradio.FileData"`) göndererek voice cloning yapabilirsin. Önce ses dosyasını HF Space'e yüklemek gerekebilir.

##### Mevcut API Fonksiyonları
| Fonksiyon | Parametreler | Açıklama |
|-----------|-------------|----------|
| `/on_language_change` | language_id, current_ref_wav, current_text | Default sesi dile göre günceller |
| `/generate_tts_audio` | text_input, audio_prompt_path_input, language_id_input, exaggeration_input, temperature_input, seed_num_input, cfgw_input | TTS üretir |
| `/update_char_count` | text | Karakter sayısını günceller |

##### Desteklenen Diller
```
en, ar, da, de, el, es, fi, fr, he, hi, it, ja, ko, ms, nl, no, pl, pt, ru, sv, sw, tr, zh
```

##### Sınırlamalar
- Text max **300 karakter**
- Rate limit: HF Spaces kaynak sınırlamaları
- Queue: HF Spaces sıraya alabilir (yoğunlukta bekleme)
- Ücretsiz: garantili uptime veya SLA yok

#### Replicate API
Chatterbox Multilingual Replicate'te mevcut:
- **URL:** https://replicate.com/resemble-ai/chatterbox-multilingual
- **Cost:** ~**$0.0074/run** (çok ucuz, ~1350 run/$10)
- **Free credits:** Yeni kullanıcılara ~$5-10 ücretsiz kredi (GitHub ile giriş)
- **Parameters:** text (max 300 chars), language, reference_audio, exaggeration, temperature, cfg_weight, seed
- **Voice cloning:** `reference_audio` parametresiyle destekleniyor
- **Speed:** GPU'da ~1-3sn
- **Limitation:** max 300 karakter

##### Replicate Billing Troubleshooting
Test edildi (27 Haz 2026): `r8_` prefiksli API key ile **HTTP 402 Insufficient Credit** hatası alındı.

**Fix:** replicate.com hesabında **Settings → Billing** sayfasına kredi kartı tanımlamak gerekir. Ücretsiz $5-10 kredi genelde kart doğrulaması sonrası aktif olur. Karttan çekim yapılmaz (sadece doğrulama). Eğer kullanıcı kart tanımlamak istemezse → Pinokio + lokal GPU alternatifi kullanılır.

#### Pinokio AI App
Chatterbox Pinokio üzerinden tek tıkla kurulabilir:
- **URL:** https://beta.pinokio.co/apps/github-com-pierrunoyt-chatterbox-tts-app
- **App:** PierrunoYT/chatterbox-tts-app (Gradio arayüzlü)
- **Includes:** Turbo, Multilingual (23+ dil), Original modelleri
- **Requires:** Windows + GPU (CPU'da çalışır ama yavaş)

## Known Limitations

| Limitation | Impact |
|------------|--------|
| CPU inference slow (10-30s/cümle) | Real-time kullanım için GPU gerekli |
| Heavy dependencies (torch ~2GB+) | İlk kurulum uzun, disk alanı gerekli |
| Default demo sesi zayıf | HF Space'teki demo eski checkpoint olabilir |
| Voice cloning aksan koruması | Hedef dilde referans yoksa aksanlı çıktı |
| V3 çok yeni (10 Haz 2026) | Community feedback sınırlı |

## Integration with Vanitas

### As Hermes TTS Provider
Chatterbox could replace ElevenLabs / Edge TTS as a local, free TTS provider. Integration approach:

1. Self-host API wrapper (FastAPI endpoint) using `chatterbox-tts-api` (travisvn/chatterbox-tts-api on GitHub)
2. Add as Hermes custom provider in config.yaml
3. Voice cloning with Edel's voice (or chosen reference voice)

### Voice Cloning Candidates (Turkish)
Edel's suggestion: **Derya Pınar Ak** (Turkish actress, b. 2003). Would need:
- 5-30sn clean audio sample (no background noise, natural speech)
- Ideally from interview/IG story, not acted performance
- Noise removal before using as reference

## Comparison with Other TTS Options

| Metric | Chatterbox V3 | Edge TTS (Emel) | ElevenLabs | Meta MMS-TTS |
|--------|--------------|-----------------|------------|-------------|
| Cost | 🆓 MIT | 🆓 Free | 💰 $5/100K | 🆓 CC-BY-NC |
| Turkish quality | ⭐⭐⭐ V3 yeni | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Voice cloning | ✅ Zero-shot | ❌ | ✅ $ | ❌ |
| GPU needed | ⚠️ CPU yavaş | ❌ Cloud | ❌ Cloud | ❌ CPU |
| Privacy | ✅ Local | ❌ Cloud | ❌ Cloud | ✅ Local |
| Latency | 🐢 10-30s (CPU) | ⚡ 0.8s | ⚡ ~75ms | 🐢 ~1.5s |

## Resources
- GitHub: https://github.com/resemble-ai/chatterbox
- HF Demo (V3): https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS
- HF Model: https://huggingface.co/ResembleAI/chatterbox
- Dev API Server: https://github.com/devnen/Chatterbox-TTS-Server
- OpenAI-compat API: https://github.com/travisvn/chatterbox-tts-api
- Resemble AI page: https://www.resemble.ai/learn/models/chatterbox
- Audio samples (23 lang): https://www.youtube.com/watch?v=GOfRG0Byaa0
