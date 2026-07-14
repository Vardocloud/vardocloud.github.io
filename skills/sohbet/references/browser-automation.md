# Browser Automation Patterns

## Playwright Setup (Oracle Cloud ARM64)

```bash
python3 -m playwright install chromium  # already in venv
```

Usage: `execute_code` ile async Python script. `asyncio.run()` ile çalıştır.

## Signup Form Automation Pattern

### Temel Akış
1. `playwright.async_api` ile browser başlat
2. Form doldururken input'ları index ile bul: `inputs = page.query_selector_all("input")`
3. Butonlara spesifik seçiciyle tıkla: `button:has-text('SIGN UP')`
4. Response'ları logla: `page.on("response", callback)` — **her zaman hem request hem response logla**

### API Response Loglaması (ZORUNLU)
```python
api_responses = []
async def log_resp(resp):
    if "api" in resp.url:
        try:
            body = await resp.text()
            api_responses.append(f"{resp.status} {resp.url.split('/')[-1]} -> {body[:300]}")
        except:
            pass
page.on("response", lambda r: asyncio.ensure_future(log_resp(r)))
```
**Neden:** Response body olmadan 422 "valid name" gibi hataları göremezsin. Tahmin ederek 3 email harcarsın.

### Çift İstek (Double Submit) Pitfall'ı
Web formlarında signup sonrası verification sayfası açıldığında, **signup form'u DOM'da kalır.** 
Verification form'unu submit ederken signup form'u da tetiklenebilir → 422/400 hatası.

**Çözüm:** Verification form'unu izole et:
```python
verify_form = page.query_selector("form:has(h2:has-text('We sent you a code'))")
code_input = verify_form.query_selector("input")
verify_btn = verify_form.query_selector("button[type='submit']")
verify_btn.evaluate("el => el.click()")  # bubbling'i önle
```

### İsim Validasyonu
Bazı siteler (Skool) yaygın olmayan isimleri reddeder. "Valeri", "Valementa", "Vividemento" → ❌. "Valerie" → ✅.

### Rate Limit Yönetimi
- 5-6 denemeden sonra 429 "too many requests"
- Aynı email ile tekrar signup → "Signup failed" (pending state)
- CloudFront 403 → IP block (WARP da işe yaramayabilir)
- **Session başına maks 5 deneme, sonra bekle.**

## Skool Spesifik

### API Endpoint'leri
| Endpoint | Method | Body | Response |
|----------|--------|------|----------|
| `/auth/request-signup` | POST | `{email, first_name, last_name, password}` | 200: verification UUID, 422: "Please use a valid name", 429: rate-limit |
| `/auth/verify-signup` | POST | `{code: "1234"}` | 200: success, 400: "invalid code", 429: rate-limit |
| `/auth/login-with-code-init` | POST | `?email=...` | 200: code sent, login başlat |
| `/auth/login-with-code` | POST | `{code: "1234"}` | 200: logged in, 429: "too many attempts" |

### Engellenen Domain'ler
- `wshu.net` (mail.tm) → 400
- `+` alias (Gmail) → sessiz başarısız

### Kod Süresi
Doğrulama kodu **30 dakika** geçerli. "Resend it" ile aynı verification ID için yeni kod alınabilir.

**Kritik Pitfall:** Her yeni signup yeni verification ID üretir. Email'e gelen kod bir önceki signup içinse, yeni signup'ta geçersiz olur. Kod her zaman **aynı browser session'ında, aynı signup sonrası** girilmeli.

### Background Process ile Kod Bekleme
Kullanıcıdan kod beklerken browser'ı açık tutmak için:
```python
# Script /tmp/verify.py yaz → terminal(background=True, notify_on_complete=true) ile çalıştır
# Script bir dosyayı poll ederek kod bekler: /tmp/skool_code.txt
# Kullanıcı kodu verince write_file ile dosyaya yaz → script okur → girer
```
**Pitfall:** `page.on("response")` callback'leri `asyncio.ensure_future()` ile sarılmalı, yoksa Sentry gibi non-JSON POST'lar `post_data_json` çağrısında patlar.

**Background Process Anti-Pattern:**
- ❌ `process(action='poll')` ile 10+ kez poll etme — process zaten `notify_on_complete=true` ile haber verecek
- ❌ Process çalışırken "bekliyor" diye 5 mesaj atma
- ✅ `notify_on_complete=true` ile başlat, sadece 2-3 kez poll et, sonra bekle

### CloudFront/WAF
- Direkt API çağrıları (curl/requests) → 403
- Browser üzerinden API istekleri → çalışır (cookie + UA header ile)
- Çok istek → IP block (WARP IP'leri aynı Cloudflare subnet'inde olduğu için birlikte flaglenir)
- **Aşma yöntemi:** Tailscale üzerinden temiz ev IP'si ile SOCKS5 proxy
- IP block geçici olabilir — 15-30 dk bekleyip tekrar dene

### TEK DENEME KURALI (KRİTİK)

Her `login-with-code-init` veya signup, kullanıcının email'ine **yeni bir kod** gönderir. Bu yüzden:
- ❌ Aynı login için birden fazla `login-with-code-init` yapma. Her biri yeni kod → spam.
- ❌ "We sent you a code" sayfasındayken sayfayı yenileme. Yeni kod gider.
- ✅ Bir login = bir kod. Olmadıysa DUR, bekle, kullanıcıya sor.
- ✅ Background process kullan: tek login, sayfada bekle, kodu dosyadan oku.

### ERR_CONNECTION_RESET / IP Block Dalgalanması

CloudFront block'u dalgalı olabilir — 12 dk önce 200 OK, şimdi ERR_CONNECTION_RESET:
- ✅ 10-15 dk bekle, tekrar dene. Block geçici olabilir.
- ❌ WARP aynı Cloudflare subnet'inde (104.28.x.x) → birlikte flaglenir.
- ✅ Kalıcı çözüm: Tailscale SOCKS5 proxy (temiz ev IP'si).
- ❌ 5 kez retry yapıp "Cannot connect" deme — durumu bildir, bekle.

### Playwright Bağlantı Retry Pattern
```python
for attempt in range(5):
    try:
        resp = await page.goto(url, timeout=10000)
        if resp and resp.status == 200:
            break
    except:
        wait = (attempt + 1) * 3
        await asyncio.sleep(wait)
else:
    print("Cannot connect after 5 attempts")
    return  # DUR, zorlama
```

## Login + 2FA Pattern

Bazı siteler (Skool) şifreyle login'de bile 2FA kodu ister:

1. Email + şifre ile login → `login-with-code-init` çağrılır
2. "We sent you a code" modal'ı açılır
3. Code input'u **input[2]** (placeholder="Code", type="text", testid="input-component")
4. Submit: modal içindeki buton yerine **Enter tuşu** en güvenlisi (modal overlay'i bypass eder)
5. `login-with-code` endpoint'i çağrılır

**Pitfall:** Login sayfasında 3 buton vardır: "Log In" (password login, büyük I), "Log in with a code" (passwordless), ve "Log in" (2FA submit, küçük i). Büyük/küçük harf farkına ve "with a code" varyantına dikkat. Yanlış buton → yeni `login-with-code-init` isteği gönderir, rate-limit yer.

**Input Indexleri (Skool spesifik):**
| Form | Input[0] | Input[1] | Input[2] | Input[3] |
|------|----------|----------|----------|----------|
| Signup | first_name | last_name | email | password |
| Login (ilk) | email | password | — | — |
| Login 2FA | email | password | **code** (placeholder="Code") | — |
| Signup 2FA | first_name | last_name | email | password → sonra modal'da ayrı code input'u |

### 429 Rate-Limit: DURMA KURALI

Eğer `login-with-code` veya `verify-signup` 429 dönerse:
- ❌ **Aynı browser session'ında tekrar deneme.** Her deneme yeni `login-with-code-init` çağrısı yapar, rate-limit sayacını artırır.
- ❌ **Edel'e "bir daha deneyeyim mi" diye sorma.** Cevap hayır. Dur, bekle.
- ✅ **Browser'ı kapat, 5-10 dk bekle.** Session cookie'leri sıfırlanır.
- ✅ **Kullanıcı "X tane kod geldi" derse ciddiye al. Bu bir hata sinyali, görmezden gelme.** Beklerken kod süresi dolar.
- ✅ **Tekrar başlarken sıfırdan:** browser.launch() → login → 2FA.

## Modal Overlay Click Blocking

Skool ve benzeri sitelerde modal arka planı (`BaseModalWrapper`) submit butonlarının üstüne biner. Normal `.click()` → `TimeoutError: ... subtree intercepts pointer events`.

**Çözümler (öncelik sırasıyla):**
1. **`await page.keyboard.press("Enter")`** — EN GÜVENLİSİ, modal overlay'den etkilenmez
2. `await btn.evaluate("el => el.click()")` — JavaScript click, bubbling yok
3. `await btn.click(force=True)` — son çare, çift submit yapabilir

## "Resend it" ile Taze Kod

Signup/login sonrası "Didn't get the email? Resend it" linki, **aynı verification ID** için yeni kod gönderir. Yeni signup yapmaya gerek yoktur. Bu sayede ID/kod eşleşme sorunu yaşanmaz.
