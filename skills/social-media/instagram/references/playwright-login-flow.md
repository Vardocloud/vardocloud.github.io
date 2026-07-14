# Instagram Playwright Giriş Akışı — Çalışan Yöntem (2 Haz 2026)

## Başarıyla test edildi: @melkora_ hesabı

### Konfigürasyon
```python
browser = p.chromium.launch(headless=True)
ctx = browser.new_context(
    proxy={"server": "socks5://127.0.0.1:1080"},  # WARP zorunlu
    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
    locale="tr-TR"
)
```

### Akış

1. **Login sayfası:** `https://www.instagram.com/accounts/login/`, `wait_until="networkidle"`
2. **Form doldur:** `input[name="email"]` ve `input[name="pass"]` (NOT `input[name="username"]`!)
3. **Submit:** `page.press('input[name="pass"]', "Enter")` (Enter tuşu, button click çalışmıyor)
4. **2FA bekleme:** 10-60 saniye poll — sayfa "Başka bir cihazdaki bildirimlerine bak" yazısından "Giriş bilgilerin kaydedilsin mi?" yazısına değişir
5. **Save login dialog:** `page.click("text=Şimdi değil")` ile geç
6. **Cookie al:** Ana sayfaya yönlenince `ctx.cookies()` ile tüm cookie'leri al

### Pitfall'lar

| Hata | Çözüm |
|------|-------|
| `button[type="submit"]` bulunamadı | `page.press('input[name="pass"]', "Enter")` kullan |
| `input[name="username"]` bulunamadı | Instagram'da name `email` |
| 2FA sayfasında hiç buton yok | Bekle — 5-10 saniye sonra Edel onaylarsa otomatik ilerler |
| Çok fazla deneme → rate limit | 10+ dakika bekle, yeni context ile dene |
| 429 HTTP hatası | WARP proxy kullanıldığından emin ol |
| Session cookie yok (sadece csrftoken, mid) | Henüz login olmamış — 2FA onayı bekleniyor |

### Cookie Kaydetme (Netscape formatı)
```python
netscape = "# Netscape HTTP Cookie File\n"
for c in cookies:
    domain = c.get('domain', '.instagram.com')
    secure = 'TRUE' if c.get('secure', False) else 'FALSE'
    expires = str(int(c.get('expires', 0))) if c.get('expires') else '0'
    netscape += f"{domain}\tTRUE\t{c.get('path', '/')}\t{secure}\t{expires}\t{c['name']}\t{c['value']}\n"
```

### instagrapi Session Formatı
```python
session = {"cookies": {c['name']: c['value'] for c in cookies if '.instagram.com' in c.get('domain', '')}}
cl.set_settings(session)  # login_by_sessionid alternatifi
```

### Çalışan Cookie'ler (başarılı girişte)
- `sessionid` — oturum anahtarı (olmazsa login başarısız)
- `ds_user_id` — kullanıcı ID'si
- `csrftoken` — CSRF koruması
- `mid` — machine ID
