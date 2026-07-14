# Anti-Bot Teşhis Katmanları

WARP IP değiştirir ama bot tespitinin tek katmanı IP değildir.

## Teşhis Sırası

### 1. IP seviyesinde mi?
- `ifconfig.me` ile görünen IP'yi kontrol et
- Cloudflare IP'si (104.x) = WARP çalışıyor
- Oracle IP'si (193.x) = WARP çalışmıyor

### 2. CloudFront WAF mi?
- Belirti: `403 ERROR` + `X-Cache: Error from cloudfront`
- Çözüm: Sadece gerçek tarayıcı — WAF challenge'ını (JS, fingerprint) Python/curl geçemez
- Browser tool'u `engine: chrome` + WARP ile dene

### 3. Backend bot tespiti mi?
- Belirti: WAF geçildi, API 200 dönüyor ama "failed" / "try again later"
- IP residential bile olsa backend fingerprint (canvas, WebGL, fontlar) tespit ediyor
- Çözüm: Gerçek kullanıcı tarayıcısı (kullanıcının kendi cihazı)

### 4. Popup/OAuth engeli mi?
- Belirti: Google/Apple butonuna tıklandı, hiçbir şey olmadı
- Sebep: Headless Chromium'da popup engelleniyor veya OAuth redirect'i çalışmıyor
- Çözüm: Email/password flow'una geç veya kullanıcıya yönlendir

## Karar Ağacı

```
Hata alındı
├─ 403 CloudFront → WAF engeli → tarayıcı zorunlu
│  ├─ Browser tool ulaşabiliyor → WAF geçildi
│  └─ Browser tool 403 → IP ban (WARP'ı kontrol et)
├─ 200 ama "failed" → Backend anti-bot
│  └─ Kullanıcıya yönlendir (kendi cihazından dene)
└─ Popup/OAuth yok → Headless kısıtı
   └─ Email flow'una geç
```

## Örnek: Skool.com (28 Mayıs 2026)

- API: `api2.skool.com/auth/request-signup`
- WAF: AWS CloudFront + `017ae153ccc5.edge.sdk.awswaf.com`
- Browser tool: WAF geçiyor, backend "Signup failed. Try again later" dönüyor
- Google OAuth: popup headless'da engelleniyor
- Sonuç: Kullanıcı kendi cihazından kaydolmalı
