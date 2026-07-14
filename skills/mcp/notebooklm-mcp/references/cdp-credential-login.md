# CDP Credential Login (v2.0.11)

## Overview

Bu doküman, notebooklm-mcp v2.0.11'in Chrome'unda **CDP (Chrome DevTools Protocol)** üzerinden Google hesabıyla login yapmayı anlatır. MCP'nin kendi Chrome'u undetected-chromedriver ile başlatılır ve authentication sayfasında (accountchooser/şifre) bekler. CDP ile müdahale ederek login işlemini tamamlayabiliriz.

## Neden Cookie Copy Çalışmaz?

Keepalive Chrome'dan cookie'leri SQLite (`Default/Cookies`) olarak kopyalamak **Google tarafından reddedilir.** Sebebi Google'ın **Cookie Binding** güvenlik önlemi:

- Google, cookie'leri Chrome instance'ının fingerprint'i ile imzalar (user-agent, port, session ID, TLS parametreleri)
- Farklı bir instance'dan gelen cookie'ler `accounts.google.com/CookieMismatch` sayfasına yönlendirilir
- Aynı profili sembolik link ile paylaşmak da çalışmaz — iki Chrome aynı anda profili kullanamaz (SQLite lock)
- **"23 cookies from storage_state" sayısı bir red herring'dir** — asıl önemli olan Google'ın yönlendirdiği URL

## Flow

```
MCP Chrome başlatılır (undetected-chromedriver)
  → login sayfası (accountchooser veya identifier)
    → CDP ile sayfaya bağlan
      → accounts.google.com/accountchooser
        → isimgorulsunn@gmail.com hesabına tıkla
      → accounts.google.com/challenge/pwd
        → şifreyi Bitwarden'dan al → input'a yaz
        → Enter tuşu gönder
      → noteboklm.google.com/notebook/<id> ✅
```

## Script

```python
# scripts/mcp_auto_login.py (veya nlm_cdp_login.py)
```

## Adımlar

### 1. MCP Chrome Portunu Bul

MCP her çalıştığında Chrome rastgele bir port açar:

```bash
ps aux | grep "chrom.*remote-debug" | grep -v "18800" | grep -v grep
# Çıktıda: --remote-debugging-port=XXXXX
```

Alternatif: HTTP API ile kontrol:

```bash
curl -s http://127.0.0.1:<PORT>/json/list
```

### 2. Target Tespiti

Chrome'da bir veya daha fazla sekme (target) vardır. Login sayfasını bul:

```python
import urllib.request, json
resp = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list")
targets = json.loads(resp.read())
for t in targets:
    if "accountchooser" in t["url"] or "signin" in t["url"]:
        ws_url = t["webSocketDebuggerUrl"]
```

### 3. WebSocket ile Bağlan

```python
import websocket, ssl
ws = websocket.create_connection(ws_url, timeout=10, sslopt={"cert_reqs": ssl.CERT_NONE})
```

### 4. AccountChooser'da Hesap Seç

```python
req = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": """
    (() => {
        const btns = document.querySelectorAll('[data-identifier]');
        for (const btn of btns) {
            if (btn.getAttribute('data-identifier') === 'isimgorulsunn@gmail.com') {
                btn.click(); return 'clicked';
            }
        }
        return 'not found';
    })()
"""}}
ws.send(json.dumps(req))
```

### 5. Şifre Sayfasında Şifre Gir

```python
# Bitwarden'dan şifre al
import urllib.request
resp = urllib.request.urlopen("http://127.0.0.1:8087/object/item/8a95abcd-65dd-4aa5-a255-b4660182d7cf")
data = json.loads(resp.read())
password = data["data"]["login"]["password"]

# Şifre input'una yaz (React controlled input için native setter)
req = {"id": 2, "method": "Runtime.evaluate", "params": {"expression": f"""
    (() => {{
        const inp = document.querySelector('input[type="password"]');
        const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        s.call(inp, {json.dumps(password)});
        inp.dispatchEvent(new Event('input', {{bubbles: true}}));
        inp.dispatchEvent(new Event('change', {{bubbles: true}}));
        return 'filled';
    }})()
"""}}
ws.send(json.dumps(req))
```

### 6. Enter Tuşu Gönder

Butona tıklamak (`#passwordNext`) bazen çalışmaz. Enter tuşu daha güvenilir:

```python
# keyDown
req = {"id": 3, "method": "Input.dispatchKeyEvent", "params": {
    "type": "keyDown", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13
}}
ws.send(json.dumps(req))

# keyUp
req = {"id": 4, "method": "Input.dispatchKeyEvent", "params": {
    "type": "keyUp", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13
}}
ws.send(json.dumps(req))
```

### 7. NotebookLM'e Yönlenmeyi Kontrol Et

```python
req = {"id": 5, "method": "Runtime.evaluate", "params": {"expression": "window.location.href"}}
ws.send(json.dumps(req))
# Response'u bekle
```

## Pitfall'lar

### CookieMismatch Error

- **Belirti:** `accounts.google.com/CookieMismatch` sayfası
- **Sebep:** İki Chrome instance'ı aynı profili kullanmaya çalışıyor (keepalive + MCP)
- **Çözüm:** Chrome'u öldür → MCP'nin yeni Chrome başlatmasına izin ver → accountchooser sayfasına düşer

### `Page.navigate` → chrome-error

- **Belirti:** `Page.navigate` çağrısından sonra `chrome-error://chromewebdata/`
- **Sebep:** MCP server moduyla ilgili network sorunu (DNS/proxy)
- **Çözüm:** `Page.navigate` yerine `Page.navigate` + beklemeyi dene, veya doğrudan keepalive Chrome'u kullan

### Şifre Input'u Value Set Edilmiyor

- **Belirti:** Şifre input'una yazılan değer görünüyor ama submit sonrası boş
- **Sebep:** React controlled input — jQuery/vanilla JS `value` setter'ını dinlemez
- **Çözüm:** `nativeInputValueSetter` pattern'ini kullan:
  ```javascript
  const nativeSetter = Object.getOwnPropertyDescriptor(
      window.HTMLInputElement.prototype, 'value'
  ).set;
  nativeSetter.call(element, value);
  element.dispatchEvent(new Event('input', {bubbles: true}));
  element.dispatchEvent(new Event('change', {bubbles: true}));
  ```

### Account'i Tıklayınca Yanıt Yok

- **Belirti:** Hesaba tıklandı ama URL değişmiyor
- **Sebep:** `data-identifier` attribute'u değişmiş olabilir
- **Çözüm:** Sayfa HTML'ini al (`document.body.innerText`) ve hesabın göründüğü DOM yolunu bul

### WebSocket BrokenPipe

- **Belirti:** CDP komutu gönderilirken `BrokenPipeError: [Errno 32] Broken pipe`
- **Sebep:** Chrome (target) kapandı — MCP test bitti, `client.close()` çağrıldı
- **Çözüm:** MCP server kullan (Chrome'u açık tutar) veya daha hızlı login yap — NotebookLM Re-auth via Bitwarden

## Overview

When NotebookLM MCP auth expires and keepalive Chrome shows `accountchooser`
with "Signed out" for all accounts, use this technique to re-authenticate via
CDP + Bitwarden password.

**Tested:** 11 Tem 2026 — ✅ successful

## Full Flow

```
┌──────────────────────────────────────────────────────────────┐
│  1. Keepalive Chrome'da accountchooser sayfası açık           │
│     (52 cookie yüklü ama "Signed out")                        │
│                                                               │
│  2. CDP ile accountchooser'da isimgorulsunn@gmail.com'a tıkla │
│     → /challenge/pwd sayfasına yönlen                         │
│                                                               │
│  3. Bitwarden'dan şifreyi al (bw-serve port 8087)             │
│     Item ID: 8a95abcd-65dd-4aa5-a255-b4660182d7cf              │
│     (Google-isimgorulsunn / isimgorulsunn@gmail.com)           │
│                                                               │
│  4. CDP ile şifreyi password input'una yaz                     │
│     (React controlled input — nativeValueSetter gerekli)      │
│                                                               │
│  5. Enter tuşu gönder (buton tıklaması çalışmıyor)            │
│     → notebooklm.google.com'a yönlenir                         │
│                                                               │
│  6. Yeni cookie'leri al → MCP'nin Chrome'una enjekte et       │
│     (Network.setCookies ile)                                   │
│     → MCP'nin Chrome'u da NotebookLM'de açılır ✅              │
└──────────────────────────────────────────────────────────────┘
```

## Step-by-Step (Python)

### Step 1: Keepalive Chrome'da hesap seç

```python
import json, urllib.request, websocket, ssl, time

# Keepalive Chrome: port 18800
resp = urllib.request.urlopen("http://127.0.0.1:18800/json/list", timeout=5)
targets = json.loads(resp.read())

# accountchooser target'ını bul
target = None
for t in targets:
    if "accountchooser" in t.get("url", ""):
        target = t
        break

ws_url = target.get('webSocketDebuggerUrl', '')
ws = websocket.create_connection(ws_url, timeout=10, sslopt={"cert_reqs": ssl.CERT_NONE})

# isimgorulsunn@gmail.com hesabına tıkla
ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {
    "expression": """
        (() => {
            const btns = document.querySelectorAll('[data-identifier]');
            for (const btn of btns) {
                if (btn.getAttribute('data-identifier') === 'isimgorulsunn@gmail.com') {
                    btn.click();
                    return 'clicked';
                }
            }
            return 'not found';
        })()
    """
}}))
time.sleep(3)
```

### Step 2: Bitwarden'dan şifre al

```python
resp_bw = urllib.request.urlopen(
    "http://127.0.0.1:8087/object/item/8a95abcd-65dd-4aa5-a255-b4660182d7cf",
    timeout=10
)
data = json.loads(resp_bw.read())
password = data.get("data", {}).get("login", {}).get("password", "")
```

### Step 3: Şifreyi challenge/pwd sayfasına gir

```python
# challenge/pwd target'ını bul
resp = urllib.request.urlopen("http://127.0.0.1:18800/json/list", timeout=5)
targets = json.loads(resp.read())
pwd_target = None
for t in targets:
    if "challenge/pwd" in t.get("url", ""):
        pwd_target = t
        break

ws_url = pwd_target.get('webSocketDebuggerUrl', '')
ws = websocket.create_connection(ws_url, timeout=10, sslopt={"cert_reqs": ssl.CERT_NONE})

# Şifreyi React controlled input'a yaz (nativeValueSetter gerekli!)
expression = f"""
(async () => {{
    const pwField = document.querySelector('input[type="password"]');
    if (!pwField) return 'no password field';

    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype, 'value'
    ).set;
    nativeInputValueSetter.call(pwField, {json.dumps(password)});

    pwField.dispatchEvent(new Event('input', {{ bubbles: true }}));
    pwField.dispatchEvent(new Event('change', {{ bubbles: true }}));

    // Enter tuşu gönder (Google's new login flow)
    pwField.dispatchEvent(new KeyboardEvent('keydown', {{key: 'Enter', keyCode: 13}}));
    return 'password filled, enter sent';
}})()
"""

ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", 
    "params": {"expression": expression, "awaitPromise": True}}))
time.sleep(3)

# Enter key via Input.dispatchKeyEvent (daha güvenilir)
ws.send(json.dumps({"id": 2, "method": "Input.dispatchKeyEvent", "params": {
    "type": "keyDown", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13
}}))
time.sleep(1)
ws.send(json.dumps({"id": 3, "method": "Input.dispatchKeyEvent", "params": {
    "type": "keyUp", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13
}}))
time.sleep(5)
```

### Step 4: Cookie'leri MCP'nin Chrome'una enjekte et

```python
# Keepalive Chrome'dan taze cookie'leri al
req_cookies = {"id": 4, "method": "Network.getAllCookies", "params": {}}
ws.send(json.dumps(req_cookies))
time.sleep(2)
# ... parse response, get cookies array ...

# MCP'nin Chrome'unun portunu bul (ps aux ile)
# Port dinamik — her restartta değişir

resp_mcp = urllib.request.urlopen("http://127.0.0.1:<MCP_PORT>/json/list", timeout=5)
mcp_targets = json.loads(resp_mcp.read())
mcp_target = mcp_targets[0]  # first page target

ws_mcp_url = mcp_target.get('webSocketDebuggerUrl', '')
ws_mcp = websocket.create_connection(ws_mcp_url, timeout=10, sslopt={"cert_reqs": ssl.CERT_NONE})

# Cookie'leri enjekte et
unique_cookies = []
seen = set()
for c in cookies:
    key = (c.get("domain",""), c.get("name",""))
    if key not in seen:
        seen.add(key)
        unique_cookies.append(c)

ws_mcp.send(json.dumps({"id": 5, "method": "Network.setCookies", 
    "params": {"cookies": unique_cookies}}))
time.sleep(1)

# NotebookLM'e yönlendir
ws_mcp.send(json.dumps({"id": 6, "method": "Page.navigate", "params": {
    "url": "https://notebooklm.google.com/notebook/<notebook_id>"
}}))
time.sleep(5)
```

### Step 5: Doğrulama

```python
ws_mcp.send(json.dumps({"id": 7, "method": "Runtime.evaluate", 
    "params": {"expression": "window.location.href"}}))
time.sleep(2)
# Response'da "notebooklm.google.com/notebook/..." görülmeli
```

## Critical Details

### ❌ Buton tıklaması çalışmaz

Google'ın yeni login flow'unda `#passwordNext` butonu bulunamaz.
`[jscontroller="soHxf"]` selector'ı da çalışmaz. **Enter tuşu** kullan.

### ✅ React controlled input

Şifre input'u React tarafından kontrol edilir. Normal `element.value = x`
çalışmaz. `nativeInputValueSetter` kullan:

```javascript
const setter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype, 'value'
).set;
setter.call(element, 'password');
element.dispatchEvent(new Event('input', {bubbles: true}));
```

### 🔑 Bitwarden Item

| Alan | Değer |
|------|-------|
| Item adı | `Google-isimgorulsunn` |
| Item ID | `8a95abcd-65dd-4aa5-a255-b4660182d7cf` |
| Email | `isimgorulsunn@gmail.com` |
| Şifre | Bitwarden vault'ta (bw-serve port 8087) |

### 📍 Sonuç URL'leri

| Sayfa | Anlamı |
|-------|--------|
| `accountchooser` | Cookie'ler tanındı, hesap seçilmeli |
| `challenge/pwd` | Şifre giriş sayfası ✅ doğru yoldayız |
| `notebooklm.google.com` | ✅ BAŞARILI — oturum açık |
| `CookieMismatch` | Aynı profil iki Chrome instance'ı arasında paylaşılmış |

## Troubleshooting

| Sorun | Çözüm |
|-------|-------|
| `challenge/pwd` sayfası gelmiyor | Keepalive Chrome yeniden başlatılmış olabilir, tekrar accountchooser'dan başla |
| Enter tuşu işe yaramadı | Sayfada başka bir challenge (2FA) olabilir. VNC'den kontrol et |
| `Network.setCookies` reddediyor | Cookie array'indeki `sourcePort` gibi alanları çıkarmayı dene |
| Cookie enjeksiyon sonrası hala signin | Cookie'ler geçerli değil. Keepalive'da login başarılı oldu mu kontrol et |
| `CookieMismatch` | Profile_dir farklı bir dizine ayarla, aynı profili iki Chrome kullanmasın |

## Script

`scripts/nlm_cdp_login.py` — bu akışı otomatize eden script.
