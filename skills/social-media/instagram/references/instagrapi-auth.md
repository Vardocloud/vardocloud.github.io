# instagrapi Login & Challenge Handling

`instagrapi` özel Python kütüphanesi — Instagram'ın gerçek mobil API'sini kullanır.
Playwright'tan daha hızlıdır, bot detection riski düşüktür, session dump/load ile
tekrar login gerektirmez.

## Kurulum

```bash
pip install instagrapi
```

Zaten kurulu: `/home/ubuntu/.hermes/hermes-agent/venv/lib/python3.11/site-packages/instagrapi/`

## Temel Login

```python
from instagrapi import Client

cl = Client()
cl.set_proxy("socks5://127.0.0.1:1080")  # WARP zorunlu
cl.set_locale("tr_TR")
cl.set_country_code(90)
cl.set_timezone_offset(3 * 3600)

# Direct login
cl.login("kullanici_adi", "sifre")

# Session kaydet (tekrar login gerektirmez)
cl.dump_settings("/tmp/hesap_session.json")

# Session ile login
cl.load_settings("/tmp/hesap_session.json")
cl.login_by_sessionid(cl.sessionid)
```

## Cookie Dönüştürme (instagrapi → Netscape)

instagrapi session JSON'undan Netscape cookie jar oluşturma:

```python
import json, os

settings = json.load(open("/tmp/hesap_session.json"))
cookies = settings.get("cookies", {})

netscape = "# Netscape HTTP Cookie File\n"
for key, val in cookies.items():
    netscape += f".instagram.com\tTRUE\t/\tTRUE\t0\t{key}\t{val}\n"

path = os.path.expanduser("~/.hermes/hesap_cookies.txt")
with open(path, 'w') as f:
    f.write(netscape)
os.chmod(path, 0o600)
```

## Challenge Tipleri ve Çözümleri

instagrapi çoğu challenge tipini otomatik çözer. `challenge_code_handler` ile
e-posta/SMS kodu girişi yapılır:

```python
def code_handler(username, choice):
    # choice: ChallengeChoice.EMAIL veya ChallengeChoice.SMS
    code = input(f"{choice.value} kodu: ")
    return code

cl.challenge_code_handler = code_handler
```

### Bilinmeyen Challenge: `STEP_NAME` / `redirect.async`

**Belirti:**
```
ChallengeResolve: Unknown step_name "STEP_NAME" for "kullanici" in challenge resolver:
{'flow_render_type': 3,
 'bloks_action': 'com.bloks.www.ig.challenge.redirect.async',
 'challenge_context': '...',
 'step_name': 'STEP_NAME',
 'challenge_type_enum_str': 'ect_...',
 'status': 'ok'}
```

**Neden:** `last_json` içinde `challenge` key'i yok — klasik challenge API path'i gelmez.
Bu Polaris auth platform challenge'ıdır (`XPolarisAuthPlatformApproveFromAnotherDeviceController`).
instagrapi `challenge.py` satır 603-607'de `ChallengeUnknownStep` fırlatır.

**Çözüm:** instagrapi bu challenge tipini çözemez. **Playwright'a geç:**
1. Playwright ile login sayfasına git
2. `name="email"` + `name="pass"` doldur
3. `page.press('input[name="pass"]', "Enter")` ile submit
4. 2FA sayfasında "Başka bir cihazdaki bildirimlerine bak" görünür
5. Bu sayfada başlangıçta **hiçbir tıklanabilir element yoktur** — "Onay bekleniyor" yazar
6. Alternatif seçenek ("Try another way") 10-20 saniye sonra belirebilir VEYA
7. Telefondan onay vermek en hızlı çözümdür

### 2FA "Device Approval" Sayfası Davranışı

Playwright ile ulaşıldığında:
- Sayfa HTML'i ~759KB, neredeyse tamamı JS
- Görünür metin: "Başka bir cihazdaki bildirimlerine bak" + cihaz adı
- `document.querySelectorAll('button, a, [role="button"]')` → **0 element**
- `page.evaluate` ile event handler araması → **0 sonuç**
- Sayfa tamamen pasif bekleme modundadır

**Strateji:**
1. `wait_for_load_state("networkidle")` + `time.sleep(15)` ile bekle
2. Alternatif buton belirirse tıkla → e-posta/SMS seç
3. Belirmezse kullanıcıdan telefon onayı iste
4. Onay sonrası sayfa otomatik yönlenir → cookie'leri kaydet

## instagrapi vs Playwright Karar Ağacı

```
Login gerekli
├─ Cookie var mı?
│  └─ EVET → Playwright veya curl direkt kullan
├─ Cookie yok
│  ├─ instagrapi.login() dene
│  │  ├─ BAŞARILI → session dump → cookie dönüştür
│  │  └─ ChallengeRequired?
│  │     ├─ EMAIL/SMS → challenge_code_handler ile çöz
│  │     └─ STEP_NAME/redirect.async → Playwright'a geç
│  └─ Playwright login
│     ├─ Normal giriş → cookie kaydet
│     └─ 2FA cihaz onayı → kullanıcıdan onay iste VEYA bekle
```

## Önemli Dosya Konumları

- instagrapi kaynak: `/home/ubuntu/.hermes/hermes-agent/venv/lib/python3.11/site-packages/instagrapi/`
- Challenge resolver: `instagrapi/mixins/challenge.py`
- `ChallengeUnknownStep` hatası: satır 603-607
- `challenge_resolve_simple`: satır 403-608
- `challenge_resolve`: satır 65-107
