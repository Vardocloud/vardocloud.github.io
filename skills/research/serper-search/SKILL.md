---
name: serper-search
description: "Serper API — en hızlı Google SERP, sub-200ms, fact-check ve hızlı taramalar için."
version: 1.0.0
metadata:
  hermes:
    tags: [research, search, serper, google-serp, fast]
    category: research
---

# Serper Search API

**Rol:** En hızlı Google SERP. Fact-check, basit sorgular, hızlı doğrulama.

## Ne Zaman Kullanılır?

- "X nedir?" tipi hızlı fact-check
- Google'da ne çıkıyor hızlıca bakmak
- Bir konunun güncel durumunu taramak
- Fallback: primary key rate-limit'e girerse secondary key

## Endpoint

```
POST https://google.serper.dev/search
Headers: X-API-KEY: API_KEY, Content-Type: application/json
Body: {"q": "query", "num": 10}
```

## Kullanım (ctx_execute_file)

```python
import requests, builtins

# Primary key
api_key = FILE_CONTENT.strip()

resp = requests.post(
    "https://google.serper.dev/search",
    headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
    json={"q": "SORGU", "num": 10},
    timeout=15
)

data = resp.json()
for r in data.get("organic", []):
    print(f"{r['title']}\n{r.get('snippet','')}\n{r['link']}\n")
```

## Fallback Zinciri

```
Primary key (2500/ay) → rate-limit → Secondary key (2500/ay) → SearXNG proxy(:8888) → Brave → DDGS
```

SearXNG proxy cascade (Tavily→Serper→Brave→DDGS) de Serper'i motor olarak kullanır.

## Limitler

- Free: 2.500 sorgu/ay (her key için, toplam 5.000)
- Sub-200ms yanıt süresi
- Sadece Google sonuçları (Bing/Yahoo yok)
- Key dosyaları: ~/.hermes/serper_key.txt ve ~/.hermes/serper_key_fallback.txt

## Pitfalls

| Pitfall | Çözüm |
|---------|-------|
| **SerpAPI ile karıştırma** | SerperAPI (serper.dev) ≠ SerpAPI (serpapi.com). Farklı servisler, farklı endpoint'ler. Biz SerperAPI kullanıyoruz. |
| 403 rate-limit | Fallback key'e geç, 1 dk bekle |
| Boş organic | Sorguyu genişlet, özel karakterleri temizle |
| İki key de limitli | SearXNG proxy'ye (port 8888) düş — proxy de Serper'i motor olarak kullanır |
