# Bundle Gündem: Haber Toplama Stratejisi

> Bu referans dokümanı, Bundle Gündem cron job'u çalışırken haber toplamak için kullanılan stratejiyi açıklar.
> Deneyim: 2026-06-14 — web_search haber sorgularında güvenilmez çıktı, web_extract çözümü keşfedildi.

## Problem: web_search Haber Sorgularında Güvenilmez

`web_search` haber sorgularında (ör: "latest news June 2026", "technology news") düşük kaliteli sonuçlar döndürür:
- Çin SEO spam'i (baidu.com, zhihu.com)
- Instagram/YouTube bağlantıları
- İlgisiz sözlük/ürün sayfaları
- Sonuçlar çoğu zaman haberle ilgili DEĞİL

**web_search haber taraması için birincil araç olarak güvenilmez.**

## Çözüm: web_extract ile Doğrudan Haber Portalları

Doğrudan haber portallarının ana sayfasını `web_extract` ile çek:

### Çalışan Kaynaklar

| Site | URL | İçerik Tipi |
|------|-----|-------------|
| BBC News | `https://www.bbc.com/news` | Genel haber (20+ başlık) |
| BBC Technology | `https://www.bbc.com/news/technology` | Teknoloji |
| BBC Business | `https://www.bbc.com/news/business` | Ekonomi/piyasalar |
| ScienceDaily | `https://www.sciencedaily.com/news/top/science/` | Bilim (atıflı araştırma) |

### web_extract Avantajları

1. **Yüksek kaliteli içerik** — Kurumsal portallar temiz yapılandırılmış içerik
2. **Güncel** — Son 24 saatteki haberler ana sayfada
3. **Otomatik özet** — web_extract LLM-summarized mode ile büyük sayfaları özetler
4. **Kaynak URL** — Her haberin linki doğrudan mevcut, wiki'ye eklenebilir
5. **Hızlı** — delegate_task'a göre çok daha hızlı (tek web_extract çağrısı)

### Kullanım Sırası

1. Önce `web_extract(["https://www.bbc.com/news"])` — en geniş haber yelpazesi
2. Sonra kategorilere göre derinleş: `/news/technology`, `/news/business`
3. Bilim için `https://www.sciencedaily.com/news/top/science/`
4. web_search sadece spesifik konu araştırması için yedek

### Uyarılar

- **Pollinations perplexity web search** API key gerektirir — key ayarlanmamışsa hata verir
- **web_extract özeti yanlış anlayabilir** — kritik haberlerde orijinal kaynağı kontrol et
- **Deduplication** — processed_titles.md ile haber başlıklarını karşılaştır, daha önce işlenmişi atla
