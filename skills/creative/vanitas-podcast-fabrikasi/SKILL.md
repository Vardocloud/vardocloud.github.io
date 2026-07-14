---
name: vanitas-podcast-fabrikasi
description: "AI podcast üretim fabrikası — konu ver, podcast paketi al. Bardo temasıyla psikoloji odaklı, akademik dili sohbet diline çeviren podcast üretimi."
category: creative
tags: [podcast, turkish, automation, bardo, psychology]
---

# Vanitas Podcast Fabrikası

AI destekli podcast üretim fabrikası. Bir **konu**, **hedef kitle** ve **süre tercihi** verin, size eksiksiz bir podcast paketi teslim edelim.

## Mimari

```
Kullanıcı Girdisi
  │ Konu + Hedef Kitle + Süre
  ▼
┌─────────────────────────────┐
│ AŞAMA 1: İçerik Planlayıcı  │
│ deepseek-v4-flash-free      │
│ (Zen API, keysiz)           │
│ Çıktı: JSON akış planı      │
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│ AŞAMA 2: Diyalog Yazarı     │
│ gpt-5.4-mini                │
│ (Pollinations, port 19999)  │
│ Çıktı: Doğal Türkçe konuşma │
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│ AŞAMA 3: Görsel + Ses       │
│ (paralel, opsiyonel)        │
│ - nanobanana-2: thumbnail   │
│ - ElevenLabs: seslendirme   │
│ - NotebookLM: alt. üretim   │
└─────────────────────────────┘
```

## Kullanım

```bash
# Doğrudan script ile
~/.hermes/skills/creative/vanitas-podcast-fabrikasi/scripts/podcast_fabrikasi.py \
  --konu "Bilinç Akışı ve Yaratıcılık" \
  --hedef-kitle "üniversite öğrencileri" \
  --sure 8
```

```bash
# Veya Hermes tetiklemesi ile (tanımlı trigger)
/hermes run vanitas-podcast-fabrikasi konu="Bilinç Akışı ve Yaratıcılık"
```

## Aşamalar

### Aşama 1: İçerik Planlayıcı
- **Endpoint:** `https://opencode.ai/zen/v1/chat/completions`
- **Model:** `deepseek-v4-flash-free`
- **API Key:** Gerekmez
- **Görev:** Podcast akış planı çıkarır (giriş, 3 ana bölüm, kapanış)
- **Host karakterleri:** 2 kişi (biri uzman, biri meraklı/dinamik)
- **Çıktı formatı:** JSON

### Aşama 2: Diyalog Yazarı
- **Endpoint:** `http://127.0.0.1:19999/v1/chat/completions`
- **Model:** `gpt-5.4-mini`
- **Görev:** Aşama 1 çıktısını alır, doğal Türkçe karşılıklı konuşma yazar
- **Özellikler:** Geçişler, espriler, "aa gerçekten mi?" anları, ayrı ses tonları

### Aşama 3: Görsel + Ses (Opsiyonel)
- **nanobanana-2:** Thumbnail ve bölüm görselleri için prompt üretimi
- **ElevenLabs bella:** Seslendirme entegrasyonu
- **NotebookLM pipeline:** Alternatif podcast üretimi (mevcut skill ile)

## Çıktılar

- `output/plan.json` — Aşama 1 podcast akış planı
- `output/diyalog.txt` — Aşama 2 karşılıklı konuşma metni
- `output/podcast_paketi/` — Tüm dosyaların toplandığı klasör

## Gereksinimler

- `curl`, `jq` (sistem araçları)
- `python3` (opsiyonel, script için)
- Zen API'ye erişim (açık)
- Pollinations API'ye erişim (localhost:19999)

## Bardo Teması

Akademik psikoloji, felsefe ve nörobilim konularını herkesin anlayabileceği sohbet diline çevirir. Vanitas'ın melankolik-kontemplatif atmosferiyle, derin konuları samimi bir podcast ortamında işler.
