# Instagram Cookie Auto-Refresh Cron

## Pattern: no_agent script + cron

Instead of manually refreshing cookies each time, use a no_agent cron job that visits Instagram via Playwright weekly/daily, then re-exports fresh cookies.

## Cron Job Kurulumu

```bash
cronjob(action='create',
  name='Instagram Cookie Refresh',
  schedule='0 10 * * *',       # Her gün 10:00 (Edel tercihi)
  script='instagram_cookie_refresh.sh',
  no_agent=True,
  deliver='origin')
```

## Script

Script: `scripts/instagram_cookie_refresh.sh` (`~/.hermes/scripts/instagram_cookie_refresh.sh`)

```bash
# Quick test:
bash ~/.hermes/scripts/instagram_cookie_refresh.sh
```

## How it works (Akış)

```
Pre-flight (cookie var mı, csrftoken+sessionid+ds_user_id var mı)
  → WARP proxy kontrolü (socks5://warp:1080)
  → Playwright: mevcut cookie'leri yükle
  → instagram.com'u aç (wait_until="networkidle")
  → Yeni cookie'leri ctx.cookies() ile al
  → sessionid kayboldu mu kontrol et (login sayfasına düştüyse kaybolur)
  → Netscape formatında kaydet (chmod 600)
  → API test: @bardopsikoloji profil sorgula (GET /api/v1/users/web_profile_info/)
  → Başarılı/başarısız raporu
```

## Pitfalls

| Hata | Ne Yapmalı |
|------|-----------|
| `BrowserType.launch: Executable doesn't exist` | `playwright install chromium` çalıştır (güncelleme sonrası gerekebilir) |
| **sessionid KAYBOLDU** | Instagram oturum açık değil → Chrome'dan EditThisCookie ile manuel Netscape export |
| WARP YOK / `checkpoint_required` | WARP proxy'sini kontrol et (`curl --socks5 warp:1080 https://www.instagram.com/`) |
| Playwright hatası | Chromium güncel mi kontrol et (`playwright install chromium`) |
| API test hata verir (refresh sonrası) | Rate-limit olabilir → 2-3 dk bekle, tekrar dene |
| **csrftoken değişmiş** | Refresh sonrası yeni csrftoken'ı cookie dosyasından çek, eskisi geçersiz kalır |
| **Session cookies `expires: -1`** | Playwright session cookie'lerde expires=-1 döner. Bu normaldir — "session (no expiry)" olarak raporlanır |

## Schedule Decision

- **Her gün 10:00** — Edel'in tercihi. Sabah mesai başlamadan cookie'ler tazelenir.
- Pazar 03:00 gibi gece yarısı schedule'ları önerilmez — Edel "o zamana kadar expire olur" diye uyardı.
- Günlük refresh, Instagram rate-limit'ine takılmaz çünkü sadece 1 sayfa yükler (login sayfası değil).
