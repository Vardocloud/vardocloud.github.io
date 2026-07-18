# Para Dergisi Kaynak Tarama Workflow'u

## Kaynaklar

1. **Web sitesi:** paradergi.com.tr — makaleler, analizler, piyasa verileri
2. **X/Twitter:** @ParaDergisi — dergi kapağı duyuruları (detaylı içerik yok)
3. **Instagram:** @paradergisi — kapak görselleri, reels

## Tarama Stratejisi

### Aşama 1: Ana Sayfa + URL Tarih-Deseni Keşfi

```python
# Ana sayfa
web_extract(["https://www.paradergi.com.tr/"])

# Bu ayki makaleler (URL'de /kategori/YYYY/MM/slug yapısı)
web_search("site:paradergi.com.tr 2026/07")

# Geçen aydan kalanları yakala
web_search("site:paradergi.com.tr 2026/06")
```

**Neden bu teknik?** Para Dergisi (ve çoğu Türk haber sitesi) URL'lerinde tarih kullanır:
`/finans/2026/07/16/uzun-vade-icin-onerilen-23-hisse`
Bu deseni `site:domain.com.tr YYYY/MM` ile aramak, son makaleleri bulmanın en hızlı yoludur.

### Aşama 2: X/Twitter Taraması — Çok Aşamalı Fallback

X/Twitter ana sayfası (`browser_navigate`) **çoğu zaman pinned/eski tweet'leri gösterir**, güncel içeriği değil. Bunun için:

```
# Aşama 2a: web_search ile tweet URL keşfi
web_search("from:@ParaDergisi since:2026-07-01")

# Aşama 2b: Bulunan tweet ID'lerini doğrudan extract et
web_extract(["https://x.com/ParaDergisi/status/<ID>"])

# Aşama 2c: (Opsiyonel) Browser snapshot — sadece yukarıdakiler başarısız olursa
browser_navigate("https://x.com/ParaDergisi")
```

**Not:** Para Dergisi'nin X hesabı sadece dergi kapağı duyurusu yapar (`"Para Dergisi'nde bu hafta.."`). Tweet metninde detaylı içerik yoktur. Detaylı haber için web sitesi kullanılır.

### Aşama 3: Makale İçerik Çekme

En önemli makaleleri `web_extract` ile detaylı çek. Para Dergisi'nde öncelikli konular:
- Hisse önerileri / portföy listeleri
- Halka arz haberleri
- BIST/piyasa yorumları
- Makroekonomik veri analizleri
- Sektörel raporlar
- SPK onayları ve düzenleme haberleri

### Aşama 4: Yapılandırılmış Çıktı

Her öneri/makale için:
1. **Kaynak + Tarih** — URL ve yayın tarihi
2. **Özet** — 2-3 cümle ana bulgular
3. **Edel uygunluk yorumu** — `📌 Edel için uygunluk: [UYGUN/KISMEN/DEĞİL] — gerekçe`

## Bilinen Sorunlar

- **SPK onaylı halka arzlar** bazen sadece Instagram reel'de duyurulur (web'de yok), Instagram da web_extract ile çekilemez. Para Dergisi'ndeki SPK haberlerini kaçırmamak için web_search ile `site:paradergi.com.tr halka arz` ara.
- **Haftalık dergi** olduğu için (günlük gazete değil), en güncel içerik genellikle Çarşamba-Perşembe yayınlanır. Haftasonu taramalarında yeni bir şey çıkmaması normaldir.
- **X/Twitter** hesabı 2026 itibarıyla düşük aktivite gösteriyor (~haftada 1 post). Ana kaynak web sitesidir.
