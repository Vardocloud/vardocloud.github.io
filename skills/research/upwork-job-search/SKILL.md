---
name: upwork-job-search
description: Upwork job search and opportunity monitoring — daily cron scanning + on-demand querying. Bypasses Cloudflare via Google Custom Search API (primary), official API (secondary), or user-side extension (fallback).
category: research
---

# Upwork Job Search & Opportunity Monitoring

## When to Use
- User wants to find Upwork job opportunities matching specific keywords/skills
- Daily automated scanning via cron job + manual on-demand queries
- Evaluating job quality (budget, client history, proposal count) before applying
- User is a freelancer looking for leads, not a client posting jobs

## Critical Understanding: Cookies ≠ Browsing

**Oturum cookie'leri canlı olsa bile, Oracle Cloud IP'sinden Upwork'e browser ile erişilemez.** Cloudflare, datacenter IP aralıklarını (Oracle Cloud, AWS, DigitalOcean) network seviyesinde bloklar — herhangi bir HTTP isteği (GET dahil) 403 alır. Bu, cookie'lerin geçerliliğinden **bağımsız** bir engeldir.

Cookie'ler sadece Camoufox tabanlı `upw_session_refresh.cjs` script'inin session refresh yapabilmesini sağlar (script Cloudflare challenge'ını bir şekilde aşar). Ancak aynı cookie'lerle bile:
- Puppeteer/Chrome 9222 (local browser) → 403
- curl/wget → 403 veya challenge sayfası
- Browserbase Cloud → login sayfası (cookie'ler cloud'da olmadığı için)

**Kısacası:** Cookie'ler = Upwork'te oturum canlı demek. Ama bu sunucudan Upwork'e göz atmak anlamına gelmez. İş aramak için aşağıdaki Cloudflare-bypass yöntemleri kullanılmalıdır.

## Architecture: Dual-Mode

### Mode 1: Daily Cron (Automated Scanning)
- Runs on schedule (recommended: every 6-12 hours)
- Searches for predefined keywords
- Filters and ranks jobs by quality signals
- Delivers summary report to user via Telegram

### Mode 2: On-Demand Query
- User asks: "Upwork'ta python işleri var mı?" or similar
- Immediate search with custom keywords
- Returns structured job list with analysis

## Data Sources (Ranked by Viability on Oracle Cloud)

### 1️⃣ Google Custom Search API (PRIMARY — Free, Works)
**Why:** Searches Google's index of Upwork, not Upwork directly. Cloudflare never sees the request.

**Setup:**
- Google Custom Search Engine (CSE) at `programmablesearchengine.google.com`
- Configure to search `site:upwork.com/nx/search/jobs/*` or `site:upwork.com/jobs/*`
- API key + Search Engine ID (cx)
- Free tier: 100 queries/day

**Query format:**
```
site:upwork.com/jobs "python" "machine learning"
```

**Output parsing:** Google returns URL + snippet. Extract job ID from URL, fetch detail page via Firecrawl if needed.

**Limitations:**
- Google indexes with delay (jobs may be 1-24 hours old)
- Cannot see proposal count or exact budget from snippet
- 100 queries/day limit

### 2️⃣ Upwork Official API (SECONDARY — Requires OAuth)
**Why:** API endpoint (`api.upwork.com/graphql`) uses different infrastructure than the website. No Cloudflare.

**Setup:**
- User creates app at `https://www.upwork.com/developer/keys/apply`
- One-time OAuth authorization from user's device (authorization code flow)
- Access token TTL: 24 hours, refresh token: 2 weeks
- Requires `Common Entities - Read-Only Access` scope

**Endpoints:**
- GraphQL: `https://api.upwork.com/graphql`
- Query: `jobs` with filters for keywords, category, budget range
- Returns structured JSON with all job fields

**Limitations:**
- Requires user to authorize once from their device
- Token refresh needed every 2 weeks
- API rate limits apply

### 3️⃣ User-Side Chrome Extension (FALLBACK)
**Why:** Runs on user's real residential IP, no Cloudflare issue.

**Tools:**
- `Upwork-Job-Scraper` Chrome extension (github: richardadonnell/Upwork-Job-Scraper)
- Configures webhook to POST job data to our server
- Runs on user's browser schedule

**Limitations:**
- User's computer must be on + Chrome running
- Webhook endpoint must be publicly accessible

### ❌ DO NOT USE (Blocked from Oracle Cloud)
These all fail because Oracle Cloud datacenter IPs are fully blacklisted by Cloudflare:
- Direct browser automation (Puppeteer, Playwright, Camoufox, nodriver)
- RSS feeds
- curl/wget
- Firecrawl (scrapes directly, gets Cloudflare challenge)
- puppeteer-real-browser (auto-solve turnstile: returns `success:true` with `0 jobs` — **false success**, does NOT fail loudly)

**Verified (June 2026):** `puppeteer-real-browser` returns `{"success":true,"totalJobs":0,...}` even when Cloudflare is serving a challenge page. Always verify `totalJobs > 0`.

See `cloudflare-bot-bypass` skill's `references/upwork-case-study.md` for full details.

### 4️⃣ Search API Fallback — Serper/Brave (Works Now, Limited Quality)

**When:** Google CSE API key henüz yapılandırılmadıysa.

**Why it works:** Serper (Google SERP) ve Brave Search kendi indekslerini sorgular — Cloudflare tetiklenmez.

**Setup:** API key'ler zaten mevcut (`~/.hermes/serper_key.txt`, `~/.hermes/brave_key.txt`). `serper-search` veya `brave-search` skill'lerindeki curl komutlarını kullan.

**⚠️ Quality Warning — Google Snippet Sorunu:**
Google'ın Upwork snippet'leri **sayfa navigasyon metnini** gösterir (Data Entry, Virtual Assistant linkleri), iş başlığını değil. Çoğu sonuç alakasız çıkar. Job ID'yi URL'den çıkarıp detay sayfasını web_extract ile kontrol et.

**Keywords stratejisi:** Dar ve spesifik sorgular kullan. Genel kelimeler çok noise üretir. En iyisi: Edel'e hangi roller ilgisini çeker diye sor, ona göre sorgu yap.

### 4️⃣ Search API Fallback — Serper/Brave (Works Now)

**When:** Google CSE API key henüz yapılandırılmadıysa veya hızlı bir tarama gerekiyorsa.

**Why it works:** Serper (Google SERP) ve Brave Search, Google/Brave'ın kendi indeksini sorgular — Cloudflare'i tetiklemez. Upwork'in Cloudflare Bot Management'ı bypass edilir.

**Setup gerektirmez:** API key'ler zaten mevcut:
- `~/.hermes/serper_key.txt` — 2.500 sorgu/ay
- `~/.hermes/brave_key.txt` — 2.000 sorgu/ay

**Query format:**
```
site:upwork.com/jobs "keyword1" "keyword2" remote
site:upwork.com/jobs (virtual assistant OR data entry) entry level
```

**Implementation:** `terminal` ile curl → Serper/Brave API → Python ile parse.

**⚠️ Quality Warning — Google Snippet Sorunu:**
Google'ın Upwork sayfalarından aldığı snippet'ler **sayfa navigasyon metnini** gösterir (Data Entry, Virtual Assistant linkleri), gerçek iş başlıklarını değil. Bu yüzden:
- Dönen sonuçların çoğu alakasız olabilir (yazılım test, video editing, fotoğrafçılık karışır)
- Her sonucun link'ine tıklayıp web_extract ile teyit gerekir
- Job ID'yi URL'den çıkarıp `web_extract` ile detay sayfasını almak daha güvenilirdir
- Google CSE API (Mode 1) kurulunca bu yöntemden daha kaliteli sonuç alınır

**Keywords stratejisi:**
Serper'da genel anahtar kelimeler çok noise üretir. Mümkün olduğunca spesifik ve dar sorgular kullan:
- `site:upwork.com/jobs "psikoloji"` → Çok az sonuç (Upwork İngilizce ağırlıklı)
- `site:upwork.com/jobs "research" "psychology"` → Daha iyi
- `site:upwork.com/jobs "virtual assistant" OR "admin support"` → Çok geniş, noise yüksek
- En iyisi: Edel'e hangi roller ilgisini çeker diye sor, ona göre dar sorgu yap

## Job Quality Scoring

When evaluating jobs, score on these signals:

| Signal | Weight | Good | Bad |
|--------|--------|------|-----|
| Payment verified | +20% | Yes | No |
| Client spent | +15% | $1K+ | $0 |
| Client rating | +10% | 4.5+ | No rating |
| Proposals | +10% | <10 | >30 |
| Budget clarity | +10% | Fixed/hourly specified | "TBD" |
| Description length | +5% | Detailed (>200 words) | Vague |

## Cron Job Configuration

```
Schedule: every 6h (or 12h for lighter usage)
Keywords: User's skill keywords (stored in config/memory)
Delivery: Telegram message with top N jobs + analysis
Filter: Only jobs scored above threshold (e.g., 60%)
```

## Output Format (Turkish)

When delivering job results to user:

```
🔍 Upwork — [keyword] işleri (son 24 saat)

✅ [Job Title]
💰 Budget: $X (Fixed/Hourly)
👤 Client: Verified ✓ | $Y spent | Rating: Z
📝 Proposals: N
🔗 [Direct link]
💡 Not: [AI analysis — why this is a good fit]

---
Toplam: N iş bulundu, M tane yüksek kaliteli
```

## Pitfalls

- ❌ **Do NOT submit proposals or applications without user's explicit approval** — hard rule
- ❌ **Do NOT auto-fill profile information** — requires user input
- ❌ **Do NOT use direct scraping from Oracle Cloud** — Cloudflare blocks all datacenter IPs
- ❌ **Do NOT pay for Apify or similar scraping services** when free alternatives exist (Google CSE, Serper)
- ❌ **Do NOT claim cookies enable browsing** — cookie'ler session refresh için yeterlidir ama Cloudflare IP block'u yüzünden browsing için kullanılamaz (403). Bunu en başta net söyle.
- ❌ **Do NOT trust Serper/Brave snippet başlıkları** — Upwork sayfalarının snippet'leri navigasyon metni gösterir, gerçek iş başlığı değil. web_extract ile sayfayı açıp kontrol et.
- ❌ **Do NOT try to browse job search pages from this server** — Camoufox + WARP + proxychains4 bile job search sayfalarında Cloudflare challenge'a takılır (104.28.x.x WARP IP'si de bot algılanır). Ana sayfa ve profil sayfaları çalışır, job search sayfaları çalışmaz.
- ❌ **Do NOT expect find-work before profile completion** — Until profile passes step 3/10 (Skills), `/nx/find-work/` redirects to `/nx/create-profile/`. Even with active cookies, job search is inaccessible via browser. Complete the profile first, then search.
- ❌ **Do NOT trust Next buttons blindly** — Upwork's Nuxt/Vue profile pages may render Next as `disabled=false` but clicking does nothing (event handler not bound). Use `window.location.href` bypass for stuck steps.
- ❌ **Do NOT waste time on WARP for job search pages** — Even with WARP+proxychains4, `/nx/search/jobs/` and `/freelance-jobs/` return Cloudflare challenge (Ray ID visible). Only `/nx/create-profile/*` pages work through WARP.
- ✅ **Always include source + freshness** next to numerical data
- ✅ **Echo → Question → Listen** when discussing opportunities with user
- ✅ **Store found jobs in wiki** for tracking and deduplication

## Related Skills
- `cloudflare-bot-bypass` — Why direct Upwork access fails from datacenter IPs
- `upwork-cookie-session` — Upwork account session management
- `upwork-mcp-integration` — Upwork MCP server setup (if using official API)
- `firecrawl` — For parsing job detail pages (only works via Google-indexed URLs, not direct Upwork)