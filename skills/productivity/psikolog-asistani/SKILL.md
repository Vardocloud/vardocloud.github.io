---
name: psikolog-asistani
description: "Psikologlar için özelleştirilmiş Vanitas paketi — danışan takip, randevu, seans notları, içerik stratejisi."
version: 1.0.0
metadata:
  hermes:
    tags: [psikoloji, asistan, bardo, danisan, randevu]
    category: productivity
---

# Psikolog Asistanı (AI Trainer Psikolog)

Psikologlar için beyaz etiketli Vanitas paketi.

## Paket İçeriği

| Özellik | Açıklama |
|----------|----------|
| Randevu takibi | Google Calendar entegrasyonu, boş slot önerisi |
| Danışan kaydı | Wiki tabanlı danışan profili (KVKK uyumlu) |
| Seans notları | Otomatik şablon, ses kaydı → metin (isteğe bağlı) |
| İçerik stratejisi | Instagram/LinkedIn için haftalık içerik takvimi |
| 7/24 iletişim | Telegram/WhatsApp üzerinden danışan soruları |

## İş Modeli

- **Hedef kitle:** İzmir özel klinik psikologları
- **Fiyat:** 3.000-5.000 TL/ay (sınırsız kullanım)
- **Demo:** 1 hafta ücretsiz deneme
- **Teslim:** 48 saatte kurulum + 2 saat eğitim

## Tetikleyiciler

- "yeni danışan"
- "randevu oluştur"
- "seans notu"
- "danışan ara"
- "içerik takvimi"
- "APA makale" / "APA özet" / "APA ne var" / "APA webinar" / "APA eğitim"

## APA Webinar Keşif ve Kayıt (3 Haz 2026)

Edel APA webinar'larını sorduğunda:

1. **Önce NotebookLM APA Bilgi'ye sor** — `cross_notebook_query` veya `notebook_query` ile mevcut içerikleri tara
2. **Kaynak içeriklerini çek** — `source_get_content` ile tam metni al, Edel'e özetle
3. **Kayıt linki ara** — `web_search` ile güncel kayıt sayfalarını bul

### 🆓 Ücretsiz vs 💰 Ücretli Ayrımı (KRİTİK)

Edel temel APA üyeliğiyle gelen ücretsiz içerikleri, CE kataloğundaki ücretli webinarlarla KARIŞTIRMA:

| Ücretsiz (Üyelik Dahil) | Ücretli (Ekstra) |
|---|---|
| "You're Invited" bülteni webinarları | CE kataloğu canlı webinarlar |
| "Regulation, AI, and Mental Health Care" | Unlimited CE Subscription |
| APA Labs Live (9 Haz 2026) | APA 2026 Convention |
| Monitor CE Corner (5 kredi/yıl) | Generative AI on-demand CE |
| APA Community Hub podcast/e-kitap | |

**Webinar linki verirken MUTLAKA ücret durumunu belirt.** Edel "paralı görünüyor" dediğinde yukarıdaki tabloyu referans al.

### Kayıt Akışı
1. MyAPA girişi: https://sso.apa.org/apasso/idm/apalogin
2. "You're Invited" bültenine abone ol (1. ve 3. Perşembe)
3. Member Update → webinar duyuruları
4. Detaylı free-vs-paid referans: `references/apa-free-vs-paid.md`

## APA Makale İşleme (30 May 2026)

APA Monitor'dan gelen makaleleri işlerken:

1. **web_extract** ile makaleyi çek (ilk 5K genelde yeterli)
2. **Pollinations webSearch** ile ana bulguları teyit et (Incapsula'yı bypass eder)
3. **Türkçe özet** formatı:
   - 🧠 ANA FİKİR (1-2 cümle)
   - 🔑 KRİTİK BULGULAR (maddeler)
   - 👥 ÖNE ÇIKAN İSİMLER (tablo: isim, rol, ne yapıyor)
   - 🇹🇷 TÜRKİYE'DEKİ PSİKOLOG İÇİN ÇIKARIMLAR (pratik + içerik fikri)
4. **NotebookLM** "APA Bilgi" notebook'una kaydet
5. Edel'e sunarken emoji seçim butonları kullan (bkz. sohbet skill)

## AEO/GEO İçerik Optimizasyonu (Psikolog Web Sitesi)

### Temel Strateji (SEO → AEO → GEO)

| Katman | Odak | Psikolog Sitesi İçin |
|--------|------|----------------------|
| **SEO (Temel)** | Site hızı, mobil uyum, teknik tarama | Google'da bulunma |
| **AEO (Answer Engine Opt.)** | İlk 40-60 kelimede cevap, SSS şeması, soru başlıkları | ChatGPT/Perplexity cevaplarında çıkma |
| **GEO (Generative Engine Opt.)** | Somut veri, güncellik, çapraz platform varlığı | AI'ın **önermesi** |

### AEO Kuralları (Makale/Blog İçin)

1. **İlk 40-60 kelime** — sorunun cevabını en başta ver
2. **Başlıkları soru formatına çevir** — "Sınav Kaygısı Nedir?" gibi
3. **SSS bloğu ekle** — sayfanın altında FAQ schema işaretlemesiyle
4. **Format:** Liste yapıları, karşılaştırma tabloları, "X vs Y" kullan

### GEO Kuralları (AI'ın Önermesi İçin)

1. **Somut veri/istatistik kullan** — düz metne göre %30 daha fazla görünürlük
2. **Son 90 günde güncelle** — güncel içerik 3 kata kadar daha fazla alıntılanır
3. **Çapraz platform varlığı** — YouTube, LinkedIn, Google My Business, yerel dizinler
4. **Entity netliği** — markanın kim olduğu, ne yaptığı net olmalı

### Prompt (İçerik Dönüşümü İçin)

```
Bu içeriği AI uyumlu hale getir:
1. Cevabı ilk 40-60 kelimede ver
2. Başlıkları soru formatına çevir
3. Somut istatistik/veri ekle
4. SSS bloğu ve şema işaretlemesi öner
5. Liste/karşılaştırma formatı kullan
```

### Bardo Psikoloji Sitesi Notları

- Site: **bardopsikoloji.com.tr** — Tailwind CSS + Alpine.js + Cloudflare
- Blog/Yazılar sayfası var ama **henüz yazı yok** — boş
- Sınav Kaygısı sayfası AEO uyumlu örnek olarak duruyor
- Potansiyel: otomatik makale üretim pipeline'ı → cron + API ile düzenli yazı
- Detaylı referans: `references/aeo-geo-psikolog.md`

## KVKK Uyumu

- Danışan verileri yerel sunucuda, şifreli
- Hiçbir veri API üzerinden dışarı çıkmaz
- Terapi asistanı projesi ile entegre (yerel model hedefi)
