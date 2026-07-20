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
- **Psikolog:** Berkcan Ulucan
- **İletişim:** 0541 850 30 02 / bardopsikoloji@gmail.com
- **Konum:** İzmir (yüz yüze + online)
- Blog/Yazılar sayfası var ama **henüz yazı yok** — boş
- Sınav Kaygısı sayfası AEO uyumlu örnek olarak duruyor
- Potansiyel: otomatik makale üretim pipeline'ı → cron + API ile düzenli yazı
- Detaylı referans: `references/aeo-geo-psikolog.md`

## Google Ads Sorun Giderme (Psikolog İçin)

### Sık Görülen Senaryo: Tıklama Var, Dönüşüm Yok

Bardo'da yaşanan durum: **36 tıklama, 0 dönüşüm.** Tipik nedenler:

| Neden | Teşhis | Çözüm |
|-------|--------|-------|
| Çok genel anahtarlar | "psikolog İzmir" gibi yüksek rekabetli terimler | Uzun kuyruklu (long-tail) hedefle: "sınav kaygısı İzmir", "online terapi İzmir" |
| Yanlış açılış sayfası | Tıklayan anasayfaya gidiyor, randevu formunu bulamıyor | Anahtar kelimeye özel landing page hazırla |
| Zayıf CTA | "Randevu Al" butonu yeterince görünür/motive edici değil | Aciliyet + garanti ekle: "İlk görüşme ücretsiz", "Hemen randevu al" |
| Mobil uyum sorunu | Tıklamalar mobil, form mobilde çalışmıyor | Formu test et, WhatsApp yönlendirmesini belirginleştir |
| Hedef dışı tıklama | İzmir dışından tıklayan online terapiyi anlamıyor | Coğrafi hedeflemeyi daralt, reklam metninde "İzmir + Online" net belirt |

### Google Ads Kontrol Listesi (Psikolog)

1. **Anahtar kelime araştırması:** Google Keyword Planner + rakibin hangi kelimelerde reklam verdiği
2. **Uzun kuyruklu hedefleme:** "çocuk psikoloğu İzmir" → "ergenlik dönemi sınav kaygısı İzmir psikolog"
3. **Reklam metni:** [Başlık] spesifik sorun + [Açıklama] çözüm + [CTA] düşük bariyer
4. **Landing page:** Anahtar kelimeyle birebir eşleşen açılış sayfası (anki sayfa değil)
5. **Dönüşüm takibi:** WhatsApp tıklama + telefon tıklama + form gönderimi ayrı ayrı izlenmeli
6. **A/B test:** En az 2 reklam varyasyonu, 2 landing page
7. **Bütçe yönetimi:** Psikoloji anahtar kelimeleri ortalama €1-5/tıklama. Haftada €50'den başla

## Site Denetim Kontrol Listesi (Psikolog Web Sitesi)

Yeni bir psikolog sitesini denetlerken sırayla kontrol et:

### 1. Teknik SEO
- [ ] Google Search Console'a kayıtlı mı?
- [ ] Google Analytics/GA4 kurulu mu?
- [ ] Sitemap.xml var mı?
- [ ] robots.txt düzgün mü?
- [ ] SSL (HTTPS) aktif mi?
- [ ] Schema.org LocalBusiness işaretlemesi var mı? (Ad, telefon, adres, çalışma saatleri)
- [ ] Canonical URL'ler doğru mu?
- [ ] Sayfa hızı (Core Web Vitals) — mobile < 4s, desktop < 2.5s

### 2. İçerik Denetimi
- [ ] Blog sayfası boş mu? (Bardo'da olduğu gibi)
- [ ] Her hizmet için ayrı sayfa var mı?
- [ ] Google My Business dolu mu? (fotoğraf, hizmetler, yorumlar)
- [ ] "Hakkımda" sayfasında uzman detayı ve fotoğraf var mı?
- [ ] Sıkça Sorulan Sorular sayfası var mı? (FAQ schema ile)
- [ ] İletişim sayfasında form + telefon + harita + WhatsApp var mı?

### 3. Eksik Sayfalar (Bardo İçin Özel)
Bardo Psikoloji'nin eksik olduğu sayfalar, sırayla açılmalı:
- [/ ] bireysel-danismanlik/ — ayrı landing page
- [/ ] aile-danismanligi/
- [/ ] ergen-danismanligi/
- [/ ] online-terapi/
- [/ ] bagimlilik-danismanligi/
- [✓] sinav-kaygisi/ — *tek düzgün sayfa*
- [/ ] "Ödevler" sayfasının amacı netleştirilmeli
- [/ ] Blog doldurulmalı (0 yazı → en az 10 yazı ilk etapta)

### 4. Google My Business
- [ ] Kategori: "Psikolog" seçilmiş mi?
- [ ] Fotoğraflar: en az 5-10 (portre, ofis, çevre)
- [ ] Hizmetler listesi dolu mu?
- [ ] Yorum yanıtlama aktif mi? (haftada 1 kontrol)
- [ ] Gönderi paylaşımı (haftada 1-2)

### Öncelik Sırası
1. **Blog içeriği üret** (0 maliyet, en yüksek etki) — AI ile haftada 2-3 yazı
2. **Her hizmet için ayrı sayfa aç**
3. **Google My Business optimize et**
4. **Google Ads'i düzelt** (doğru anahtar kelime + landing page)
5. **Teknik SEO fix** (hız, schema, sitemap)

Detaylı referans: `references/aeo-geo-psikolog.md`

## KVKK Uyumu

- Danışan verileri yerel sunucuda, şifreli
- Hiçbir veri API üzerinden dışarı çıkmaz
- Terapi asistanı projesi ile entegre (yerel model hedefi)
