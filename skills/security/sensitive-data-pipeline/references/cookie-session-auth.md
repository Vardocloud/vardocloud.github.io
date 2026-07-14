# Cookie-Based Session Auth Pattern

## Problem

Bazı platformlar (Upwork, LinkedIn, bankalar) Cloudflare Bot Management veya benzeri sistemlerle bot login'ini engeller. Tüm browser bypass teknikleri (stealth plugin, camoufox, proxy rotation) form submit/POST isteklerinde bloklanır.

## Çözüm

Kullanıcının kendi cihazından bir kere login olup cookie'leri export etmesi → otomatik session refresh ile cookie'ler taze tutulur.

## Akış

```
Kullanıcı (Chrome)
  ↓ "Beni hatırla" ile login ol
  ↓ Cookie export (Chrome extension veya DevTools)
  ↓ cookies.json
Vanitas
  ↓ Cookie'leri ~/.hermes/secrets/ sitesinde sakla (600 permission)
  ↓ Camoufox/Playwright ile context.addCookies()
  ↓ Upwork'e navigate → otomatik login
  ↓ Cookie süresi doldu mu?
    → Hayır: session geçerli, işlem yap
    → Evet: email+password ile re-login → yeni cookie'leri kaydet
  ↓ Cron job (her 12 saatte bir) ile refresh
```

## Cookie Export (Kullanıcı Tarafı)

Chrome'da:

1. **Extension ile:** Chrome Web Store → "Export cookie JSON file for Puppeteer"
2. **Manuel (DevTools):** F12 → Application tab → Cookies → www.site.com → sağ tık → Export
3. **Telefonda:** Remote debugging veya dosya paylaşımı

## Cookie Format Dönüşümü

Chrome export'tan gelen cookie'ler Playwright formatına dönüştürülmeli:

```javascript
const pwCookies = rawCookies.map(c => ({
  name: c.name,
  value: c.value,
  domain: c.domain.startsWith('.') ? c.domain : '.' + c.domain,
  path: c.path || '/',
  httpOnly: c.httpOnly || false,
  secure: c.secure || true,
  sameSite: normalizeSameSite(c.sameSite)
}));
```

## sameSite Normalizasyonu

Chrome'daki `sameSite` değerleri Playwright'ın beklediği ile uyuşmaz:

| Chrome Değeri | Playwright Değeri |
|---------------|-------------------|
| `unspecified` | `Lax` |
| `no_restriction` | `None` |
| `lax` | `Lax` |
| `strict` | `Strict` |
| `none` | `None` |

## Cookie Güvenliği

- Cookie dosyaları **600 permission** ile saklanır
- Path: `~/.hermes/secrets/` — external API'ler erişemez
- Cron job ile düzenli refresh edilir
- Password de temp dosyada saklanır, primary model context'ine girmez

## Session Refresh Script

Script konumu: `/home/ubuntu/.hermes/upw_session_refresh.cjs`

```javascript
// upw_session_refresh.cjs
// 1. Var olan cookie'leri yükle
// 2. Camoufox ile Upwork'e git
// 3. Session hala geçerli mi kontrol et (URL'de login sayfası değilse OK)
// 4. Geçersizse → email+password ile re-login dene
// 5. Yeni cookie'leri .json olarak kaydet (600 permission)
// 6. Cron ile her 4 saatte bir çalıştır
```

### Cron Job

```bash
schedule: "0 */4 * * *"    # her 4 saatte bir (00,04,08,12,16,20)
name: "Upwork Cookie Refresh (4h)"
script: node /home/ubuntu/.hermes/upw_session_refresh.cjs
deliver: origin
```

Cron job adı: `Upwork Cookie Refresh (4h)`, job_id: `cfb2a93e2677`

### Prerequisites

- Camoufox kurulu: `npm install camoufox` + `npx camoufox fetch`
- Password /tmp/pw_val.txt'de (bw_secure_get.py ile alınır)
- Cookie'ler `~/.hermes/secrets/upwork_cookies.json` (600 permission)

### Password Management

Script `fs.readFileSync('/tmp/pw_val.txt','utf8').trim()` ile password'ü dosyadan okur — primary model context'ine girmez.

**ÖNEMLİ:** `process.env.PW` yazma — `redact_secrets: true` sistemi bunu `proces...` ile değiştirir ve script bozulur.

### Güvenlik Kuralı

Cookie session ile giriş yapıldığında, hesap üzerinde etkili işlemler (profil düzenleme, başvuru yapma, form gönderme) **ASLA** direkt yapılmaz. Önce kullanıcıya bilgi ver, onay al. Bot detection riski olan platformlarda (Upwork, LinkedIn) bu özellikle kritiktir — bot davranışı tespit edilip hesap banlanabilir.

## Cloudflare Re-Login Blok Durumunda Alternatifler (2026-06)

Cookie'ler expire olduğunda ve Cloudflare headless browser login'i blokladığında:

### ❌ Çalışmayan Yöntemler (Denendi)
- **VNC ile manuel Cloudflare verify butonu**: Butona tıklanınca istek yeniden yönlendirilir, loop'a girer (denendi, başarısız)
- **Camoufox/Playwright headed**: Cloudflare Oracle Cloud datacenter IP'yi tanır, challenge verir
- **undetected-chromedriver**: Aynı IP sorunu

### ✅ Alternatif Çözümler
1. **Apify Actor (upwork-job-scraper)**: Login gerektirmez, Cloudflare'i kendi altyapısında aşar. Ücretsiz tier: 5K işlem/ay. Webhook ile job'ları doğrudan sunucuya gönderir. ~$5/ay ücretli plan da var.
2. **nodriver** (`pip install nodriver`): undetected-chromedriver'ın yaratıcısının yeni projesi, driver seviyesinde stealth. Datacenter IP'de hala sorun olabilir ama en güçlü ücretsiz yöntem.
3. **Chrome Extension (Upwork-Job-Scraper)**: Kullanıcının kendi bilgisayarında çalışır → webhook ile sunucuya JSON gönderir. Cloudflare sorunu yok (gerçek Chrome). Dezavantaj: bilgisayar açık + Chrome çalışıyor olmalı.
4. **RSS Feed alternatifi**: Upwork eski RSS'yi kapattı ama `tdsreader` gibi projeler Google Sheets + Apps Script ile feed benzeri yapı kurmuş.

### Önerilen Sıralama
1. Önce **Apify** dene (en az çaba, webhook ile otomatik, Cloudflare derdi yok)
2. Yedek olarak **nodriver** kur ve dene
3. Uzun vadede kullanıcıdan **ayda 1 cookie export** iste (en garanti ama manuel)
