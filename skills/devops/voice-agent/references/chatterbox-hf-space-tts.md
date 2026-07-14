# Chatterbox TTS via HuggingFace Spaces (Ücretsiz)

> Keşif tarihi: 27 Haziran 2026
> Model: Chatterbox Multilingual V3 (Resemble AI, 0.5B, MIT)
> HF Space: ResembleAI/Chatterbox-Multilingual-TTS-V3
> Space URL: https://resembleai-chatterbox-multilingual-tts-v3.hf.space

## Neden Chatterbox + HF Spaces?

| Kriter | ElevenLabs (Bella) | Chatterbox HF Space |
|--------|-------------------|---------------------|
| Ücret | $5/ay | **Ücretsiz** (rate limit var) |
| Türkçe | ✅ | ✅ (23 dil) |
| Voice Cloning | ✅ (ürcretli) | ✅ (zero-shot, ücretsiz) |
| Hız | ~200-500ms | ~1-5sn (GPU'da, space yoğunluğuna bağlı) |
| Kalite | Çok iyi | V3: ElevenLabs'a yakın, V2: orta |
| Lisans | Kapalı | MIT (açık kaynak) |

**Dezavantajlar:**
- HF Space rate limit: Aşırı kullanımda "too many requests" veya GPU sırası
- Space soğuk başlatma: Uzun süre kullanılmazsa ilk istek 20-30sn sürebilir (warm-up)
- Maks 300 karakter/metin
- Gradio Space API'si resmi olmayan bir integration (değişebilir)

## API Keşfi

### Gradio API Endpoint'leri

```
# API bilgisi (tüm fonksiyonlar ve parametreler)
GET  /gradio_api/info

# Dosya upload (voice cloning için referans ses)
POST /gradio_api/upload
     files={'files': ('ref.wav', file_handle, 'audio/wav')}
     → ["/tmp/gradio/xxx/ref.wav"]

# TTS + Voice Cloning (async SSE)
POST /gradio_api/call/generate_tts_audio
     json={"data": [text, ref_audio_or_null, lang, exagger, temp, seed, cfg]}
     → {"event_id": "xxx"}

GET  /gradio_api/call/generate_tts_audio/{event_id}
     → SSE stream → complete event → JSON with audio URL

# Dil değiştirme (varsayılan referans sesi günceller)
POST /gradio_api/call/on_language_change
     json={"data": [lang, ref_audio_or_null, text]}
     → {"event_id": "xxx"}
```

### generate_tts_audio Parametreleri

| # | Parametre | Tip | Varsayılan | Açıklama |
|---|-----------|-----|-----------|----------|
| 1 | `text_input` | string | - | **Zorunlu.** Maks 300 karakter |
| 2 | `audio_prompt_path_input` | object/null | null | Referans ses (voice cloning için). `{"path": "...", "meta": {"_type": "gradio.FileData"}}` veya `None` |
| 3 | `language_id_input` | string | "en" | tr, en, fr, de, ja, ko, zh, ar, vs. (23 dil) |
| 4 | `exaggeration_input` | number | 0.5 | 0.25-2.0. Konuşma ifadesi. 0.5=nötr |
| 5 | `temperature_input` | number | 0.8 | 0.05-5.0. Rastgelelik |
| 6 | `seed_num_input` | integer | 0 | 0=rastgele, herhangi=tekrarlanabilir |
| 7 | `cfgw_input` | number | 0.5 | 0.2-1.0. CFG/Pace ağırlığı. 0=language transfer |

### Desteklenen Diller

```
en, ar, da, de, el, es, fi, fr, he, hi, it, ja, ko, ms, nl, no, pl, pt, ru, sv, sw, tr, zh
```

## Kullanım Örneği (Python)

### 1. Basit TTS (varsayılan sesle)

```python
import requests, json, re

base = "https://resembleai-chatterbox-multilingual-tts-v3.hf.space"

# TTS çağrısı başlat
r = requests.post(f"{base}/gradio_api/call/generate_tts_audio", json={
    "data": [
        "Merhaba, ben Vanitas.",  # text_input
        None,                      # audio_prompt (default voice)
        "tr",                      # language
        0.5,                       # exaggeration
        0.8,                       # temperature
        42,                        # seed
        0.5                        # cfg
    ]
})
event_id = r.json()["event_id"]

# SSE stream'den ses URL'ini al
r2 = requests.get(f"{base}/gradio_api/call/generate_tts_audio/{event_id}", stream=True)
full = "".join(chunk.decode() for chunk in r2.iter_content(chunk_size=1) if chunk)

# Ses URL'ini regex ile bul
audio_url = re.search(r'"url":\s*"([^"]+)"', full).group(1)

# İndir
audio_data = requests.get(audio_url).content
with open("output.wav", "wb") as f:
    f.write(audio_data)
```

### 2. Voice Cloning (özel sesle)

```python
# 1. Referans sesi upload et
with open("derya_referans.wav", "rb") as f:
    r = requests.post(f"{base}/gradio_api/upload",
                      files={"files": ("ref.wav", f, "audio/wav")})
    uploaded_path = r.json()[0]  # "/tmp/gradio/xxx/ref.wav"

# 2. TTS + cloning
ref_audio = {"path": uploaded_path, "meta": {"_type": "gradio.FileData"}}
r = requests.post(f"{base}/gradio_api/call/generate_tts_audio", json={
    "data": ["Merhaba, ben Vanitas.", ref_audio, "tr", 0.5, 0.8, 42, 0.5]
})
# ... aynı SSE stream okuma işlemi ...
```

### 3. Voice Cloning için Referans Ses Hazırlama

Chatterbox zero-shot cloning için 5-30 saniye arası temiz, tek sesli kayıt idealdir.

```bash
# YouTube röportajından ses kesiti alma
# 1. Sesi indir
yt-dlp -x --audio-format wav "https://youtube.com/watch?v=VIDEO_ID" -o "full.wav"

# 2. 20 saniyelik temiz bölüm kes (ör: 15:15-15:35 arası)
ffmpeg -i full.wav -ss 915 -t 20 -acodec pcm_s16le -ar 16000 -ac 1 ref.wav

# -ss 915 = 15:15 (dakika:saniye → saniye)
# -t 20 = 20 saniye
# -ar 16000 = 16kHz (Chatterbox için uygun)
# -ac 1 = mono
```

**Önemli:** Referans sesin hedef dilde (Türkçe) olması önerilir. Farklı dilde referans → aksanlı çıktı. `cfgw=0` ile cross-language transfer denenebilir.

### Ses Analizi ile Doğru Kesiti Bulma

Hangi saniyelerde konuşma olduğunu tespit etmek için RMS analizi:

```python
import numpy as np
from scipy.io import wavfile

rate, data = wavfile.read('/tmp/full.wav')
for sec in range(30):
    chunk = data[sec*rate:(sec+1)*rate]
    rms = np.sqrt(np.mean(chunk.astype(np.float32)**2))
    print(f"{sec:2d}s: RMS={rms:.1f} {'🔊' if rms > 500 else '🔉'}")
```

Yüksek RMS değeri (>500) = konuşma var. RMS değeri 0'a yakın = sessizlik.
Bu şekilde hangi saniyelerde hedef kişinin konuştuğunu bulup doğru `-ss` parametresini ayarla.

## Varsayılan Sesler

HF Space'te her dil için built-in default sesler var:
- `tr_m.flac` — Türkçe erkek (on_language_change ile yüklenir)
- `en_f1.flac` — İngilizce kadın
- Varsayılan ses kalitesi cloning'den düşük olabilir

Cloning her zaman varsayılan sesten daha iyi sonuç verir.

## Bilinen Sorunlar

1. **Soğuk başlatma:** Space uzun süre kullanılmazsa HF GPU'yu boşaltır. İlk istek 20-30sn sürebilir. Sonraki istekler hızlıdır.
2. **Rate limit:** HF Spaces'ın GPU kullanım kotası var. Aşırı kullanımda 429 veya sıraya alma olabilir.
3. **Maks 300 karakter:** Uzun metinler kesilmek zorunda.
4. **Gradio API stabil değil:** Sürüm yükseltmelerinde API endpoint'leri değişebilir. Web UI'den "Generate" çalışsa bile API endpoint'leri backend hatası dönebilir.
5. **Backend kararsızlığı:** Space yoğun kullanımda veya bellek limitinde "event: error / data: null" döner. Browser üzerinden çalışsa bile API istekleri backende ulaşmayabilir. Space'i manuel uyandırmak (browser'da sayfayı açıp Generate'e tıklamak) bazen düzeltebilir.
6. **V2 ve V3 Space'leri aynı anda çökebilir:** Her iki space de aynı altyapıyı kullandığından, biri çökerse diğeri de etkilenebilir.
7. **Alternatif:** Replicate API (ücretli ~$0.0074/run, $10 kredi ile ~1350 run, GPU'da hızlı).

## Vanitas Entegrasyon Notları

Mevcut TTS pipeline: `text_to_speech` tool → ElevenLabs (Bella) via Pollinations.

Chatterbox HF Space alternatifi için:
1. Hermes TTS provider'ına yeni bir `chatterbox-hf` provider'ı eklenebilir
2. VOICE_TOKEN yerine HF Space URL'si + upload mekanizması
3. Rate limit/aşırı yük durumunda ElevenLabs fallback

**Öncelik:** Önce kalite testi yap (Varsayılan TR sesi + Derya Pınar Ak cloning testi yapıldı, sonuç: beğeni bekleniyor).
