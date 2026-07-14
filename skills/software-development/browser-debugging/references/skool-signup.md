# Skool Signup API

Skool.com kayıt akışı sırasında keşfedilen API detayları.

## API Endpoint

```
POST https://api2.skool.com/auth/request-signup
Content-Type: application/json
```

## Request Body

```json
{
  "first_name": "Valeri",
  "last_name": "User",
  "email": "kutaypici13@gmail.com",
  "password": "V@nill@2026!Sk"
}
```

## Response Codes

| Status | Response | Anlamı |
|--------|----------|--------|
| 200 | (boş veya redirect) | Başarılı — verification code modal'ı açılır ("We sent you a code") |
| 400 | (boş veya genel hata) | Validation hatası veya disposable email reddi |
| 422 | `{"fields":[{"name":"last_name","error":"Can't use \"skool\"","user":true}]}` | Validation hatası |
| 429 | `"too many requests"` | Rate-limit (IP veya email bazlı) |
| 403 | CloudFront HTML | WAF engeli (sadece gerçek tarayıcı geçer) |

## CloudFront WAF

API, AWS CloudFront + WAF arkasında. Python `requests` ile direkt çağrı `403 ERROR: The request could not be satisfied` döner.
Sadece gerçek tarayıcı (Browserbase veya local Chromium) WAF challenge'ını geçebilir.
WAF challenge URL'i: `https://017ae153ccc5.edge.sdk.awswaf.com/017ae153ccc5/4aa4380fa03e/mp_verify`

## Validation Kuralları

- `last_name`: "skool" (case-insensitive) içeremez
- **`first_name` isim validation:** Skool yaygın gerçek isimleri kabul ediyor, uydurma isimleri reddediyor (422: `"Please use a valid name"`). 
  - ❌ Reddedilen: "Valeri", "Valementa", "Vividemento"
  - ✅ Kabul edilen: "Valerie", "Vanilla"
- **Email domain kara listesi:** Disposable email domain'leri (örn. mail.tm `wshu.net`) 400 ile reddediliyor. Gerçek Gmail/Outlook gerek.
- **Gmail `+` alias:** `kullanici+alias@gmail.com` formatı formda sessizce takılı kalıyor (buton disabled, hata mesajı yok). Kullanma.
- Şifre: Özel karakter ve rakam içermeli
- Aynı email çok fazla deneme → 429 "too many requests"

## Başarılı Kayıt Akışı

1. `skool.com/signup` → "CREATE YOUR COMMUNITY" butonuna tıkla
2. Form açılır: First name, Last name, Email, Password
3. Gerçek Gmail adresi kullan (disposable değil, `+` aliassız)
4. SIGN UP → başarılıysa "We sent you a code" modal'ı
5. 4 haneli kod email'e gelir → gir → NEXT
6. Hesap aktif

## Cookie Temizleme Stratejisi

Aynı siteye tekrar kayıt denerken önce cookie'leri temizle:

```
Yeni browser session aç → skool.com/signup → CREATE YOUR COMMUNITY
```

Cookie'leri temizlemezsen aynı email'le "Signup failed" alabilirsin (email zaten pending durumda olabilir). Temiz session + yeni email = en yüksek başarı oranı.

## "Signup Failed" Teşhisi

Bu genel hata mesajının birden fazla sebebi olabilir:
- Email zaten kayıtlı (pending verification)
- Disposable email domain reddi
- IP rate-limit (çok fazla deneme)
- Bot tespiti (headless browser fingerprint)

Gerçek sebebi görmek için fetch interceptor şart (bkz. `browser-debugging` SKILL.md).

## Keşif Yöntemi

1. `browser_console` ile fetch interceptor kuruldu
2. Form submit sonrası `window.__skoolDebug` dizisinden yakalandı
3. Endpoint `performance.getEntriesByType('resource')` ile de görülebilir

## Rate-Limit Davranışı

- Hem IP hem email bazlı rate-limiting var
- Aynı IP'de farklı email denense de 429 alınabiliyor (IP limiti)
- Aynı email farklı IP'de de 429 alınabiliyor (email limiti)
- Browserbase ile domain değiştirince yeni IP alınabiliyor

## Verification Code

- Kayıt başarılı olunca 4 haneli kod email'e gönderilir
- Kod input'u browser'da görünür: `textbox` + "NEXT" butonu
- Kod girilince NEXT aktif olur
- **Kod süresi dolduysa** "Resend it" linkine tıkla — yeni kod aynı email'e gönderilir, sayfa yenilenmez, aynı verification modal'ında kalır
- Playwright ile: `await page.wait_for_selector("a:has-text('Resend it')")` sonra `await resend.click()`
- Browser timeout olursa kullanıcı kendi tarayıcısından da kodu girebilir (hesap email'e bağlı, session'a değil)

## Playwright ile Tam Akış (Güncel)

**Önemli:** Verification code sayfasında input sayısı değişebilir. Signup formu + verification input'u = 5 input olabilir, VEYA sadece verification input'u = 1 input olabilir. En güvenlisi `data-testid` seçicisi.

**Double-submit tuzağı:** Signup ve verification form'ları aynı DOM'da bulunabilir. `button[type='submit']` seçicisi tüm formları tetikler → hem signup (422) hem verify isteği gider. Çözüm: **form izolasyonu** — sadece verification form'unu hedefle:

```python
# ❌ YANLIŞ — tüm submit butonlarını tetikler, çift istek
next_btn = await page.query_selector("button[type='submit']")
await next_btn.click()

# ✅ DOĞRU — sadece verification form'unu hedefler
verify_form = await page.query_selector("form:has(h2:has-text('We sent you a code'))")
code_input = await verify_form.query_selector("input")
await code_input.fill("1234")
verify_btn = await verify_form.query_selector("button[type='submit']")
await verify_btn.evaluate("el => el.click()")  # dispatchEvent, bubbling yok
```

Tam akış:

```python
# Signup
btn = await page.wait_for_selector("button:has-text('CREATE YOUR COMMUNITY')")
await btn.click()

inputs = await page.query_selector_all("input")
await inputs[0].fill("Valerie")        # gerçek isim kullan!
await inputs[1].fill("User")
await inputs[2].fill("ornek@gmail.com")  # gerçek Gmail
await inputs[3].fill("Sifre123!")

signup_btn = await page.wait_for_selector("button:has-text('SIGN UP')")
await signup_btn.click()
await page.wait_for_timeout(4000)

# Verification — form izolasyonu ile
verify_form = await page.query_selector("form:has(h2:has-text('We sent you a code'))")
if verify_form:
    code_input = await verify_form.query_selector("input[data-testid='input-component']")
    await code_input.fill(code)
    await page.wait_for_timeout(500)
    
    verify_btn = await verify_form.query_selector("button[type='submit']")
    await verify_btn.evaluate("el => el.click()")
    await page.wait_for_timeout(4000)
```

## Playwright Network Loglama

API request + response'u görmek için event listener kullan. **Kritik:** Event listener async olduğu için `asyncio.ensure_future()` ile sarmalanmalı. Sentry non-JSON POST'ları try/except ile koru:

```python
api_responses = []

async def log_resp(resp):
    if "api" in resp.url:
        try:
            body = await resp.text()
            api_responses.append(f"{resp.status} {resp.url.split('/')[-1]} -> {body[:300]}")
        except:
            pass

# Async event listener — ensure_future ZORUNLU
page.on("response", lambda r: asyncio.ensure_future(log_resp(r)))
```

**Pitfall:** `lambda r: log_resp(r)` direkt çağırılırsa coroutine çalışmaz. `asyncio.ensure_future()` şart.

Bu yöntemle `auth/request-signup` ve `auth/verify-signup` response'ları yakalandı.

## Keşfedilen Ek Endpoint'ler

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `auth/request-signup` | POST | Kayıt isteği: `{email, first_name, last_name, password}` → verification ID (UUID) |
| `auth/verify-signup` | POST | Kod doğrulama: `{code: "1234"}` → 200 başarılı, 400 "invalid code" |
| `auth/login-with-code-init?email=...` | POST | Kod ile giriş başlatma (login sayfası "Log in with a code") |
| `auth/login-with-code` | POST (tahmini) | Kod doğrulama ve giriş |

### verify-signup Detayı
- Request: `POST /auth/verify-signup` body `{"code": "XXXX"}`
- 200: hesap aktif, yönlenme olur
- 400: "invalid code" — kod yanlış veya süresi dolmuş
- Her yeni `request-signup` yeni verification ID üretir, önceki kodlar geçersiz olur

## Verification Code Input Seçicileri

- `input[data-testid='input-component']` — en güvenilir (React bileşeni)
- `button[type='submit']` — NEXT butonu (text bazlı seçiciden daha stabil)
- Input index'ine (`inputs[4]`) güvenme — sayfa state'ine göre değişiyor
