# Turkish TTS Provider Comparison (2026-06-24)

Kapsamlı Türkçe TTS karşılaştırması — ücretsiz, açık kaynak, ve bulut seçenekleri.

## Kullanım Stratejisi

**3-katmanlı TTS stratejisi:**

| Katman | Servis | Ne Zaman | Maliyet |
|--------|--------|----------|---------|
| 🥇 **Primary** | Edge TTS (tr-TR-EmelNeural) | Normal, internet var | 🆓 Ücretsiz |
| 🥈 **Paid** | ElevenLabs / Fish Audio / MiniMax | Kalite önemliyse | 💰 ~5$/ay |
| 🥉 **Future** | Coqui XTTS-v2 (voice cloning) | Edel'in sesi klonlanınca | 🆓 Ücretsiz |

**⚠️ Piper TTS dfki test edildi (24 Haz 2026):** Edel "kötü beğenmedim" dedi — robotik ve doğal değil. Fallback olarak tut ama primary yerine geçmez. Meta MMS-TTS (mms-tts-tur) denenmeyi bekliyor.

## Karşılaştırma Tablosu

| # | Servis | Türkçe | Maliyet | Kalite | Hız | Tip | Durum |
|---|--------|--------|---------|--------|-----|-----|-------|
| 1 | **Edge TTS** (tr-TR-EmelNeural) | ✅ Native | 🆓 | ⭐⭐⭐⭐ | ⚡ Hızlı | ☁️ Bulut | ✅ **CURRENT** |
| 2 | **Piper TTS** (dfki-medium) | ✅ tr_TR | 🆓 CPU | ⭐⭐ Robotik | ⚡ Çok hızlı | 💻 Local | ❌ **Edel beğenmedi** (2026-06-24) |
| 3 | **Meta MMS-TTS** (mms-tts-tur) | ✅ Türkçe | 🆓 36M params | ⭐⭐⭐⭐ VITS | 🐢 Orta | 💻 Local | ⏳ Test edilecek |
| 4 | **Coqui XTTS-v2** | ✅ 13 dil | 🆓 GPU | ⭐⭐⭐⭐ | 🐢 GPU gerekli | 💻 Local | ⏳ Planlanan |
| 4 | **Chatterbox Multilingual V3** | ✅ 23 dil (Türkçe dahil) | 🆓 MIT | ⭐⭐⭐⭐ | 🐢 CPU ~10-30s, GPU hızlı | 💻 Local | ⏳ Test edildi (27 Haz 2026) |
| 5 | **Kokoro** (82M) | ❌ TR yok | 🆓 Apache 2.0 | ⭐⭐⭐⭐ | ⚡ CPU'da | 💻 Local | ⏳ Community çalışıyor |
| 6 | **ElevenLabs Bella** (Pollinations) | ✅ Native | 💰 ~6.4 pollen/call | ⭐⭐⭐⭐⭐ | ⚡ Hızlı | ☁️ Bulut | ❌ Bakiye yetmez |
| 7 | **ElevenFlash** (Pollinations) | ✅ Native | 💰 ~1.6 pollen/call | ⭐⭐⭐⭐ | ⚡ Hızlı | ☁️ Bulut | ❌ Bakiye yetmez |
| 8 | **Qwen-TTS** (Pollinations) | ❌ TR yok | 💰 ~0.25 pollen/call | ⭐⭐⭐ | 🐢 Orta | ☁️ Bulut | ❌ TR desteklemez |
| 9 | **openai-audio** (Pollinations) | ❌ EN only | 💰 ~0.00002/token | ⭐⭐⭐⭐ | ⚡ Hızlı | ☁️ Bulut | ❌ TR desteklemez |
| 10 | **Qwen3-TTS** (open-source) | ❌ TR yok | 🆓 | ⭐⭐⭐⭐ | 🐢 GPU gerekli | 💻 Local | ❌ TR yok (yabancı aksan) |
| 11 | **MiniMax Speech 2.8** | ✅ 40+ dil | 💰 ~$30/1M | ⭐⭐⭐⭐⭐ | ⚡ Hızlı | ☁️ Bulut | ⏳ 5 deneme hakkı var |
| 12 | **Fish Audio S2** | ✅ 80+ dil | 💰 ~$15/1M | ⭐⭐⭐⭐ | ⚡ Hızlı | ☁️ Bulut | ⏳ Ücretli |
| 13 | **ElevenLabs API** (direkt) | ✅ 29 dil | 💰 $0.05/1K | ⭐⭐⭐⭐⭐ | ⚡ ~75ms | ☁️ Bulut | 💰 5$ = 2 hafta |
| 14 | **Deepgram Aura-2** | ⚠️ EN aksan | 🆓 | ⭐⭐ | ⚡ Çok hızlı | ☁️ Bulut | ❌ Yabancı aksan |
| 15 | **Cartesia Sonic 3.5** | ✅ Native | 🆓 27dk/ay | ⭐⭐⭐⭐⭐ | ⚡ ~0.5s | ☁️ Bulut | ❌ 401 (API key yok) |
| 16 | **gTTS** (Google) | ✅ tr | 🆓 | ⭐⭐ Robotik | ⚡ Hızlı | ☁️ Bulut | 🔧 Basit yedek |
- **Keşif:** 24 Haz 2026 — Fish Audio S2, 80+ dil desteği
- **Türkçe:** Var. Ses örnekleri:
  - **Türkçe Erkek Ses** (1,499+ kullanıcı, anlatıcı) — "Bir kurşun insan vücuduna girdiğinde..."
  - **Turkish Deep Voice** (56+ kullanıcı, derin erkek)
  - **Turkish Gojo** (dinamik erkek)
- **Artı:** En ucuz ($15/1M), 80+ dil, ses klonlama
- **Eksi:** Türkçe kadın sesi yok gibi, research lisansı
- **Fiyat:** $15/1M UTF-8 byte (EN'de karakter, ZH'de 2-3x)
- **Platform:** https://fish.audio/ — ücretsiz deneme, kredi kartı gerekmez
- **Not:** Pollinations'ta yok, doğrudan Fish Audio API'si gerek

### 12. MiniMax Speech 2.8 💰 ~$30-50/1M
- **Keşif:** 24 Haz 2026 — 40+ dil, 300+ ses
- **Türkçe:** Var. Kadın sesleri:
  - **Articulate Podcaster** 🚺 — Sıcak, doğal, ilgi çekici
  - **News Anchor** 🚺 — Profesyonel, net
  - **Formal Broadcaster** 🚺 — Temiz, objektif
  - **Helpful Instructor** 🚺 — Pürüzsüz, sakin
  - **Professional Anchor** 🚺 — Artistik, dokulu
  - **Enthusiastic Speaker** 🚺 — Parlak, enerjik
  - **Energetic Speaker** 🚺 — Genç, canlı
- **Erkek Sesleri:** Digital Advisor, Academic Lecturer, Documentary Narrator, Gritty Storyteller, Wise Historian, vb.
- **Versiyonlar:**
  | Sürüm | Fiyat | Kalite | Kullanım |
  |-------|-------|--------|----------|
  | Speech 2.8 Turbo | ~$30/1M | Hızlı, iyi | Gerçek zamanlı |
  | Speech 2.8 HD | ~$50/1M | Studio | Kayıt, prodüksiyon |
- **Özellikler:** Ses klonlama (10sn), emotion control, voice design
- **Platform:** minimax.io/audio — 5 ücretsiz deneme hakkı!
- **API:** Doğrudan MiniMax API'si (Pollinations'ta yok)
- **Cloudflare:** developers.cloudflare.com/ai/models/minimax/speech-2.8-hd/
- **Replicate:** replicate.com/minimax/speech-2.8-hd
- **Fiyat Hesaplama:** 5$ = ~166K karakter (Turbo) / ~100K karakter (HD)
- **Not:** Edel MiniMax API key'ini Bitwarden Secrets'a koydu.

### 13. Google Gemini TTS ⏳ Araştırılacak
- **Google AI Studio / Gemini API** üzerinden TTS
- **Türkçe:** Belirtilmiş — "Dil desteği için..."
- **Limit:** 32K token context
- **Fiyat:** Free tier var (sınırlı)
- **Kaynak:** ai.google.dev/gemini-api/docs/speech-generation

---

## Detaylı İnceleme

### 1. Edge TTS (tr-TR-EmelNeural) ✅ CURRENT
- **Kurulum:** `pip install edge-tts`
- **Kullanım:** `edge_tts.Communicate(text, "tr-TR-EmelNeural")`
- **Sesler:** `tr-TR-EmelNeural` (kadın), `tr-TR-AhmetNeural` (erkek)
- **Çıktı:** MP3, tempfile ile geçici dosyaya kaydet
- **Artı:** Ücretsiz, native Türkçe, yüksek kalite, Microsoft altyapısı
- **Eksi:** İnternet gerekli, ses değiştirme/kopyalama yok
- **Entegrasyon:** WebSocket üzerinden base64 MP3 olarak browser'a gönder
- **Kod:**
```python
import tempfile, os
communicate = edge_tts.Communicate(text, "tr-TR-EmelNeural")
tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
tmp.close()
await communicate.save(tmp.name)
with open(tmp.name, "rb") as f:
    data = f.read()
os.unlink(tmp.name)
```

### 2. Piper TTS (dfki-medium) ❌ Beğenilmedi
- **Test Sonucu (24 Haz 2026):** Edel test etti, "kötü beğenmedim" dedi. Robotik ve doğal değil.
- **Türkçe Sesler:**
  | Ses | Cinsiyet | Kalite | Örnekleme | Lisans |
  |-----|----------|--------|-----------|--------|
  | dfki | 🤷 Muhtemelen kadın | medium | 22.05KHz | CC BY-NC-SA 4.0 |
  | fettah | 🚹 Erkek | medium | 22.05KHz | ? |
  | fahrettin | 🚹 Erkek | medium | 22.05KHz | ? |
- **Kurulum:** `pip install piper-tts`
- **Model:** ~15-20M parametre, ONNX formatı
- **API:** `PiperVoice.load()` → `voice.synthesize(text)` → AudioChunk.audio_int16_bytes
- **Uyarı:** dfki non-commercial lisans — ticari kullanımda farklı model gerekir
- **Kaynak:** https://huggingface.co/rhasspy/piper-voices/tree/v1.0.0/tr/tr_TR
- **Not:** Piper Python API'de `synthesize` generator döndürür (AudioChunk), direkt bytes değil. `chunk.audio_int16_bytes` ile raw PCM alınır.

### 3. Meta MMS-TTS (mms-tts-tur) ⏳ Test Edilecek
- **Keşif:** 24 Haz 2026 — Meta AI'nın Massively Multilingual Speech projesi
- **Türkçe:** Özel `tur` checkpoint: `facebook/mms-tts-tur`
- **Model:** VITS (Variational Inference with adversarial learning for end-to-end Text-to-Speech)
- **Parametre:** 36.3M (çok hafif!)
- **Lisans:** CC-BY-NC 4.0 (non-commercial)
- **Kurulum:** `pip install --upgrade transformers accelerate scipy`
- **Kullanım:**
```python
from transformers import VitsModel, AutoTokenizer
model = VitsModel.from_pretrained("facebook/mms-tts-tur")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-tur")
inputs = tokenizer("Merhaba Edel", return_tensors="pt")
with torch.no_grad():
    output = model(**inputs).waveform
```
- **Artı:** Meta altyapısı, VITS kalitesi, çok hafif, Türkçe'ye özel
- **Eksi:** Non-commercial lisans, Transformers bağımlılığı (torch +2GB), orta hız
- **Kaynak:** https://huggingface.co/facebook/mms-tts-tur
- **Not:** 1100+ dilde MMS projesinin Türkçe ayağı. `transformers>=4.33` gerekli.

### 4. Coqui XTTS-v2 ⏳ Planlanan
- **Türkçe:** Var, 13 dil arasında
- **Özellik:** 6 saniye ses örneği ile ses klonlama
- **Lisans:** Apache 2.0
- **Gereksinim:** GPU (RTX 3060+)
- **Hedef:** Edel'in sesini klonlamak için
- **Kurulum:** `pip install TTS`
- **Kullanım:** `tts --model_name tts_models/tr/common-voice/glow-tts ...`

### 4. Pollinations TTS Fiyatlandırması
- **Anahtar Tipi:** sk_ (secret key, limitsiz, pollen harcar)
- **Bakiye (24 Haz 2026):** 0.156 pollen
- **1 pollen = $0.001 USD**

| Model | Pollen/call | $/call | Durum |
|-------|-------------|--------|-------|
| ElevenLabs | ~6.4 | ~$0.0064 | ❌ Yetmez |
| ElevenFlash | ~1.6 | ~$0.0016 | ❌ Yetmez |
| Qwen-TTS | ~0.25 | ~$0.00025 | ❌ Yetmez |
| openai-audio | ~0.00002/token | ~$0.00000002/token | ⚠️ Çok az |

**Geçmiş kullanım:** 
- 17 Haz: 169 elevenlabs istek = $1.078 (6.4 pollen/istek)
- 16 Haz: 52 elevenlabs istek = $0.808 (15.5 pollen/istek)
- Qwen-TTS sadece 1 kez kullanılmış: $0.000247

### 5. Yeni Açık Kaynak Modeller (2026)

| Model | Param | VRAM | Türkçe | Lisans | Öne Çıkan |\n|-------|-------|------|--------|--------|-----------|\n| Kokoro | 82M | CPU/3GB | ❌ (community çalışıyor) | Apache 2.0 | CPU'da çalışır, 8 dil |\n| **Chatterbox Multilingual V3** | **500M** | **4GB+ RAM (CPU), GPU önerilir** | **✅ 23 dil** | **MIT** | **Zero-shot cloning, accent preservation, V3 (10 Haz 2026)** |\n| Qwen3-TTS | 1.7B | 8GB+ | ❌ (yabancı aksan) | Apache 2.0 | 10 dil, streaming |\n| VibeVoice (MS) | 1.5B | 8GB+ | ❌ (EN/ZH only) | Research | 90dk çoklu konuşmacı |\n| Fish Speech S2 | ? | 4GB+ | ✅ (80+ dil) | Research | En çok dil desteği |

---

## Önerilen Strateji

### Kısa Vade (Şimdi)
- **Edge TTS** ile devam — çalışıyor, kaliteli, bedava, entegrasyonu tamam ✅
- Piper TTS (dfki) test edildi, **beğenilmedi** — robotik ve doğal değil ❌
- **Meta MMS-TTS** (mms-tts-tur) test edilmeyi bekliyor — VITS tabanlı, 36M parametre, umut vadediyor

### Orta Vade (Ücretli Alternatifler)
Edel 5$ bütçe ile kaliteli TTS'ye geçmeyi düşünüyor (24 Haz 2026). Seçenekler:

| Servis | Fiyat | 5$ ile | Türkçe Sesler |
|--------|-------|--------|---------------|
| **ElevenLabs API** (direkt) | $0.05/1K karakter | ~100K karakter (~2 hafta) | Native Türkçe, en kaliteli |
| **Fish Audio S2** | ~$0.015/1K karakter | ~333K karakter (~1.5 ay) | Erkek ses ağırlıklı, 80+ dil |
| **MiniMax Speech 2.8** (Turbo) | ~$0.030/1K karakter | ~166K karakter (~1 ay) | 300+ ses, kadın/erkek, 50+ dil |
| **MiniMax Speech 2.8** (HD) | ~$0.050/1K karakter | ~100K karakter (~2 hafta) | Studio kalitesi, emotion control |

**Öneri:** MiniMax Speech 2.8 en iyi fiyat/kalite dengesi — 300+ ses, kadın sesleri var (Articulate Podcaster, News Anchor), 5 ücretsiz deneme hakkı sunuyor. Fish Audio en ucuzu ama erkek ses ağırlıklı.

### Uzun Vade
- Coqui XTTS-v2 ile Edel'in sesini klonla — kişiselleştirilmiş TTS
- Ya da Chatterbox-Turbo ile daha kaliteli klonlama

---

## Kaynaklar

- Edge TTS: `pip install edge-tts`, `edge-tts --list-voices`
- Piper TTS: https://github.com/rhasspy/piper, https://rhasspy.github.io/piper-samples/
- Coqui TTS: https://github.com/coqui-ai/TTS, `pip install TTS`
- Kokoro: https://huggingface.co/hexgrad/Kokoro-82M
- Chatterbox: ocdevel.com/blog/20250720-tts
- Qwen3-TTS: https://github.com/QwenLM/Qwen3-TTS
- Fish Audio: https://fish.audio/
- Pollinations TTS: Pollinations MCP → getPricing, getBalance, getUsage
