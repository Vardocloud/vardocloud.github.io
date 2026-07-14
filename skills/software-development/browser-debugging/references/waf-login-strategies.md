# WAF Anti-Bot Karşılaştırması ve Login Stratejileri

## Genel Login Stratejisi (Skool + APA Deneyimleri)

### Altın Kural: Önce Tespit, Sonra Aksiyon

1. **Siteyi tanı**: curl ile test et → WAF var mı, hangisi?
2. **WAF'ı tanı**: Cloudflare mu, Incapsula mı, Datadome mu?
3. **Zayıf noktayı bul**: RSS var mı, API endpoint'i var mı, mobile endpoint?
4. **Browserbase ile dene**: Çoğu WAF Browserbase stealth ile geçilir
5. **Playwright'ı sadece Browserbase başarısız olursa dene**

### WAF Tipleri ve Çözümleri

| WAF | Tespit Yöntemi | Çözüm | Cookie Export |
|-----|---------------|-------|---------------|
| **Incapsula/Imperva** | `_Incapsula_Resource` JS, `reese84` cookie, **plugins=0 kontrolü** | **SADECE Browserbase** | ❌ Çalışmaz |
| **AWS CloudFront WAF** | `edge.sdk.awswaf.com` challenge, 403 HTML | Browserbase veya Playwright local ✅ | ⚠️ Bazen |
| **Cloudflare** | JS challenge, `cf_clearance` | Browserbase veya Playwright | ⚠️ Bazen |
| **DataDome** | `datadome` cookie, behavioral | Browserbase (residential proxy şart) | ❌ |
| **Akamai** | `_abck` cookie, sensor data | Browserbase | ❌ |
| **Custom/Basic** | Basit rate-limit, IP block | Playwright + WARP | ✅ |

> **Kritik ayrım:** Incapsula **`navigator.plugins.length`** kontrolü yapar — headless Chrome'da bu değer 0'dır. AWS CloudFront ve Cloudflare bu kontrole sahip DEĞİLDİR, bu yüzden Playwright local ile geçilebilirler. Incapsula = en agresif WAF.

### Login Akışı Adımları

```
1. CURL TESTİ
   ├── curl -sI https://site.com → WAF var mı?
   ├── curl ile form submit → çalışıyor mu?
   └── API endpoint keşfi → /api/auth, /login, vs.

2. TARAYICI TESTİ
   ├── browser_navigate → sayfa açılıyor mu?
   ├── WAF challenge görünüyor mu?
   └── Login formu erişilebilir mi?

3. LOGIN DENEMESİ
   ├── browser_type (email, password)
   ├── browser_click (submit)
   ├── browser_console → hata mesajı var mı?
   └── browser_snapshot → yönlendi mi, login oldu mu?

4. FETCH INTERCEPTOR (Hata Ayıklama)
   ├── browser_console → interceptor kur
   ├── Login dene
   ├── browser_console → API response'unu oku
   └── 401/403/422 → neyi reddetti?

5. COOKIE DURUMU
   ├── browser_console → document.cookie
   ├── Auth cookie'sini tanı (ERIGHTS, session, cf_clearance, vs.)
   ├── Cookie'leri JSON'a kaydet
   └── Cookie'leri curl'da dene → çalışıyor mu?
```

### Kritik Pitfall: Cookie Reuse

Her WAF cookie'leri farklı doğrular:

- **Incapsula `reese84`**: Browser fingerprint hash'i — ASLA curl'da çalışmaz
- **Cloudflare `cf_clearance`**: IP + User-Agent bazlı — bazen curl'da çalışır
- **Session cookie (`JSESSIONID`, `PHPSESSID`)**: Genelde IP/UA'dan bağımsız — çalışır
- **OAuth token (`ERIGHTS`, JWT)**: Teorik olarak client-independent — AMA WAF header'ları da kontrol eder

### Paralel Test Stratejisi

Zaman kazanmak için her zaman **paralel test** yap:

```
Test 1: curl direkt → WAF tespiti
Test 2: curl + WARP → IP değişimi yeterli mi?
Test 3: Browserbase → stealth yeterli mi?
Test 4: Playwright local → daha hızlı/ucuz alternatif
```

Hepsini aynı anda başlat, ilk çalışanı kullan.

### Form Validation Debugging

"Login failed" gibi sessiz hataların sebebini bulmak için:

1. **Mutlaka fetch interceptor kur**
2. API response koduna bak: 401 (auth), 403 (forbidden), 422 (validation)
3. 422 ise hangi alan reddedildi? → response body'yi oku
4. Rate-limit (429) varsa bekle, tekrar dene

### Skool'dan Alınan Dersler

- **React form'lar**: `browser_type` kullan, `el.value` React state'i güncellemez
- **Çoklu form**: `form:has(h2:has-text('...'))` ile spesifik form seç
- **Double-submit**: `button[type='submit']` tüm formları tetikler
- **İsim validation**: Uydurma isimler reddedilir (Valeri ❌, Valerie ✅)
- **Gmail `+` alias**: Backend reddedebilir, düz email kullan
- **Disposable email**: Domain kara listesi var
- **Signup vs Login**: Aynı session'da kal, yeni signup yeni verification ID üretir

### APA'dan Alınan Dersler

- **Incapsula agresif**: Plugins=0, headless Chrome'un en büyük işareti
- **Xvfb + headed Chrome DAHİ çalışmaz**: `webdriver=False`, `plugins=5` (gerçek plugin'ler), headed mod, stealth aktif — **hiçbiri yeterli değil**. Incapsula incident ID ile reddediyor. Sebep: datacenter IP'si (Oracle Cloud). WARP proxy bile datacenter IP olarak işaretlenmiş.
- **Browserbase şart**: Sadece residential proxy + stealth kombinasyonu Incapsula'yı geçer
- **RSS bypass**: WAF genelde statik XML endpoint'lerine uygulanmaz
- **`reese84` kutsal**: Export edip curl'da kullanamazsın — TLS + canvas + WebGL fingerprint eşleşmesi gerek
- **WARP tek başına yetmez**: IP değişir ama fingerprint aynı kalır, ayrıca WARP IP'leri de datacenter/proxy olarak flag'lenir
- **Stealth modülü sınırlı**: `webdriver`'ı gizler ama `plugins`'i gizleyemez
- **React select/combobox**: `el.value = 'PsycArticles'` JS manipülasyonu React state'ini güncellemez. `browser_type` veya `browser_click` ile native event gönderilmeli. Aksi takdirde buton tıklaması formu submit etmez, sessizce resetler.

### Hızlı Referans: WAF Tespit İmzaları

```
Incapsula:       /_Incapsula_Resource  → visid_incap_*, reese84 (plugins=0 KONTROLÜ!)
AWS CloudFront:  edge.sdk.awswaf.com   → 403 HTML (plugins kontrolü YOK)
Cloudflare:      /cdn-cgi/challenge/   → cf_clearance, __cf_bm
DataDome:        datadome cookie       → datadome
Akamai:          _abck cookie          → bm_sz
```

### Doğru Araç Seçimi
### Doğru Araç Seçimi

```
WAF yok / basit    → curl, Python requests
Cloudflare         → Browserbase (önce), Playwright+stealth (yedek)
Incapsula          → SADECE Browserbase
DataDome/Akamai    → Browserbase (residential proxy şart)
Herhangi WAF+RSS   → curl ile RSS'i çek (WAF atlanır!)
```

### Kural: Mevcut Aracı Tercih Et

❌ Yeni araç kurmadan önce mevcut araçları dene:
- Hermes browser (Browserbase) → çoğu WAF'ı geçer
- curl + RSS → WAF'sız endpoint'leri bul
- Playwright (local) → sadece basit WAF'larda

Yeni kurulum (Xvfb, browser-use, yeni tarayıcı) sadece mevcut tüm araçlar denendikten sonra ve **Edel onayıyla**. Headed Chrome + Xvfb bile Incapsula'yı geçemez — zaman kaybı.

> **Neden bu sıralama?** Incapsula `navigator.plugins.length=0`'ı kontrol eder (headless Chrome işareti) — Playwright ne yaparsan yap geçemez. CloudFront ve Cloudflare bu kontrolü yapmaz, bu yüzden önce daha hızlı ve ücretsiz olan Playwright denenir. Skool (CloudFront) ✅, APA (Incapsula) ❌.
