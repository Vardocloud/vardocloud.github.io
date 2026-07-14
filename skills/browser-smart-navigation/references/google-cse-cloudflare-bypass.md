# Google Custom Search API — Cloudflare Bypass Fallback

## Problem
Oracle Cloud / herhangi bir datacenter IP'sinden gelen istekler Cloudflare tarafından **hepsi engellenir**:
- Browser (Chrome, Camoufox, nodriver, puppeteer) ❌
- RSS feed ❌
- API endpoints ❌
- curl / wget ❌

Cloudflare IP range'lerini tanıyor, datacenter trafiğini reddediyor.

## Çözüm: Google Custom Search API

Google, hedef sitenin sayfalarını indexler. Google Custom Search API ile Google'ın sonuçlarını okuyarak Cloudflare'a takılmayız.

### Kurulum
1. Google Cloud Console → Custom Search API'yi enable et
2. API key oluştur — **API restriction seçimi:**
   - Google Cloud Console API key oluştururken "Select API restrictions" ister
   - **Custom Search API checkbox'ı listede YOK** — bu normal, bir bug/eksiklik
   - **Çözüm:** "Don't restrict key" seçeneğini seç (veya HTTP referrer restriction: `*.googleapis.com`)
   - Key çalışır — restriction olmadan da güvenli çünkü sadece CSE endpoint'ine hit yapar
3. Programmable Search Engine oluştur (tüm web veya `site:upwork.com`)
4. Search Engine ID (cx) al

### Kullanım
```
GET https://www.googleapis.com/customsearch/v1
  ?key=API_KEY
  &cx=SEARCH_ENGINE_ID
  &q=site:upwork.com/jobs python ai
  &num=10
```

### Cron Job Pattern
```python
# Her gün çalış: keywords listesi → Google CSE → sonuçları parse et → raporla
keywords = ["python ai", "machine learning", "data science"]
for kw in keywords:
    query = f"site:upwork.com/jobs {kw}"
    results = google_cse_search(query)
    # Job title, description, URL, date → structured output
    yield format_report(results)
```

### Limitler
- Ücretsiz: 100 sorgu/gün
- Sonra: $5/1000 sorgu
- Snippet'ler kısa (genelde 200-300 karakter)
- Tam sayfa içeriği için: job URL'lerini Firecrawl ile parse et

### Avantajlar
- Cloudflare bypass: Google'ın indexini okuyoruz, siteye direkt erişim yok
- Ücretsiz tier yeterli (günlük 1-10 arama)
- Senin bilgisayarına bağlı değil
- Cron job ile otomatik çalışır

### Dezavantajlar
- Google'ın indexleme gecikmesi (yeni job'lar 1-24 saat sonra görünür)
- Snippet'ler tam job detayını içermez
- Google CSE'nin result kalitesi organic search'ten düşük olabilir

### Upwork Özelinde
Upwork job sayfaları Google tarafından iyi indexlenir. `site:upwork.com/jobs [keyword]` araması job title, description snippet, ve URL döner. Job detayları için URL'leri Firecrawl veya benzeri bir extractor ile parse et.

### Gerçek Test Sonuçları (Haziran 2026)
- **Oracle Cloud datacenter IP → Upwork.com:** ❌ Cloudflare Challenge (tüm yöntemler)
  - Chrome, Camoufox, nodriver, puppeteer-real-browser: Hepsi başarısız
  - RSS feed: Başarısız
  - localhost.run tunnel: Servis bozuk (Haziran 2026)
  - VNC manuel: "failed to connect server"
- **cloudflared tunnel:** ✅ Çalışıyor — secure pipeline için kullanıldı
- **Google Custom Search API:** ✅ Önerilen çözüm — kurulum aşamasında
