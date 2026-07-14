---
name: brave-search
description: "Brave Search API — bağımsız index, privacy odaklı, alternatif kaynak taraması."
version: 1.0.0
metadata:
  hermes:
    tags: [research, search, brave, alternative-index]
    category: research
---

# Brave Search API

**Rol:** Alternatif kaynak taraması. Google/Bing'den bağımsız kendi index'i var.

## Ne Zaman Kullanılır?

- Tavily/Serper'ın bulamadığı şeyleri ararken
- Google'ın filtrelediği/sansürlediği içeriklerde
- Privacy gerektiren hassas araştırmalarda
- Çapraz doğrulama için (farklı index'ten teyit)

## Endpoint

```
GET https://api.search.brave.com/res/v1/web/search
Headers: Accept: application/json, X-Subscription-Token: API_KEY
Params: q, count (max 20), offset, freshness (pd|pw|pm)
```

## Kullanım (ctx_execute_file)

```python
import requests
api_key = FILE_CONTENT.strip()

resp = requests.get(
    "https://api.search.brave.com/res/v1/web/search",
    headers={"Accept": "application/json", "X-Subscription-Token": api_key},
    params={"q": "SORGU", "count": 10},
    timeout=30
)

data = resp.json()
for r in data.get("web", {}).get("results", []):
    print(f"{r['title']}\n{r.get('description','')}\n{r['url']}\n")
```

## Limitler

- Free: 2.000 sorgu/ay
- 1 sorgu/sec rate limit
- Key: ~/.hermes/brave_key.txt (600)

## Pitfalls

| Pitfall | Çözüm |
|---------|-------|
| Rate-limit (429) | 1 saniye bekle, tekrar dene |
| Boş sonuç | Sorguyu İngilizce'ye çevir, daha genel terimler kullan |
| Gzip encoding hatası | `Accept-Encoding: gzip` header'ı ekle |
