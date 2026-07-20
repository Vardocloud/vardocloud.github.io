# Podcast Bölümü — Yeni mi, Eski mi? Tarih Belirleme Heuristiği

APA cron'da Speaking of Psychology veya diğer podcast'lerde yeni bölüm bulduğunda, bölümün "yeni yayınlanmış" mı yoksa "atlanmış eski bölüm" mü olduğunu belirlemek önemlidir. Eski bölümleri raporlamak [SILENT] protokolünü ihlal eder.

## Hızlı Kontrol Listesi

| Gösterge | Yeni | Eski (Atlanmış) |
|----------|------|-----------------|
| Bölüm numarası | En son bilinen numaradan yüksek | Aynı veya düşük |
| Bonus bölüm? | Dikkat — her zaman değerlendir | Tarih referansı ara |
| İçerikte zaman referansı | "This month", "last week", "new study" | "Earlier this year", belirli bir ay/etkinlik adı |
| Survey/source yılı | Current year | Previous year |
| Sosyal medya tanıtımı | Son 7 gün içinde | Haftalar/aylar önce |

## Bonus Bölümler (En Riskli)

Bonus bölümlerin numarası olmaz. Tarihlerini belirlemek için:

1. **İçerikteki en son zaman referansını bul:**
   - "APA 2025 Stress in America survey" → 2026 başı veya ortası
   - "Mental Health Awareness Month" (Mayıs) → Mayıs ayı kaydı
   - "APA 2026 Convention, August 6-8" → Ağustos öncesi kayıt
   - "New study published in Journal of X this month" → görece güncel

2. **LinkedIn/Instagram cross-reference:**
   - APA'nın resmi hesabından tanıtım paylaşımı varsa, paylaşım tarihi ≈ yayın tarihi
   - Konuğun kendi hesabındaki paylaşım da aynı işi görür
   - Instagram shortcode'ları base64 benzeri encoding kullanır — çözmeye çalışma, paylaşımın metnine bak

3. **Eğer tarih hâlâ belirsizse:**
   - Son 7 gün içinde yayınlandığına dair GÜÇLÜ bir kanıt yoksa → *atlanmış eski içerik* varsay
   - Index'e ekle ama raporlama — eski içerik sessizce indekslenir

## Verimsiz Yöntemler (Kaçın)

- Sayfa kaynağında `article:published_time` meta etiketi arama (APA podcast sayfalarında genelde yok)
- JSON-LD structured data scraping (süre ve isim içerir, tarih içermez)
- Browser console ile DOM'da tarih arama (tool call israfı)
- RSS feed scraping (mevcut değil veya eski)

## Örnek: "Managing Stress in Turbulent Times" Bonus Episode (20 Tem 2026)

- **İçerik ipucu:** "APA's 2025 Stress in America survey" → survey bir önceki yıla ait → 2026 kaydı
- **LinkedIn referansı:** APHA CEO'su paylaşmış, "Mental Health Awareness Month" demiş → Mayıs 2026
- **Sonuç:** 2+ aylık bölüm, yeni değil → index'e ekle ama raporlama
- **Tool call maliyeti:** 6 web_search + 2 web_extract + 1 browser_navigate + 2 browser_console (ÇOK FAZLA — ilk 2 adım yeterliydi)

## Kural

> Bir podcast bölümünün yeni olduğunu doğrulamak için 2'den fazla tool call harcama. İlk 2 adımda (bölüm numarası + içerik zaman referansı) karar veremiyorsan → eski varsay + index'e ekle + raporlama.
