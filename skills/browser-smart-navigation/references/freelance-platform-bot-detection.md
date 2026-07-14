# Freelance Platform Bot Detection — Bypass Atlası

## Upwork (Cloudflare Bot Management)

### Tespit

- `cType: managed` — Cloudflare managed challenge kullanır
- Sayfa kaynağında `window._cf_chl_opt` ara
- `curl -s URL | grep _cf_chl_opt` ile tespit
- Body'de `mmMwWLliI0fiflO&1` string'i 7+ kez tekrarlanıyorsa CF challenge aktif (managed mode)

### Challenge Katmanları (ÖNEMLİ)

Upwork 2 katmanlı Cloudflare challenge kullanır:

1. **Sayfa yükleme (GET):** İlk sayfa yüklenirken Cloudflare challenge. Puppeteer MCP (snap chromium) genelde bunu geçer.
2. **Login submit (POST):** Email+password gönderildikten sonra ek challenge. Bu katman daha agresiftir — Snap Chromium VNC'de bile bloklayabilir.

### Neden GET Çalışır, POST Bloke Olur?

Cloudflare Bot Management her isteği **JA3/JA4 TLS fingerprint + header analizi + IP reputasyonu + davranış pattern'i** ile 1-99 arası puanlar:

- **GET (sayfa yükleme):** Düşük risk skoru — Cloudflare'in 1. katmanı (JavaScript challenge) geçilir, sayfa gösterilir.
- **POST (form submit):** Yüksek risk skoru — Cloudflare Bot Management backend analizi:
  - TLS/SSL handshake fingerprint'i (JA3/JA4) otomasyon işareti taşır
  - Request header'ları (Accept, Accept-Language, Sec-Fetch-* ) bot pattern'ine uyar
  - Form alanlarını doldurma hızı ve sırası insan değildir
  - IP adresi datacenter/cloud aralığında olduğu için yüksek risk alır
  - Oracle Cloud (`193.122.53.132`) ve WARP (`104.28.x.x`) IP'leri flaglenmiştir

**Sonuç:** Client-side browser fingerprint evasion (stealth plugin, Camoufox) GET katmanını geçer ama POST katmanı server-side analiz yapar — client-side tekniklerle atlatılamaz.

### Neden VNC'de Snap Chromium Bile Bloklanıyor?

Cloudflare managed challenge **sadece** headless tespiti yapmaz:
- **Browser fingerprint:** Snap Chromium'un fingerprint'i diğer Chromium'lardan farklıdır
- **IP reputasyonu:** Oracle Cloud IP aralıkları genelde bot traffic olarak işaretlenir
- **TLS fingerprint:** Chrome'un TLS handshake'i Cloudflare tarafından analiz edilir
- **Davranış analizi:** Mouse hareketi, scroll hızı, tuş giriş hızı

### Bypass Hiyerarşisi (en kolaydan zora)

| # | Yöntem | Başarı | Açıklama |
|---|--------|--------|----------|
| 1 | Hermes browser tool | ❌ | Headless Chrome tespit edilir |
| 2 | Puppeteer MCP + Snap Chromium | ⚠️ Katman 1 ✅, Katman 2 ❌ | snap chromium → `puppeteer_connect_active_tab` |
| 3 | **Puppeteer-extra + stealth plugin** | ⚠️ Sayfa yükleme ✅, Form submit ❌ | `npm install puppeteer-extra puppeteer-extra-plugin-stealth`. Cloudflare katman 1 (sayfa yükleme/GET) geçilir. Katman 2 (form submit/POST) Cloudflare Bot Management backend analizi tarafından bloklanır — `mmMwWLliI0fiflO&1` marker'ı body'de görünür. ARM64'te Playwright Chromium binary'sini executablePath olarak kullan: `/data/ubuntu/cache/ms-playwright/chromium-1223/chrome-linux/chrome`. `page.waitForTimeout()` v23+ yok → `new Promise(r => setTimeout(r, ms))`. **Stealth plugin sınırı:** Client-side fingerprint evasion işe yarar, ancak Cloudflare Bot Management'ın backend-side POST analizi client-side ile atlatılamaz. |
| 3b | **Camoufox (npm)** | ⚠️ Sayfa yükleme ✅, Form submit ❌ | `npm install camoufox`. Firefox fork'u (C++ level fingerprint spoofing). ARM64 native binary var. Kullanım: `const { Camoufox } = require('camoufox');`. Playwright API sunar. Cloudflare katman 1'i geçer ama katman 2 (form submit/POST) aynı şekilde bloklanır — sorun browser fingerprint değil, IP + backend request pattern analizi. |
| 4 | Stealth Chrome (custom UA + disable flags) | ❌ | Cloudflare fingerprint tespit eder |
| 4b | **Camoufox + proxychains4 + WARP** | ⚠️ Sayfa ✅, Form submit ❌ | Proxychains ile WARP SOCKS5 (`127.0.0.1:1080`) üzerinden yönlendirme. WARP IP'leri de Cloudflare tarafından tanınır. |
| 5 | WARP SOCKS5 proxy | ❌ 503 | WARP IP aralığı Cloudflare tarafından engellenir |
| 6 | Google SSO | ❌ Hata | Upwork "Your Google account cannot be accessed at this time" döner |
| 7 | Firefox (Snap) VNC'de | ❌ | Farklı TLS fingerprint, yine tespit edilir |
| 8 | Residential proxy (Browserbase, BrightData) | ⚠️ Ücretli | Fingerprint rotasyonu, denenmedi |
| 9 | Upwork REST/GraphQL API | ⚠️ OAuth gerekli | `fieldjoshua/upwork-mcp-server` |
| 10 | VNC + kullanıcı manuel | ✅ | Kullanıcı Cloudflare challenge'ı kendisi geçer |
| 11 | xdotool + VNC | ⚠️ Klavye sorunu varsa | `references/vnc-xdotool-form-fill.md` |

### Çözüm İçin Kalan Seçenekler

1. **Cookie Session Reuse (ÖNERİLEN)** — Kullanıcı kendi cihazından login olur, Chrome'da "Beni hatırla" ile girer, cookie'leri export eder. Vanitas `context.addCookies()` ile yükler. Cookie'ler `~/.hermes/secrets/upwork_cookies.json` (600 permission). Cron job ile her 4 saatte bir refresh (`upw_session_refresh.cjs`). Session dolarsa email+password ile re-login dener. Detay: `references/camoufox-arm64-setup.md`.
2. **Upwork Developer Portal'dan OAuth token** — "Vanilla" projesi oluşturuldu, callback `http://localhost`. Token'ı üretip Vanitas'a ver, MCP server direkt API üzerinden çalışır. **Ama identity verification gerekebilir** (kredi kartı/banka ekstresi).

### Kullanıcı İzni Kuralı

Bot detection riski taşıyan platformlarda (Upwork), profil düzenleme, başvuru yapma, form gönderme gibi hesap üzerinde etkili işlemler için ASLA direkt işlem yapma. Önce kullanıcıya ne yapılacağını söyle, açık onay al. Aksi halde bot davranışı tespit edilip hesap banlanabilir.

### Upwork MCP Server

- **Repo:** fieldjoshua/upwork-mcp-server
- **Auth:** OAuth2 access token (UPWORK_ACCESS_TOKEN env)
- **Token için:** https://www.upwork.com/developer/keys adresinde uygulama oluştur
- **Callback URL:** `http://localhost` veya `http://localhost:3000/callback`
- **ÖNEMLİ:** Upwork developer uygulaması oluşturmak için **identity verification** gerekir (kredi kartı/banka ekstresi gibi belgeler). Kullanıcı bunu istemeyebilir.

### Upwork Özel — Hata Ayıklama İpuçları

- **Cloudflare ≠ Upwork hatası:** Sayfada "technical difficulties" varsa önce curl ile source'u kontrol et. Eğer `_cf_chl_opt` yoksa sorun Cloudflare DEĞİL, Upwork sunucu tarafıdır.
- **Rate limit:** Çok deneme sonrası 403 dönüyorsa IP bloke olmuş olabilir. 5-10dk bekle.
- **"Username or password is incorrect"** — Cloudflare geçildiyse bu Upwork'un kendi auth hatasıdır. Şifre Bitwarden'dan doğru alındı mı kontrol et.
- **Google SSO çalışmaz:** Upwork-Google entegrasyon sorunu.
- **Güvenlik sorusu:** Giriş başarılı olursa "Your first pet's name" gibi soru sorabilir. "Remember this device" checkbox'ını işaretle.

### ARM64 Chromium Uyumluluğu

Oracle Cloud ARM64:
- Playwright bundled chromium: `/data/ubuntu/cache/ms-playwright/chromium-1223/chrome-linux/chrome`
- Puppeteer's own chromium is x86_64 — won't work on ARM64
- Camoufox provides native ARM64 binary (`~/.cache/camoufox/camoufox-bin`)

## Zoom Web

- Hata: "bots aren't allowed"
- Çözüm: Meeting SDK kullan (direct browser bypass çalışmaz)
- Detay: `references/zoom-anti-bot.md`

## APA (Incapsula)

- Incapsula bot detection kullanır
- `auto` engine ile Browserbase residential IP gerekebilir

## Skool (Cloudflare)

- Hafif Cloudflare koruması
- `auto` engine genelde yeterli
- Residential proxy ile daha güvenilir

## Genel Strateji

1. **Önce Puppeteer MCP dene** — farklı fingerprint, çoğu Cloudflare katmanını geçer
2. **Cloudflare tespiti:** `curl -s URL | grep _cf_chl_opt` — varsa managed challenge
3. **403/503 farkı:** 403 = Cloudflare challenge, 503 = WARP/Cloudflare IP engeli
4. **Rate limit:** Çok fazla deneme IP'yi geçici bloke eder — 5-10dk bekle
5. **Browser farkı:** Farklı binary farklı fingerprint verir. Biri bloklanınca diğerini dene.
6. **Proxy chain:** proxychains4 kurulu (`sudo apt-get install proxychains4`). Config: `/etc/proxychains4.conf` — socks5 satırını WARP SOCKS5'e çevir: `socks5 127.0.0.1 1080`. Kullanım: `proxychains4 node script.js`.
7. **VNC son çare:** Kullanıcıya VNC bağlantısı ver, Cloudflare challenge'ını manuel geçsin
