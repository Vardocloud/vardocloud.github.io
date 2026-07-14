---
name: notebooklm-cdp-recovery
description: >-
  NotebookLM oturumu dustugunde (CookieMismatch, RotateCookiesPage) CDP ile
  canli Chrome'dan cookie extraction, Google login automation, Himalaya IMAP
  share request handling, ve MCP kurtarma proseduru. 3 katmanli auth: cookie
  extraction → autologin → manuel TOTP. Dual Chrome mimarisi ve hesap yonetimi.
  Routing icin: notebooklm-routing skill.
---

# NotebookLM CDP Recovery — Full Auth Canlandırma Protokolü

İlgili ana skill: `notebooklm-mcp` (mcp) — MCP server kurulumu, CLI referansı, tüm araçlar.

## Ne Zaman Kullanılır

- `mcp_notebooklm_healthcheck` → `authenticated: false` / `needs_auth`
- Keepalive Chrome'larda **RotateCookiesPage** iframe'i görüldüğünde
- Cookie sayısı < 30 veya auth cookie sayısı 0 olduğunda
- `notebooklm-mcp test` timeout verdiğinde

## Ön Kontrol

```python
import json, urllib.request

# Canlı Chrome portlarını tara
for port in [18800, 49537, 52065, 60079]:
    try:
        tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3).read())
        for t in tabs[:3]:
            u = (t.get('url','') or '')[:100]
            if 'notebooklm' in u: print(f"Port {port}: NotebookLM canlı - {u[:80]}")
    except: pass

# Cookie sayısını kontrol et
# 53+ cookie (40+ auth) = sağlam
# 23 cookie (0 auth) = ölü
```

## Katman 1: Canlı Chrome'dan Cookie Çekme (En Kolay)

En kolay yol: NotebookLM açık olan bir Chrome portu bul, cookie'leri çek, MCP profillerine yaz, gateway restart.

```python
import json, urllib.request, websocket, time, pathlib

CDP_PORT = 52065  # Canlı port (49537 veya 52065 genelde)

tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json", timeout=5).read())
page = next((t for t in tabs if t.get("type") == "page"), None)
ws_url = page["webSocketDebuggerUrl"]
ws = websocket.create_connection(ws_url, timeout=15)

# Enable network + page
ws.send(json.dumps({"id":1,"method":"Runtime.enable"}))
ws.send(json.dumps({"id":2,"method":"Page.enable"}))

# Get all cookies
ws.send(json.dumps({"id":3,"method":"Network.getAllCookies"}))
while True:
    resp = json.loads(ws.recv())
    if resp.get("id") == 3:
        cookies = resp.get("result",{}).get("cookies",[])
        break
ws.close()

# MCP formatına çevir
cookies_json = [{
    "name": c["name"], "value": c["value"],
    "domain": c.get("domain",""), "path": c.get("path","/"),
    "secure": c.get("secure",False), "httpOnly": c.get("httpOnly",False),
    "sameSite": c.get("sameSite","Lax"),
    "expirationDate": c.get("expires", time.time()+86400),
    "hostOnly": not (c.get("domain","") or "").startswith(".")
} for c in cookies]

# Legacy + Pro profillerine yaz
for profile in ["legacy", "pro"]:
    p = pathlib.Path.home() / ".notebooklm-mcp-cli" / "profiles" / profile / "cookies.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(cookies_json, f, indent=2)
```

### Gateway Restart

```bash
# Docker içinde çalışıyorsan gateway process'ini öldür (entrypoint restart eder)
kill $(cat ~/.hermes/gateway.pid)

# Docker dışındaysan
docker restart vanatis-hermes
```

**ÖNEMLİ**: Gateway restart session'ı keser. Edel yeni mesaj atınca test et.

## Katman 2: Autologin Script (nb_autologin.py)

Cookie'ler tamamen öldüyse Bitwarden'dan credential alıp otomatik login dene.

```bash
# Lock files temizle (stale lock varsa)
rm -f ~/.hermes/logs/nb_autologin.lock ~/.hermes/logs/nb_keepalive.lock

# Pro hesap (kenshin4155@gmail.com)
python3 ~/.hermes/scripts/nb_autologin.py --profile pro

# Legacy hesap (isimgorulsunn@gmail.com)
python3 ~/.hermes/scripts/nb_autologin.py --profile legacy
```

**Not**: Bu script `nb_keepalive.py` tarafından fallback olarak çağrılır ama lock varsa atlar.

## Katman 3: Manuel CDP Login (2FA Dahil)

Autologin "Too many failed attempts" verirse, MCP'nin temiz Chrome'unda manuel CDP login dene.

### 3a — Credential'ları Al

```python
BW_SERVE = "http://127.0.0.1:8087"
items_req = urllib.request.Request(f"{BW_SERVE}/list/object/items")
with urllib.request.urlopen(items_req, timeout=10) as r:
    items = json.loads(r.read())

username = password = totp_secret = None
for item in items.get("data",{}).get("data",[]):
    name = item.get("name","").lower()
    if name == "google-pro":  # kenshin4155
        data = json.loads(urllib.request.urlopen(urllib.request.Request(f"{BW_SERVE}/object/item/{item['id']}")).read())
        login = data["data"]["login"]
        username = login["username"]
        password = login["password"]
        totp_secret = login.get("totp")
        break
```

### 3b — Login Flow

```python
import websocket, time, pyotp

CDP_PORT = 60079  # MCP'nin Chrome portu (yeni MCP server başlatınca değişir)

tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json", timeout=5).read())
page = next((t for t in tabs if t.get("type") == "page"), None)
ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=15)

def send(method, params=None):
    # Send CDP command and wait for response
    ...

def ev(expr):
    # Evaluate JS in page
    ...

# 1. Navigate to clean sign-in
send("Page.navigate", {"url": "https://accounts.google.com/signin/v2/identifier"})

# 2. Email → identifierId'ye yaz, Next'e tıkla
ev("document.querySelector('#identifierId')?.focus()")
send("Input.insertText", {"text": username})
ev("document.querySelector('#identifierNext')?.click()")

# 3. Password → input[type=password]'a yaz, passwordNext'e tıkla
ev("document.querySelector('input[type=password]')?.focus()")
send("Input.insertText", {"text": password})
ev("document.querySelector('#passwordNext')?.click()")

# 4. 2FA → div[role=link] içinde "Google Authenticator" seçeneğini bul
ev("""
document.querySelectorAll('div[role=link]').forEach(el => {
    if(el.innerText.includes('Authenticator')) el.click();
})
""")

# 5. TOTP → totpPin input'una kodu yaz, "Next" butonuna tıkla
code = pyotp.TOTP(totp_secret).now()
ev(f"document.getElementById('totpPin').value = '{code}'")
ev("""
var evt = new Event('input', {bubbles: true});
document.getElementById('totpPin').dispatchEvent(evt);
""")
Array.from(document.querySelectorAll('button')).find(b => b.innerText === 'Next')?.click()
```

### 3c — TOTP Detayları

TOTP sayfası (`/challenge/totp`):
- Input: `<input type=tel id=totpPin>`
- `Input.insertText` **append** eder, değeri set etmez!
- **Çözüm**: Doğrudan JavaScript ile `value = '...'` set et, input event'i dispatch et
- "Next" butonunu `button` etiketi içinde text "Next" ile bul

**Önemli**: TOTP kodu 30sn geçerli. Hızlı ol.

## Cookie'leri MCP Chrome'una Enjekte Etme

Gateway restart almazsa (session korunması gerekirse), canlı Chrome'dan çekilen cookie'leri doğrudan MCP'nin Chrome'una enjekte et:

```python
# 1. Kaynak Chrome'dan cookie'leri al (port 47407 gibi)
ws.send(json.dumps({"id":50,"method":"Network.getAllCookies"}))

# 2. Hedef Chrome'da (port 57919/60079) Network.clearBrowserCookies
ws2.send(json.dumps({"id":250,"method":"Network.clearBrowserCookies"}))

# 3. Network.setCookie ile tek tek set et
for c in auth_cookies:
    ws2.send("Network.setCookie", {
        "url": f"{'https' if c['secure'] else 'http'}://{c['domain'].lstrip('.')}{c['path']}",
        "name": c["name"], "value": c["value"],
        "domain": c["domain"], "path": c.get("path","/"),
        "secure": c.get("secure",False),
        "httpOnly": c.get("httpOnly",False),
        "sameSite": c.get("sameSite","Lax")
    })
```

## Notebook Erişim İzni Sorunu

Cookie'ler doğru olsa bile notebook **erişim izni** gerektirebilir:
- Sayfa: `https://notebooklm.google.com/accessrequest/<notebook_id>`
- Sebep: Hesabın (ör. kenshin4155) notebook'a erişim yetkisi yok
- Çözüm 1: Notebook sahibi (isimgorulsunn) → Erişim izni vermeli
- Çözüm 2: MCP'yi isimgorulsunn hesabıyla kullan (legacy profil)
- "Erişim iste" butonu → tıklanırsa sahibine email bildirimi gider

**Tespit**: Keepalive Chrome'da notebook çalışıyorsa ama MCP Chrome'unda "accessrequest" sayfası gösteriyorsa → erişim izni sorunu.

## Account Management (Dual Chrome Architecture — v5.0)

Two separate Chrome instances, one per Google account. Each has its own CDP port:

| Instance | Port | Account | MCP Profile |
|----------|------|---------|-------------|
| Chrome 1 | 18800 | kenshin4155 | pro (mcp_notebooklm_*) |
| Chrome 2 | 18801 | isimgorulsunn | legacy (mcp_notebooklm_legacy_*) |

No account switching needed — both run simultaneously. Cookies are extracted from each port independently by the keepalive cron.

**Routing rules:** `notebooklm-routing` skill has the full decision tree.

### Pro vs Legacy Account Identities

| Account | Email | TOTP | Key Notebooks |
|---------|-------|------|---------------|
| pro | kenshin4155 | Yes | Vanitas AI, APA Monitor 2026 |
| legacy | isimgorulsunn | No (App Password for IMAP) | Ekonomi Zekasi, BDT, Hafiza Arsivi |

**ÖNEMLİ**: notebook'u hangi hesabın kullanacağını BİL. `Ekonomi Zekası` isimgorulsunn'a ait.
kenshin4155 ile direkt URL'den erişmek "Access Request" sayfasına düşürür.

### Share Request Email'ini Himalaya ile Bulma

Kullanıcı "Erişim iste" butonuna tıklayınca Google, notebook sahibine email gönderir.
Bu email'i **Himalaya IMAP** ile okuyup onay bağlantısını bul:

```bash
# 1. Son emailleri listele (isimgorulsunn inbox)
himalaya envelope list --page-size 10 --output json

# 2. "Share Request" email'ini bul ve oku
himalaya message read <ID>

# 3. Email içindeki onay linkini al (c.gle kısa linki)
himalaya message export <ID> --full | grep -oP 'https?://[^"<> ]+' | head -5
```

**Not**: `c.gle` linkleri Google tracking linkleridir, curl ile 404 döner.
Tarayıcıda (CDP) açılması gerekir.

Detaylı iş akışı için: `references/share-request-email.md`

### Notebook'a Ana Sayfadan Erişmeyi Dene

Direkt URL (`/notebook/{id}`) access request veriyorsa, önce NotebookLM
ana sayfasına (`notebooklm.google.com`) git:
- **"Benimle paylaşılanlar"** → tıkla, açılır
- **"Not defterlerim"** → direkt erişimin var
- Hiçbir yerde yoksa → access request onaylanmamış

### Account Switching via URL

NotebookLM supports multiple accounts via the `authuser` URL parameter. However,
**this does NOT work for cookie extraction** — Google cookies are domain-scoped
and a single Chrome only holds one active account's session at a time. 

For real multi-account extraction, use the dual Chrome architecture (separate
`user-data-dir` + CDP port per account). See Account Management section above.

### Bitwarden'dan Credential Alma

```python
BW_SERVE = "http://127.0.0.1:8087"
items_req = urllib.request.Request(f"{BW_SERVE}/list/object/items")

with urllib.request.urlopen(items_req, timeout=10) as r:
    items = json.loads(r.read())

for item in items.get("data",{}).get("data",[]):
    name = item.get("name","").lower()
    if "google" in name:  # google-pro (kenshin4155) veya google-isimgorulsunn
        data = json.loads(urllib.request.urlopen(
            urllib.request.Request(f"{BW_SERVE}/object/item/{item['id']}"), timeout=10).read())
        login = data["data"]["login"]
        print(f"  {name}: {login['username'][:3]}... | pwd={bool(login.get('password',''))} | totp={bool(login.get('totp',''))}")
```

**İsim farkı**: Bitwarden'da `google-pro` (küçük harf) ve `Google-isimgorulsunn` (büyük G).
Case-sensitive arama yaparken dikkat et.

### Autologin Account Chooser Loop (Yaygın Sorun)

`nb_autologin.py` bazen `/challenge/pwd` sayfasında account chooser elementi
(`data-identifier`) bulup döngüye girer — tıklar ama sayfa ilerlemez.

**Belirtiler**: Her 3sn'de bir url değişir ama hep `challenge/pwd` sayfasında kalır.
Title: "Welcome".

**Sebep**: Google'ın "Welcome" sayfası account chooser gibi görünür ama `data-identifier`
click'i login'i ilerletmez. Sayfa passkey veya Google Prompt gösteriyordur.

**Çözüm**:
1. "Try another way" butonunu dene
2. Alternatif: MCP Chrome'unu temizle, **yeni bir tab** aç, farklı URL'den başla
3. Eğer hala olmuyorsa → Google rate-limit ("Too many failed attempts") — 30-60dk bekle
4. Diğer hesabı dene (pro yerine legacy veya tersi)

## MCP Server Lifecycle

Gateway restart edilince:
1. Eski MCP server process'i ölür
2. Gateway yeni MCP server başlatır (genelde gecikmeli, 30-60sn)
3. Yeni MCP server kendi Chrome'unu açar (yeni port)
4. Yeni Chrome, `chrome_profile_notebooklm` profilindeki cookie'leri okur
5. Eğer profile taze cookie'ler kaydedilmişse → auth başarılı

**Not**: MCP server kendi kendine restart olmaz. Gateway management katmanı restart eder veya Edel yeni session açar.

## Notebook Hesap Geçişi (Account Switching)

NotebookLM birden fazla Google hesabı arasında geçiş yapmayı destekler.
Eğer Chrome profiline iki hesap da giriş yapmışsa sağ üst avatar'dan geçiş yapılabilir.
Keepalive Chrome'da (port 18800) her iki hesap da aynı profilde tutulur.

**Notebook erişim sorunu**: `1d205988-6c7f-41e8-8079-dd579444cc1e` (Ekonomi Zekası)
isimgorulsunn hesabına ait. kenshin4155 ile direkt URL'den erişmek "Access Request" sayfasına
düşürür. Çözüm: NotebookLM ana sayfasına git, "Benimle paylaşılanlar"da görünüyorsa oradan aç.
Veya isimgorulsunn'un kenshin4155'e Düzenleyici yetkisi vermesi gerekir.

NOT: Tek bir Chrome'da iki farklı Google hesabına aynı anda login olunca NotebookLM
hesap değiştirme özelliği çalışır. nb_autologin.py her iki profili de ayrı ayrı dener.

## Combined Google Sign-in Form

Google bazen email (`#identifierId`) ve password (`input[type=password]`) alanlarını
**aynı sayfada** gösterir. Bu durumda:
- `#passwordNext` yoktur — submit `#identifierNext` ile yapılır
- Önce password alanını JS ile doldur (`el.value = '...'`), sonra `#identifierNext`'e tıkla
- Submit olmuyorsa anti-bot engeli vardır — farklı Chrome profili dene

## Cookie'leri Chrome Cookies SQLite DB'ye Kaydetme

Gateway restart sonrası yeni MCP Chrome'unun eski cookie'leri okuması için:

```python
import sqlite3, pathlib, time
profile_path = pathlib.Path.home() / ".hermes" / "chrome_profile_notebooklm"
cookies_db = profile_path / "Default" / "Cookies"
conn = sqlite3.connect(str(cookies_db))
conn.execute("DELETE FROM cookies WHERE host_key LIKE '%google%' OR host_key LIKE '%notebooklm%'")
for c in fresh_cookies:
    domain = c.get("domain","").lstrip(".")
    if "google" in domain or "notebooklm" in domain:
        conn.execute(
            "INSERT INTO cookies (host_key,name,value,path,expires_utc,is_secure,is_httponly,has_expires,is_persistent) VALUES (?,?,?,?,?,?,?,1,1)",
            (domain, c["name"], c["value"], c.get("path","/"),
             int(c.get("expires", time.time()+86400) * 1000000),
             1 if c.get("secure") else 0, 1 if c.get("httpOnly") else 0)
        )
conn.commit(); conn.close()
```

## Keepalive Chrome Otomatik Kurtarma

`nb_keepalive.py` her 20dk'da bir Chrome CDP'yi kontrol eder, ölüyse restart atar,
cookie'leri tazeler, CDP başarısızsa autologin dener.

**Uyarı**: "✅ Cookies refreshed successfully" mesajı yanıltıcı olabilir — RotateCookiesPage
yüzünden cookie'ler geçersiz olsa bile bu mesajı basar. Cookie sayısı + auth cookie oranını
kontrol et (53/42/41 = sağlam, 23/18/0 = ölü).

## Pitfalls

- **Port 18800** keepalive ana Chrome'udur ama RotateCookiesPage'de takılabilir
- **49537/52065** genelde canlı NotebookLM session'ına sahiptir (keepalive restart'ları)
- **RotateCookiesPage iframe'i** ana oturumu etkilemez — sadece arkaplan cookie rotasyonu
- **Cookie extraction'dan sonra gateway restart** şarttır (MCP bellekteki cookie'leri yeniden okumaz)
- **TOTP input'u** `type=tel` — Input.insertText append eder; value'yu JS ile set et (el.value='...')
- **Google "Too many failed attempts"** — aynı Chrome'da çok deneme yaparsan 1 saat bloke
- **MCP'nin Chrome portu** her restartta değişir — grep -oP 'remote-debugging-port=\K[0-9]+'
- **Gateway restart** = session kesilir. Edel'e bildir.
- **isimgorulsunn hesabında TOTP yok** — phone verification veya Google Prompt gerekebilir
- **Sign-in formu birleşik olabilir** — #passwordNext yoksa #identifierNext dene
- **Keepalive "successful" yanıltır** — cookie count + auth count kontrol et
