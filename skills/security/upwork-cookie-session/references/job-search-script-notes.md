# Upwork Job Search with Camoufox — Session Notes (Updated 14 June 2026)

## Background
Camoufox + WARP + proxychains4 ile Upwork ana sayfasına erişilebiliyor. Cookie'ler çalışıyor, oturum açık.
Ancak job search sayfaları Cloudflare challenge gösteriyor — WARP IP'si de bot algılanıyor.

## Key Findings

### Çalışan
- Camoufox + proxychains4 (`geoip: false`) + WARP → Upwork ana sayfası ✅
- Cookie inject ile oturum açık, create-profile sayfası görüntülenebiliyor ✅
- `/nx/create-profile/general` ve `/nx/create-profile/skills` sayfaları çalışıyor ✅
- Profil title sayfası (`/nx/create-profile/title`) ✅

### Çalışmayan
- `/nx/find-work/` → profil 3/10'da kaldığı için `/nx/create-profile/skills`'e yönlendirir
- `/freelance-jobs/` → Cloudflare challenge (WARP IP = 104.28.x.x)
- `/search/jobs/?q=...` → Cloudflare challenge veya 404
- GraphQL API (`api.upwork.com/graphql`) → 401 (authentication failed)
- Camoufox proxy parametresi (socks5) → NS_ERROR_UNKNOWN_PROXY_HOST
- Browserbase Cloud → Cloudflare challenge (residential IP bile takılıyor)

### Mevcut Script
`/home/ubuntu/.hermes/upw_job_search.cjs` — deneme amaçlı, cookie load + Camoufox + proxychains4.
Çalıştırma: `cd ~/.hermes && proxychains4 -q node upw_job_search.cjs`

## Profile Completion Flow (Tested 14 June 2026)

Profili tamamlamak için Camoufox ile adım adım ilerlenebilir:

### Step 3/10 — Skills
- URL: `https://www.upwork.com/nx/create-profile/skills`
- **Input:** `input[placeholder="Enter skills here"]`
- **Dropdown:** `[role="option"]` — ilk eşleşen tıkla (tam eşleşme genelde ilk sırada)
- **Max 15 skills**
- **⚠️ Pitfall:** Camoufox crash olursa TÜM skill'ler silinir — sayfa refresh'te kaydedilmez. Her ekleme sonrası tag sayısını kontrol et.
- **Next butonu:** `button` içinde "Next" metni olan

### Step 4/10 — Profile Title
- URL: `https://www.upwork.com/nx/create-profile/title`
- Tek bir input: "Your professional role"
- Örnek: "Psychology Researcher & Academic Writer"

### Psikoloji Alanı Skill'leri (Upwork'te mevcut)
Arama terimleri ve çıkan öneriler:
- `psycholog` → Psychology, Counseling Psychology, Industrial Psychology
- `mental` → Mental Health
- `counseling` → Counseling, Counseling Psychology, Child Counseling
- `academic` → Academic Research, Academic Editing, Academic Proofreading, Academic Content Development
- `research` → Research Paper Writing, Research Methods, Research Papers
- `behavioral` → Cognitive Behavioral Therapy
- `thesis` → Thesis, Thesis Writing

## Camoufox Crash Pattern (Playwright Bug)
```
TypeError: Cannot read properties of undefined (reading 'url')
    at FFBrowserContext.<anonymous> (FFPage._onUncaughtError)
```
**Tetikleyici:** `waitUntil: 'commit'` ile direkt `/nx/create-profile/skills`'e gitmek.
**Workaround:**
1. Önce `upwork.com/` ana sayfasına git (`waitUntil: 'load'`)
2. Sonra hedef sayfaya git (`waitUntil: 'load'`)
3. `page.on('pageerror', () => {})` handler'ı her zaman ekle
4. Crash olursa script'i yeniden çalıştır (retry)
