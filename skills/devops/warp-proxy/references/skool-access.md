# Skool Erişim ve Gezinti

## Erişim

- **Birincil yöntem:** `browser_navigate` + `browser.engine: auto` (Browserbase cloud)
- **Fallback 1:** Puppeteer MCP (`puppeteer_navigate` + `puppeteer_screenshot` + `vision_analyze`)
- **Fallback 2:** Browser Use CDP Remote Browser (Playwright `connect_over_cdp`) — **ÜCRETSİZ residential IP**
- **Neden Browserbase birincil:** Browserbase residential IP'leri Cloudflare tarafından bloklanmaz
- **Neden Puppeteer fallback:** Browserbase uzun session'larda veya çok sayfa değişiminde timeout verebilir (30-60sn). Puppeteer MCP sunucuda local Chromium kullanır, timeout olmaz
- **Neden CDP fallback:** Ücretsiz, residential IP, uzun session stabil. Dashboard'dan CDP URL'si gerekli.
- **Neden `engine: chrome` çalışmaz:** WARP = Cloudflare IP'leri → Skool (Cloudflare korumalı) kendi IP'lerini bloklar

### Browser Use CDP ile Skool Login

CDP URL'si Browser Use dashboard'dan alınır (`wss://<session-id>.cdp.browser-use.com`).

```python
import asyncio
from playwright.async_api import async_playwright

CDP_URL = "wss://<session-id>.cdp.browser-use.com"

async def skool_login():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()
        
        await page.goto("https://www.skool.com/login", wait_until="networkidle", timeout=30000)
        
        email = await page.query_selector('input[type="email"]')
        await email.fill("isimgorulsunn@gmail.com")
        
        pwd = await page.query_selector('input[type="password"]')
        await pwd.fill("41y%#Y8#Htts*kx3*amf5YJNU37^mn")
        
        btn = await page.query_selector('button[type="submit"]')
        await btn.click()
        
        await page.wait_for_load_state("networkidle", timeout=15000)
        await asyncio.sleep(3)
        
        content = await page.content()
        if "Vanilla" in content:
            print("LOGIN OK")
        
        await browser.close()

asyncio.run(skool_login())
```

**⚠️ CLOUD SESSION PARA HARCAR:** `browser_use_sdk.v3` ile `sessions.create()` ücretlidir. CDP bağlantısı ÜCRETSİZ.

## Puppeteer MCP Fallback Stratejisi

Browserbase timeout verdiğinde:
1. `puppeteer_navigate` ile sayfaya git
2. `puppeteer_fill` ile form doldur (`input[type="email"]`, `input[type="password"]`)
3. `puppeteer_click` ile butona tıkla (`button[type="submit"]`)
4. `puppeteer_screenshot` + `vision_analyze` ile içerik çıkar
5. Sayfa değişimi için `puppeteer_navigate` ile direkt URL'ye git (link tıklama yerine)

**Puppeteer MCP kısıtları:**
- `:has-text()`, `:contains()` seçicileri çalışmaz → `button[type="submit"]`, `input[type="..."]` kullan
- `puppeteer_evaluate` React sayfalarda `undefined` döner → screenshot + vision kullan
- Sayfalar arası hızlı geçişte "detached Frame" hatası → navigate'ler arası kısa bekleme ekle
- **Yedek yöntem:** Puppeteer MCP (`puppeteer_navigate` + `puppeteer_fill` + `puppeteer_click`)
  - Browserbase timeout verdiğinde (30sn+) kullan
  - ✅ Cloudflare/CloudFront WAF'ını aşar (gerçek Chromium)
  - ⚠️ `puppeteer_evaluate` React sayfalarda `undefined` döner — bunun yerine screenshot + vision kullan
  - ⚠️ `:has-text()` ve `:contains()` CSS seçicileri çalışmaz — `button[type="submit"]` kullan
  - Detaylı Puppeteer MCP bilgisi: `browser-debugging/references/puppeteer-mcp.md`

## Login

### ⚠️ Şifre Geçmişte Başarısız Olmuştu — Güncellendi (24 Haz 2026)

24 Haz 2026'da Browserbase Hermes browser'da şifre (`41y%#Y8#Htts*kx3*amf5YJNU37^mn`) ile login **başarılı** oldu. Şifre kalıcı olarak geçersiz değil — önceki başarısızlıklar Cloudflare/Browserbase geçici iletişim sorunundan kaynaklanmış olabilir.

**Login stratejisi (öncelik sırasına göre):**
1. **Önce şifreyle dene** — email + password ile `browser_type` + `browser_click("LOG IN")`
2. Şifre başarısız olursa ("Request failed" hatası) → "Log in with a code" + Gmail API fallback'ine geç
3. O da başarısız olursa → sayfayı yenile (yeni browser tab/session) ve tekrar dene

### 🔐 "Log in with a code" ile Login (FALLBACK — Şifre başarısız olursa)

Browserbase'de (`engine: auto`, Hermes browser) şu adımlarla başarılı login sağlanmıştır:

1. `browser_navigate("https://www.skool.com/login")` — login sayfası
2. `browser_type(@e5, "isimgorulsunn@gmail.com")` — email gir (ref'ler değişebilir, snapshot ile kontrol et)
3. `browser_click(@e4)` — "Log in with a code" butonuna tıkla
4. "We sent you a code" ekranı görünür — kod giriş alanı (`ref=e12` vb.) ve LOG IN butonu (`ref=e11` vb.) çıkar
5. Gmail'den kodu oku:
   ```bash
   GAPI="python /home/ubuntu/.hermes/skills/productivity/google-workspace/scripts/google_api.py"
   $GAPI gmail search "from:noreply@notifs.skool.com is:unread" --max 1
   ```
   En yeni email'in subject alanında kod: "XXXX is your Skool log in code"
6. `browser_type(@eXX, "KOD")` — kodu gir (snapshot'tan ref'i al)
7. `browser_click(@eYY)` — LOG IN butonuna tıkla (enable olduğunu kontrol et)
8. Hemen hedef URL'e git: `browser_navigate("https://www.skool.com/...")`

**⚠️ Kod 10 dakika geçerli.** Süresi dolarsa yeni kod iste — en yeni email en üsttedir.
**⚠️ Cookie drop:** Browserbase'de login sonrası navigate'da cookie'ler kaybolabilir ve "JOIN GROUP" görünebilir. Login → hedef URL zincirini aynı anda tut.
**⚠️ Snapshot başarısız olabilir:** Login sonrası redirect sırasında snapshot timeout verebilir. Beklemeden doğrudan hedef URL'e git.
**⚠️ Snapshot'taki ref'ler her seansta değişir:** `@e5`, `@e4`, `@e12`, `@e11` gibi ref'ler referanstır; her yeni browser_navigate'te yeniden snapshot alıp güncel ref'leri kullan.

- **URL:** `https://www.skool.com/login`
- **Email:** `isimgorulsunn@gmail.com`
- **Şifre:** ❌ Kalıcı olarak geçersiz
- **Birincil Login:** "Log in with a code" + Gmail API (google-workspace skill'i)
- **Profil adı:** Vanilla Gotus

## Topluluklar (5 Haziran 2026)

| # | Topluluk | URL | Üye | 3 Haz | Değişim | Durum |
|---|----------|-----|-----|-------|---------|-------|
| 1 | AI with Apex | ai-with-apex | 350 | 349 | +1 | 🔓 JOIN — ban kalkmış, içerik görünür, "JOIN FREE NOW" (Max Gibson, Voice AI odaklı) |
| 2 | Yapay Zeka ve Otomasyon | yapay-zeka-ve-otomasyon-5916 | 697 | 697 | = | ⏳ PENDING (Emrullah Yaprak, Türkçe, VPS/Deployment) |
| 3 | Yapay Zeka Sistemleri | mustafa-dikmen-ile-yapay-zeka-1691 | 2.1k | 2.1k | = | 🔓 JOIN GROUP (Mustafa Dikmen, en büyük Türkçe topluluk) |
| 4 | Zero2Launch | zero2launch-ai-automation-5951 | 5.4k | 5.4k | = | ✅ ÜYE — tüm sekmeler açık (Duyet Tran, "Claude + Higgsfield MCP Work...") |
| 5 | The AI Forge | ai-builders-forge-5366 | 510 | 511 | -1 | ⏳ PENDING (Leonardo Grigorio, n8n + MCP + Claude Code, "MVP in 30 days") |
| 6 | AI Automation Society | ai-automation-society | 391.1k | 389.2k | +1.9k | ✅ ÜYE — "Q&A w/ Nate in 4 days", Nate Herk "YouTube Resources 📚" |
| 7 | AI Money Lab | ai-seo-with-julian-goldie-1553 | bilinmiyor | — | — | ✅ UYE — 30+ modül (aylık AI Automation güncellemeleri, 50+ AI SEO Tools, AI SEO course). ⚠️ "200+ ChatGPT AI SEO Prompts" ve "N8N Automation Templates" modülleri ücretsiz değil — premium kursa ($497) yönlendirir. (Julian Goldie. Dogru URL: ai-seo-with-julian-goldie-1553. 404 veren slug: ai-seo-with-julian-goldie. Julian'in premium toplulugu AI Profit Boardroom: ai-profit-lab-7462) |
|| 8 | Yapay Zekâdan Gelire | u-gpt-ile-yapay-zekadan-gelire-4122 | 777 | — | +514 | ✅ JOINED (Umut Aktu, AI influencer/UGC/markalarla çalışma, ücretsiz. Slug değişti: yapay-zekadan-gelire 404 veriyor) |

## Login-with-Code + Gmail Entegrasyonu (1 Jun 2026)

Şifre bilinmiyorsa veya şifreyle giriş çalışmazsa:

1. `browser_type(@e5, "isimgorulsunn@gmail.com")` → email gir
2. `browser_click(@e4)` → "Log in with a code" butonu
3. Kod email'e düşer → Gmail API ile oku (`google-workspace` skill'i)
4. `$GAPI gmail search "from:noreply@notifs.skool.com is:unread"` → kodu bul
5. `browser_type(@e36, "KOD")` + `browser_click(@e29)` → LOG IN

**Pitfall:** Kod 10 dakika geçerli, süresi dolmuşsa yeni kod iste. Her kod isteği yeni email üretir, eskiler UNREAD kalır — en yeni email'deki kodu al.

## Login Akışı

1. `browser_navigate("https://www.skool.com/login")`
2. Email: `browser_type(@e5, "isimgorulsunn@gmail.com")` 
3. Şifre: `browser_type(@e6, "41y%#Y8#Htts*kx3*amf5YJNU37^mn")`
4. `browser_click(@e5)` — LOG IN butonu (ref değişebilir, snapshot ile kontrol et)
5. Giriş sonrası ana sayfaya yönlenir — profil menüsünde "Vanilla Gotus" görünür

## Gezinti

Her topluluk URL'si `https://www.skool.com/<slug>` formatında. About sayfası için `/about` eklenebilir.
Tam üye olunan topluluklarda Community/Classroom/Calendar/Leaderboards sekmeleri görünür.
Pending/üye olunmayan topluluklarda about sayfası ve "MEMBERSHIP PENDING" / "JOIN GROUP" butonu görünür.

## Classroom Modül Navigasyonu (9 Haz 2026)

Skool Classroom modülleri `disabled` button olarak render edilir — doğrudan butona `browser_click` işe yaramaz.

**Doğru yöntem:** Button'un içindeki `clickable [onclick]` child elemente tıkla:
```
button "N8N Automation Templates ..." [disabled, ref=e20]
  - generic [ref=e64] clickable [onclick]    → BUNU tıkla
```

**Tıklama sonrası doğrulama:** Skool client-side routing kullanır — snapshot/vision URL değişimini yakalamayabilir. `browser_console` ile kontrol et:
```js
document.location.href
```
URL `classroom/cd2c9e1b?md=...` formatına dönerse modül açılmıştır.

**İçerik değerlendirme:** Modül içinde link (`"Here you go - enjoy!"`) görünüyorsa bu genelde premium upsell'dir — Google Drive veya Notion gibi dış kaynağa değil, ücretli kurs satış sayfasına yönlendirir (9 Haz 2026: AI Money Lab'de 200+ ChatGPT AI SEO Prompts ve N8N Automation Templates modülleri Julian'ın $497 premium kursuna yönlendiriyordu).

## Pitfalls

- **🔴 KRİTİK: Şifre konumu (3 seans üst üste başarısız):** Şifre `41y%#Y8#Htts*kx3*amf5YJNU37^mn` BU DOSYADA (`references/skool-access.md`). `.env`'de `SKOOL_PASSWORD` olarak HENÜZ YOK. Login gerektiğinde `.env`, password store, wiki, session history aramak yerine ÖNCE bu dosyayı `skill_view(name='warp-proxy', file_path='references/skool-access.md')` ile oku. Bu dosya credential'ların tek yetkili kaynağıdır.
- `engine: chrome` ile Skool'a ERİŞİLEMEZ — Cloudflare timeout (60sn)
- Şifre özel karakter içeriyor (`%`, `#`, `*`, `^`) — browser_type ile düzgün yazılır
- Login sonrası bazen direkt topluluk sayfasına yönlenir (AI with Apex gibi)
- **Browserbase session'ları kısa ömürlü** — sayfalar arası cookie drop olabiliyor, her oturumda yeniden login gerekebilir
- **Login sonrası snapshot timeout (30sn):** LOG IN tıklandıktan sonra browser_snapshot 30sn timeout verebilir — bu login'in başarısız olduğu anlamına gelmez. Redirect sırasında sayfa yüklenirken timeout olur. **Çözüm:** Snapshot beklemeden doğrudan bir topluluk URL'sine `browser_navigate` yap — profilde "Vanilla Gotus" görünüyorsa login başarılıdır.
- **Puppeteer MCP detached frame:** `puppeteer_navigate` "detached Frame" hatası veriyorsa önceki oturumdan kalan stale Chromium frame'i var demektir. Aynı seansta tekrar denemek genelde işe yaramaz — Browserbase ile devam et.
- **🔴 delegate_task + Puppeteer MCP = SESSİZ TIMEOUT (5 Haz 2026):** `delegate_task` subagent'ları Puppeteer MCP araçlarına (`puppeteer_navigate`, `puppeteer_fill`, `puppeteer_screenshot` vb.) ERİŞEMEZ. Subagent'lar sadece standart araç setine sahiptir — MCP araçları parent session'a özeldir. Skool kontrolünü paralelleştirmek için `delegate_task` kullanılırsa her subagent 600sn boyunca sessizce timeout verir (bu seansta 3 paralel subagent × 600sn = ~30 dakika kayıp). **Çözüm:** Skool kontrolünde tüm toplulukları parent session'dan sırayla kontrol et (`puppeteer_navigate` → `puppeteer_screenshot` → `vision_analyze` döngüsü). 6 topluluk ~3-5 dakika sürer — paralelleştirmeye değmez.
- **Yedek: Puppeteer MCP** — Browserbase timeout verdiğinde Puppeteer MCP ile devam et. `puppeteer_evaluate` React sayfalarda `undefined` döner, screenshot + vision kullan. `:has-text()` ve `:contains()` seçicileri çalışmaz, `button[type="submit"]` kullan.
- **⚠️ Puppeteer MCP login sınırlı (9 Haz 2026):** Local Chromium + Cloudflare kombinasyonu Skool'da login'i başarısız kılabilir. `puppeteer_fill` + `puppeteer_click` ile form doldurulsa bile sonraki sayfada "LOG IN" butonu hala görünür. **Önce Browserbase ile dene**, Puppeteer MCP'yi sadece içerik okuma (screenshot + vision) için kullan, login için değil.
- **Public ≠ Üye:** Zero2Launch public olduğu için içerik login olmadan da görünüyor, bu üye olunduğu anlamına gelmez — About sayfasındaki JOIN butonu ile teyit et
- **JOIN GROUP formu:** Bazı topluluklar (örn. Yapay Zeka Sistemleri) katılım için soru formu gösteriyor. Seçenek seç + answer yaz + email doldur = JOIN GROUP aktif olur
- **Katılım durumu kopukluğu:** Skool arayüzü bazen yanıltıcı olabilir — "form dolduruldu" diye not düşülen grup sonraki kontrolde JOIN GROUP gösterebilir. Her taramada güncel durumu kontrol et.
- **BANNED durumu:** "JOIN GROUP" yapılan bir topluluk sonraki kontrolde BANNED gösterebilir — disabled "BANNED" butonu ile. Ban sebebi görünmez, tekrar başvuru mümkün değildir (2 Haz 2026: AI with Apex).
- **Browserbase Classroom timeout:** AI Money Lab gibi topluluklarda Classroom sekmesi (/classroom) Browserbase'de 30-60sn timeout verebilir. Cozum: browser_console ile DOM icerigini cek, veya Puppeteer MCP fallback kullan.
- **Community switcher (client-side routing):** Skool'da bazı topluluklar (AI Money Lab gibi) dogrudan URL ile erisilebilir (ai-seo-with-julian-goldie-1553). Ancak switcher her zaman daha guvenilirdir. Alternatif: document.querySelector('[class*="SwitcherHome"]').click() ile ac.
