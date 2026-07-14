# APA Pipeline v5.0 — Çok Kanallı Tarama + İçerik Kategorizasyonu

> Kullanıcı tarafından 25 Haziran 2026'da tanımlanan genişletilmiş APA tarama protokolü.
> NotebookLM Pipeline cron modunun üzerine bindirilmiş beş kanallı tarama sistemi.

## Beş Kanal

| Kanal | Kaynak | İçerik Türü | İşlem |
|-------|--------|-------------|-------|
| **A — Gmail** | `apa.org` domaininden son 7 günlük e-posta bültenleri | Six Things, Media Watch, Science Spotlight, Practice Update, Editor's Choice, Advocacy | Her bülten türüne göre kategorize et, içeriği çıkar |
| **B — Monitor & Press Releases** | `web_search site:apa.org/monitor/2026/06` + `/news/press/` | Dergi makaleleri, basın açıklamaları | Tam metin çek, wiki'ye kaydet |
| **C — Speaking of Psychology** | `/news/podcast` veya Media Watch newsletter cross-ref | Sesli röportaj/podcast bölümleri | Başlık + konuşmacı + ana argüman + neden dinlemeli |
| **D — Events** | `apa.org/events` | Webinar, seminer, konferans | **Sadece ücretsiz** etkinlikleri kaydet |
| **E — Division İçerikleri** | Division 12 (Klinik) ve Division 29 (Psikoterapi) | Özel bültenler, CE fırsatları | Varsa işle |

## Newsletter Türleri ve Ayırt Edici Özellikler

| Bülten | Sıklık | İçerik | İşlem Önceliği |
|--------|--------|--------|----------------|
| **Six Things** | Haftalık (Salı) | 6 madde: genellikle klinik pratik + araştırma + güncel konular. Her biri 1-2 paragraf. "Psychologists We're Talking About" bölümü içerir. | 🥇 En kapsamlı, her maddeyi ayrı işle |
| **Media Watch** | Haftalık (Perşembe) | Psikolojinin medyada temsili, popüler kültürde psikoloji. **Speaking of Psychology podcast bölümlerini cross-reference eder.** | 🥇 Podcast keşfi için kritik |
| **Science Spotlight** | Haftalık | Yeni araştırma makaleleri, etkinlik duyuruları. Genelde 3-4 araştırma + etkinlik. | 🥇 Araştırma kanalı |
| **Practice Update** | Haftalık | Klinik pratik, CE fırsatları, federal düzenlemeler. | 🥈 Klinik pratik odaklı |
| **Editor's Choice** | Haftalık (Cuma) | APA dergilerinden "editörün seçtiği" makaleler. 5-7 makale özeti. | 🥈 Her makale için ayrı kaynak |
| **Advocacy** | Haftalık | Psikolog hakları, yasal düzenlemeler, savunuculuk. | 🥉 Sadece belirgin değişiklik varsa |
| **CE Roundup** | Aylık | Sürekli eğitim fırsatları. | 🥉 Kaydetme, etkinlik listesine ekle |
| **Membership/Promosyon** | Ara sıra | APA üyelik promosyonları. | ⚫ **ATLA** |

## Medya Keşfi (Media Watch → Speaking of Psychology)

Media Watch bülteni sık sık yeni Speaking of Psychology bölümlerine atıf yapar.
Örnek pattern: "In this week's Speaking of Psychology podcast, [isim] discusses [konu]..."

**Keşif sırası:**
1. Media Watch bültenini tara → podcast reference var mı kontrol et
2. Varsa: başlık + konuşmacı + konuyu çıkar (bülten genelde 1-2 cümle özet verir)
3. Yoksa: `web_search` veya `web_extract` ile `/news/podcast` sayfasını kontrol et

## İçerik Kategorizasyonu

Her içerik şu kategorilerden BİRİNE atanır:

- 🧠 **KLİNİK PRATİK** — Tedavi protokolleri, terapi yöntemleri, vaka çalışmaları, klinik rehberler, CE fırsatları
- 🤖 **AI × PSİKOLOJİ** — AI değerlendirme araçları, dijital terapi, yapay zeka etiği, chatbot'lar
- 📈 **KARİYER & GELİŞİM** — CE fırsatları, sertifikalar, psikolog hakları, kariyer kaynakları, federal düzenlemeler
- 🔬 **ARAŞTIRMA** — Yeni çalışmalar, meta-analizler, güncel bulgular, metot yenilikleri
- 📅 **ETKİNLİK** — Webinar, seminer, konferans (sadece ücretsiz)

## İçerik Formatları

### Bilimsel Makale / Araştırma (🔬 veya 🧠)
```
1. **Ne anlatıyor?** — Yazının temel sorusu, neyi araştırmış (1-2 cümle)
2. **Ne diyor?** — Temel bulgular, varsa çarpıcı veri
3. **Bunun anlamı ne?** — Klinik/pratik çıkarım, "Yani..."
4. **Kaynak** — Yazar/lar, dergi, yıl
```
Uzunluk: Haber → 3-5 cümle. Normal makale → 5-10 cümle (2 paragraf). Uzun derleme → 10-15 cümle (3-4 paragraf).

### Podcast (🎧)
```
Kim anlatmış? → Ne diyor? → Neden dinlemeli? (3-5 cümle)
```

### Etkinlik (📅)
```
Tarih, konu, konuşmacılar, ücretsiz mi, kayıt linki
```

## Rapor Formatı

```
🧠 APA GÜNLÜK — [TARİH]
────────────────────

📋 KATEGORİ 1: [Klinik Pratik / AI×Psikoloji / vs.]

❶ [Makale Başlığı]
Ne anlatıyor? → ...
Ne diyor? → ...
Bunun anlamı ne? → Yani ...
📎 Kaynak: [Yazar, Dergi, Yıl]

❷ [İkinci makale]
...

📋 KATEGORİ 2: ...

🎧 Speaking of Psychology: [Bölüm başlığı]
...

📅 ÖNE ÇIKAN ETKİNLİK: ...

📌 ÖZET: Bu gün APA'da öne çıkan konu: [bir cümle]
```

## NotebookLM Kayıt

ID: `c44469fe-a69a-4a86-8dd8-756c2f365109` ("APA Bilgi")

Her yeni içerik için:
1. `notebook_get` ile mevcut kaynakları kontrol et → duplicate atla
2. `source_add(type="url"` veya `type="text"`) ile ekle
3. Başlığa kategori emoji'sini ekle: `[🧠 Klinik] veya [🤖 AI] veya [📈 Kariyer]`

Eğer NotebookLM auth stale ise (common): geç, hata yüzünden pipeline'ı durdurma. Wiki dosyası birincil teslimattır, NotebookLM bonus.

## Öncelik Sırası

1. 🤖 AI + psikoloji makaleleri → her zaman ilk işle
2. 🧠 Klinik uygulama → ikinci öncelik
3. 🔬 Yeni araştırma → üçüncü öncelik
4. 📈 Kariyer/federal → zaman kalırsa
5. 📅 Etkinlik → direkt formatla, derin işleme gerekmez

## Six Things — Özel İşlem (En Dense Bülten)

Six Things haftalık 6 maddelik bültendir. Her madde:
- Farklı bir kategoriye ait olabilir (AI, klinik, araştırma, kariyer)
- Alt başlık + kısa açıklama + link formatındadır
- Sonunda "Psychologists We're Talking About" bölümü (2-3 kişi)
- **Her madde ayrı ayrı işlenmeli** — bir bülten 6 farklı wiki dosyası demek olabilir

Six Things'i tararken: her başlık için index.md'de duplicate kontrolü yap (bazı maddeler daha önce başka kanaldan işlenmiş olabilir).
