# Instagram İçerik Araştırma Workflow'u

## Problem
Edel Instagram linkleri gönderdiğinde (reel/post) içeriğini anlamak gerekir. Ancak Instagram:
- `web_extract` tarafından desteklenmez
- `browser_navigate` ile açmak timeout verir (JS render, login perdesi)
- `curl + meta tag scraping` boş döner (Instagram artık SSR meta vermiyor)

## Çözüm: Pollinations web_search

Pollinations web_search (perplexity-fast modeli) arama motoru önbelleğinden Instagram içeriğini çözümleyebilir.

### Kullanım

```python
# Tek link sorgulama
mcp_pollinations_webSearch(
    query="instagram.com/reel/DaI2ZmFtz8R",
    model="perplexity-fast"
)
```

### Dönen Bilgiler
- Kullanıcı adı (örn. "codescaptain")
- Post başlığı/içeriği (Türkçe veya İngilizce)
- Beğeni/yorum sayısı
- Hashtag'ler
- Varsa lead magnet bilgisi ("88 yazana PDF" gibi)

### Sınırlamalar
- Her zaman tam metin dönmeyebilir (arama motoru önbelleğindeki kadarı)
- Yeni paylaşımlar henüz indekslenmemiş olabilir
- Görsel/video içeriğini tanımlayamaz

## Proaktif Analiz Pattern'i

Edel "ben söylemeden ne yapman gerektiğini düşün" dediğinde veya talimat vermeden link gönderdiğinde:

1. Tüm linkleri Pollinations web_search ile analiz et
2. Ortak stratejiyi bul (lead magnet, tool showcase, engagement bait, etc.)
3. Bardo Psikolojisi'ne uyarlanmış versiyonlar çıkar
4. Seçeneklerle gel, pasif bekleme

### Örnek Uyarlama Tablosu

| Instagram'daki Taktik | Psikoloji Uyarlaması |
|---|---|
| Lead magnet ("88 yaz → PDF al") | "TERAPİ" yaz → "İlk Seans Rehberi" PDF |
| AI araç tanıtımı (codescaptain) | "Psikologlar için kullandığım 5 araç" karuseli |
| Yazılım rehberi + GitHub | "Bilinçaltı savunma mekanizmaları" rehber serisi |

## Alternatif Yöntemler (Pollinations çalışmazsa)

- Instagram oembed API'si: `curl -s "https://api.instagram.com/oembed?url=..."` — çoğu zaman boş döner
- Google'da reel ID'sini arat: bazen başka siteler referans vermiş olabilir
- Instagram'ın text-based versiyonu yok — başka bir yedek yöntem şu an bilinmiyor
