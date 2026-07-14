---
name: tavily-search
description: "Tavily Search API — derin araştırmalarda BİRİNCİL araç. web_search fallback'tir."
version: 1.1.0
metadata:
  hermes:
    tags: [research, search, tavily, deep-research]
    category: research
    priority: critical
    auto_load_triggers:
      - "araştır"
      - "bul"
      - "keşfet"
      - "hangileri"
      - "neler var"
      - "alternatif"
      - "karşılaştır"
      - "üniversite"
      - "program"
      - "literatür"
      - "deep research"
      - "derin araştırma"
---

# Tavily Search — Deep Research Primary Tool

**KURAL:** Herhangi bir araştırma görevinde İLK adım Tavily'dir. web_search sadece fallback.

## Neden Tavily?

| Tavily | web_search |
|--------|-----------|
| AI-synthesized answer | Snippet listesi |
| 15 sonuç (advanced) | 5 sonuç |
| Deep/advanced mod | Yüzey seviyesi |
| GitHub repo keşfi | Bilinen URL'ler |
| Program/üniversite tarama | Basit fact check |

## Trigger Kelimeler (OTOMATİK)

Edel şunlardan birini söylediğinde bu skill'i yükle ve Tavily ile başla:
- "araştır", "bak", "bul", "keşfet", "tara", "incele"
- "hangileri var", "neler var", "alternatifleri"
- "karşılaştır", "en iyi", "öner"
- "üniversite", "program", "bölüm", "yüksek lisans"
- "literatür", "makale", "çalışma", "araştırma"
- "repo", "GitHub", "tool", "araç"

## Kullanım

⚠️ **ÖNEMLİ:** API key gizli dosyadadır. `$(cat file)`, `execute_code`, `write_file` ile key okumak BAŞARISIZ olur (secret redaction / smart approval). **SADECE `ctx_execute_file` çalışır.**

### Pattern 1: ctx_execute_file — tek veya paralel sorgu (HER ZAMAN çalışır)

```python
# mcp_context_mode_ctx_execute_file ile
# path: /home/ubuntu/.hermes/tavily_key.txt
# language: python

import requests, json

api_key = FILE_CONTENT.strip()

queries = [
    ("Label 1", "query 1 here"),
    ("Label 2", "query 2 here"),
    ("Label 3", "query 3 here"),
]

for label, query in queries:
    print(f"\n{'='*60}")
    print(f"🔍 {label}")
    print(f"{'='*60}")
    
    resp = requests.post(
        "https://api.tavily.com/search",
        headers={"Content-Type": "application/json"},
        json={
            "api_key": api_key,
            "query": query,
            "search_depth": "advanced",
            "include_answer": True,
            "max_results": 8
        },
        timeout=60
    )
    
    data = resp.json()
    answer = data.get('answer')
    if answer:
        print(f"\n📝 AI ÖZET:\n{answer[:1500]}")
    
    results = data.get('results') or []
    print(f"\n🔗 KAYNAKLAR ({len(results)}):")
    for i, r in enumerate(results):
        print(f"  {i+1}. {r['title'][:120]}")
        print(f"     {r.get('content','')[:250]}")
        print(f"     {r['url']}")
        print()
```

### Pattern 2: Tek sorgu — hızlı (terminal, key'i manuel oku)

Key'i önce `read_file` ile sessizce oku (context'e girmez), sonra `terminal` ile curl + pipe kullan. `$(cat file)` bash substitution yerine key'i `--data-raw` içine gömmek de redacte uğrar — bu pattern sadece key dosyasını okuduktan SONRA çalışır. Tercihen Pattern 1 kullan.

### Pattern 3: Derin katmanlı (2 turlu)

1. Tur: Pattern 1 ile genel sorgu(lar)
2. Cevaptan çıkan spesifik terimlerle 2. Tur Pattern 1

## Ne Zaman Tavily DEĞİL?

- "bugün hava nasıl" — basit fact, web_search yeterli
- "şu linki özetle" — direkt web_extract
- "X nedir" — tanım soruları, web_search
- Edel spesifik olarak "web_search ile bak" dediyse

## Pitfalls

| Pitfall | Çözüm |
|---------|-------|
| **`$(cat ~/.hermes/tavily_key.txt)` bash substitution** | ❌ HİÇ ÇALIŞMAZ. Secret redaction key'i `***` yapar → API 403. SADECE `ctx_execute_file` kullan. |
| **`execute_code` ile `builtins.open(key)`** | ❌ Smart approval BLOCK eder. `execute_code` içinde key dosyası okuma. |
| **`terminal` + curl + inline key** | ❌ `--data-raw` içinde key redacte uğrar. Çalışmaz. |
| **Çok spesifik sorgu → 0 sonuç** | 3 sorgu da boş döndüyse sorguları GENİŞLET. "Tavily vs Google search comparison accuracy benchmark 2025" yerine "Tavily search API review" dene. |
| Tavily boş döndü (rate limit/sıfır sonuç) | web_search'e fallback yap |
| `answer` null geldi | `d.get('answer')` kontrol et, `if a:` ile koru |
| `results` null geldi | `or []` fallback kullan |
| API key dosyası yok | Edel'e bildir, web_search ile devam et |
| Tavily + web_search aynı sonuçları veriyor | Normal — Tavily'nin answer'ı asıl değer katar |

## Akış Şeması (Güncel — SearXNG proxy + cascade)

```
Araştırma tetiklendi
    │
    ▼
web_search (auto-detect → Tavily) — Hermes tool
    │
    ▼
Sonuç var mı? ─── HAYIR ──▶ SearXNG proxy (:8888)
    │                              │
    EVET                      Tavily→Serper→Brave→DDGS
    │                         (otomatik cascade, 5dk cache)
    ▼                              │
Yeterli mi? ─── HAYIR ──▶    Sonuç var mı?
    │                              │
    EVET                      ┌────┴────┐
    │                        EVET     HAYIR
    ▼                         │         │
Edel'e sun                   Edel'e    DDGS
                             sun      (son çare)
```

**Not:** web_search tool'u config'de `search_backend: ''` olduğu için Tavily auto-detect çalışır.
SearXNG proxy (:8888) ayrıca Tavily'yi birincil motor olarak kullanır — aynı API anahtarı, ekstra cache katmanı.

## Maliyet

- API key: `TAVILY_API_KEY` (Bitwarden, dev tier, ~1000/ay)
- SearXNG proxy de aynı key'i kullanır (cache sayesinde tekrarlı sorgular API'ye gitmez)
- web_search tool'u da aynı key'i auto-detect ile kullanır
- Rate limit: Cömert, normal kullanımda sorun çıkmaz
