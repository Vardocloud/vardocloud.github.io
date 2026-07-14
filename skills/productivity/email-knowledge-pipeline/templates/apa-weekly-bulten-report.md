# APA Haftalık Bülten — Derin İçerik Raporu Şablonu

> **Kullanım:** Bu şablon APA (ve benzeri akademik kurum) haftalık bültenlerini işlerken kullanılır.
> Her bülten için ayrı bir bölüm açılır, her makale için metadata alanları doldurulur.
> **Versiyon:** 20 Haziran 2026 — Pipeline v4.0 formatı.

---

## Yapı

```
🧠 APA HAFTALIK BÜLTEN — [TARİH ARALIĞI]
────────────────────────────

❶ [BÜLTEN ADI] ([TARİH])

a) [Makale Başlığı] — [Yazarlar, Dergi]

📋 Araştırma Sorusu: [Ne test edilmiş? 1-2 cümle]
📊 Yöntem: [Kaç katılımcı, hangi desen, veri toplama aracı]
🔍 Bulgular: [Sayısal veri varsa belirt: N, p, etki büyüklüğü, yüzdeler]
💡 Klinik Anlamı: [Bu bulgu terapist/pratik için ne ifade ediyor?]

b) [Makale Başlığı] — ...

❷ [BİR SONRAKİ BÜLTEN]
...

📌 ÖNE ÇIKAN: [Kritik bir maddeyi vurgula — 1-2 cümle]
```

## Bilimsel Makale İçin Metadata (ADIM 2)

Her bilimsel makale için şu alanlar zorunludur:

| Alan | İçerik | Örnek |
|------|--------|-------|
| **📋 Araştırma Sorusu** | Ne test edilmiş? Neden önemli? | "Yapay zekayı terapi yedekçisi olarak kullanan hasta oranını ölçmek" |
| **📊 Yöntem** | Desen, örneklem, araç | "APA üyesi 1,200 psikologla anket, online survey" |
| **🔍 Bulgular** | Sayısal veri, istatistik | "%77 hasta AI kullanıyor, %35'i terapi yerine" |
| **💡 Klinik Anlamı** | Pratik çıkarım | "Hastalara AI kullanımını sor, dijital okuryazarlığı değerlendir" |

## Haber/Medya İçeriği İçin Metadata

| Alan | İçerik |
|------|--------|
| **Konu** | Ne hakkında? |
| **Uzmanlar** | APA üyesi hangi uzmanlar yorum yapmış? (isim + kurum) |
| **Klinik Katkı** | Edel'in perspektifine katkısı ne? |

## Etkinlik İçin Metadata (Ücretsiz — Sadece)

| Alan | İçerik |
|------|--------|
| **📅 Etkinlik Adı** | ...
| **📆 Tarih** | ...
| **📍 Yer** | online / fiziksel
| **💰 Ücret** | Sadece ücretsiz olanlar kaydedilir. Paralıysa BELİRTME, kaydetme.
| **📝 Açıklama** | 1-2 cümle
| **🔗 Link** | Kayıt/etkinlik linki

## Ücret Kuralı (KRİTİK)

- **Ücretsiz etkinlik:** Kaydedilir, başlıkta "Ücretsiz" vurgulanır
- **Ücretli etkinlik:** Kaydedilmez. Bilgi kirliliği yaratma.
- **Bilinmiyorsa:** Araştır (web_extract ile pricing sayfasını kontrol et). Bulamazsan kaydetme.

## Teslimat Formatı

Aynı formatta, ama ek olarak her bölümün sonuna "Klinik Anlamı" alanı mutlaka eklenir.
Raporun sonunda 1-2 cümle öneri/öne çıkan vurgulanır.

---

## Kullanım Akışı

1. Gmail'de apa.org domaininden mailleri tara
2. Her mailin body'sini `gmail get` ile çek, linkleri bul
3. Linkleri `curl -sIL` ile resolve et (click.info.apa.org tracking URL'leri)
4. Hedef sayfaları `web_extract` ile çek (Firecrawl, Imperva/Incapsula'yı aşar)
5. Her makale için yukarıdaki metadata alanlarını doldur
6. Wiki'ye kaydet: `~/wiki/apa-articles/YYYY-MM-<slug>.md` (İngilizce)
7. NotebookLM: 1 deneme, başarısızsa geç
8. Raporu yapılandırılmış formatta sun
