# Açık Kaynak TTS Araştırması — 27 Haziran 2026

Vanitas'ın ElevenLabs bağımlılığını kırmak için yapılan kapsamlı TTS araştırması.

## Özet

| Model | Param | Türkçe | Hız (CPU) | Voice Cloning | Lisans | Durum |
|-------|-------|--------|-----------|:-------------:|--------|-------|
| **Chatterbox V3** | 500M | ✅ 23 dil | 🐢 89sn (CPU) | ✅ Zero-shot | MIT | ⏸️ GPU gerek |
| **Kokoro** | 82M | ⚠️ Kısmen | ⚡ Çok hızlı | ❌ | ? | ⏳ Araştırılmalı |
| **F5-TTS** | ~300M | ❌ (EN/CN) | 🐢 GPU gerek | ✅ En iyisi | CC-NC | ❌ Türkçe yok |
| **Parler-TTS** | Hafif | ❌ | ⚡ CPU hızlı | ❌ | ? | ❌ Türkçe yok |
| **VoxCPM2** | ? | ✅ 30 dil | 🐢 GPU gerek | ✅ + LoRA | ? | 🔍 |
| **Meta MMS-TTS** | 36.3M | ✅ Türkçe | ⚡ CPU hızlı | ❌ | CC-BY-NC | ✅ Test edildi |
| **Edge TTS** | Cloud | ✅ Emel/Ahmet | ⚡ Anlık | ❌ | Ücretsiz | ✅ Kullanımda |
| **Piper** | Hafif | ✅ tr_TR | ⚡ CPU hızlı | ❌ | CC | ❌ Beğenilmedi |
| **ElevenLabs** | Cloud | ✅ En iyisi | ⚡ ~75ms | ✅ $ | Ücretli | 💰 Planlanan |

## Chatterbox Multilingual V3 — Detaylı Test

### Kurulum
```bash
pip install chatterbox-tts  # PyPI'da chatterbox-tts, NOT chatterbox
```

### Test Kodu
```python
import torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
wav = model.generate("Merhaba, ben Vanitas.", language_id="tr")
ta.save("/tmp/chatterbox_test_tr.wav", wav, model.sr)
```

### Test Ortamı
- CPU: Intel i7-12650H (16 cores)
- RAM: 7.6GB total, ~5.7GB available
- GPU: Yok
- Python: 3.11.15
- chatterbox-tts: 0.1.7
- torch: 2.6.0 (CPU)

### Test Sonuçları
- **89 saniye** — 10 kelimelik Türkçe cümle için
- 1000 token üzerinden 96'sında EOS (alignment_stream_analyzer forcing EOS)
- Per-token hız: ~2.3 it/s
- RAM kullanımı: ~4-6GB
- Varsayılan ses: built-in speaker (HF Space'teki erkek ses)
- Ses kalitesi: Edel beğenmedi (erkek ses, doğal değil)

### Bağımlılıklar
- torch 2.6.0, torchaudio 2.6.0, transformers 5.2.0
- gradio 6.8.0, diffusers 0.29.0, librosa 0.11.0
- Toplam ~3-4GB (torch + CUDA libs CPU'da bile yüklenir)

## Replicate API Seçeneği

Chatterbox Replicate'te bulut GPU'da çalışır:
- **Fiyat:** $0.0074/run (1 run = 1 cümle)
- **Ücretsiz kredi:** Yeni kullanıcılara ~$5-10
- **Limit:** text max 300 karakter
- **Voice cloning:** `reference_audio` parametresiyle
- **Hız:** GPU'da ~1-3sn
- **Parametreler:** text, language, reference_audio, exaggeration (0.25-2.0), temperature (0.05-5.0), cfg_weight (0.2-1.0), seed

$10 ücretsiz krediyle ~1350 run yapılabilir. Aylık konuşma trafiğine bağlı.

**⚠️ Billing Sorunu:** Test edildi (27 Haz 2026) — `r8_` prefiksli API key ile HTTP 402 Insufficient Credit. Çözüm: replicate.com → Settings → Billing → kredi kartı doğrulaması. Karttan çekim yapılmaz, sadece ücretsiz krediyi aktifleştirir.

## Pinokio AI'da TTS Modelleri

Pinokio (https://beta.pinokio.co) bir AI model yöneticisi. Windows'ta tek tıkla kurulum sağlar.

### Mevcut TTS App'leri:
1. **ChatterBox** — `pierrunoyt/chatterbox-tts-app` (Turbo, Multilingual 23+, Original)
2. **Kokoro-TTS** — `pinokiofactory/kokoro-tts` (82M parametre, çok hafif)
3. **Parler-TTS** — `cocktailpeanutlabs/parler-tts` (hafif, prompt kontrollü)
4. **VoxCPM2** — `timoncool/VoxCPM2_portable-pinokio` (30 dil, voice cloning, LoRA)
5. **F5-TTS** — YouTube üzerinden tespit edildi
6. **Qwen3-TTS MLX** — Apple Silicon için

### Pinokio Avantajları
- Windows'ta tek tıkla kurulum
- Gradio arayüz
- GPU varsa hızlı çalışır
- Tamamen ücretsiz ve lokal

### Pinokio Dezavantajları
- GPU yoksa CPU'da yavaş
- Windows'a kurulum gerekli
- Disk alanı (modeller büyük)

## HuggingFace Spaces API — En Pratik Ücretsiz Çözüm

Chatterbox Multilingual V3, HuggingFace Spaces'te **tamamen ücretsiz** çalışır. Edel'in en çok aradığı şey: ücretsiz, Türkçe, voice cloning destekli, GPU'da hızlı.

### Artıları
- ✅ **Tamamen ücretsiz** — üyelik/kredi kartı gerekmez
- ✅ GPU'da çalışır (Space'in kendi GPU altyapısı) — 1-5sn
- ✅ Voice cloning destekler
- ✅ 23 dil + Türkçe
- ✅ V3 checkpoint (10 Haz 2026)
- ✅ API key gerekmez

### Eksileri
- ⚠️ 300 karakter sınırı
- ⚠️ HF Spaces yoğunluğunda kuyruk olabilir
- ⚠️ Garantili SLA yok
- ⚠️ Rate limit var

### API Kullanımı
```python
# Detay: references/chatterbox-tts-integration.md
base = "https://resembleai-chatterbox-multilingual-tts-v3.hf.space"
# /gradio_api/call/generate_tts_audio ile TTS
```

## Voice Cloning Stratejisi

### Chatterbox Zero-Shot Cloning (HF Space API)
```python
import requests, json, re

base = "https://resembleai-chatterbox-multilingual-tts-v3.hf.space"

# 1. Referans ses yükle
with open("/path/to/reference.wav", "rb") as f:
    r = requests.post(base + "/gradio_api/upload", files={"files": ("ref.wav", f, "audio/wav")})
    ref_path = r.json()[0]

# 2. TTS + Voice cloning
payload = {
    "data": [
        "Merhaba, ben Vanitas.",                  # text_input (max 300 chars)
        {"path": ref_path, "meta": {"_type": "gradio.FileData"}},  # audio_prompt
        "tr",                                      # language_id
        0.5, 0.8, 42, 0.5                          # exaggeration, temp, seed, cfg
    ]
}
r = requests.post(base + "/gradio_api/call/generate_tts_audio", json=payload, timeout=60)
eid = r.json()["event_id"]

# 3. SSE'den ses URL'sini oku
r = requests.get(f"{base}/gradio_api/call/generate_tts_audio/{eid}", timeout=120, stream=True)
full = "".join(chunk.decode() for chunk in r.iter_content(chunk_size=1) if chunk)
audio_match = re.search(r'"url":\s*"([^"]+)"', full)
if audio_match:
    audio_data = requests.get(audio_match.group(1), timeout=30).content
```

**Alternatif — on_language_change ile referans set etme:**
Bazı durumlarda doğrudan generate_tts_audio'ya referans göndermek error verebilir. Önce on_language_change ile referansı yükleyip sonra generate_tts_audio'yu referans OLMADAN çağırmak daha stabil:
```python
# Önce referans yükle ve on_language_change'e gönder
ref_obj = {"path": ref_path, "meta": {"_type": "gradio.FileData"}}
requests.post(base + "/gradio_api/call/on_language_change", json={
    "data": ["tr", ref_obj, "test"]
})

# Sonra referans OLMADAN TTS yap (güncellenmiş default ses kullanılır)
requests.post(base + "/gradio_api/call/generate_tts_audio", json={
    "data": ["Merhaba", None, "tr", 0.5, 0.8, 42, 0.5]
})
```

**⚠️ Gradio API endpoint'leri (HF Spaces):**
- `GET /gradio_api/info` — tüm fonksiyonları ve parametreleri listeler
- `POST /gradio_api/call/{fn}` — async job başlatır, event_id döner
- `GET /gradio_api/call/{fn}/{event_id}` — SSE stream, event:complete/data tipinde
- `POST /gradio_api/upload` — dosya yükler, path döner

### Referans Ses Gereksinimleri
- 5-30 saniye temiz kayıt
- Arka plan gürültüsüz
- Doğal konuşma (rol yapma değil)
- Tek konuşmacı
- Tercihen hedef dilde (Türkçe)
- Stüdyo/TV programı kaydı tercih sebebi

### Aday: Derya Pınar Ak — Klonlama Testi (27 Haz 2026)

Türk oyuncu (d. 2003). Bilinen yapımlar: 3391 Kilometre, Hükümsüz, Snow and the Bear.

**Kaynak:** 25dk TV röportajı ("Yasemİnce İtiraflar", Günaydın kanalı, 2024)
- YouTube: https://www.youtube.com/watch?v=tgzphtFs7-Y
- Program stüdyosu kalitesinde ses

**Çıkarılan referans kesitleri (20'ser saniye, 16kHz mono WAV):**
| Kesit | Zaman | İçerik |
|-------|-------|--------|
| ref1 | 03:49-04:09 | Eleştirileri anlatıyor |
| ref2 | 15:15-15:35 | Oyunculuğa giriş hikayesi |
| ref3 | 09:24-09:44 | Uzak mesafe ilişkisi |
| giriş | 00:00-00:22 | Program girişi (Edel'in önerisi) |

**Klonlama Sonucu:** Edel'in değerlendirmesi: *"Türkçe telaffuz yetersiz ve tonlama klonlama olarak yetersiz."* Muhtemel nedenler:
1. Röportaj ses kalitesi stüdyo olsa da ideal klonlama kalitesinde değil
2. Muhabir sesi referansa karışmış olabilir
3. Chatterbox V3'ün Türkçe tonlama başarımı sınırlı

**Öğrenilen ders:** Daha temiz bir kaynak (direkt stüdyo kaydı, dublaj, reklam) gerekli. Edel'in önerisi: 00:00-00:24 arası giriş konuşması stüdyo kalitesindeyse denenmeli (test sırasında HF Space çöktü, tekrar denenecek).

### Önemli Uyarı
Zero-shot cloning'de referans ses hedef dilde olmazsa, kaynak aksan hedef dile taşınır (accent preservation). Bir İngiliz konuşmacının sesini Türkçe konuşturunca İngiliz aksanıyla konuşur. En iyi sonuç için referans ses Türkçe olmalıdır.

## HF Space Kararlılık Sorunları

**⚠️ Space backend çökebiliyor:** HF Spaces idle kalınca uyku moduna geçer veya backend hatası verebilir (V3 ve V2 space'lerinde gözlemlendi). Çözüm:
1. Browser'da space sayfasını ziyaret et (https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS-V3)
2. "Generate" butonuna tıkla — space ayağa kalkar
3. API tekrar çalışmaya başlar
4. Eğer hata devam ederse: birkaç saat bekle, HF tarafındaki geçici bir kesinti olabilir

**⚠️ Aylık bütçe eşiği:** Edel $5/ay altı çözümleri tercih eder. $10 Replicate kredisi \"çok para\" olarak değerlendirildi (27 Haz 2026). Ücretsiz çözümler (HF Spaces, Edge TTS, Meta MMS-TTS) her zaman önceliklidir. Ücretli bir TWS çözümü önermeden önce mutlaka ücretsiz alternatifleri tüket.

Vanitas için ideal TTS çözümü henüz bulunamadı:
- **Chatterbox** — kaliteli ama GPU gerekli, CPU 89sn çok yavaş
- **Edge TTS** — ücretsiz, iyi kalite ama Edel "robotik" buldu
- **ElevenLabs Bella** — en kaliteli, $5/ay
- **Meta MMS-TTS** — test edildi, değerlendirme bekleniyor

**Öneri:** GPU'lu bir ortamda (Replicate ücretsiz krediyle veya Pinokio'da GPU varsa) Chatterbox V3'ü voice cloning ile test etmek, sonra karar vermek.
