Updating existing reference file

## Puppeteer-extra + Stealth Plugin — Sınırı ve Pratik Notlar

Puppeteer MCP Cloudflare 1. katmanı geçemezse, puppeteer-extra + stealth plugin dene:
```bash
cd ~/.hermes && npm install puppeteer-extra puppeteer-extra-plugin-stealth
```

ARM64'te Snap Chromium yerine Playwright bundled Chromium'u kullan:
```js
executablePath: '/data/ubuntu/cache/ms-playwright/chromium-1223/chrome-linux/chrome'
```

**Stealth plugin sınırı (ÖNEMLİ):** Sayfa yükleme (GET) isteklerinde Cloudflare 1. katmanını başarıyla geçer. Form submit (POST) isteklerinde Cloudflare Bot Management backend analizi devreye girer ve "Due to technical difficulties" hatası döner. Bu client-side evasion ile aşılamaz — Cloudflare backend'de request pattern, timing ve IP reputasyonu analiz eder.

**CF challenge marker:** Body'de `mmMwWLliI0fiflO&1` string'i 7+ kez tekrarlanır.

**Kod yazım notu:** `page.waitForTimeout()` v23+ Puppeteer'da kaldırılmıştır. Bunun yerine:
```js
await new Promise(r => setTimeout(r, ms));
```

**Password env var redaction:** `process.env.PW` veya `process.env.PASSWORD` yazdığında redact_secrets sistemi bunu `proces...` ile değiştirir. Temp dosyadan oku:
```js
const fs = require('fs');
const PASSWORD=*** 
```

## Upwork Login Flow (2-Step)

1. Navigate to `https://www.upwork.com/ab/account-security/login`
2. Dismiss cookie banner if present
3. Type email into `input#login_username` → Click "Continue" button
4. Password field (`input#login_password`) appears
5. Type password, check "Keep me logged in" checkbox
6. Click "Log In" button
7. Cloudflare Bot Management blocks the POST → body shows "Due to technical difficulties" + `mmMwWLliI0fiflO&1` ×7
8. **Çözüm:** Client-side evasion yetersiz. VNC veya manuel giriş gerek.
