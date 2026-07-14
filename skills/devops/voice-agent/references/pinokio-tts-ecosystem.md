# Pinokio TTS Ekosistemi — Araştırma Raporu

> Keşif tarihi: 27 Haziran 2026
> Araştırma yöntemi: beta.pinokio.co kataloğu + GitHub repoları + HF modelleri
> Kapsam: Türkçe destekli, voice cloning yapabilen, ücretsiz/kartsız çözümler

## Neden Pinokio?

Pinokio, AI modellerini tek tıkla kurup çalıştıran bir platformdur. TTS modelleri için:
- Python/CUDA/bağımlılıkları otomatik kurar
- Gradio web arayüzü ile kullanıma hazır açar
- Local GPU'da çalıştığı için API ücreti yok
- Windows + NVIDIA destekli (RTX 4060 için uygun)

## TTS Modelleri Karşılaştırma

| # | Model | Param | Türkçe | Voice Cloning | VRAM | Öne Çıkan |
|---|-------|-------|--------|--------------|------|-----------|
| 1 | **VoxCPM2** ⭐ | **2B** | ✅ 30 dil arasında | ✅ Voice Design + Cloning + Ultimate | ~5-6 GB | 48kHz, Apache-2.0, ses tasarımı |
| 2 | **ChatterBox V3** | 0.5B | ✅ 23 dil | ✅ Zero-shot | ~3-4 GB | Tanıdık, Turbo modeli var |
| 3 | **Ultimate TTS Studio** | Çoklu | ⚠️ Motorlara göre | ✅ (Chatterbox, Fish-Speech, F5) | Motor başı ~2-4 GB | ALL-IN-ONE: 8 motor tek arayüzde |
| 4 | **Fish-Speech** | ~500M | ❓ Duyulmamış | ✅ Kaliteli | ~4 GB | Seste kaliteli, popüler |
| 5 | **F5-TTS** | ~300M | ❌ (EN/CN) | ✅ En iyisi | ~3 GB | Voice cloning'de lider ama Türkçe yok |
| 6 | **OpenVoice** | ~200M | ❌ (Türkçe zayıf) | ✅ Anlık | ~2 GB | MyShell, instant cloning |
| 7 | **X-Voice** | ? | ❓ (27 dil, belki) | ✅ | ? | Evrensel çevirmen |
| 8 | **Kokoro TTS** | **82M** | ⚠️ Kısmi (özel train gerek) | ❌ | CPU'da çalışır | Süper hafif, anlık CPU |
| 9 | **Parler-TTS** | ~600M | ❌ | ❌ | CPU'da çalışır | Prompt kontrollü (cinsiyet/tarif) |
| 10 | **Supertonic** | ? | ❓ | ❌ | Çok düşük | Aşırı hızlı, on-device |

### Adayların Detaylı Analizi

#### 1. VoxCPM2 — En Kapsamlı Aday 🥇

**Pinokio linki:** `timoncool/VoxCPM2_portable-pinokio`
**Asıl repo:** OpenBMB/VoxCPM
**Model:** openbmb/VoxCPM2 (HuggingFace)
**Lisans:** Apache-2.0

**Özellikler:**
- **2 milyar parametre** — en büyük açık kaynak TTS modeli
- **Tokenizer-free diffusion autoregressive** — doğrudan continuous speech üretimi
- **30 dil** (Türkçe listede!): Arabic, Burmese, Chinese, Danish, Dutch, English, Finnish, French, German, Greek, Hebrew, Hindi, Indonesian, Italian, Japanese, Khmer, Korean, Lao, Malay, Norwegian, Polish, Portuguese, Russian, Spanish, Swahili, Swedish, Tagalog, Thai, **Turkish**, Vietnamese
- **Voice Design** — hiç referans ses olmadan, sadece metin tarifiyle ses yaratma:
  ```python
  # Örnek: "(Genç kadın, sıcak ve tatlı ses) Merhaba!"
  ```
- **Controllable Voice Cloning** — referans + stil kontrolü (duygu, hız, ifade)
- **Ultimate Cloning** — referans + transkript → birebir aynı ses
- **48kHz çıktı** (AudioVAE V2 ile super-resolution)
- **RTF ~0.3** RTX 4090'da (1sn ses 0.3sn'de üretilir)
- **pip install voxcpm** ile kurulum

**RTX 4060 8GB için uygunluk:**
- 2B model ~5-6 GB VRAM → 8GB'da çalışır (diğer process'lere dikkat)
- Flash-Attention 2 + Triton optimizasyonları mevcut
- Pinokio kurulumu: ~4-5 GB model indirir, 15-20 dk sürebilir
- Denemeden net performans bilinmez — sınırda çalışabilir

#### 2. Ultimate TTS Studio — ALL-IN-ONE 🥈

**Pinokio linki:** `SUP3RMASS1VE/Ultimate-TTS-Studio-SUP3R-Edition-Pinokio`
**Asıl repo:** SUP3RMASS1VE/Ultimate-TTS-Studio-SUP3R-Edition
**Gereksinim:** NVIDIA ONLY
**Durum:** 13 yıldız, 3 fork, son güncelleme Şubat 2026

**İçindeki Motorlar:**
| Motor | Türkçe | Cloning | Not |
|-------|--------|---------|-----|
| Kokoro | ⚠️ Kısmi | ❌ | 82M, CPU'da bile hızlı |
| KittenTTS | ❓ | ❓ | Yeni motor |
| Higgs Audio | ❓ | ❓ | Ses işleme |
| **Chatterbox** | ✅ 23 dil | ✅ | Tanıdık, 0.5B |
| **Fish-Speech** | ❓ | ✅ Kaliteli | Popüler voice cloning |
| **F5-TTS** | ❌ (EN/CN) | ✅ En iyisi | Voice cloning lideri |
| index-tts / indextts2 | ❓ | ✅ | |

**Özel Özellikler:**
- **Conversation Mode** — iki ses karşılıklı konuşsun diye
- **eBook-to-Audiobook** — kitap → sesli kitap
- **Unified Interface** — tüm motorlar tek arayüzde
- **Vibe Voice** — ayrı panel

**Avantaj:** Tek kurulumda 8 farklı motor. Biri çalışmazsa diğerini dene.

#### 3. ChatGPT (referans, HF Space'te test edildi)

Detaylı kullanım: `references/chatterbox-hf-space-tts.md`

**Durum:** V3 Space'inde backend hatası alındı (27 Haziran akşamı). Daha önce çalışıyordu. Geçici bir HF sorunu olabilir.

#### 4. OpenVoice (MyShell)

**Pinokio linki:** `cocktailpeanutlabs/openvoice`
**Türkçe:** ❌ — GitHub issue #414: "Turkish is not supported", sentezi çok zayıf
**Voice cloning:** ✅ — çok hızlı, anlık

#### 5. X-Voice

**Pinokio linki:** `6morpheus6/x-voice`
**Özellik:** 27 dil, multilingual, voice cloning
**Türkçe:** ❓ Bilinmiyor (dil listesi net değil)

## Tavsiye Sıralaması (RTX 4060 8GB, Türkçe + Cloning)

```
1. Denenecek: VoxCPM2 (en kapsamlı, Türkçe resmi destek)
2. Yedek: Ultimate TTS Studio (çoklu motor, içinde Chatterbox + Fish-Speech var)
3. Son çare: HF Space Chatterbox (ücretsiz ama backend dengesiz)
4. Ücretli: ElevenLabs 5$/ay (en kaliteli, en stabil)
5. API: Replicate Chatterbox ($0.007/run, $10 kredi gerek)
```

## Voice Cloning Pipeline (YouTube → Klonlanmış Ses)

Bu pipeline her TTS modeli için aynı mantıkla çalışır:

```
1. KAYNAK BUL → YouTube/Instagram'da hedef kişinin konuşma videosu
2. İNDİR → yt-dlp ile ses indir (-x --audio-format wav)
3. KES → ffmpeg ile 15-20 saniyelik temiz bölüm (sadece hedef ses)
4. DÖNÜŞTÜR → 16kHz, mono, WAV (modelin beklediği format)
5. YÜKLE → Modelin API'sine/UI'sına referans ses olarak ver
6. ÜRET → İstediğin metni o sesle konuştur
```

### ffmpeg Kesme Notları

```bash
# Dakika:saniye'den saniyeye çevirme
# 03:49 → 3*60 + 49 = 229 saniye
ffmpeg -i full.wav -ss 229 -t 20 -acodec pcm_s16le -ar 16000 -ac 1 ref.wav

# Parametreler:
#   -ss 229  : başlangıç saniyesi
#   -t 20    : 20 saniye uzunluk
#   -ar 16000: 16kHz sample rate (çoğu TTS modeli için ideal)
#   -ac 1    : mono kanal
#   -acodec pcm_s16le: 16-bit PCM WAV
```

### Referans Ses Kalitesi İpuçları

- **5-30 saniye** arası ideal (Chatterbox için 5-30sn, VoxCPM2 için 5-50sn)
- **Arka plan gürültüsüz** (stüdyo kaydı veya temiz röportaj)
- **Tek ses** (muhabir/başka kişi karışmayacak)
- **Doğal konuşma tonu** (rol yapma değil, günlük konuşma)
- **Hedef dilde olması** önerilir (Türkçe referans → Türkçe çıktı)
- Farklı dilde referans verilirse aksanlı çıktı alınabilir
- `cfgw=0` ile cross-language transfer denenebilir (Chatterbox için)

## Maliyet Karşılaştırması

| Çözüm | Aylık Maliyet | Ses Kalitesi | Cloning | Stabilite |
|-------|:------------:|:-----------:|:-------:|:---------:|
| Pinokio + VoxCPM2/Komşu | **$0** | ⭐⭐⭐ Variable | ✅✅ | ⚠️ Modela bağlı |
| ElevenLabs 5$ | **$5/ay** | ⭐⭐⭐⭐⭐ | ✅✅ | ✅✅ |
| Replicate API | **$0.007/run** | ⭐⭐⭐⭐ | ✅ | ✅✅ |
| HF Space Chatterbox | **$0** | ⭐⭐⭐ | ✅ | ❌ Sık sık çöküyor |

## Ekipman Gereksinimleri

| Model | Min VRAM | Önerilen | RTX 4060 8GB? |
|-------|----------|----------|:-----------:|
| VoxCPM2 (2B) | 5 GB | 8 GB | ⚠️ Sınırda çalışır |
| Chatterbox (0.5B) | 3 GB | 4 GB | ✅ Rahat |
| Fish-Speech | 3 GB | 4 GB | ✅ Rahat |
| F5-TTS | 3 GB | 4 GB | ✅ Rahat |
| Kokoro (82M) | CPU | CPU | ✅ CPU'da bile |
| Ultimate TTS Studio | Motora bağlı | 6 GB | ⚠️ Motor seçimine bağlı |

Tüm modeller NVIDIA CUDA gerektirir (Kokoro ve Parler-TTS hariç).
RTX 4060 8GB + Intel i7-12650H için önerilen: Önce VoxCPM2'yi dene, çalışmazsa Chatterbox'a geç.
