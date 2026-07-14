---
name: browser-smart-navigation
description: "Web sitelerinde akıllı gezinme stratejisi. Buton, link ve içerikleri bulmak için decision tree + anti-repeat kuralları. Token tasarrufu sağlar, element kaçırmayı önler."
version: 1.0.0
author: Vanitas
metadata:
  hermes:
    tags: [browser, navigation, vision, efficiency, tokens, web]
    applies_to: [Vanitas]
    triggered_by: [browser-navigate, web-scraping, login, form-fill, browser-click, browser-snapshot]
---

# Akıllı Browser Gezinme

Butonları, linkleri ve içerikleri bulmak için sistematik yaklaşım. Token israfını önler.

## Karar Ağacı

Her sayfa yüklendiğinde bu sırayı izle:

### ADIM 1: Snapshot al (HER ZAMAN full=true)

`browser_snapshot(full=true)` — `full=false` KULLANMA

ref ID'leri kaydet (örn: @e5, @e12)

- Element bulundu mu? → `browser_click` / `browser_type` ile devam et
- HAYIR → ADIM 2'ye geç

### ADIM 2: Vision ile kontrol

`browser_vision` — ekran görüntüsünü analiz et

- Buton, form, link var mı?
- Bulduğun elementin pozisyonunu ADIM 1'deki ref ID ile eşleştir
- Bulamadıysan → ADIM 3'e geç

### ADIM 3: Console kontrolü

`browser_console` — JS hatalarını kontrol et

- Hata varsa → bekle (3-5 sn), ADIM 1'e dön
- Hata yoksa → ADIM 4'e geç

### ADIM 4: Aşağı kaydır

```
browser_scroll(direction="down")
browser_snapshot(full=true)
```

- Dynamic content için (Skool, Reddit, Twitter vs.)
- Yeni içerik geldi mi? → ADIM 1'e dön
- HAYIR → ADIM 5'e geç

### ADIM 5: Sayfa içi arama

`browser_get_images` + `browser_console`

- Resimleri listele, son hataları kontrol et
- Hala bulamadıysan → Sayfayı yeniden yükle veya URL kontrol et

## Anti-Repeat Kuralları (KRİTİK)

| Kural | Açıklama |
|-------|----------|
| URL tekrarı | Aynı URL'ye 2'den fazla kez navigate ETME |
| Snapshot limiti | Aynı sayfada 3'ten fazla snapshot ALMA |
| Vision limiti | Vision'ı 2'den fazla kullanma |
| Session hafızası | Her navigasyon öncesi: "Bu URL'ye zaten gittim mi?" diye sor |
| Session ID | Aynı session'da devam et, yeni session açma |

## Navigasyon Stratejisi

### ⚠️ Stale Ref ID Tuzağı (KRİTİK)

Sayfa state'i değiştiğinde (form açıldı, modal geldi, navigasyon oldu) **ESKİ snapshot'ın ref ID'leri geçersiz olur.** Eski ref'e tıklamak sayfayı bozabilir → "Unknown ref" hatası → sonraki snapshot boş gelir.

**Kural:** Her sayfa-state değişiminden SONRA yeni snapshot al. Önceki snapshot'tan ref ID'sini ezberleyip yeni sayfada kullanma.

**Kurtarma:**
1. `browser_snapshot(full=true)` dene — boş gelirse
2. Base URL'e yeniden `browser_navigate(url)` yap
3. Taze snapshot al, yeni ref ID'lerini kullan

### Basit sayfalar (haber, blog, wiki)

1. `browser_navigate(url)`
2. `browser_snapshot(full=true)` — metni oku
3. Bitti — `web_extract` daha hızlı olabilir

### Karmaşık sayfalar (Skool, LinkedIn, Twitter)

1. `browser_navigate(url)`
2. `browser_snapshot(full=true)` — elementleri bul
3. `browser_vision` — görsel kontrol
4. `browser_scroll(down)` — aşağı kaydır
5. `browser_snapshot(full=true)` — yeni elementler
6. Gerekirse `browser_click` ile devam et

### Login sayfaları

1. `browser_navigate(login_url)`
2. `browser_snapshot(full=true)` — input alanlarını bul
3. Snapshot boş gelirse → **JS-rendered SSO** olabilir:
   - `browser_console` ile input'ları kontrol et (`document.querySelectorAll('input')`)
   - Form alanlarını JavaScript ile doldur (detay: `references/js-rendered-sso-login.md`)
4. `browser_type(ref_id, email)` — email gir
5. `browser_type(ref_id, password)` — şifre gir
6. `browser_snapshot(full=true)` — submit butonunu bul
7. `browser_click(submit_ref_id)` — giriş yap
8. `browser_snapshot(full=true)` — başarılı mı kontrol et

### Form doldurma

1. `browser_snapshot(full=true)` — tüm input alanlarını listele
2. Her alan için `browser_type(ref_id, value)`
3. `browser_snapshot(full=true)` — submit butonunu bul
4. `browser_click(submit_ref_id)`

### ⚠️ SPA Custom Form Components (React/Angular/Vue)

SPA'lerdeki özel form component'leri (combobox, dropdown, date picker, select) standart `browser_type` veya `browser_click` ile çalışmayabilir. Bu component'ler DOM event'lerini kendi synthetic event sistemleriyle yönetir.

**React Combobox/Dropdown — Adım Adım:**

1. **Doğrudan combobox'a tıklama** — `browser_click(combobox_ref)` genelde işe yaramaz çünkü React component'i click event'ini parent wrapper'da dinler.

2. **Parent wrapper'ı tıkla** — Snapshot'ta combobox'ın üstündeki `generic [ref=..] clickable [cursor:pointer]` elementi bul. Ona `browser_click` yap. (Zoom'da çalışan yöntem)

3. **Listbox'ın açılmasını bekle** — Tıklamadan hemen sonra `browser_snapshot(full=true)` al. Açılan dropdown `listbox [ref=..]` olarak görünür, içinde `option` elementleri olur.

4. **Seçeneği tıkla** — `browser_click(option_ref)` ile istediğin seçeneği seç.

5. **React state güncellenmezse — JS fallback:**
   ```javascript
   // 1. Input'u bul
   const input = document.querySelector('[aria-label="..."]');
   // 2. Native value setter kullan (React controlled input)
   const nativeSetter = Object.getOwnPropertyDescriptor(
     window.HTMLInputElement.prototype, 'value'
   ).set;
   nativeSetter.call(input, 'değer');
   // 3. React event'lerini tetikle
   input.dispatchEvent(new Event('input', { bubbles: true }));
   input.dispatchEvent(new Event('change', { bubbles: true }));
   // 4. Varsa React _valueTracker'ı da güncelle
   if (input._valueTracker) {
     input._valueTracker.setValue('değer');
   }
   input.dispatchEvent(new Event('change', { bubbles: true }));
   ```
   Bu yöntem Zoom, Salesforce, HubSpot gibi React SPA'lerde çalışır.

**Belirtiler — Combobox açılmıyorsa:**

| Belirti | Olası Sebep |
|---------|-------------|
| `browser_click(combobox_ref)` işe yaramıyor | React event'i parent'da dinleniyor |
| Dropdown açılıyor ama tıklama kaydolmuyor | React state güncellenmedi — JS fallback dene |
| Snapshot'ta `expanded=true` ama option yok | Virtualized list — scroll gerekebilir |
| Form submit "required field" hatası veriyor | React state güncellenmedi — JS fallback şart |

## Kullanıcı İzni Kuralları (KRİTİK)

Bot detection riski taşıyan platformlarda (Upwork, freelance siteler, LinkedIn, Instagram) profil düzenleme, form gönderme, başvuru yapma gibi **hesap üzerinde etkili işlemler** için:
1. **ASLA** direkt işlem yapma — önce kullanıcıya ne yapmak istediğini söyle
2. **İzin al:** "Şunu yapabilir miyim?" diye sor, açık onay bekle
3. **Bot riskini belirt:** "Bot görürlerse hesap banlanabilir" gibi uyarı ekle
4. **Alternatif sun:** Manüel yapmak isterse cookie export'u iste

**İstisna:** Salt okuma işlemleri (sayfa görüntüleme, içerik okuma) için izin gerekmez.

## Token Tasarruf İpuçları

1. **Önce web_extract dene** — Basit sayfalar için browser'dan hızlı ve ucuz
2. **full=true** — Tek seferde tüm sayfayı gör, birden fazla snapshot alma
3. **Vision'ı son çare olarak kullan** — Snapshot yetersiz kaldığında
4. **Console kontrol et** — JS hatalarını erken tespit et, gereksiz tıklamayı önle
5. **Scroll + snapshot** — Dynamic content için en etkili yöntem

## Hata Durumları

| Durum | Çözüm |
|-------|-------|
| Snapshot boş dönüyor | Sayfa henüz yüklenmedi → bekle, tekrar dene |
| Stale ref → "Unknown ref" hatası → sonraki snapshot boş | Sayfa state'i bozuldu → **base URL'e yeniden navigate et**. Eskimiş ref ID'lerini kullanma — her sayfa değişiminden sonra taze snapshot al. |
| ref ID bulamıyor | Vision ile kontrol et, elementin pozisyonunu bul |
| Click çalışmıyor | Element tıklanabilir olmayabilir → `browser_cdp` ile test et |
| Login başarısız | 2FA/CAPTCHA olabilir → `browser_vision` ile kontrol et |
| Headless browser tespiti — freelance/platform bot koruması (Upwork, Zoom Web) | Bu platformlar headless Chrome'u agresif tespit eder. **Sistematik deneme sırası (en kolaydan zora):** (1) Normal browser → Cloudflare challenge. (2) Puppeteer MCP + snap chromium (Cloudflare'ın 1. katmanını geçer, login'de 2. katman challenge çıkabilir). (3) Puppeteer-extra + stealth plugin (`npm install puppeteer-extra puppeteer-extra-plugin-stealth`) — Snap Chromium ve Hermes browser tool'un geçemediği CF challenge katmanlarını **sayfa yüklemede** geçer, ancak form submit/POST isteklerinde Cloudflare Bot Management 2. katman devreye girer ve bloklar. (4) Stealth Chrome (özel UA + `--disable-blink-features=AutomationControlled`). (5) WARP SOCKS5 proxy — Cloudflare WARP IP'lerini 503 ile engeller. (6) Google SSO (Upwork'te çalışmaz). (7) Firefox (farklı engine). (8) Platform REST/GraphQL API araştırması. (9) MCP Server (OAuth gerekebilir). (10) VNC → kullanıcı manuel girişi. (11) **Camoufox (Firefox fork)** — C++ seviyesinde fingerprint spoofing, ARM64 binary mevcut. `npm install camoufox` + `npx camoufox fetch` ile kurulur. Playwright API'si. Sayfa yüklemede CF 1. katmanı geçer ama form submit (POST) hâlâ bloklanabilir. (12) **Cookie session reuse** — En güvenilir yöntem. Kullanıcıdan cookie export alınır → Camoufox ile `context.addCookies()` yüklenir. Süresi dolunca `upw_session_refresh.cjs` ile re-login + cron job. (13) **Proxychains4 + WARP** — `apt install proxychains4`, config'e `socks5 127.0.0.1 1080`, `proxychains4 node script.cjs` ile çalıştır. WARP IP'leri CF tarafından da tanınabilir. **Stealth plugin sınırı:** GET isteklerinde (sayfa yükleme) başarılı, POST isteklerinde (form submit) Cloudflare Bot Management backend analizi tarafından bloklanır — bu client-side evasion ile aşılamaz. **Çözüm:** Cookie session reuse (kullanıcıdan cookie export al, `context.addCookies()` ile yükle, cron job ile refresh). Detay: `references/camoufox-arm64-setup.md`. **Cloudflare tespiti:** Sayfa kaynağında `_cf_chl_opt` ara. `cType: 'managed'` = Bot Management. Body'de `mmMwWLliI0fiflO&1` string'i 7+ kez tekrarlanıyorsa CF challenge aktif. **⚠️ Oracle Cloud Datacenter IP Kuralı:** Oracle Cloud IP'lerinden gelen TÜM istekler Cloudflare tarafından engellenir — browser hangisi olursa olsun fark etmez. Browser fingerprint spoofing işe yaramaz, IP range bazlı bloklama vardır. **Çözüm:** (a) Google Custom Search API (`references/google-cse-cloudflare-bypass.md`), (b) Apify gibi residential IP servisleri, (c) Kullanıcının kendi bilgisayarında çalışan browser extension. **ARM64 not:** Puppeteer'ın kendi chromium x86_64 binary'sidir. Playwright bundled chromium `/data/ubuntu/cache/ms-playwright/chromium-1223/chrome-linux/chrome` kullan. |
| Cloudflare engeli | **Oracle Cloud datacenter IP'leri Cloudflare tarafından BLOKLANIR** — browser türü fark etmez. **Çözüm sırası:** (1) **Google Custom Search API** (ÜCRETSİZ, cloudflare-free) — `site:upwork.com/jobs [keywords]`, Google'ın indexini oku. Detay: `references/google-cse-cloudflare-bypass.md`. (2) Apify / residential IP servisleri. (3) Kullanıcının bilgisayarında browser extension. **NOT:** localhost.run Haziran 2026'dan beri bozuk — tunnel sağlayıcı olarak cloudflared kullan (`cloudflared tunnel --url http://127.0.0.1:PORT`). |
| Timeout | `browser_console` ile durumu kontrol et |

## Engine Seçimi Sayfası

| Platform | Önerilen Engine | Neden |
|----------|----------------|-------|
| Skool (Cloudflare) | `auto` | Browserbase residential IP |
| APA (Incapsula) | `auto` | Gerçek fingerprint |
| Google/YouTube | `chrome` + WARP | Cloudflare bypass |
| Instagram (Reels) | `chrome` | Login pop-up'ı kapat → vision ile içerik analizi. Pop-up'ı kapatmak için browser_snapshot ile ref ID bul, click et, sonra browser_vision. Ses yok — sadece görsel analiz. |

## Kombinasyon Örnekleri

### Skool'da içerik bulma

1. `browser_navigate("https://www.skool.com/...")`
2. `browser_snapshot(full=true)`
3. `browser_vision`
4. `browser_scroll(down)`
5. `browser_snapshot(full=true)`

### LinkedIn post paylaşma

1. `browser_navigate("https://www.linkedin.com/feed/")`
2. `browser_snapshot(full=true)`
3. `browser_click(@e5)` — "Start a post" butonu
4. `browser_type(@e12, "Post içeriği...")`
5. `browser_snapshot(full=true)`
6. `browser_click(@e15)` — Post butonu
