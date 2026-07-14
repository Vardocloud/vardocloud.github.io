---
name: unified-search
description: "Çok katmanlı arama orkestratörü — Tavily + SerperAPI + Brave + SearXNG proxy + web_search. Sorgu tipine göre en uygun API'yi seçer, paralel arama yapar, çapraz doğrular."
version: 2.0.0
metadata:
  hermes:
    tags: [research, search, orchestration, multi-api, unified]
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
      - "geniş araştır"
      - "çapraz kontrol"
      - "iş ilanı"
      - "kariyer"
      - "iş bul"
      - "iş ara"
      - "pozisyon"
      - "açık pozisyon"
      - "staj"
---

# ⚠️ ABSOLUTE ROUTING RULES

**These rules are injected into the system prompt. MUST follow — no exceptions.**

1. ANY search → FIRST load `unified-search` skill → classify query → pick best API
2. **web_search (Hermes tool) auto-detects → Tavily.** It is NOT SearXNG. Treat as Tavily-backed (~1.000/mo).
3. **API priority:** 🧠Tavily(deep) → 🚀SerperAPI(Google SERP) → 🦁Brave(alt index) → 🔍SearXNG proxy(:8888) → 🦆DDGS(fallback)
4. "araştır/bak/bul/keşfet/alternatif/karşılaştır" → MANDATORY Tavily direct call first
5. **"geniş araştır" → 3'lü PARALEL:** Tavily + SerperAPI + Brave → sonuçları birleştir
6. Cross-check → 2 APIs, compare, flag discrepancies
7. web_search is LAST RESORT — only when Tavily/SerperAPI/Brave ALL fail or limits exhausted

---

# Unified Search — Çok Katmanlı Arama Orkestratörü

**KURAL:** Her aramada bu skill devrededir. Sorgu tipine göre en uygun API'yi seç.

## Mimari

```
Sorgu geldi
    │
    ▼
┌─────────────────────────────────────┐
│         Sorgu Sınıflandırma          │
│  ≤4 kelime basit → SerperAPI        │
│  "araştır/incele" → Tavily          │
│  "geniş/kapsamlı" → Paralel 3'lü    │
└─────────────────────────────────────┘
    │
    ├── 🔬 DERİN ("araştır", "incele", "analiz et")
    │   → Tavily (AI sentez, 1000/ay)
    │   → Boş → SerperAPI (Google SERP, 2500/ay/key)
    │
    ├── ⚡ HIZLI ("nedir", "kimdir", "hava durumu")
    │   → SerperAPI (Google SERP, <200ms)
    │   → Rate-limit → SearXNG proxy → DDGS
    │
    ├── 🌐 GENİŞ ("geniş araştır", "tüm kaynaklardan")
    │   → 3 API PARALEL: Tavily + SerperAPI + Brave
    │   → Sonuçları birleştir, duplicate'leri temizle
    │
    └── 🔄 ÇAPRAZ DOĞRULAMA ("teyit et", "doğrula")
        → 2+ API aynı sorgu → tutarlılık kontrolü
```

## API Envanteri (Gerçek Durum — 21 Haz 2026)

| API | Rol | Auth | Limit/ay | Endpoint |
|-----|-----|------|----------|----------|
| 🧠 **Tavily** | AI sentez, derin okuma | `TAVILY_API_KEY` (Bitwarden) | ~1.000 | api.tavily.com/search |
| 🚀 **SerperAPI** | Google SERP, sub-200ms | `~/.hermes/serper_key.txt` + fallback | 2.500 × 2 key = 5.000 | google.serper.dev/search |
| 🦁 **Brave** | Bağımsız index, privacy | `BRAVE_API_KEY` (Bitwarden) | ~2.000 | api.search.brave.com |
| 🔍 **SearXNG proxy** | Tavily→Serper→Brave→DDGS kaskad, cache 5dk | `.env` okuyarak, port 8888 | Sınırsız | http://127.0.0.1:8888/search?format=json |
| 🔍 **web_search** | Tavily auto-detect | Gateway env → TAVILY_API_KEY | ~1.000 | Hermes tool |
| 🌐 **web_extract** | Firecrawl | `FIRECRAWL_API_KEY` (Bitwarden) | Firecrawl limit | Hermes → Firecrawl |

### Hermes Backend Auto-Detect Priority
`web_search` boş `search_backend` ile bu sırayla seçer:
1. 🧠 Tavily (`TAVILY_API_KEY` env)
2. 🔍 SearXNG (`SEARXNG_URL=http://127.0.0.1:8888`)
3. 🦁 Brave-free (`BRAVE_SEARCH_API_KEY` env — alias wrapper'da)
4. 🦆 DDGS (her zaman)

## Sorgu Sınıflandırma

| Tier | Sorgu Tipi | Örnek | API'ler | Token |
|---|---|---|---|---|
| 🟢 Hafif | ≤4 kelime, basit | "hava durumu", "X nedir" | 🚀SerperAPI | ~500 |
| 🟡 Orta | 4-8 kelime, karşılaştırma | "X vs Y", "en iyi X" | 🚀SerperAPI + 🦁Brave | ~2K |
| 🔴 Ağır | "araştır/incele/alternatif" | üniversite, program | 🧠Tavily → 🦁Brave → 🚀SerperAPI | ~5K |
| 🟣 Kritik | "derin/geniş/kapsamlı" | tez, sistematik | 🧠🦁🚀 3'lü PARALEL | ~8K |

**Karar Ağacı (her aramada):**
```
Sorgu <4 kelime VE basit → SerperAPI
"araştır/incele/karşılaştır/alternatif" → Tavily
"derin/geniş/kapsamlı" → PARALEL 3'lü
Hiçbiri → SerperAPI + Brave çapraz
Sonuç yok → bir üst tier'a yükselt
Tüm API limitleri dolu → SearXNG proxy → DDGS
```

## Pattern 1: Derin Araştırma (Tavily → SerperAPI → Brave)

```python
# ctx_execute ile Tavily (path: ~/.hermes/tavily_key.txt)
# Boş → SerperAPI (key: ~/.hermes/serper_key.txt)
# Boş → Brave (key: Bitwarden BRAVE_API_KEY)
```

## Pattern 2: Paralel Geniş Tarama (OTOMATİK)

**"geniş araştır" dediğinde OTOMATİK çalışır:**

```python
# delegate_task ile 3 paralel sorgu:
# Task 1: Tavily (derin AI sentez)
# Task 2: SerperAPI (Google SERP)
# Task 3: Brave (bağımsız index)
# Sonuçları birleştir: duplicate URL temizle, API etiketi ekle
```

## Pattern 3: Çapraz Doğrulama

```python
# SerperAPI + Brave aynı sorgu
# Aynı linkler var → yüksek güven
# Farklı → "⚠️ Kaynaklar arasında fark var" uyarısı
```

## Pattern 5: Üniversite Program Araştırması (Türkiye)

**Ne zaman:** "üniversite", "program", "başvuru", "yüksek lisans", "yökdil", "ales", "master" gibi terimlerle Türkiye'deki üniversite program araştırması yaparken.

## Pattern 5: Üniversite Program Araştırması (Türkiye)

**Ne zaman:** "üniversite", "program", "başvuru", "yüksek lisans", "yökdil", "ales", "master" gibi terimlerle Türkiye'deki üniversite program araştırması yaparken.

**⚠️ CRITICAL:** Türk üniversiteleri başvuru tarihlerini **önce Instagram'da**, sonra web sitesinde duyurur. Web_extract tek başına yeterli değildir.

**⚠️ GEOGRAPHIC SCOPE (25 Haz 2026 Dersi):** Sadece İstanbul/Ankara/İzmir'e bakıp "Türkiye'yi taradım" deme. 81 ildeki üniversiteleri en az 5-6 coğrafi bölgeden örneklemle tara. `site:edu.tr "klinik psikoloji" "yüksek lisans" -instagram -facebook` gibi geniş sorgular kullan. Taranan/taranmayan illeri net ayır. Referans: `anti-hallucination` skill'inde `references/81-il-tarama-protokolu-25-haz-2026.md`

**⚠️ PRICE VERIFICATION (25 Haz 2026 Dersi):** Subagent'ların getirdiği ücret bilgisine ASLA güvenme. Resmi üniversite sayfasındaki ücret tablosunu/Excel/PDF'i bizzat aç, oku. Subagent'lar aggregator sitelerden eski fiyatları güncelmiş gibi sunar.

**Adımlar:**
1. Instagram'da enstitü hesabını bul: `site:instagram.com ÜniversiteAdı Sosyal Bilimler Enstitüsü başvuru`
2. Enstitünün kendi duyuru sayfasını kontrol et (SBE, SABE, LEE farklı olabilir)
3. Varsa PDF ilanı indir, başvuru takvimini oku
4. Her veri noktası için **kaynak URL** ver — kullanıcı "referans ver" dediğinde tek satır özet değil, linkli tablo sun

**⚠️ Sayfa Okuma Kuralı (24 Haz 2026):** Türk üniversite sayfalarında içerik genellikle accordion/toggle menüler, sekmeler veya JavaScript ile yüklenir. Web_extract'in gösterdiği ilk 5000 karakterle yetinme:
- `browser_navigate` ile sayfayı aç
- Accordion başlıklarını (`browser_click`) tek tek tıkla
- Sayfayı sonuna kadar scroll et (`browser_scroll`)
- Varsa kontenjan PDF'ini ayrıca aç
- Tezli ve tezsiz programlar genellikle ayrı tablolardadır — ikisini de kontrol et

Detaylar: `references/turkish-university-research.md`

---

## Pattern 4: İş İlanı Arama (Türk Platformları)

**Ne zaman:** "iş ilanı", "kariyer", "açık pozisyon", "iş bul" vs.

**⚠️ CRITICAL:** Sadece unvanla arama yapma. Önce CV oku → anahtar kelime çıkar → 3 sorgu seti oluştur.

Detaylar: `references/turkish-job-search.md`, `references/global-filtration-companies.md`

## Limit Takip Tablosu (her aramada güncelle)

```
🧠 Tavily: ~X/1.000 (%Y)  🚀 SerperAPI: ~X/5.000 (%Y)  🦁 Brave: ~X/2.000 (%Y)
```

## Limit Tükenme Uyarıları (ZORUNLU)

| Durum | Aksiyon |
|---|---|
| API boş/rate-limit | "⚠️ X API limiti doldu, Y'ye geçiyorum" |
| Ayın 20'sinden sonra | %80 aşıldıysa uyar: "📊 X API kotasının %80'i doldu" |
| Tüm API'ler tükendi | "🔴 Tüm arama API'leri tükendi. SearXNG proxy + DDGS'ye düştüm." |
| Ay başı (1-3) | Kotalar sıfırlandı, sessiz çalış |

## Fallback Zinciri

```
Derin:    Tavily → SerperAPI → Brave → SearXNG proxy(:8888) → DDGS
Hızlı:    SerperAPI (key1) → SerperAPI (key2) → SearXNG proxy → DDGS
Geniş:    3'lü PARALEL → boş kalan → SearXNG proxy → DDGS
Çapraz:   2 API → 1'i boş → SearXNG proxy teyit
```

## Pitfalls

| Pitfall | Çözüm |
|---------|-------|
| 3 API de boş | Sorguyu İngilizce'ye çevir, terimleri genişlet |
| Tavily rate-limit | SerperAPI'ye düş, sonra Brave'e |
| **SerperAPI 403** | Fallback key'e geç (`serper_key_fallback.txt`) |
| **SerpAPI değil SerperAPI** | Doğru endpoint: `google.serper.dev/search` (POST, X-API-KEY header). SerpAPI (serpapi.com) farklı servis. |
| Paralel çağrı timeout | Tek API'ye düş, sonuçları tek tek al |
| Aynı sonuçlar farklı API'lerden | Normal — duplicate temizliği yap |
| **SearXNG proxy noise** | Akademik araştırmada SerperAPI tercih et. Proxy'de sonuç pozisyonu kaskad motorlardan karışabilir. |
| **SearXNG proxy cache** | 5dk TTL var. Aynı sorgu tekrar edilirse API çağrısı yapılmaz, cache'ten döner. |
| **BRAVE_SEARCH_API_KEY yok** | Hermes wrapper'da `BRAVE_API_KEY` → `BRAVE_SEARCH_API_KEY` alias'ı var. Gateway restart sonrası aktif. |
| **Tavily curl'de JSON kaçar** | Python `urllib.request` kullan. Heredoc'ta key dosyasını oku. |
| Brave gzip | `gzip.decompress(resp.read())` ile aç |
| LinkedIn scraping bloklanır | Sadece web_search SERP, web_extract'e güvenme |
| Link genel kariyer sayfası | Spesifik `/is-ilani/...` URL'si bul. site: araması kullan. |

## Skill References

- `references/turkish-job-search.md` — Türk iş platformları URL pattern'leri
- `references/fee-table-interpretation.md` — Üniversite ücret tablosu okuma
- `references/university-research-pattern.md` — Master program araştırma pattern'i
- `references/university-program-research.md` — Program sayfası çapraz doğrulama (Türkiye ekleri: Instagram kaynağı, erken/normal başvuru, YÖKDİL muafiyeti, değerlendirme formülleri, enstitü türleri, başvuru adımları)
- `references/global-filtration-companies.md` — Global filtrasyon firmaları
- `references/searxng-proxy.md` — SearXNG proxy dokümantasyonu
- `references/searxng-proxy.md` — SearXNG proxy dokümantasyonu
