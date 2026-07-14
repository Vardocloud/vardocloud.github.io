---
name: polymarket-ai-trading-system
category: mlops
description: Build an AI-assisted, test-first trading system for Polymarket-style prediction markets (sinyal üretimi + kalite kontrol + paper/shadow + küçük canlı deneme) with risk gates.
tags: [polymarket, prediction-markets, trading, paper-trade, backtesting]
related_skills: [research/polymarket]
---

# Polymarket AI Trading System (Test-First)

## Amaç
Polymarket üzerinde kısa vadeli alım-satım yapmak için:
- AI ile sinyal üretmek
- kârlılığı kanıt ve metrikle yönetmek
- canlıya çıkmadan önce paper-trade + shadow mode ile doğrulamak

## Paper Trade Backend: polymarket-paper-trader

Bu skill'in önerilen paper trade backend'i **`polymarket-paper-trader`** (v0.1.7+) aracıdır.

### Özellikleri
- Gerçek Polymarket order book'larını kullanır (sahte fiyat değil)
- Level-by-level order book execution (slippage simülasyonu dahil)
- Birebir aynı fee modeli
- Multi-outcome market desteği
- Limit order state machine (GTC, GTD)
- Strateji backtesting (geçmiş fiyat snapshot'ları ile)
- MCP Server desteği (AI agent entegrasyonu için 26 tool)
- Benchmark/karşılaştırma: birden fazla hesap ve stratejiyi yan yana test

### Kurulum
Paket adı: `polymarket-paper-trader` (PyPI'da mevcut). pip ile kurulum yapılır, Python 3.10+ gerekir.

### İlk Kullanım
Kurulumdan sonra:
- `pm-trader init --balance 10000` ile $10k sanal bakiye oluştur
- Gamma API ile marketleri keşfet (pm-trader search değil — bkz: uyarılar)
- `pm-trader book SLUG` ile order book derinliğini kontrol et
- İlk trade'de $10-20'yi geçme (slippage riski, bkz: Pitfall 5)
- `pm-trader buy SLUG yes 100` ile market alışı yap (önce küçük dene!)
- `pm-trader portfolio` ile portföy durumunu gör
- `pm-trader stats` ile ROI, win rate, drawdown metriklerini gör
- `pm-trader benchmark run MODULE.FUNC` ile backtest çalıştır

Detaylı CLI referansı için: `references/paper-trader-commands.md`

### MCP Server (AI Agent Entegrasyonu)
`pm-trader mcp` komutu ile stdio transport üzerinden MCP server başlatılır. 26 tool sunar: init_account, get_balance, search_markets, buy, sell, portfolio, history, stats, backtest ve daha fazlası.

### Çoklu Hesap Yönetimi
Farklı stratejileri aynı anda test etmek için `pm-trader accounts create "isim"` ile ayrı hesaplar oluşturulur ve `--account` flag'i ile kullanılır.

## Veri/Doğrulama Katmanı (Resolution-grade kaynak)
Her market için aşağıdaki eşleştirmeleri yap:
- Market question → resolution rules (Polymarket sayfasındaki Rules)
- Doğrulanabilir veri kaynakları (resmi duyuru/kurum/şeffaf veri sağlayıcı)
- AI'nın kullanacağı haber/kaynaklar için domain allowlist ve zaman penceresi

> Pitfall 1: AI'nın doğru bilgiyi yanlış olaya bağlaması. Event eşleşmesi zorunludur.
> Pitfall 2 (ÖNEMLİ — Edel düzeltmesi): Politi-fail / meme marketleri asla ciddi analize tabi tutma. "Jesus before GTA VI", "Rihanna album" gibi marketler rasyonel değildir — onları analiz etmek havadan para kazanma gibi görünür ve kullanıcının gözünde sistemi itibarsızlaştırır. SADECE gerçek haber-driven marketleri (Starmer, Kraken IPO, Ukrayna, Trump politikası, OpenAI) analiz et. Meme marketleri sessizce filtrele, analiz raporunda bile bahsetme.
> Pitfall 3: Pollinations free-tier'da rate limit (429) çok agresif. Python script'inden LLM çağırmak güvenilmez. Çözüm: data collection script'i (collect_data.py) sadece veri toplar, LLM analizi cronjob agent'ında (deepseek-v4-flash-free) yapılır. Local Ollama (phi4-mini:3.8b, ARM64 CPU) çok yavaş (~60sn/market) — kullanma.
> Pitfall 4 (CLI quirks): pm-trader `--format json` DESTEKLENMEZ — output zaten JSON. `--limit` flag'i markets search'te çalışır. `--yes` flag'i blogwatcher-cli'da yok (remove için pipe kullan: `echo \"y\" | blogwatcher-cli remove \"Name\"`). blogwatcher-cli add'de feed URL'i `--feed-url` ile gönderilmezse auto-discovery çalışmayabilir.

> Pitfall 6 (OUTCOME NAMES — 27 Haz 2026): Polymarket'te tüm marketler "yes"/"no" outcome'u kullanmaz. Spor marketlerinde "over"/"under", "home"/"away", "draw" gibi farklı isimler olabilir. **Gamma API'den her zaman `outcomes` field'ını kontrol et.** `pm-trader buy SLUG over 5` gibi kullan. Yanlış outcome girersen `INVALID_OUTCOME` hatası alırsın.

> Pitfall 7 (FOK vs FAK — 27 Haz 2026): Düşük hacimli marketlerde FOK (fill-or-kill) reddedilir çünkü tüm emir tek seferde dolmaz. $100 likiditeli bir markette $5'lik FOK emir bile `ORDER_REJECTED` döndürebilir. **FAK (immediate-or-cancel) kullan** — kısmi doluma izin verir. Komut: `pm-trader buy SLUG outcome AMOUNT --type fak`. Ancak FAK da çok kötü fiyattan dolabilir (99¢'den dolduran test görüldü).

> Pitfall 8 (LIQUIDITY HIERARCHY — 27 Haz 2026): Polymarket'te likidite hiyerarşisi:
> 1. **Dünya Kupası 2026** ($60-100M) — en likit, YES fiyatları 0.1¢-22¢ arası
> 2. **GTA VI meme** ($10-20M) — yüksek hacim ama 50/50 floor nedeniyle edge yok
> 3. **Siyasi/jeopolitik** ($100K-2M) — orta likidite, whale_watch fırsatları
> 4. **Spor (liga/dayalı)** ($100-100K) — düşük likidite, FAK gerekir, slippage çok yüksek
> 5. **Niş (hava/hukuk/IPO)** ($1K-500K) — değişken, her zaman order book kontrol et
>
> Pitfall 5 (REAL-WORLD LIQUIDITY — 27 Haz 2026): Yüksek hacimli ($500K+) bir markette bile YES tarafındaki ask derinliği ince olabilir. **Örnek:** Kraken IPO (Dec 2026, $541K hacim) marketinde YES ask'te 31¢'de sadece 6 share, 32¢'de 5 share vardı. $50'lik YES market order'ı 4 kademe doldurup ortalama maliyeti 46.14¢'ye çıkardı (midpoint 29.5¢ idi — anında -%36 unrealized loss). **Bu gerçek Polymarket order book verisidir, paper trader slippage'ı doğru simüle eder.**
>
> Çözümler:
> - **Order book kontrolü:** Trade öncesi `pm-trader book SLUG` ile derinliği gör
> - **Pozisyon büyüklüğü:** İlk 3 kademedeki toplam ask/bid derinliğinin en fazla %50'si kadar al/sat
> - **Limit order tercih et:** Market order (fok/fak) yerine spread içine limit order koy. Komut: `pm-trader orders place SLUG yes buy MIKTAR FIYAT`
> - **İlk trade'lerde $10-20'yi geçme** — likiditeyi tanıyana kadar küçük gir
> - **Slippage beklentisi:** $50+ emirlerde ortalama maliyet midpoint'tan %30-50 sapabilir

## ⚠️ Docker/Container Ortam Notu — /data/ Yolu
Bu skill içinde geçen `/data/pm-trader/` yolları, Polymarket verilerinin saklandığı varsayılan data dizinini gösterir. Ancak Hermes Docker container'ında `/data/` mount edilmemiş olabilir (WSL/Docker'da ekstra volume gerekir). Gerçek çalışan yol:

```
pm-trader varsayılanı: ~/.local/share/pm-trader/
Script çıktısı:        ~/.hermes/data/ (mispricing)
Cron data cache:       pm-trader markets list → JSON
```

**Kural:** `pm-trader` komutları kendi default data dizinini kullanır. Script'lerde `/data/pm-trader/` yolu mevcut değilse `~/.local/share/pm-trader/` veya `pm-trader` çıktısını doğrudan pipe et kullan.

## Haber Kaynağı Mimarisi (RSS + SearXNG Hybrid)

Haber-driven stratejiler için iki katmanlı kaynak mimarisi.

### Katman 1 — RSS Feed Bundle (birincil, sıfır maliyet)

**Araç:** `blogwatcher-cli` v0.2.1+ ile yönetilir. Varsayılan DB yolu: `/data/pm-trader/blogwatcher.db` (Docker'da yoksa `pm-trader` data dizini altında oluşturulabilir)

**ARM64 kurulum:**
```bash
curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_arm64.tar.gz -o /tmp/bw.tar.gz
tar xzf /tmp/bw.tar.gz -C /tmp blogwatcher-cli
sudo mv /tmp/blogwatcher-cli /usr/local/bin/
```

**Feed ekleme (homepage + explicit feed URL):**
```bash
blogwatcher-cli --db /data/pm-trader/blogwatcher.db add "Name" "https://example.com" --feed-url "https://example.com/feed.xml"
# remove requires pipe confirmation:
echo "y" | blogwatcher-cli --db /data/pm-trader/blogwatcher.db remove "Name"
```

**Blogwatcher-cli komut farkı (27 Haz 2026 düzeltmesi):** Skill'de `refresh` ve `list` olarak geçen komutlar gerçek CLI'da farklıdır:\n\n| Skill'de yazan | Gerçek komut | Açıklama |\n|---|---|---|\n| `blogwatcher-cli list` | `blogwatcher-cli blogs` | Feed'leri listeler |\n| `blogwatcher-cli refresh` | `blogwatcher-cli scan` | Yeni makaleleri çeker |\n| `blogwatcher-cli list --unread` | `blogwatcher-cli articles` | Makaleleri listeler |\n| `--yes` flag | Yok | Remove için `echo \"y\" | blogwatcher-cli remove \"Name\"` |\n\n**DB yolu:** Varsayılan `~/.blogwatcher-cli/blogwatcher-cli.db` (skill'de belirtilen `/data/pm-trader/blogwatcher.db` değil). `--db path` ile override edilebilir.\n\n**DB şeması (önemli kolonlar):**\n- `articles.published_date` (NOT `published_at`)\n- JOIN: `articles.blog_id = blogs.id`

**14 çalışan kaynak, 4 kategoride:**

| Kategori | Kaynak | Feed URL |
|---|---|---|
| Kripto | CoinDesk | coindesk.com/arc/outboundfeeds/rss |
| Kripto | CoinTelegraph | cointelegraph.com/rss |
| Kripto | Decrypt | decrypt.co/feed |
| Kripto | Blockworks | blockworks.com/feed |
| UK Siyaset | BBC Politics | feeds.bbci.co.uk/news/politics/rss.xml |
| UK Siyaset | BBC World | feeds.bbci.co.uk/news/world/rss.xml |
| UK Siyaset | Guardian Politics | theguardian.com/politics/rss |
| UK Siyaset | Telegraph | telegraph.co.uk/rss.xml |
| Tech/AI | TechCrunch | techcrunch.com/feed/ |
| Tech/AI | Ars Technica | feeds.arstechnica.com/arstechnica/index |
| Tech/AI | The Verge | theverge.com/rss/index.xml |
| Tech/AI | OpenAI Blog | openai.com/news/rss.xml |
| Tech/AI | Hacker News | hnrss.org/frontpage |
| Dünya | Al Jazeera | aljazeera.com/xml/rss/all.xml |

**Not:** Reuters ve AP'nin public RSS'i yok — içerikleri SearXNG üzerinden çekilir.

### Katman 2 — SearXNG (ikincil, self-hosted)

Self-hosted, limitsiz, kredi derdi yok. Docker ile çalışır.

**API:** `http://127.0.0.1:8888/search`
**Port:** `127.0.0.1:8888:8080` (sadece localhost)

**settings.yml'de json formatı açık olmalı:**
```yaml
search:
  formats: [html, json]
server:
  limiter: false
  public_instance: false
```

**Kullanım:**
```bash
curl 'http://127.0.0.1:8888/search?q=bitcoin+etf&format=json&language=en&categories=news&time_range=month'
```

**Python:**
```python
resp = requests.post('http://127.0.0.1:8888/search', data={'q': q, 'format': 'json', 'language': 'en'})
for r in resp.json()['results'][:5]:
    print(r['title'], r['url'], r.get('content','')[:200])
```

### Kullanım Sırası
1. Önce RSS bundle (blogwatcher DB → 48 saat)
2. Eksikse SearXNG
3. Son çare Serper (kredili)

> **Serper sadece backup** — RSS + SearXNG öncelikli. Edel'in setup'ında Serper backup pozisyonunda.

## Strateji Pattern'leri

### Pattern 1: News Signal 📡
AI'nın haber akışını tarayıp market fiyatıyla karşılaştırdığı temel strateji.

**Tavsiye edilen implementasyon:** `pm-trader markets list` ile market verisi çekilir, analiz cronjob agent'ında yapılır. `collect_data.py` (varsa) opsiyoneldir — yoksa `pm-trader markets list` doğrudan kullanılır.

**⚠️ ÖNEMLİ — news_signal_collect.sh path sorunu (26 Haz 2026):**
Hermes Docker container'ında `/data/` mount edilmemiş olabilir. Eski script (`cd /data/pm-trader && python3 strategies/collect_data.py`) hata verir. **Fix:**
```bash
# news_signal_collect.sh — çalışan versiyon:
DATA_DIR="/home/ubuntu/.local/share/pm-trader"
mkdir -p "$DATA_DIR"
pm-trader markets list > "$DATA_DIR/latest_scan.json" 2>/dev/null
pm-trader portfolio --format json 2>/dev/null > "$DATA_DIR/portfolio.json"
```

**⚠️ ÖNEMLİ — pm-trader markets search sınırlaması:** `pm-trader markets search "trump"` gibi genel terimler, alakalı marketler yerine en popüler marketleri döndürür (çoğunlukla GTA VI meme marketleri). Bunun yerine **Gamma API'yi direkt kullan** ve tag bazında event'leri çek:

```python
# DOĞRU: Gamma API events endpoint (tag bazlı)
url = f"https://gamma-api.polymarket.com/events?tag={tag}&closed=false&limit=8&order=volume_usd&asc=false"
# tag: crypto, politics, tech, world, finance

# YANLIŞ: pm-trader search (meme market döndürür)
pm-trader markets search "trump"
```

**⛔ collect_data.py uyarısı (26 Haz 2026):** `collect_data.py` script'i Hermes Docker container'ında mevcut olmayabilir (`/data/pm-trader/strategies/` dizini yok). Çözüm: `pm-trader markets list` ile doğrudan market verisi çekilir. Bu komut 20+ market döndürür, JSON formatında.

**Akış (tek aşamalı — collect_data.py yoksa):**

**Aşama 1 — Data Collection (script, ~10sn):**
```bash
pm-trader markets list > /path/to/latest_scan.json
```
`collect_data.py` (varsa) Gamma API + RSS haberlerini de ekler. Yoksa sadece `pm-trader markets list` yeterlidir.

**Aşama 2 — LLM Analysis (cronjob agent):**
- Cronjob agent'ı latest_scan.json'u okur
- Her market için rss_news + searxng_news'i analiz eder
- Karar: BUY YES / BUY NO / HOLD (deepseek-v4-flash ile)
- Paper trade açar, özet raporlar

**Neden iki aşama?**
- Pollinations free tier rate limit (429) — script'ten API çağırmak güvenilmez
- Local Ollama (phi4-mini) çok yavaş (62sn/market) — ARM64 CPU'da inference yavaş
- Hermes cronjob agent = deepseek-v4-flash, hızlı, limitsiz, sıfır maliyet
- Script terminal'de çalışır, LLM analizi agent context'inde — ayrı kaynaklar

**Cronjob yapılandırması:**
```bash
**Cronjob yapılandırması (deepseek-v4-flash-free, ücretsiz):**
```bash
# Model: opencode-zen'de deepseek-v4-flash-free (ücretsiz, limitsiz)
# NOT: news_signal_collect.sh /data/pm-trader/ gerektirmez — pm-trader markets list kullanır
# NOT: collect_data.py opsiyoneldir — pm-trader markets list yeterlidir
cronjob action=create \
  name="Polymarket News Signal Scan" \
  schedule="0 10 * * 1,3,5" \
  script=news_signal_collect.sh \
  model=deepseek-v4-flash-free,provider=opencode-zen \
  deliver=origin \
  prompt="..."
```
```

**Meme market filtresi (stratejide):**
```python
# pm-trader markets search "trump" gibi genel terimler GTA VI marketlerini de döndürür
# Filtre: question'da "gta vi", "jesus", "rihanna", "playboi", "carti" varsa ve volume<500K ise atla
question = m.get('question', '').lower()
if any(w in question for w in ['gta vi', 'jesus', 'rihanna', 'playboi']):
    if volume < 500000:
        continue
```

**Prompt şablonu (LLM analizi için):**
```
Market: {question}
Current price: {outcome} @ ${price}
End date: {end_date}

Recent news about this topic:
{news_snippets}

Analyze: Is the market price consistent with the news? 
Is there a trading opportunity? Respond with:
- SIGNAL: yes/no
- DIRECTION: YES/NO
- CONFIDENCE: 0-100
- REASONING: 1-2 sentences
```

**Risk parametreleri (önerilen başlangıç):**
- **Pozisyon büyüklüğü:** Order book derinliğine göre belirle (bkz: Pitfall 5). Sabit $500 kullanma — önce `pm-trader book SLUG` ile ilk 3 kademedeki toplam derinliği kontrol et, bunun %50'sini geçme
- İlk 10 trade'de $10-20/pozisyon (likiditeyi öğrenme aşaması)
- Maksimum 3 eşzamanlı pozisyon
- Stop-loss: fiyat %10 tersine giderse çık
- Min fiyat farkı: AI analizi marketten %15+ farklıysa trade

### Pattern 2: Obvious Mispricing 💰
Düşük risk, yüksek edge fırsatları. Market fiyatının bariz şekilde yanlış olduğu durumları tespit eder.

**⚠️ ÖNEMLİ DÜZELTME (25 Haz 2026):** Bu pattern'in orijinal edge hesaplaması hatalıydı. Aşağıdaki doğru analizi oku.

**GTA VI "Before" Marketlerinin Gerçek Dinamiği:**

Bu marketlerdeki kritik kural: *"If neither occurs by July 31, 2026 — resolve 50-50"*.

GTA VI **Fall 2026 için onaylanmış** (Rockstar/Take-Two). Yani 31 Temmuz'dan önce GTA VI çıkma ihtimali **~%0**. Bu şu anlama gelir:

- P(GTA VI before Jul 31) ≈ **%0**
- P(X event before Jul 31) = p (bilinmeyen)
- P(neither) = 1 - p

Resolution:
- X gerçekleşirse → YES=$1, NO=$0
- GTA VI çıkarsa → NO=$1, YES=$0 (ama bu olmayacak)
- Hiçbiri olmazsa → **50/50, her iki tarafa $0.50**

NO için fair value:
```
= G × $1 + p × $0 + (1-G-p) × $0.50
= G + 0.5(1-G-p)
= 0.5 + 0.5(G-p)
G ≈ 0 olduğu için:
= 0.5 - 0.5p
```

Yani:
| p (diğer olay ihtimali) | Fair NO fiyatı | NO @ 48¢'de edge |
|---|---|---|
| %0 (hiç olmaz) | 50.0¢ | +2.0¢ (%4.2) |
| %5 | 47.5¢ | -0.5¢ (negatif!) |
| %10 | 45.0¢ | -3.0¢ (negatif!) |

**Maksimum edge: ~%4.2** (p=%0 varsayımıyla). **%40-47 değil.** Orijinal hesaplamadaki hata:
1. GTA VI'nın 31 Temmuz'dan önce çıkma ihtimalini %95 varsaydı — oysa Fall 2026 onaylanmış, çıkma ihtimali ~%0
2. Diğer olayın (albüm vb.) gerçekleşme ihtimalini sıfır varsaydı
3. Formül `0.95 × $1 + 0.05 × $0.50 = $0.975` yanlıştı çünkü 50/50'de **her iki outcome da $0.50 alır** — bu bir "para iade" değil, her iki tarafın da eşit değer kazanmasıdır

**Sonuç:** GTA VI "before" marketleri, 50/50 fallback clause'u sayesinde her iki tarafta da ~50¢'de efficient fiyatlanır. Edge maksimum %4.2 (p=%0 ise) — transaction cost ve spread'i geçmez. **Bu kategoride gerçek mispricing yoktur.** Pattern tarihi referans olarak tutulur ama ARTIK trade açılmaz.

**Detection logic (GÜNCELLENMİŞ):**
```python
# GTA VI "before" marketleri: 50/50 floor nedeniyle edge yok
# NO fiyatı $0.50-$0.52 aralığı = efficient pricing
# Sadece NO < $0.45 ise anlamlı edge olabilir (ama hiç görülmedi)
# ÖNERİ: Bu marketleri tamamen filtrele, tarama raporunda bile bahsetme
# Daha iyi mispricing fırsatları: sport, finance, crypto kategorilerinde ara
```

**Risk parametreleri:**
- $200/pozisyon (news signal'dan daha düşük risk)
- Max 5 pozisyon
- Edge > %15 zorunlu
- Volume > $10K zorunlu

**Cronjob: Salı-Perşembe 10:00 UTC+3**
```bash
# Script: mispricing_scan.sh
#   pm-trader markets search "before gta vi" --limit 30
#   Python inline: filtrele (no_price < 0.52, likidite > $10K, olay imkansıza yakın)
#   Çıktı: ~/.hermes/data/latest_mispricing.json
# Model: deepseek-v4-flash-free, provider=opencode-zen
```

**⚠️ Uyarılar:**
- Meme marketlerde analiz yaparken ciddiyetini koru. Kullanıcıya "bak bu bariz hata, alıyoruz" mesajı yeterli — fazla açıklama gerekmez.
- **50/50 floor:** GTA VI yarış marketlerinde resolution kuralı "ikisi de olmazsa 50/50" olduğu için NO fiyatı $0.50 tabanına dayanır. Jesus, BTC $1M, Trump, China marketlerinin NO fiyatı ~$0.50-$0.505'e oturmuştur — burada EDGE YOKTUR. Sadece hâlâ $0.50'nin altında işlem gören marketler (şu an Rihanna ~48¢, Carti ~46¢) gerçek sinyaldir.
- **Clarity, not essays:** Kullanıcıya trade özetini verirken "şu markette şu gerekçeyle şu trade'i açtım" formatı yeterli. 3 paragraflık açıklama yazma — 2-3 cümle maksimum.

## Market Keşfi (Gamma API ile Tarama)

Polymarket'te aktif ve yüksek hacimli marketleri bulmak için:

```bash
# En yüksek hacimli event'ler (sıralı)
curl -s 'https://gamma-api.polymarket.com/events?closed=false&limit=30&order=volume_usd&asc=false'

# Kategoriye göre marketler
curl -s 'https://gamma-api.polymarket.com/events?tag=crypto&limit=10&closed=false&order=volume_usd&asc=false'
curl -s 'https://gamma-api.polymarket.com/events?tag=politics&limit=10&closed=false&order=volume_usd&asc=false'
curl -s 'https://gamma-api.polymarket.com/markets?tag=crypto&limit=20&closed=false&order=volume&asc=false'
```

**Önemli:**
- Her event birden çok market içerir (zaman bazlı dilimler)
- `outcomePrices` JSON string olarak double-encoded gelir — `json.loads()` ile parse et
- Fiyat = olasılık: 0.65 = %65
- `volume` USDC cinsindendir
- `conditionId` ile fiyat geçmişi sorgulanabilir

Detaylı API referansı için: `references/polymarket-api-endpoints.md`

### Pattern 3: Copy Trading Evaluator (İzleme Modu) 🐋

Balina trader'ları ve yüksek hacimli marketlerdeki anomalileri tespit eder. **SADECE değerlendirme — otomatik trade AÇMAZ.** Amaç: hangi marketlerin balina ilgisi gördüğünü ve hangi fiyatların aşırı uçlarda olduğunu izlemek.

**Çalışan implementasyon:** `/data/pm-trader/strategies/copy_trade_evaluator.py`

**Akış:**
1. Gamma API'den en yüksek hacimli 20 event çekilir (crypto, politics, world, finance)
2. Her marketteki son trades incelenir
3. Resolved marketler (fiyat %0 veya %100) filtrelenir — zaten kesinleşmiş, sinyal değiller
4. 2 sinyal tipi üretilir:

| Sinyal | Koşul | Aksiyon |
|--------|-------|---------|
| `whale_watch` | Hacim > $1M + fiyat 0.25-0.75 (contested) | **IZLE** — balina girişi olabilir |
| `near_extreme` | Hacim > $500K + fiyat < %20 veya > %80 | **ARASTIR** — piyasa kesin ama ters fırsat var mı? |

**Çıktı:** `/data/pm-trader/latest_copy_trade_eval.json`

**Önemli tasarım kararları:**
- `action` alanı her zaman `IZLE` veya `ARASTIR` — asla `BUY` veya `SELL`
- Resolved marketler (0%, 100%) atlanır — false positive'leri önler
- Threshold'lar: whale_watch için $1M+ contested, near_extreme için $500K+ + uç fiyat

**Manuel çalıştırma:**
```bash
cd /data/pm-trader && python3 strategies/copy_trade_evaluator.py
```

**Gelecek adımlar (uygulanmadı, sadece değerlendirme):**
- Polymarket API'den top trader adreslerini tespit etmek (≈80 satır ekleme)
- "Whale buying YES on X market" tespiti
- Gerçek copy trade için Polygon cüzdanı + USDC gerekir

---

### Pattern 4: Bregman Arbitraj 📐
```python
total = yes_price + no_price
if total < 0.98:
    edge_pct = (1.0 - total) / total * 100  # % garanti kâr
    # Her iki tarafı da al → hangi sonuç çıkarsa çıksın $1.00 alırsın
```

**Çalışan implementasyon:**
- `collect_data.py` v2.1 → `get_markets_direct()` içinde YES+NO kontrolü, `arbitrage_opportunities` listesine ekler
- `mispricing.py` → scan sonrası aynı kontrolü yapar, çıktıya `arbitrage_opportunities` ekler
- Her iki script de `arbitrage_opportunities` alanını JSON çıktısına yazar

**Eşikler:**
- `total < 0.98` → fırsat (threshold, ayarlanabilir)
- Her pozisyona ~$100-200 (düşük notional, seyrek fırsat)
- Fee/slippage edge'i yememeli — fee_rate_bps kontrol et

**Beklenen getiri:** Düşük (%1-3) ama **sıfır risk**. Fırsatlar seyrek — volatil anlarda ve düşük hacimli marketlerde çıkar.

---

### Pattern 5: Dexter's Lab Simülasyon (BTC Takip) ₿

Polymarket'te BTC fiyatı ile anlık hareketler arasındaki gecikmeyi yakalamayı hedefler.

**⚠️ ÖNEMLİ — 5dk BTC Up/Down Marketleri YOK (11 Haz 2026):** Dexter's Lab'ın kullandığı 5-15 dakikalık "BTC Up or Down" marketleri Polymarket'te **artık mevcut değil.** Bu pattern'in orijinal mekanizması (Binance'dan BTC fiyatı al → Polymarket gecikmesini yakala → 5dk markete gir) şu an çalışmaz.

**Mevcut simülasyon:** `/data/pm-trader/strategies/dexters_lab_sim.py`
- Binance'dan BTC fiyatını takip eder (snapshot veya WebSocket)
- 24s değişim > %2 ise "OLASILIK_VAR", > %1 ise "IZLE", yoksa "BEKLE"
- Gerçek emir yok — sadece sinyal takibi
- Çıktı: `/data/pm-trader/dexters_lab_sim.json`

**Gelecekte gerçek altyapı için gerekenler:**
1. Polygon cüzdanı + USDC
2. CLOB API entegrasyonu (EIP-712 signature)
3. Binance WebSocket (BTC anlık fiyat)
4. Düşük latency sunucu (mevcut Oracle Cloud yeterli olmayabilir)
5. 2-3 saniye içinde karar + emir gönderme

**Modlar:**
- `python3 dexters_lab_sim.py` — snapshot (tek seferlik)
- `python3 dexters_lab_sim.py --continuous` — WebSocket canlı takip (60sn örnek toplar)

**Simülasyon başarılı olursa → paper trade → küçük canlı test sırası izlenir.**

---

## Test Planı (Zorunlu sıralama)

### Evre 0 — Offline/Backtest
- polymarket-paper-trader ile backtest: `pm-trader benchmark run`
- Minimum parametre (overfit azalt)
- Fee + slippage simülasyonu dahil

### Evre 1 — Paper-trade
- Gerçek Polymarket order book'larına karşı simüle et
- Slippage ve fee gerçekçi (level-by-level execution)
- Metriğe göre otomatik durdurma

### Evre 2 — Shadow mode (emir yok)
- Gerçek veri akışıyla sinyal üret
- No-trade zone etkinliği ölç

### Evre 3 — Small live test
- Çok küçük notional
- Hard risk gates: daily loss limit, max drawdown, max concurrent positions

## Başarı Ölçütleri
Her evrede raporla: Net PnL, ROI, Max drawdown, Win rate, Expectancy.

## Context (Memory) Yönetimi — Kritik

Polymarket sistemini Hermes'e entegre ederken context/memory şişmesini önlemek için:

**🚫 YAPMA:**
- Sürekli açık MCP server bağlantısı (context'i kalıcı olarak şişirir)
- Her trade kararını kullanıcıya tek tek sormak
- Tüm market/pazar verisini sohbet context'inde tutmak

**✅ YAP:**
- **Cronjob tabanlı çalışma**: Strateji tarama + paper trade cronjob olarak çalışır. Her run bağımsız session'dadır, context'e etkisi sıfırdır.
  - **Program:** Pazartesi-Çarşamba-Cuma, 10:00 UTC+3 (haftasonu likidite düşük, spread açık)
  - **Neden 3 gün:** Haftasonu sinyal-gürültü oranı kötü; Pazartesi haftayı açar, Çarşamba pivot, Cuma kapatış
  - **Süreç:** Market tara → sinyal varsa paper trade yap → özet çıkar
  - **Yapı:** Bağımsız session, context sıfır, results auto-deliver
- **Sadece özet bildir**: Kullanıcıya trade başına değil, periyodik özet raporlar iletilir (ör: "Bu hafta +$85, 3 trade").

**📋 Standart Rapor Formatı (cron job output):**
Tüm cron job raporları aşağıdaki formatta teslim edilir:
```markdown
📡 **{Scan Başlığı}** — {tarih}
├ Marketler taranan: {sayı}
├ Sinyaller: {sayı}
├ Yeni trades: {sayı}
└ Edge: ~{yüzde}

**Detaylı Analiz:**
1. {Market / sinyal 1 — edge hesaplaması, neden trade/non-trade}
2. {Market / sinyal 2 — ...}

**Portföy Durumu:**
- 💰 Nakit: ${X}
- 📊 Pozisyon: {Y}
{var ise: - 📈 PnL: ${Z}}

**Not:** {bir insight veya uyarı}
```
- Emoji tree yapısı (├ └) ile hiyerarşik özet
- Detaylı analiz numbered list ile
- Portföy durumu ayrı blokta
- Not varsa en sonda
- **Data diskinde loglama**: Tüm trade geçmişi, P&L, portföy durumu `/data/pm-trader/` altındadır. Sadece ihtiyaç halinde okunur.
- **delegate_task ile analiz**: Detaylı market analizi gerektiğinde arka plan subagent'ına devredilir, sonuç kısaca iletilir.

**Data Dizini:**
- Binary ve data dosyaları ana diskten (`/`) değil, `/data/` diskine kurulur (75G boş alan) — **Docker container'da mevcut değilse** `~/.local/share/pm-trader/` kullanılır
- Ortam değişkeni: `PM_TRADER_DATA_DIR=/data/pm-trader` (opsiyonel)
- Trade logları, strateji backtest sonuçları, portföy snapshotaları bu dizinde kalır
- **Cron veri toplama (script hatasına karşı):** `pm-trader markets list` doğrudan JSON döndürür — pipe/capture ile kullanılır. Ek Python script'i gerektirmez.

## Canlı geçiş kriteri (gate)
- Shadow mode'da sinyal eşikleri stabil
- Paper-trade'de drawdown limiti hiç aşılmamış
- Farklı piyasa rejimlerinde performans bozulmamış

---

## references
- `references/paper-trader-commands.md` — Komple CLI komut referansı ve kullanım örnekleri
- `references/polymarket-market-landscape.md` — Güncel market kategorileri, hacimler ve strateji önceliklendirme
- `references/rss-feed-bundle.md` — 14 RSS kaynağının tam listesi, ekleme komutları ve bakım notları
- `references/mispricing-strategy.md` — Obvious Mispricing stratejisi detaylı teori ve trade yönetimi
- `references/cron-schedule.md` — Tüm cronjob'ların programı, ID'leri ve model ayarları
- `references/kraken-ipo-first-trade.md` — İlk paper trade deneyimi: Gamma API keşfi, order book analizi, slippage dersi (27 Haz 2026)
- `scripts/mispricing_scan.sh` — Otomatik mispricing tarama scripti (Gamma API tabanlı, Bregman kontrolü dahil)
- `scripts/news_signal_collect.sh` — News Signal veri toplama scripti (blogwatcher + pm-trader)
- `scripts/pm_master_scan.py` — Tüm pattern'leri tek script'te çalıştıran master scan (Pattern 1-5)
- `scripts/whale_tracker.py` — Copy Trading/Whale izleme scripti (Gamma API + sinyal üretimi)
- `scripts/btc_tracker.py` — Dexter's Lab BTC simülasyonu (Binance API + sinyal üretimi)
- `references/cron-schedule.md` — Güncel cronjob ID'leri ve schedule
