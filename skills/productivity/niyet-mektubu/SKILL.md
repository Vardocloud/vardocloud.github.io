---
name: niyet-mektubu
description: "Akademik niyet mektubu (Statement of Purpose / SOP) yazımı — lisansüstü başvurular için. Transkript ve CV'den veri çıkar, yapılandır, yaz, humanize et."
version: 1.0.0
author: Vanitas (Edel için)
---

# Niyet Mektubu (SOP) Yazımı — Edel İçin

## Ne Zaman Kullanılır

- Yüksek lisans / doktora başvuruları için niyet mektubu (Statement of Purpose) gerektiğinde
- Edel "niyet mektubu", "SOP", "statement of purpose", "başvuru yazısı" dediğinde
- Bir program için kişiselleştirilmiş akademik başvuru metni gerektiğinde

## İş Akışı (5 Aşama)

### Aşama 1: Veri Topla

Adayın şu belgelerinden veri çıkar:

| Kaynak | Ne Çıkarılacak | Yöntem |
|---|---|---|
| **Transkript** | GPA trendi, öne çıkan dersler, zayıf/güçlü dönemler | `pdftotext` ile terminal (ctx_execute_file binary PDF'de çalışmaz — bkz. Pitfall #1) |
| **CV / LinkedIn** | Stajlar, sertifikalar, iş deneyimi, projeler, beceriler | `pdftotext` ile terminal |
| **Sohbet** | Motivasyon hikayesi, kariyer hedefi, program tercih nedeni | Doğrudan Edel'e sor |

**Toplanması gereken spesifik veriler:**

1. **Entelektüel motivasyon:** Adayı bu alana yönelten spesifik bir anı/deneyim/gözlem
2. **Akademik hazırlık:** Hangi derslerde parladı, tez/bitirme projesi var mı, araştırma becerisi
3. **Klinik/uygulamalı deneyim:** Stajlar, gönüllülük, saha çalışması, kendi pratiği
4. **Kariyer hedefi:** Terapist mi, araştırmacı mı, akademisyen mi? Doktora düşünüyor mu?
5. **Program uyumu:** Neden BU program — spesifik hocalar, laboratuvarlar, klinik imkanlar

### Aşama 2: SOP'u Yapılandır

Admit-lab.com'dan (Dr. Philippe Barr, eski profesör ve kabul komitesi danışmanı) alınan 4 sinyalli yapı:

```
1. AÇILIŞ — Spesifik bir deneyim/anı ile başla
   ❌ "I am writing to apply..."
   ❌ "İnsanlara yardım etmek istiyorum..."
   ✅ "Adliyede geçirdiğim ilk gün..."

2. AKADEMİK HAZIRLIK — Hangi dersler, hangi beceriler
   GPA düşükse: yükseliş hikayesi olarak sun
   GPA yüksekse: tutarlı başarı olarak sun

3. KLİNİK / UYGULAMALI DENEYİM — Stajlar, sertifikalar, pratik
   Sadece "yaptım" değil — "ne öğrendim, nasıl değiştim"

4. PROGRAM UYUMU + KARİYER HEDEFİ — Neden BU program
   Jenerik "iyi üniversite" → KOMİTE ELER
   Spesifik: hocalar, laboratuvar, klinik imkanlar
```

**Kapanış:** Kısa, direkt. "Umutluyum", "heyecanlıyım" gibi jenerik ifadeler olmadan.

### Aşama 3: Yaz

**Kural:** Karusal metinleri ASLA sohbet modeliyle yazma. İki seçenek:

| Yöntem | Ne Zaman |
|---|---|
| **GPT 5.4 Mini (Yazar ajanı)** | Pollinations API key mevcutsa — birincil yöntem |
| **Sohbet modeli + Humanizer** | API key yoksa fallback — ama sonra humanizer'dan MUTLAKA geçir |

GPT 5.4 Mini için: Pollinations `chatCompletion` API'sine detaylı sistem prompt'u + kullanıcı prompt'u gönder.

Sistem prompt'unda şu AI kalıplarını YASAKLA:
- "pivotal", "crucial", "landscape", "tapestry"
- "additionally", "moreover", "furthermore"
- "not only...but also", "in conclusion"
- Em dash (—)
- "transformative", "groundbreaking", "profound"

### Aşama 4: Humanize Et

Humanizer skill'indeki 29 AI pattern'ine karşı tara:

**En sık yakalanan pattern'ler (Türkçe SOP için):**
- "berraklaştı", "derinleştirebileceğim" gibi süslü kelimeler
- "somut avantaj" gibi CV/pazarlama dili
- "inanıyorum" ile biten jenerik kapanışlar
- Eşit uzunlukta cümleler (burstiness düşük)
- Üçlü kalıplar ("X, Y ve Z")

**Humanizer adımları:**
1. Metni oku, AI pattern'lerini işaretle
2. Her pattern'i doğal alternatifle değiştir
3. Cümle uzunluklarını karıştır (bazıları 3 kelime, bazıları 20)
4. Son bir "AI kokuyor mu?" okuması yap

### Aşama 5: AI Detection Test (Opsiyonel)

Edel isterse, bitmiş metni bir AI detection tool'una sok:

| Araç | Güçlü Yönü | Turnitin Bypass | Ücret |
|---|---|---|---|
| **StudyAgent** | Akademik yazı odaklı, atıf korumalı | ✅ | 500 kelime/gün ücretsiz |
| **StealthGPT** | GPTZero, Originality.ai bypass | ✅ | Ücretli |
| **WriteHuman AI** | Doğal ritim, cümle çeşitliliği | ⚠️ | Freemium |
| **QuillBot** | Erişilebilir, bilindik | ❌ 2025'te yakalanıyor | Freemium |

**Uyarı:** CEOWorld 2025 karşılaştırması: "Akademik kariyeriniz söz konusuysa, tamamen ücretsiz bir araca güvenmek ciddi risktir."

Detaylı araç karşılaştırması: `references/ai-detection-bypass.md`

### Aşama 6: Edel'e Sun

Final metni Telegram'da göster. Edel son rötuşları yapacak — hiçbir araç %100 insan dokunuşunun yerini tutmaz.

---

## Pitfall'lar

### Pitfall #1: ctx_execute_file binary PDF'de çalışmaz

`ctx_execute_file` PDF gibi binary dosyaları UTF-8 decode edemez → `UnicodeDecodeError`.

**Doğru yöntem:**
```bash
pdftotext "/path/to/file.pdf" - 2>&1 | head -200
```

`fitz` (PyMuPDF) de terminal üzerinden Python ile kullanılabilir. Ama en hızlısı `pdftotext`.

### Pitfall #2: GPA düşükse saklama, hikayeleştir

2.33 GPA'i "zayıflık" olarak sunma. Son dönem 3.06 yapmışsa:
> "Eğitimimin ilk yıllarında net bir klinik yönelimim yoktu... Son sınıfa geldiğimde Klinik Psikoloji, Psikopatoloji dersleriyle birlikte hangi alanda ilerlemek istediğim netleşti. Son dönem GPA'imin 3.06'ya çıkması da bunun göstergesiydi."

### Pitfall #3: Jenerik program uyumu → komite eler

"NEU iyi bir üniversite olduğu için" → ❌
"NEU'nun hastane bünyesinde staj imkanı sunması ve KKTC'de konumlanması" → ✅

Her zaman spesifik bir nedene bağla.

### Pitfall #4: Pollinations API key eksikse

API key yoksa `chatCompletion` auth hatası verir. Fallback: sohbet modeliyle yaz, sonra humanizer'dan geçir.

---

## Companion Skill'ler

- **email-workflow:** Aynı başvuru sürecindeki e-postalar (referans talebi, belge iletimi) için
- **humanizer:** Metindeki AI izlerini temizlemek için (29 pattern)
- **ocr-and-documents:** PDF'lerden metin çıkarma (transkript, CV)
- **psikolog-asistani:** Psikolog pratiği yönetimi (SOP'un konusu değil, companion)

## Ekli Dosyalar

- `templates/europass-cv.html` — Europass formatında CV için HTML şablonu (WeasyPrint ile PDF'e çevrilir)
- `references/cv-yl-basvuru-rehberi.md` — CV yapım rehberi ve Europass format detayları
- `references/ai-detection-bypass.md` — AI detection araç karşılaştırması

## PDF Çıktısı (Europass CV)

CV'yi Europass formatında PDF'e çevirmek için:

```python
from weasyprint import HTML
HTML('templates/europass-cv.html').write_pdf('output.pdf')
```

Container'da LibreOffice yoktur — WeasyPrint birincil yöntemdir.

---

## Kaynaklar

- **SOP Yapısı:** Dr. Philippe Barr, Admit Lab — [Statement of Purpose for Psychology: What Committees Want](https://admit-lab.com/blog/statement-of-purpose-for-masters-in-psychology/)
- **AI Detection:** CEOWorld 2025 karşılaştırması — `references/ai-detection-bypass.md`
- **Humanizer Pattern'leri:** Wikipedia WikiProject AI Cleanup — 29 pattern
- **Stanford Academic Advising:** Referans mektubu ve SOP zaman planlaması
- **MIT Drennan Lab:** Başvuru belgelerinin tek e-postada toplanması
- **CV Yapımı (YL Başvurusu):** `references/cv-yl-basvuru-rehberi.md` — referans ekleme kuralı, research interests, bölüm sırası, Edel'in Claude.ai+Vanitas çalışma akışı
