---
name: ai-content-automation
description: "AI-powered content creation automation for YouTube/social media passive income — tool stack, workflow design, niche selection, monetization."
version: 1.0.0
metadata:
  hermes:
    tags: [content, automation, youtube, ai, passive-income, social-media]
    category: media
---

# AI Content Automation

Using AI tools to automate content creation for YouTube/social media for passive income. Covers "faceless YouTube" / AI-powered channel automation.

## Tetikleyiciler

- "YouTube otomasyonu" / "YouTube automation"
- "AI içerik üretimi" / "AI content creation"
- "pasif gelir YouTube" / "passive income"
- "faceless channel" / "sesiz kanal"
- "Viewmax" / "n8n" / "Make.com" content workflow
- Edel "AI araçları keşfet" dediğinde

## Core Tool Stack

| Araç | Ne İşe Yarar | Maliyet |
|------|-------------|---------|
| **Claude / GPT** | Script yazma, içerik araştırma | API/abonelik |
| **ElevenLabs / Edge TTS** | Seslendirme (AI voiceover) | Edge: ücretsiz, Eleven: $5/ay |
| **CapCut / Canva** | Video montaj, altyazı, thumbnail | Ücretsiz tier yeterli |
| **Make.com / n8n** | Otomasyon zinciri | Make: 1000 ops/ay ücretsiz, n8n: self-host ücretsiz |
| **Pexels / Pixabay** | Stock görsel/video (ücretsiz) | Ücretsiz |
| **YouTube Studio** | Yayın, monetizasyon, analitik | Ücretsiz |
| **Viewmax** | Short video aracı | $14-49/ay, Trustpilot 2.9/5 — önerilmez |

## YouTube Otomasyonu Workflow

### 1. Niche Seçimi

**İyi nişler (düşük rekabet + yüksek talep):**
- Kitap özetleri (1 video = 1 kitap)
- Psikoloji konseptleri (Jung, stoacılık, bilinç)
- Bilimsel merak (beyin, zihin, davranış bilimleri)
- Tarih / biyografiler (az bilinen hikayeler)
- Felsefe (kısa düşünce deneyleri)
- Belgesel tarzı kısa belgeseller

**Kaçınılması gerekenler:**
- "Kripto para", "çabuk zengin ol" — doymuş pazar
- Telif hassas konular (müzik, film sahneleri)
- AI sesi bariz belli olan nişler (kullanıcı fark eder, izlenme düşer)

### 2. Script Üretimi (AI)

Prompt şablonu:
```
Write a [5-7 minute] YouTube script about [topic].
Structure: hook (first 15s), explanation, examples, key takeaways, CTA.
Use conversational Turkish. Include 3-4 visual cues [BRoll: ...].
```

Hedef: ~1000-1500 kelime (5-7 dk video)

### 3. Seslendirme

1. **Edge TTS** (birincil — ücretsiz, Türkçe destek):
   ```python
   # pip install edge-tts
   import edge_tts
   communicate = edge_tts.Communicate(script, "tr-TR-EmelNeural")
   await communicate.save("output.mp3")
   ```
2. **ElevenLabs** (opsiyonel — daha doğal, Türkçe sınırlı):
   - $5/ay başlangıç
   - Multilingual v2 modeli

### 4. Görsel / Video Montajı

**Seçenek A: CapCut** (manuel ama hızlı)
- Görsel + metin + AI ses senkronizasyonu
- Otomatik altyazı

**Seçenek B: Python + moviepy** (programatik, ölçeklenebilir)
```python
from moviepy.editor import *
# Görselleri sırayla yükle, ses ile senkronize et
```

**Seçenek C: Stock footage** (Pexels/Pixabay)
- API ile otomatik görsel çekme
- `pexels-api` Python paketi

### 5. Otomasyon Zinciri (n8n/Make.com)

Temel akış:
1. Claude → Script üret (markdown)
2. Edge TTS → Ses dosyası (mp3)
3. Pexels API → İlgili görseller
4. MoviePy → Video montajı
5. YouTube API → Yükle + zamanla

### 6. Yayın Takvimi

- **Haftada 3 video** minimum büyüme
- Tutarlı saat/gün
- Shorts + uzun video mix
- Thumbnail: Canva'da şablon yap, her videoda güncelle

## Monetizasyon

| Gelir Türü | Ne Zaman | Tahmini |
|-----------|----------|---------|
| YouTube Ads | 1K abone + 4K saat izlenme | $1-10/1K görüntülenme |
| Affiliate link | İlk günden | Değişken |
| Sponsorship | 10K+ abone | $100-500/video |
| Digital ürün | İlk günden | Değişken |

**Gerçekçi beklenti:**
- İlk 3 ay: $0-50 (monetizasyon kapalı)
- 3-6 ay: $50-300/ay (monetizasyon açar)
- 6-12 ay: $300-2000/ay (düzenli içerik)
- 12+ ay: nişe bağlı, stabil büyüme

## Başlangıç Planı (İlk Hafta)

| Gün | Yapılacak |
|-----|-----------|
| 1 | Niche seç + kanal aç |
| 2 | 3 script yaz (Claude ile) |
| 3 | Edge TTS + CapCut ile ilk video |
| 4 | YouTube'a yükle + thumbnail |
| 5 | n8n/Make otomasyon taslağı |
| 6-7 | 2. ve 3. videoyu üret + yayınla |
| 30 | Değerlendir: izlenme, abone, feedback |

## Bilinen Tuzaklar (Pitfalls)

- **Monetizasyon gecikmesi:** 1K abone + 4K saat izlenme şartı — ilk 3-6 ay $0 kazanç normal
- **AI sesi barizse düşük izlenme:** Edge TTS Türkçe sesleri (Emel) iyi. ElevenLabs daha iyi. Test et, karar ver.
- **Telif:** Stock görsel/müzik lisansına dikkat. YouTube Content ID uyarısı yiyebilirsin.
- **YouTube politikası:** Tamamen AI üretimi içerik için "Altered or synthetic content" etiketi ekle.
- **Dağıtım:** İçerik üretmek yetmez — SEO (başlık, açıklama, etiket) + tanıtım da gerek.
- **Zaman:** Otomasyonla bile her video ~2-3 saat. Haftada 3 video = ~6-9 saat.
- **Viewmax önerilmez:** Trustpilot 2.9/5, $14-49/ay, aynı işi ücretsiz Edge TTS + CapCut ile yapabilirsin.
- **Tutarlılık:** 2 haftada 1 video atarsan büyüme olmaz. Haftada 3 minimum.
