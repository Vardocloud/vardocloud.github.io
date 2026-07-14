# JS-Rendered SSO Login Pages

Bazı SSO (Single Sign-On) login sayfaları JavaScript ile render edilir ve `browser_snapshot` boş dönebilir. Bu durumda form alanlarına `browser_console` ile erişilir.

## Belirtiler

- `browser_navigate(login_url)` → snapshot'ta sadece boş sayfa veya `<iframe>` görünür
- `browser_snapshot(full=true)` → 0 element döner
- Sayfa URL'si `sso.` subdomain'inde (örn. `sso.apa.org`, `sso.company.com`)

## Tanı Yöntemi

```javascript
// 1. Input field'ları var mı kontrol et
document.querySelectorAll('input').length

// 2. Input detaylarını gör
Array.from(document.querySelectorAll('input')).map(i => i.name || i.id || i.type)

// 3. Butonları kontrol et
Array.from(document.querySelectorAll('button, a')).filter(el => el.textContent.toLowerCase().includes('google')).length
```

## Adım Adım

### 1. Navigate Et

```javascript
browser_navigate("https://sso.apa.org/...")
```

### 2. Snapshot Al

```javascript
browser_snapshot(full=true)
```

Boş gelirse panik yapma — JavaScript ile render ediliyordur.

### 3. Console ile Kontrol Et

```javascript
browser_console(expression="document.querySelectorAll('input').length + ' inputs: ' + Array.from(document.querySelectorAll('input')).map(i => i.name || i.id || i.type).join(', ')")
```

### 4. Input Alanlarını Doldur

Email/username alanı:
```javascript
browser_console(expression="document.querySelector('input[name=\"email\"]').value = 'kullanici@email.com'; 'OK'")
```

Şifre alanı:
```javascript
browser_console(expression="document.querySelector('input[name=\"password\"]').value = 'sifre'; 'OK'")
```

Not: `name` attribute'ü değişebilir. `input[type="password"]`, `input[name="username"]`, `input[id="login-email"]` gibi alternatifleri dene.

### 5. Submit Et

Submit butonunu bul ve tıkla:
```javascript
browser_console(expression="let btn = document.querySelector('button[type=\"submit\"]') || document.querySelector('input[type=\"submit\"]'); if(btn) { btn.click(); 'Submitted' } else { 'No submit button found' }")
```

### 6. Sonucu Kontrol Et

```javascript
browser_console(expression="document.title + ' | URL: ' + window.location.href")
```

- URL değişmediyse → login başarısız, hata mesajını kontrol et
- Hata mesajı için:
```javascript
browser_console(expression="let err = document.querySelector('.alert, .error, .message, [class*=\"error\"], [class*=\"alert\"]'); err ? err.textContent.substring(0,200) : 'No error element'")
```

## Google/Apple SSO Butonları

SSO sayfalarında genelde "Sign in with Google/Apple" butonları olur. Bunları bul:

```javascript
browser_console(expression="Array.from(document.querySelectorAll('a, button, div')).filter(el => el.textContent.toLowerCase().includes('google') || (el.innerHTML && el.innerHTML.toLowerCase().includes('google'))).length + ' Google buttons'")
```

Google butonuna tıkla:
```javascript
browser_console(expression="let btn = Array.from(document.querySelectorAll('a, button, div')).find(el => el.textContent.toLowerCase().includes('google') || (el.innerHTML && el.innerHTML.toLowerCase().includes('google'))); if(btn) { btn.click(); 'Clicked' } else { 'Not found' }")
```

Google login popup'ı açılabilir. Popup içindeki elementlere doğrudan erişilemeyebilir — `browser_snapshot` ile ana sayfanın durumunu kontrol et.

## Dialog/Modal Yönetimi

SSO sayfasında "verify your email" gibi dialog'lar çıkabilir:

```javascript
// Dialog içeriğini kontrol et
let dialog = document.querySelector('[role=\"dialog\"], .modal, .overlay');
dialog ? dialog.textContent.substring(0, 200) : 'No dialog'
```

## Hata Durumları ve Çözümleri

| Hata | Sebep | Çözüm |
|------|-------|-------|
| "email/username or password is incorrect" | Yanlış şifre veya email | Farklı email dene veya şifre sıfırlama |
| "locked out of one-time code login due to 5 failed login attempts" | Çok fazla başarısız deneme | Şifre ile login dene (one-time code lock bağımsız) |
| "verify your email" dialog'u | Google SSO email doğrulama | Email'e gelen linki onayla (kullanıcıya sor) |
| Snapshot boş, console'da input var | JS render gecikmesi | `browser_console` ile devam et, snapshot'a güvenme |
| Popup açıldı ama erişilemiyor | Cross-origin popup | Dialog'u kapat, ana sayfada farklı yöntem dene |
| Login sonrası redirect olmuyor | 2FA/CAPTCHA | `browser_vision` ile ekranı kontrol et |

## Örnek: APA SSO Login (PsycNet)

```
URL: https://sso.apa.org/apasso/idm/login?ERIGHTS_TARGET=https://psycnet.apa.org/home
Inputs: _csrf, ERIGHTS_TARGET, email, login-email, _csrf, ERIGHTS_TARGET, username, password, rememberMe, _csrf, email, identifier, ERIGHTS_TARGET
Google button: mevcut (Google logo SVG)
```

Akış:
1. Email gir → `document.querySelector('input[name="email"]').value = 'email'`
2. Şifre gir → `document.querySelector('input[name="password"]').value = 'şifre'`
3. Submit → `document.querySelector('input[type="submit"]').click()`
4. Başarısız olursa → Google SSO dene
5. Google SSO → "verify your email" dialog'u çıkabilir
