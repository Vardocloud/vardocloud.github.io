# Instagram Login + Cookie Save (Playwright)

Tam çalışan login script'i. Cookie yoksa veya instagrapi challenge'a takılırsa kullan.

## Script

```python
from playwright.sync_api import sync_playwright
import os, time

COOKIE_PATH = os.path.expanduser("~/.hermes/INSTAGRAM_COOKIES.txt")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        proxy={"server": "socks5://127.0.0.1:1080"},
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
    )
    page = ctx.new_page()
    
    page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle", timeout=30000)
    time.sleep(3)
    page.fill('input[name="email"]', "KULLANICI_ADI")
    page.fill('input[name="pass"]', "SIFRE")
    page.press('input[name="pass"]', "Enter")
    time.sleep(8)
    
    url = page.url
    
    # 2FA handling
    if "challenge" in url.lower() or "checkpoint" in url.lower():
        text = page.inner_text("body")
        if "another device" in text.lower():
            print("[!] Device-based 2FA — onay bekle veya 'Try another way' tıkla")
        elif "code" in text.lower():
            print("[*] Code-based verification — kodu gir")
    
    if "instagram.com" in url and "challenge" not in url.lower() and "login" not in url.lower():
        cookies = ctx.cookies()
        netscape = "# Netscape HTTP Cookie File\n"
        for c in cookies:
            domain = c.get('domain', '.instagram.com')
            secure = 'TRUE' if c.get('secure', False) else 'FALSE'
            expires = str(int(c.get('expires', 0))) if c.get('expires') else '0'
            netscape += f"{domain}\tTRUE\t{c.get('path', '/')}\t{secure}\t{expires}\t{c['name']}\t{c['value']}\n"
        
        with open(COOKIE_PATH, 'w') as f:
            f.write(netscape)
        os.chmod(COOKIE_PATH, 0o600)
        print(f"[OK] {len(cookies)} cookies saved to {COOKIE_PATH}")
    
    browser.close()
```

## Notes

- **Form alanları:** `name='email'` (username/email) + `name='pass'` (şifre)
- **Submit:** `page.press('input[name="pass"]', "Enter")` — `button[type="submit"]` çalışmaz
- **Mobile UA zorunlu:** Desktop UA reddedilir
- **WARP proxy zorunlu:** Oracle Cloud IP'si Meta tarafından bot işaretlenir
- **Rate-limit:** Peş peşe 2+ başarısız deneme → login sayfasına dönme. 5+ dk bekle.
- **2FA:** Cihaz onayı (telefon bildirimi) veya e-posta kodu. "Try another way" ile e-posta'ya geçilebilir.
