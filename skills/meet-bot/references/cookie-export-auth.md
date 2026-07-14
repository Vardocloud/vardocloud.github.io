# Cookie Export Auth — Google Meet Kalıcı Oturum

Google Cloud IP'lerinden otomatik tarayıcıyla giriş imkansız. Tek çalışan yöntem:
Edel'in kendi cihazından (telefon/bilgisayar) Google oturum cookie'lerini dışa aktarıp
sunucuya Playwright storage state olarak yüklemek.

## Neden Gerekli?

Google, veri merkezi IP'lerinden gelen otomatik tarayıcıları tespit edip engelliyor.
Hepsi aynı hatayı verir: `"Couldn't sign you in — This browser or app may not be secure"`

- ❌ `playwright-stealth` Python paketi
- ❌ `puppeteer-extra-plugin-stealth` Node.js
- ❌ Chrome persistent context (`launch_persistent_context`)
- ❌ CDP üzerinden gerçek Chromium bağlantısı
- ❌ `hermes meet auth` (Xvfb + VNC olmadan)
- ❌ OAuth token → Playwright cookie dönüşümü (2026-05-25): Google Calendar OAuth token'ları cookie'ye çevrilip `auth.json`'a yazıldı ama Google tarayıcı parmak izi + IP'yi de kontrol ediyor — salt cookie yeterli değil

Hepsi aynı hatayı verir: `"Couldn't sign you in — This browser or app may not be secure"`

## Yöntem A: EditThisCookie (Telefon — En Kolay)

1. **Telefonda Kiwi Browser yükle** (Chrome tabanlı, eklenti destekler)
2. Kiwi'de `accounts.google.com`'a git, Google hesabınla giriş yap
3. **EditThisCookie** eklentisini yükle (Chrome Web Store'dan)
4. Eklentiyi aç → **Export** → JSON olarak kopyala
5. JSON'u Edel'e gönder, sunucuya kaydet

## Yöntem B: Chrome DevTools (Masaüstü)

1. Chrome'da `accounts.google.com`'a giriş yap
2. F12 → Application → Storage → Cookies → `https://accounts.google.com`
3. Tüm cookie'leri tek tek not al (name, value, domain)
4. Veya EditThisCookie masaüstü eklentisiyle tek tıkta export

## Sunucuya Yükleme (Vanitas)

Cookie'ler alındıktan sonra Playwright storage state formatına dönüştür:

```python
import json

# Edel'den gelen cookie JSON'u
raw_cookies = json.loads(edel_cookie_json)

# Playwright storage state formatı
storage_state = {
    "cookies": [],
    "origins": [
        {
            "origin": "https://accounts.google.com",
            "localStorage": []
        }
    ]
}

for c in raw_cookies:
    storage_state["cookies"].append({
        "name": c["name"],
        "value": c["value"],
        "domain": c.get("domain", ".google.com"),
        "path": c.get("path", "/"),
        "expires": c.get("expirationDate", -1),
        "httpOnly": c.get("httpOnly", False),
        "secure": c.get("secure", True),
        "sameSite": c.get("sameSite", "Lax")
    })

path = "/home/ubuntu/.hermes/workspace/meetings/auth.json"
with open(path, "w") as f:
    json.dump(storage_state, f)

# Doğrula
google_count = len([c for c in storage_state["cookies"] if "google" in c["domain"]])
print(f"Kaydedildi: {google_count} Google cookie (5+ hedef)")
```

## Doğrulama

```bash
python3 -c "
import json
with open('$HOME/.hermes/workspace/meetings/auth.json') as f:
    d = json.load(f)
google = [c for c in d.get('cookies',[]) if 'google' in c.get('domain','')]
print(f'Google cookies: {len(google)} (5+ = OK)')
for c in google:
    print(f'  {c[\"name\"]} @ {c[\"domain\"]}')
"
```

5'ten fazla Google cookie'si varsa auth başarılı.

## Süre

Cookie'ler genelde 14 gün geçerli. Süre dolunca işlem tekrarlanır.
