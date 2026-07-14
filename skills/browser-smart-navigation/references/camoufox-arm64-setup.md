# Camoufox — ARM64 Kurulum ve Kullanım

## Nedir

Camoufox, Firefox tabanlı bir browser fork'udur. C++ seviyesinde fingerprint spoofing yaparak Cloudflare Bot Management, Incapsula ve diğer bot detection sistemlerini bypass eder. npm paketi olarak gelir, Playwright API'si üzerinden kullanılır.

## Kurulum

```bash
cd ~/.hermes
npm install camoufox
npx camoufox fetch   # Firefox binary'sini indirir (~247MB)
chmod +x ~/.cache/camoufox/camoufox-bin
```

Binary otomatik olarak `~/.cache/camoufox/` altına indirilir.

## ARM64 (aarch64) Uyumluluğu

- Camoufox binary'si **ARM64 için mevcut** — Oracle Cloud'da test edilmiştir.
- `ELF 64-bit LSB pie executable, ARM aarch64` olarak gelir.
- Binary: `/home/ubuntu/.cache/camoufox/camoufox-bin`
- Tüm Firefox eklentileri (`libxul.so`, `libnss3.so` vs.) ARM64 native olarak gelir.

## Kullanım

```javascript
const { Camoufox } = require('camoufox');

const browser = await Camoufox({
  headless: true,           // headless mod
  os: 'windows',            // işletim sistemi spoof
  humanize: 1.5,            // insan benzeri davranış (0=kapalı, 1.5=orta)
  locale: ['en-US'],
  screen: { min_width: 1280, min_height: 720 }
});

const page = await browser.newPage();
await page.setViewportSize({ width: 1366, height: 768 });
await page.goto('https://site.com', { waitUntil: 'load' });
```

## Önemli Parametreler

| Parametre | Değerler | Etkisi |
|-----------|----------|--------|
| `headless` | `true`, `false`, `virtual` | `virtual` = Xvfb ile sanal ekran |
| `os` | `'windows'`, `'macos'`, `'linux'` | OS fingerprint spoof |
| `humanize` | `0`-`2` | Mouse hareketleri, bekleme süreleri |
| `locale` | `['en-US']` | Dil ayarı |
| `screen` | `{min_width, min_height}` | Ekran çözünürlüğü aralığı |

## Cookie Yönetimi

Cookie'leri yüklemek için (en güvenilir Cloudflare bypass yöntemi):

```javascript
const cookies = JSON.parse(fs.readFileSync('cookies.json', 'utf8'));
const pwCookies = cookies.map(c => ({
  name: c.name,
  value: c.value,
  domain: c.domain.startsWith('.') ? c.domain : '.' + c.domain,
  path: c.path || '/',
  httpOnly: c.httpOnly || false,
  secure: c.secure || true,
  sameSite: normalizeSameSite(c.sameSite)
}));

await page.context().addCookies(pwCookies);
await page.goto('https://site.com');
```

**sameSite normalizasyonu:**

```javascript
function normalizeSameSite(ss) {
  const val = (ss || '').toLowerCase();
  if (!val || val === 'unspecified') return 'Lax';
  if (val === 'no_restriction') return 'None';
  if (val === 'lax') return 'Lax';
  if (val === 'strict') return 'Strict';
  if (val === 'none') return 'None';
  return 'Lax';
}
```

## Test — Cloudflare Geçişi

```bash
cd ~/.hermes && node -e "
const { Camoufox } = require('camoufox');
(async () => {
  const browser = await Camoufox({ headless: true, os: 'windows', humanize: 1 });
  const page = await browser.newPage();
  await page.goto('https://www.upwork.com/', { waitUntil: 'load' });
  console.log('URL:', page.url());
  console.log('Title:', await page.title());
  await browser.close();
})();
"
```

## Sınırlamalar

1. **Proxy SOCKS5 desteği yok (direct)** — Camoufox Firefox fork'u SOCKS5 proxy'i direkt desteklemez (`NS_ERROR_UNKNOWN_PROXY_HOST`). proxychains4 ile çalıştırılmalıdır:
   ```bash
   proxychains4 node script.cjs
   ```
2. **Cloudflare form submit bloğu** — Camoufox sayfa yüklemeyi geçer (GET) ancak form submit (POST) Cloudflare Bot Management tarafından bloklanabilir. Cookie session reuse bu sorunu çözer.
3. **Firefox olduğu için Chromium-specific özellikler yok** — `getByRole`, `locator` gibi Playwright API'leri çalışır.
4. **waitUntil parametresi** — Playwright formatını kullanır: `'load'`, `'domcontentloaded'`, `'networkidle'`, `'commit'`. Puppeteer'daki `'networkidle2'` ÇALIŞMAZ.

## proxychains4 ile WARP SOCKS5 Kullanımı

```bash
sudo apt-get install -y proxychains4
sudo sed -i 's/^socks4.*/socks5 127.0.0.1 1080/' /etc/proxychains4.conf
proxychains4 node upw_session_refresh.cjs
```

## Chrome'dan Cookie Export (Kullanıcı İçin)

Platform bot detection'ını bypass etmenin en güvenilir yolu, kullanıcının kendi cihazından export ettiği cookie'leri kullanmaktır.

### Adımlar

1. Kullanıcı Chrome'da Upwork'e "Beni hatırla" ile login olur
2. Chrome Web Store'dan "Export cookie JSON file for Puppeteer" extension'ını yükler
3. Extension simgesine tıklar → "Export" → `.json` dosyası indirir
4. Dosyayı Vanitas'a gönderir

### İçe Aktarma

```javascript
const cookies = JSON.parse(fs.readFileSync('/path/to/cookies.json', 'utf8'));
const pwCookies = cookies.map(c => ({
  name: c.name,
  value: c.value,
  domain: c.domain.startsWith('.') ? c.domain : '.' + c.domain,
  path: c.path || '/',
  httpOnly: c.httpOnly || false,
  secure: c.secure || true,
  sameSite: normalizeSameSite(c.sameSite)
}));
await page.context().addCookies(pwCookies);
```

### Cookie Filtreleme

Export edilen cookie'ler genelde tüm tarayıcı cookie'lerini içerir. Hedef domain'inkileri filtrele:

```javascript
const filtered = cookies.filter(c => 
  c.domain && c.domain.includes('upwork.com')
);
```

### Cookie Güvenliği

- Cookie dosyası `~/.hermes/secrets/` altında saklanır, permission 600
- External API'lere (Pollinations, OpenAI) asla gönderilmez
- Sadece local Node.js script'lerinde kullanılır

## sameSite Normalizasyonu

Chrome'dan export edilen cookie'lerde `sameSite` değerleri farklı formatlarda gelir. Playwright `Strict|Lax|None` bekler:

```javascript
function normalizeSameSite(ss) {
  const val = (ss || '').toLowerCase();
  if (!val || val === 'unspecified') return 'Lax';
  if (val === 'no_restriction') return 'None';
  if (val === 'lax') return 'Lax';
  if (val === 'strict') return 'Strict';
  if (val === 'none') return 'None';
  return 'Lax';
}
```

Görülen değerler: `'lax'`, `'strict'`, `'no_restriction'`, `'unspecified'`.

## Session Refresh — Cron Job Pattern

Cookie'lerin sürekli geçerli kalması için düzenli refresh:

**Script:** `/home/ubuntu/.hermes/upw_session_refresh.cjs`
**Konum:** Cookie'ler `~/.hermes/secrets/upwork_cookies.json` (600 permission)

### Script Mantığı

1. Var olan cookie'leri yükle
2. Camoufox ile Upwork'e git
3. Session geçerliyse → sadece cookie'leri tazele
4. Session dolarsa → email+password ile re-login dene
5. Yeni cookie'leri kaydet (600 permission)

### Cron Job

```bash
# Her 4 saatte bir refresh
0 */4 * * *
```

Cron job adı: `Upwork Cookie Refresh (4h)`, job_id: `cfb2a93e2677`

**ÖNEMLİ:** Cron job prompt tabanlı çalışır (agent script'i çalıştırır). Eğer script her seferinde çalışıyorsa sorun yok. Ama eğer token optimizasyonu gerekirse `no_agent=true` + `script=` ile direkt çalıştırılabilir.

## Session Refresh Script (upw_session_refresh.cjs)
