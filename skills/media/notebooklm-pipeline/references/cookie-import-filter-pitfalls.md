# Cookie Import & Auth Pitfalls (24 Haz 2026)

Bu referans, `nlm login --manual -f` ve VNC+CDP cookie extraction yöntemleriyle ilgili
son oturumda keşfedilen tuzakları ve çözümleri içerir.

## 1. HTTP 413 — Request Entity Too Large

**Belirti:** `nlm login --manual -f cookies.json` başarılı olur (`✓ Successfully authenticated!`)
ama `nlm list notebooks` veya `nlm login --check` **HTTP 413** döner.

**Neden:** `nlm login --manual` tüm cookieleri (2497 adet, 870KB) profile kaydeder.
`nlm` daha sonra NotebookLM'e HTTP isteği yaparken tüm cookieleri header'da gönderir →
Google sunucusu "Request Entity Too Large" hatası döner.

**Çözüm:** SADECE Google domain'lerini filtrele:
```bash
# Önce cookieleri Google-only filtrele
python3 -c "
import json
with open('cookies.json') as f:
    raw = f.read()
if raw.startswith('1|'):  # Bazı export'larda '1|' prefix olabiliyor
    raw = raw[2:]
cookies = json.load(raw)
filtered = [c for c in cookies if 'google' in c.get('domain','').lower()]
print(f'Total: {len(cookies)} → Google: {len(filtered)}')
with open('/tmp/nblm_cookies.json', 'w') as f:
    json.dump(filtered, f)
"

# Sonra import et
nlm login --manual -f /tmp/nblm_cookies.json
```

**Sonuç:** 40-200 Google cookie'si yeterli ve HTTP 413'ü önler.

## 2. Chrome 149+ encrypted_value

**Durum:** Chrome 149 ve üzeri, Linux'ta cookie değerlerini `encrypted_value` sütununda
saklar (`value` sütunu boş string). Bu, Chrome'un OS keyring'ine bağlı bir
şifreleme kullanır.

**Ne işe yarar:** SQLite'dan direkt cookie okuyamazsın:
```python
# ÇALIŞMAZ - value boş string
import sqlite3
conn = sqlite3.connect('/path/to/Default/Cookies')
c = conn.cursor()
c.execute("SELECT host_key, name, value FROM cookies WHERE host_key LIKE '%notebooklm%'")
# → value hep '' (boş) döner, gerçek değer encrypted_value'da
```

**Çözüm:** Çalışan Chrome'a CDP (Chrome DevTools Protocol) ile bağlan, `Page.cookies()`
veya `Network.getAllCookies()` ile export et.

## 3. CDP Cookie Extraction (24 Haz 2026 — ÖNERİLEN YÖNTEM)

Cookie'leri Chrome SQLite'tan okuyamadığında, **çalışan Chrome** örneğine
`--remote-debugging-port` ile bağlan.

### Adımlar

```bash
# 1. Chrome'u remote debugging port ile başlat
chromium --user-data-dir=/path/to/profile --no-sandbox \
  --disable-dev-shm-usage --disable-gpu \
  --remote-debugging-port=9222 https://notebooklm.google.com &

# 2. Kullanıcı VNC'den manuel login yapar
# 3. CDP endpoint'ini kontrol et
curl http://127.0.0.1:9222/json/version
# → {"Browser": "Chrome/149...", "webSocketDebuggerUrl": "ws://127.0.0.1:9222/..."}

# 4. Playwright ile cookies al
python3 << 'PYEOF'
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]  # mevcut context
        cookies = await context.cookies()
        # storage_state.json olarak kaydet
        await context.storage_state(path="/tmp/storage_state.json")
        print(f"Exported {len(cookies)} cookies")
        await browser.close()

asyncio.run(main())
PYEOF
```

**Alternatif — Python websockets ile direkt CDP:**
```python
import json, urllib.request
# CDP WebSocket URL'sini al
resp = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read())
ws_url = resp[0]['webSocketDebuggerUrl']
# websockets ile bağlan, Network.getAllCookies çağır
```

## 4. VNC Stack — Container Uyumluluğu

noVNC web dosyaları `/opt/novnc/` veya `/home/ubuntu/noVNC/` altındadır.
**`/usr/share/novnc` çoğu container'da bulunmaz.**

```bash
# Doğru websockify çağrısı
websockify --web /opt/novnc 6080 127.0.0.1:5900
```

### x11vnc Flags (Container'da çalışması için zorunlu)
```bash
x11vnc -display :<N> -forever -shared -nopw -noxdamage -nodpms
```
- `-noxdamage`: MIT-SHM hatasını önler
- `-nodpms`: DPMS extension uyarısını bastırır
- `-shared`: birden çok bağlantıya izin verir
- `-nopw`: şifresiz erişim

### Xvfb Display Seçimi
Container'da root'a ait eski bir Xvfb (:99) çalışıyor olabilir:
```bash
# Kontrol
ps aux | grep Xvfb
# → root Xvfb :99 ... (Jun23'ten beri)

# Yeni display kullan (:100, :101 vb.)
Xvfb :100 -screen 0 1920x1080x24 -ac -noreset
```
Root Xvfb'i öldüremezsen (`pkill Xvfb` yetmez), farklı display numarası kullan.

## 5. nlm login Browser Mode — Silent Failure

`nlm login` (browser mode, --manual olmadan) bazen Chrome başlatmadan sessizce
çalışır durur. Belirtiler:
- Process `running` ama hiç çıktı üretmez
- Chrome process list'te görünmez
- Hiçbir hata mesajı dönmez

**Çözüm:** Önce mevcut cookie profilini temizle, sonra dene:
```bash
rm -rf ~/.notebooklm-mcp-cli/profiles/default
DISPLAY=:<N> nlm login
```
Eğer hâlâ çalışmazsa, direkt Chrome açıp manuel login yap:
```bash
DISPLAY=:<N> chromium --user-data-dir=/path/to/profile --no-sandbox \
  https://notebooklm.google.com
```

## 6. pkill -f Kendini Öldürme Tuzağı

```bash
# DİKKAT: Bu komut kendini de öldürür!
pkill -f "nlm login"   # pkill process'i de "nlm login" pattern'ine uyar

# GÜVENLİ:
kill <PID>                     # spesifik PID
pkill -f "nlm login" 2>/dev/null && true  # hata yut, ama yine de riske girme
```

## 7. nlm Profile Yapısı

```
~/.notebooklm-mcp-cli/profiles/default/
├── cookies.json    # Flat dict: {"cookie_name": "value", ...}
└── metadata.json   # {"csrf_token": null, "session_id": null, "email": null, ...}
```

- `cookies.json` flatten edilmiş formattadır (orijinal export'taki domain/path/secure
  gibi alanlar kaybolur). Bu nedenle bazı `__Secure-` prefix'li cookieler doğru
  çalışmayabilir.
- `csrf_token` ve `session_id` `nlm login --manual` sonrası `null` kalır.
  `nlm` bunları ilk RPC çağrısında HTML'den otomatik çıkarmaya çalışır.
- `nlm login --manual` işe yaramazsa (Google cookie'leri IP'den reddediyorsa),
  VNC + manuel login + CDP cookie export en güvenilir yöntemdir.
