# APA Incapsula Araştırma Notları (29 Mayıs 2026)

## Incapsula WAF Davranışı

APA.org, Imperva/Incapsula WAF kullanıyor. Koruma katmanları:

1. **JS Challenge** — `/_Incapsula_Resource?SWJIYLWA=...` script'i, çözülmezse sayfa boş döner
2. **Cookie doğrulaması** — `visid_incap_*`, `incap_ses_*`, `reese84` cookie'leri
3. **Browser fingerprint** — `reese84` cookie'si TLS fingerprint, canvas, WebGL gibi sinyallerle eşleştirilir

## Tespit Edilen Incapsula Sinyalleri

- `navigator.webdriver === true` → headless tespiti
- `navigator.plugins.length === 0` → headless Chrome göstergesi
- TLS fingerprint (JA3) → Python requests vs gerçek Chrome farkı
- IP reputation → Oracle Cloud IP'leri düşük reputation

## Denediğimiz Yöntemler ve Sonuçları

### Çalışanlar ✅

1. **Browserbase (Hermes browser tool)** — En güvenilir. Stealth mode + residential proxy.
   - `browser_navigate` → sayfayı açar
   - `browser_console` → `document.querySelector('main').innerText` ile tam metin
   - Cookie'ler: `incap_ses_*`, `reese84`, `AWSALB` otomatik yönetilir

### ÇALIŞMAYANLAR ❌

2. **RSS feed (curl)** — 29 Mayıs 2026 itibarıyla Incapsula uygulanmaya başladı. 925 byte `_Incapsula_Resource` sayfası dönüyor.

3. **Playwright local (stealth + WARP)** — `navigator.webdriver=false` yapıldı ama `plugins=0` yakalandı.
4. **Cookie export → curl/Python requests** — `reese84` fingerprint doğrulaması nedeniyle çalışmaz.
5. **Playwright local (headless, WARP, stealth)** — Sayfa yükleniyor ama içerik boş.
6. **curl direkt** — 925 byte `_Incapsula_Resource` sayfası
7. **curl + WARP proxy** — aynı şekilde 925 byte Incapsula
8. **Python requests + tüm header taklitleri** — Incapsula geçilmiyor

## Çıkarılan Dersler

- **Incapsula, cookie tabanlı bypass'a izin vermez** — cookie'leri kopyalasan da browser fingerprint eşleşmezse reddeder
- **Browserbase'in stealth modu**, residential proxy + gerçek Chrome fingerprint'i ile Incapsula'yı aşabiliyor
- **RSS endpoint'leri genelde WAF dışıdır** — APA örneğinde olduğu gibi, keşif için RSS kullan, tam metin için browser
- **Playwright stealth tek başına yeterli değil** — `navigator.plugins` spoofing'i eksik

## Login Akışı (Browserbase ile)

1. `browser_navigate("https://sso.apa.org/apasso/idm/apalogin?ERIGHTS_TARGET=https://www.apa.org")`
2. `browser_type` ile email (`#loginName`) ve şifre (`#loginPassword`) gir
3. `browser_click` ile LOG IN butonu
4. Login sonrası cookie'leri `browser_console("document.cookie")` ile al
5. Cookie'leri `~/.hermes/secrets/apa_cookies.json`'a kaydet
6. **Pitfall**: Bu cookie'ler sadece Browserbase session'ında geçerli, curl'da çalışmaz
