---
name: browser-debugging
description: "Tarayıcı otomasyonunda hata ayıklama — API endpoint keşfi, fetch interceptor, session teşhisi, rate-limit handling, form validation hatalarını yakalama."
version: 1.1.0
metadata:
  hermes:
    tags: [browser, debugging, api, interception, automation]
    category: software-development
---

# Browser Debugging

Hermes browser tool'u ile web otomasyonu yaparken karşılaşılan sorunları teşhis etme ve çözme teknikleri.

## Ne Zaman Kullanılır

- Form submit başarısız oluyor ama hata mesajı görünmüyorsa
- API endpoint'i bilinmiyorsa
- Sayfa `about:blank`'e düşüyorsa
- Rate-limit (429) alınıyorsa
- Backend validation hatalarını görmek gerekiyorsa

## Temel Teknikler

### 1. API Interception (Fetch Interceptor)

Sayfanın yaptığı API çağrılarını yakalamak için `browser_console` ile fetch override:

```javascript
window.__debug = [];
const origFetch = window.fetch;
window.fetch = function(url, opts) {
  const req = {url: typeof url === 'string' ? url : url.url, method: opts?.method || 'GET', body: opts?.body};
  return origFetch.apply(this, arguments).then(async r => {
    const clone = r.clone();
    const text = await clone.text();
    window.__debug.push({...req, status: r.status, response: text.slice(0, 500)});
    return r;
  });
};
```

Sonra `JSON.stringify(window.__debug)` ile debug verisini oku.

**Pitfall:** Sayfa re-render olursa interceptor kaybolur. Form submit'ten hemen ÖNCE kur, hemen SONRA oku.

### 2. Endpoint Keşfi (Performance API)

Sayfanın yaptığı tüm network isteklerini görmek için:

```javascript
performance.getEntriesByType('resource')
  .filter(r => r.name.includes('api') || r.initiatorType === 'fetch')
  .map(r => r.name)
```

Bu yöntem interceptor gerektirmez, sayfa yüklendikten sonra bile geçmiş istekleri gösterir.

### 3. Session Teşhisi

Sayfa durumunu hızlıca kontrol etmek için:

```javascript
// Sayfa gerçekten yüklü mü?
window.location.href  // about:blank ise session çökmüş

// Form var mı?
document.querySelectorAll('input').length

// Hata mesajı var mı?
document.body.innerText.slice(0, 500)
```

### 4. "Sayfa Neden Boşalıyor?" Teşhisi

`about:blank` genelde inactivity timeout'tan kaynaklanır. Hermes browser'ın varsayılan inactivity süresi kısa olabilir — uzatmak gerekebilir. Ayrıca cloud provider (Browserbase) timeout'ları da local Chromium'a fallback yapmadan önce session'ı sıfırlayabilir.

**Browserbase timeout → Playwright fallback:** Browserbase uzun session'larda veya çok sayıda sayfa değişiminde kopabilir (30-60sn timeout). Çözüm: Playwright ile sunucuda local Chromium kullan. Hermes venv'inde zaten kurulu:

```bash
python3 -m playwright install chromium  # ilk kurulum (bir kere)
```

```python
from playwright.async_api import async_playwright
# headless=True → arka planda, headless=False → debug için
async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto("https://...")
    # ... işlemler
    await browser.close()
```

**Playwright vs Browserbase karşılaştırması:**

| Durum | Browserbase | Playwright |
|-------|-------------|------------|
| CloudFront/WAF | ✅ Geçer (stealth) | ✅ Geçer (gerçek Chrome) |
| Uzun session | ❌ Timeout | ✅ Stabil |
| IP rate-limit | IP değişebilir | Sabit sunucu IP'si |
| Kurulum | Yok (built-in) | `playwright install chromium` |
| Form doldurma | `browser_type` + `browser_click` | `page.fill()` + `page.click()` |

**⚠️ ARM64 (Oracle Cloud):** Bu sunucu ARM64 olduğu için `playwright install chromium` standart `chrome` binary'si yerine `headless_shell` kurar. Binary yolu:
```
~/.cache/ms-playwright/chromium_headless_shell-1223/chrome-linux/headless_shell
```
Playwright launch ederken `executable_path` parametresiyle belirt:
```python
browser = await p.chromium.launch(
    executable_path='~/.cache/ms-playwright/chromium_headless_shell-1223/chrome-linux/headless_shell',
    headless=True
)
```
Selenium ve SeleniumBase ARM64'te çalışmaz — sadece Playwright kullan.

**Ne zaman Playwright:** Browserbase 2+ kez timeout verdiğinde veya uzun çok adımlı form akışlarında. `execute_code` içinde çalışır, async/await ile.

### 5. Rate-Limit Handling (429)

Rate-limit alınınca:
1. `browser_navigate` ile farklı bir siteye git (örn. `cloudflare.com`)
2. `browser_navigate` ile `ifconfig.me`'ye git — IP değişti mi kontrol et
3. Yeni IP ile tekrar dene

Browserbase cloud provider kullanılıyorsa her site değişiminde yeni IP alınabilir.

### 6. Validation Hatalarını Yakalama

"Signup failed" gibi genel hataların gerçek sebebini görmek için mutlaka interceptor kur.
Örnek: `{"fields":[{"name":"last_name","error":"Can't use \"skool\"","user":true}]}` — 422 validation hatası, bot tespiti değil.

### Pitfall: Gereksiz Alternatif Arama

Browserbase bir sitede çalışıyorsa, "daha iyisi var mı" diye Xvfb, headed Chrome,
farklı tarayıcı gibi alternatiflere vakit harcama. Özellikle Incapsula gibi agresif
WAF'larda Browserbase tek çözüm olabilir. **Çalışan çözümü karmaşıklaştırma.**

İstisna: Kullanıcı "daha ucuz/sürdürülebilir alternatif" isterse araştır.

Aynı siteye tekrar kayıt denenirken önce cookie'leri temizle. Tarayıcı state'i temizlenince yeni bir kullanıcı gibi görünürsün:

```javascript
// Browser console'dan (localStorage erişimi varsa)
localStorage.clear();
sessionStorage.clear();
document.cookie.split(";").forEach(c => {
  document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date(0).toUTCString() + ";path=/");
});
```

Eğer localStorage erişimi yoksa (SecurityError), yeni domain'e navigate edip geri dönmek de session cookie'lerini temizleyebilir.

## Pitfalls

| Hata | Sebep | Çözüm |
|------|-------|-------|
| React form doldurulamıyor | JS ile `el.value = x` React state'i güncellemez | `browser_type` kullan (native input event gönderir) |
| React select/combobox JS manipülasyonu | `el.value = 'optionValue'` state'i güncellemez, buton tıklaması formu sessizce resetler | `browser_click` ile dropdown'u aç, option'a `browser_click` ile tıkla |
| `browser_console` boş dönüyor | Sayfa re-render oldu, değişkenler silindi | Her sayfa değişiminde interceptor'u yeniden kur |
| Aynı browser session'da IP değişmiyor | Browserbase session reuse | Farklı domain'e navigate et, session yenilenebilir |
| `engine: local` çalışmıyor | Gateway restart gerekir | Gateway'i restart et |
| Fetch interceptor `Failed to fetch` | CORS | Normal — interceptor clone'lama için, response'u etkilemez |
| Gmail `+` alias ile form takılıyor | Backend `+` karakterini reddediyor olabilir | Düz email kullan, alias kullanma |
| Disposable email (temp-mail) reddediliyor | Backend domain kara listesi var | Gerçek Gmail/Outlook kullan |
| "Signup failed" sessiz hatası | Validation detayı UI'da gösterilmiyor | Mutlaka fetch interceptor kur, API response'unu oku |
| Browserbase 2+ kez timeout | Uzun session, çok sayfa değişimi | Playwright fallback'e geç VEYA **Puppeteer MCP** ile devam et (sunucuda local Chromium, bkz. `references/puppeteer-mcp.md`). Puppeteer MCP, Browserbase'den daha hızlı sayfa geçişi yapar ama seçici kısıtları var |
| **İki AYRI browser session — kritik** | `mcp_puppeteer_puppeteer_*` ve Hermes `browser_*` tool set'leri iki farklı, bağımsız browser instance'ıdır. Birinde login yapıp cookie almak diğerine yansımaz. | Bir tool set'inde login olduysan, aynı set'te kalmaya devam et. Geçiş yaparsan yeniden login gerekir. Hermes `browser_*` = Browserbase cloud veya local Chromium (engine ayarına göre). Puppeteer MCP = sunucuda ayrı bir Chromium process'i. |
| Playwright `pip install` PEP 668 hatası | Sistem python'ına kurmaya çalışıyor | `python3 -m pip install playwright` (venv aktifken). Playwright zaten hermes venv'inde kurulu olabilir |
| `curl_cffi` SOCKS dependency hatası | Sistemde SOCKS kütüphanesi eksik | Playwright kullan — daha güvenilir, gerçek Chrome fingerprint'i |
| Playwright response listener çalışmıyor | `lambda r: log_resp(r)` direkt çağrıldı | `lambda r: asyncio.ensure_future(log_resp(r))` — async callback'ler ensure_future ister |
| Playwright çift submit (422 + 200) | `button[type='submit']` tüm formları tetikledi | Form izolasyonu: `form:has(h2:has-text('...'))` ile spesifik formu seç |
| Puppeteer MCP `:has-text()` / `:contains()` hata veriyor | MCP implementasyonu bu seçicileri desteklemez | `button[type=\"submit\"]` veya `input[type=\"...\"]` kullan. Linkler için direkt `puppeteer_navigate` ile URL'ye git. Detay: `references/puppeteer-mcp.md` |
| Puppeteer MCP `evaluate` hep `undefined` | React hydration timing | Screenshot + vision analizi kullan, JS'e güvenme |
| Puppeteer MCP "detached Frame" hatası | Sayfalar arası çok hızlı geçiş, önceki sayfanın frame'i kapanmadan yeni navigate | Navigate'ler arası kısa bekle (sayfanın tam yüklenmesini bekle). Aynı domain'de kalarak navigate et. Hata alınınca tekrar aynı URL'ye navigate et |
| **Camoufox çoklu URL crash** | Aynı session'da 2+ `page.goto()` → `TypeError: Cannot read properties of undefined (reading 'url')` | Her URL için ayrı `AsyncCamoufox` session'ı aç. Tek session → tek URL |

## 8. Playwright Network Loglama (Request + Response)

Playwright ile çalışırken API isteklerini ve cevaplarını yakalamak, fetch interceptor'dan daha güvenilirdir (sayfa re-render'ından etkilenmez):

```python
api_calls = []

def log_request(request):
    try:
        if "api" in request.url:
            data = ""
            try:
                data = str(request.post_data_json) if request.method == "POST" else ""
            except Exception:
                data = "[non-JSON]"
            api_calls.append(f"REQ: {request.method} {request.url} -> {data[:200]}")
    except Exception:
        pass  # asla event listener'ı kırma

def log_response(response):
    try:
        if "api" in response.url:
            body = ""
            try:
                body = (await response.text())[:500]
            except Exception:
                body = "[body read error]"
            api_calls.append(f"RESP: {response.status} {response.url} -> {body[:300]}")
    except Exception:
        pass

page.on("request", log_request)
page.on("response", log_response)
```

**Pitfall:** `request.post_data_json` Sentry gibi JSON olmayan POST isteklerinde `Error: POST data is not a valid JSON object` fırlatır. Mutlaka try/except ile sar. Event listener içinde fırlayan istisna **tüm scripti durdurur**.

**Neden fetch interceptor yerine Playwright event?**
- Sayfa re-render'ında kaybolmaz
- CORS kısıtlaması yok
- Response body'yi de okuyabilir
- `browser_console` timeout'undan etkilenmez

"Sigup failed" gibi sessiz hatalarda API response'unu okumadan asla tekrar deneme — önce hatanın sebebini gör.

## 11. Incapsula/Imperva WAF Bypass (APA Deneyimi)

Incapsula, headless browser'ları tespit etmekte Cloudflare'dan daha agresiftir.

### Incapsula Tespit Sinyalleri

| Sinyal | Önem | Açıklama |
|--------|------|----------|
| `navigator.webdriver` | 🔴 Kritik | `playwright-stealth` ile gizlenebilir |
| `navigator.plugins.length` | 🔴 Kritik | **0 plugin = headless**. Stealth bunu gizleyemez! |
| Canvas fingerprint | 🟡 Orta | Headless Chrome vs gerçek Chrome farkı |
| WebGL vendor/renderer | 🟡 Orta | "Google Inc." vs boş string |
| `reese84` cookie | 🔴 Kritik | **Browser fingerprint'e bağlı** — curl'da çalışmaz |
| TLS fingerprint (JA3) | 🟡 Orta | Python vs Chrome TLS farkı |

### Çalışan Yöntemler

| Yöntem | Durum | Not |
|--------|-------|-----|
| **Browserbase (Hermes browser)** | ✅ | Stealth mode + residential proxy Incapsula'yı geçer |
| **Puppeteer MCP + stealth** | ✅ | Local Chromium + stealth plugin, WARP SOCKS5 ile |
| **RSS/XML endpoint'leri** | ✅ | Çoğu WAF statik content'e uygulanmaz |
| Playwright + stealth + WARP | ❌ | `plugins=0` yakalanır (**CloudFront'da çalışır!**) |
| Cookie export → curl | ❌ | `reese84` fingerprint validasyonu |
| `curl_cffi` | ❌ | TLS fingerprint farklı, sunucuda SOCKS dependecy sorunu |

### Incapsula Cookie Yapısı

```
visid_incap_<id>  → Ziyaretçi ID'si
incap_ses_<id>    → Oturum cookie'si 
reese84           → Anti-bot fingerprint (KRİTİK — export edilemez)
nlbi_<id>         → Load balancer cookie'si
```

`reese84` cookie'si tarayıcının canvas, WebGL, font, plugin gibi yüzlerce özelliğinin hash'idir. Sunucu her istekte bu hash'i doğrular — farklı bir client'tan (curl) gönderirsen geçersiz sayar.

### Incapsula vs Diğer WAF'lar

| Özellik | Incapsula | AWS CloudFront | Cloudflare |
|---------|-----------|---------------|------------|
| JS Challenge | `/_Incapsula_Resource` | `edge.sdk.awswaf.com` 403 | `/cdn-cgi/challenge/` |
| Headless tespit | 🔴 Agresif (**plugins=0**) | 🟢 Temel (JS odaklı) | 🟡 Orta (JS challenge) |
| Playwright local | ❌ Çalışmaz | ✅ Çalışır (Skool) | ✅ Genelde çalışır |
| Cookie export | ❌ (`reese84`) | ⚠️ Bazen | ⚠️ (`cf_clearance`) |
| Browserbase | ✅ | ✅ | ✅ |
| RSS bypass | ✅ Genelde | ✅ | ⚠️ Sitene bağlı |

## 12. Camoufox — Incapsula/Imperva için Anti-Detection Browser

Incapsula sitelerde Playwright Chromium yetersiz kaldığında (body "Request unsuccessful. Incapsula incident ID"), **Camoufox** kullan. Firefox tabanlı anti-detection browser'dır, Incapsula JS challenge'larını bypass eder.

### Kurulum

```python
# execute_code içinde:
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "camoufox"], capture_output=True)
```

### Temel Kullanım

```python
from camoufox.async_api import AsyncCamoufox

async with AsyncCamoufox(headless=True) as browser:
    page = await browser.new_page()
    await page.goto("https://protected-site.com/login", timeout=30000)
    await page.wait_for_timeout(3000)
    # Form doldurma, buton tıklama...
```

### Playwright vs Camoufox

| Playwright | Camoufox |
|-----------|----------|
| Chromium-based | Firefox-based |
| `playwright.async_api` | `camoufox.async_api` |
| Incapsula'da yakalanır | Incapsula JS challenge'ını **geçer** |
| `browser.new_context()` | `browser` direkt context |

### Pitfalls

1. **Sunucuda sadece headless çalışır** — `headless=False` DISPLAY ister. `headless=True` kullan.
2. **Form submit hala engellenebilir** — Incapsula sayfa yüklenmesine izin verir ama form submit'i bloklayabilir. Belirti: form.submit() POST tetiklemez, buton tıklamaları POST tetiklemez, sayfa sessizce login formuna geri döner. Debug: CSRF token'larını, buton ID'lerini, JS validasyonu kontrol et.
3. **Hybrid yaklaşım:** Form submit bloklanırsa Camoufox'tan cookie + CSRF al, `curl_cffi` ile POST yap.
4. **Kilitlenme riski:** 3 başarısız denemeden sonra dur. 5 deneme → account lockout.
5. **Datacenter IP block:** Incapsula datacenter IP'leri (WARP dahil) tamamen bloklayabilir. Belirti: body'de "Incapsula incident ID", input count=0, WARP proxy ile bile. Çözüm: gerçek residential browser'dan cookie export.
6. **Çoklu URL crash (4 Haz 2026):** Aynı Camoufox session'ında 2+ URL'ye `page.goto()` yapmak, ikinci sayfada `TypeError: Cannot read properties of undefined (reading 'url')` ile browser'ı çökertir. `page.on("pageerror")` handler'ı bunu yakalayamaz — bu bir sayfa hatası değil, browser-level Firefox crash'idir. **Çözüm:** Her URL için ayrı `async with AsyncCamoufox(headless=True) as browser:` session'ı aç. Tek session → tek URL.

Detaylar: `references/incapsula-camoufox.md` |

### API Endpoint'ler
- `POST /auth/request-signup` — body: `{first_name, last_name, email, password}` → response: verification ID (UUID)
- `POST /auth/verify-signup` — body: `{code: "XXXX"}` → 200 başarılı, 400 "invalid code", 422 validation
- `POST /auth/login-with-code-init?email=...` — login sayfasındaki alternatif doğrulama

### Validation Kuralları
- `+` karakterli Gmail alias'ları (`user+tag@gmail.com`) validation'da takılabiliyor
- Disposable email domain'leri (mail.tm, wshu.net vb.) reddediliyor
- **İsim validation:** Skool uydurma isimleri reddediyor. Reddedilenler: "Valeri", "Valementa", "Vividemento". Kabul edilen: "Valerie", "Vanilla". Yaygın gerçek isimler kullan.
- Aynı email ile tekrar signup → "Signup failed" (email zaten pending durumda, verification ID değişir)
- Aynı email çok deneme → 429 "too many requests" (rate-limit)

### Kod Doğrulama
- Doğrulama kodu input'u: `input[data-testid='input-component']`
- Kod süresi ~60 saniye, süresi dolunca "Resend it" linkine tıkla
- **Kritik:** Her yeni signup isteği YENİ verification ID üretir. Önceki signup'ın kodu çalışmaz. Kod email'e geldikten sonra yeni signup yapma — aynı session'da kodu gir.
- Login sayfasında "Log in with a code" seçeneği alternatif doğrulama akışı olabilir

## 11. Incapsula/Imperva WAF Bypass

Incapsula (Imperva) WAF, üç katmanlı koruma kullanır: JS challenge, cookie doğrulaması, ve browser fingerprint eşleştirmesi.

### Tespit Sinyalleri

Incapsula sayfası belirtileri:
- 925 byte HTML, içinde `/_Incapsula_Resource?SWJIYLWA=` script'i
- Cookie'ler: `visid_incap_*`, `incap_ses_*`, `reese84`
- `reese84` — kritik cookie, browser fingerprint ile eşleştirilir
- HTTP 403 veya 200 (ama içerik boş/Incapsula sayfası)

### Ne Çalışır ✅

1. **Browserbase (Hermes browser)** — stealth mode + residential proxy Incapsula'yı geçer
2. **Browser console extract** — `document.querySelector('main').innerText` ile içerik alınır
3. **RSS/API endpoint'leri** — genelde WAF dışıdır, önce bunları dene

### Ne Çalışmaz ❌

- **Cookie export → curl** — `reese84` browser fingerprint ile eşleşmediği için reddedilir
- **Playwright local + stealth** — `navigator.plugins=0` yakalanır
- **Playwright + WARP proxy + stealth** — IP değişir ama fingerprint aynı kalır

### Pitfall: Cookie Export Aldatmacası

Incapsula cookie'lerini Browserbase'den alıp curl/Python requests'te kullanmak **çalışmaz**. `reese84` cookie'si TLS fingerprint (JA3), canvas, WebGL gibi sinyallerle eşleştirilir. Farklı HTTP client → farklı fingerprint → red.

### Strateji

1. Keşif için **RSS/API endpoint'lerini** dene (WAF uygulanmamış olabilir)
2. Tam içerik için **Hermes browser** kullan (Browserbase stealth modu)
3. Cookie export'a güvenme — çalışmaz

Bir sayfada birden fazla `<form>` varsa (örn. signup formu + verification formu aynı DOM'da), `button[type='submit']` seçicisi tüm formları tetikleyebilir.

**Belirti:** İki API isteği görünür — biri başarılı (200), diğeri validation hatası (422). Sayfa beklenmedik şekilde refresh olur.

**Çözüm:** Hedef formu spesifik olarak seç:

```python
# Yanlış — tüm formları tetikler
submit_btn = await page.query_selector("button[type='submit']")
await submit_btn.click()

# Doğru — sadece verification form'unu hedefler
verify_form = await page.query_selector("form:has(h2:has-text('We sent you a code'))")
code_input = await verify_form.query_selector("input")
await code_input.fill(code)
verify_btn = await verify_form.query_selector("button[type='submit']")
await verify_btn.evaluate("el => el.click()")  # dispatchEvent, bubbling yok
```

**Alternatif:** `form.evaluate("el => el.submit()")` ancak bu sayfa refresh'ine yol açabilir (React SPA'larda). Butona tıklamak daha güvenli.

**Pitfall:** `force=True` ile tıklamak modal overlay'leri aşar ama çift tıklamaya yol açabilir. İlk tercih: spesifik form seçimi.

## 13. Browser Use CDP Remote Browser (Ücretsiz Residential IP)

Browser Use, ücretsiz remote browser sunar — CDP (Chrome DevPortocol) üzerinden bağlanılır. Cloud session'lar PARALI ama CDP linki ÜCRETSİZ.

### Kurulum

```bash
pip install browser-use-sdk playwright
```

### CDP Bağlantısı

1. Browser Use dashboard'dan CDP URL'si al: `wss://<session-id>.cdp.browser-use.com`
2. Playwright ile bağlan:

```python
import asyncio
from playwright.async_api import async_playwright

CDP_URL = "wss://<session-id>.cdp.browser-use.com"

async def connect():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()
        
        await page.goto("https://example.com")
        print(await page.title())
        
        await browser.close()

asyncio.run(connect())
```

### Diğer Browser Araçlarıyla Karşılaştırma

| Özellik | Browser Use CDP | Browserbase | Puppeteer MCP | Playwright Local |
|---------|----------------|-------------|---------------|-----------------|
| Maliyet | **Ücretsiz** | Ücretsiz (limited) | Ücretsiz | Ücretsiz |
| IP | Residential | Residential | Sunucu IP | Sunucu IP |
| Anti-bot | ✅ Stealth | ✅ Stealth | ⚠️ Plugin gerekli | ❌ Yakalanır |
| CDP | ✅ Standart | ❌ API | ✅ Standart | ✅ Lokal |
| Uzun session | ✅ | ❌ Timeout | ✅ | ✅ |

### Pitfalls

| Hata | Sebep | Çözüm |
|------|-------|-------|
| CDP URL değişmiş | Yeni oturum açılmış | Dashboard'dan güncel URL'yi al |
| `browser-use-sdk` cloud session para harcar | API ücretli | CDP linki kullan, `sessions.create()` KULLANMA |
| Sayfa boş screenshot | Sayfa henüz yüklenmedi | `wait_until="networkidle"` + `asyncio.sleep(3)` |
| Connection refused | CDP URL süresi dolmuş | Yeni CDP URL'si al |

### Kullanım Alanları

- **Skool login** — Cloudflare korumalı, residential IP gerekli
- **APA/Incapsula** — Anti-bot korumalı siteler
- **Genel web otomasyonu** — Yüksek kaliteli residential IP gerektiğinde

## 14. CDP Target Routing — browser_console Yanlış Sekmeyi Hedeflediğinde

`browser_navigate` çağrısından sonra `browser_console`'un beklendiği gibi çalışmadığı, farklı bir sekmeye (ör. "New Tab") yöneldiği durumlar. Bu, özellikle Browserbase cloud'da görülür — birden fazla tab açıldığında `browser_console` her zaman en son aktif sekmeyi hedeflemez.

### Belirti
- `browser_navigate(url)` doğru sayfayı gösteriyor (snapshot'ta doğru içerik)
- `browser_console` boş dönüyor veya beklenmeyen çıktı veriyor
- `browser_console(expression="document.location.href")` başka bir URL döndürüyor (örn. `about:blank`)
- İkinci `browser_console` çağrısı aynı sonucu veriyor

### Çözüm — CDP ile Doğrudan Tab Hedefleme

```python
# 1. Tüm açık sekmeleri listele
browser_cdp(method="Target.getTargets", params={})

# 2. Çıktıda her target'ın targetId, title, url alanlarını kontrol et.
#    Hedef sayfanın URL'ini (veya title'ını) içeren target'ı bul.
#    Örnek çıktı:
#    {"targetInfos": [
#       {"targetId": "A", "type": "page", "title": "New Tab", "url": "about:blank"},
#       {"targetId": "B", "type": "page", "title": "AI Automation Society", "url": "https://www.skool.com/ai-automation-society"}
#    ]}
#    Doğru target = "B" (URL/title eşleşen)

# 3. Doğru target_id ile Runtime.evaluate kullan
browser_cdp(method="Runtime.evaluate", params={
    "expression": "document.body.innerText.substring(0, 5000)",
    "returnByValue": true
}, target_id="TARGET_ID")

# 4. Post URL'lerini çıkarmak için:
browser_cdp(method="Runtime.evaluate", params={
    "expression": """Array.from(document.querySelectorAll('a'))
    .map(a => ({title: a.textContent?.trim()?.slice(0,100), href: a.href}))
    .filter(h => h.href && h.href.includes('/ai-automation-society/') 
      && !h.href.includes('?c=') && !h.href.includes('/classroom'))
    .slice(0,30)""",
    "returnByValue": true
}, target_id="TARGET_ID")
```

### Ne Zaman Kullanılır

| İşaret | Olasılık |
|--------|----------|
| `browser_navigate` snapshot doğru, `browser_console` farklı URL döndürüyor | 🔴 Yüksek — bu yöntemi dene |
| `browser_console` ilk çağrı çalışıyor, ikincide boş dönüyor | 🟡 Orta — önce `browser_snapshot` ile state tazele |
| `browser_console` "Request failed" hatası veriyor | 🟢 Düşük — farklı sorun (Cloudflare) |

### Alternatif: browser_vision

CDP çalışmazsa `browser_vision` dene — Browserbase screenshot alır, sayfanın görsel durumunu gösterir:

```python
browser_vision(question="Sayfada hangi postlar görünüyor?")
```

### Pitfall: target_id Süreklilik Sağlamaz

Aynı target_id'yi kullanarak yapılan birden fazla `browser_cdp` Runtime.evaluate çağrısı **bağımsız isteklerdir** — aralarındaki JS state'i (tanımlanan değişkenler) bir sonraki çağrıda kaybolabilir. Her evaluate'de ihtiyacın olan tüm mantığı tek expression'a sığdır.

**Doğru:** Tek expression'da tüm işi bitir:
```python
browser_cdp(method="Runtime.evaluate", params={
    "expression": "Array.from(document.querySelectorAll('a'))...",
    "returnByValue": true
}, target_id="B")
```

**Yanlış:** Değişkene atayıp sonraki çağrıda kullan:
```python
# İLK çağrı
browser_cdp(..., params={"expression": "window.myData = [...]"}, target_id="B")
# İKİNCİ çağrı — window.myData undefined olabilir!
browser_cdp(..., params={"expression": "JSON.stringify(window.myData)"}, target_id="B")
```

### Örnek Vaka (23 Temmuz 2026)

AI Automation Society feed'inde post linkleri çekilirken `browser_console` ikinci çağrıda "New Tab" sekmesine yöneldi, URL `about:blank` döndü. `browser_navigate` snapshot doğru sayfayı gösteriyordu ama console başka bir sekmedeydi. `Target.getTargets` ile iki target tespit edildi (New Tab + ai-automation-society). Doğru target_id ile `Runtime.evaluate` kullanıldı.

## Reference

- `references/skool-signup.md` — Skool kayıt akışı: API endpoint, validation kuralları, hata mesajları
- `references/waf-login-strategies.md` — WAF login stratejileri
- `references/incapsula-camoufox.md` — Camoufox anti-detection browser ile Incapsula bypass
- `references/puppeteer-mcp.md` — Puppeteer MCP: anti-bot bypass, stealth plugin, ARM64 kurulum
- `references/browser-use-cdp.md` — Browser Use CDP remote browser: ücretsiz residential IP, bağlantı, pitfall'lar
