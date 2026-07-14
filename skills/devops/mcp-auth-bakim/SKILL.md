---
name: mcp-auth-bakim
description: "NotebookLM auth bakımı (LEGACY — eski pip v2.0.11 sistemi). GÜNCEL SİSTEM İÇİN → skill_view('notebooklm-pipeline')."
version: 2.2.0
author: Vanitas
tags: [notebooklm, mcp, auth, legacy, deprecated]
---

# MCP Auth Bakım — 🔴 LEGACY (12 Tem 2026)

**⚠️ BU SİSTEM GÜNCEL DEĞİLDİR.** Aşağıdaki içerik eski `notebooklm-mcp v2.0.11` (pip) paketini anlatır.

## Güncel Sistem

| Eski (bu skill) | Yeni |
|----------------|------|
| `pip install notebooklm-mcp` (v2.0.11, buggy) | `uv tool install notebooklm-mcp-cli` (v0.8.6+) |
| undetected-chromedriver | CDP-based auth (keepalive Chrome) |
| `_ensure_client()` auth bug → authfix wrapper | Auth düzgün çalışır |
| Tek profil | Multi-profile: legacy + pro |

**Güncel auth setup için:**
```
skill_view(name="notebooklm-pipeline", file_path="references/mcp-server-setup.md")
skill_view(name="notebooklm-pipeline", file_path="references/keepalive-mcp-bridge.md")
```

## Keepalive Kuralı (Hâlâ Geçerli)

Keepalive Chrome (port 18800) auth'u canlı tutar. Her 20 dk'da bir:
1. CDP cookie extraction
2. `sync_mcp_auth()` ile profillere yaz

Keepalive Chrome'u asla habersiz kapatma. Aşağıdaki eski bölümler legacy referanstır.

---

## 🔴 KRİTİK KURAL: KEEPALIVE CHROME'U ASLA HABERSİZ KAPATMA

**5 Tem 2026 — Edel'in net talimatı:** Keepalive Chrome (port 18800) 7/24 çalışan bir sistem bileşenidir. Habersiz kapatıldığında auth session kaybolur ve Edel'in tekrar VNC'den giriş yapması gerekir.

- **ASLA** `kill`/`pkill` ile keepalive Chrome'u sonlandırma
- Kapatman gerekiyorsa **ÖNCE Edel'e sor**, onay al
- Kapalıysa: `start-chrome-keepalive.sh` ile geri başlat (background=true)
- İhlal (5 Tem 2026): habersiz kapatıldı, auth kayboldu — bir daha asla

---

## 🔴 KRİTİK KURAL: MCP'Yİ YENİDEN KURMA — KEEPALIVE KULLAN

**Edel'in net talimatı: "Kurmana gerek yok. Compass kurallarını uygula, notebooklm zaten var."**

NotebookLM auth'u keepalive tarafından yönetilir. MCP çalışmıyorsa veya auth sorunu varsa:
1. **ÖNCE** `python3 ~/.hermes/scripts/nb_keepalive.py` çalıştır (compass kuralı)
2. **Keepalive'nin Chrome CDP'sini kullan** (port 18800) — MCP'yi yeniden yapılandırma
3. **MCP'yi sadece Edel açıkça istediğinde yeniden yapılandır**

| Yanlış (YAPMA) | Doğru (YAP) |
|----------------|-------------|
| `hermes mcp remove notebooklm-mcp && hermes mcp add ...` | `python3 ~/.hermes/scripts/nb_keepalive.py` |
| npm install -g notebooklm-mcp | Keepalive CDP kullan (port 18800) |
| MCP Chrome profiline cookie kopyala | Keepalive profili zaten auth'lu |

---

## 🔴 KRİTİK: İki Ayrı Chrome Profili Var

| Sistem | Chrome Profili | Auth Yönetimi |
|--------|---------------|---------------|
| **Keepalive** (nb_keepalive.py) | `~/.hermes/chrome_profile_notebooklm` | CDP + BWS, 30dk'da bir tazeler |
| **MCP v2.0** (Node.js) | `~/.local/share/notebooklm-mcp/chrome_profile/` | `setup_auth`/`re_auth` ile login, headless çalışır |

**⚠️ BU İKİ PROFİL AYRI DIR.** Keepalive'in tazelediği cookie'ler MCP v2.0 profiline otomatik geçmez.

### 🔐 Cookie Şifreleme Anahtarı Farkı (KRİTİK)

Bu, MCP auth sorunlarının **en kritik sebebidir.** İki Chrome binary'si cookie'leri OS Crypt ile kendi anahtarlarıyla şifreler:

| Chrome | Binary | Cookie Şifreleme |
|--------|--------|-----------------|
| Keepalive | `/usr/lib/chromium/chromium` (sistem) | Kendi OS Crypt anahtarı |
| MCP v2.0 | `~/.cache/ms-playwright/.../chrome-headless-shell` (bundled) | **Farklı** OS Crypt anahtarı |

Keepalive'in Chromium'u cookie'leri kendi anahtarıyla şifreler (`encrypted_value`). MCP'nin bundled Chromium'u bu anahtarı **bilmez**, bu yüzden cookie'leri çözemez ve AccountChooser'a yönlenir.

#### ✅ ÇÖZÜM: Chromium Binary Uyumluluğu (executablePath Patch)

**En kalıcı ve tek doğru çözüm:** MCP'nin, keepalive ile aynı sistem Chromium binary'sini kullanmasını sağlamak.

**Nasıl çalışır:**
1. MCP `dist/session/shared-context-manager.js` içinde `chromium.launchPersistentContext(userDataDir, options)` çağrısı yapar
2. `options`'a `executablePath: "/usr/bin/chromium"` eklenirse, MCP bundled Chromium yerine sistem Chromium'unu kullanır
3. İki Chrome aynı binary → aynı OS Crypt anahtarı → cookie'ler uyumlu

**Kurulum:**
```bash
# 1. Patch uygula (otomatik script)
bash ~/.hermes/scripts/mcp-chromium-patch.sh

# 2. Veya manuel — dist/session/shared-context-manager.js'de:
#    const nbChromiumPath = process.env.NOTEBOOKLM_CHROMIUM_PATH;
#    const baseLaunchOptions = {
#        ...(nbChromiumPath && { executablePath: nbChromiumPath }),
#        ...

# 3. Wrapper'a ekle (~/.local/bin/notebooklm-mcp-wrapper.sh):
export NOTEBOOKLM_CHROMIUM_PATH="/usr/bin/chromium"

# 4. npm update sonrası patch sıfırlanırsa:
bash ~/.hermes/scripts/mcp-chromium-patch.sh  # yeniden uygular
```

**Patch sonrası:**
- ✅ Cookie şifreleme anahtarları uyumlu
- ✅ SQLite seviyesinde cookie kopyalama çalışır
- ✅ storageState.json ile cookie transferi çalışır
- ✅ MCP profili ayrı kalır (symlink gerekmez, çakışma riski yok)

**⚠️ Profil symlink YAPMA.** İki Chrome farklı profil kullanmalı (`--user-data-dir`). Aynı profil = cookie çakışması + Singleton lock. OpenCode modeli Windows'ta bu hatayı yaptı ve profilleri ayırdı.

**⚠️ MCP `get_health: false` — SEBEBİ AUTH BUG (12 Tem 2026).** `notebooklm-mcp v2.0.11`'de `_ensure_client()` browser'ı başlatır ama `authenticate()`'i **hiç çağırmaz**. Bu yüzden `_is_authenticated` her zaman `False` kalır. Browser'ın cookie'leri geçerli olsa bile tüm tool çağrıları "Not authenticated or browser not ready" hatası verir. **Bu lazy init değil, koddaki bug'dır.** Çözüm: `references/python-v2.0.11-auth-bug.md`'deki authfix wrapper'ı kullan. Gerçek auth kontrolü için `ask_question` kullan.
- ✅ CDP cookie'lerini MCP profiline `value` + `encrypted_value` (value'nun bytes hali) olarak yazmak
- ✅ **executablePath override** — MCP'ye sistem Chromium'unu kullandırtmak (kök neden çözümü, `scripts/mcp-chromium-patch.sh`)

### 🔗 Chrome Profil Symlink (Hızlı Çözüm)

MCP'nin kendi Chrome profili auth sorunu yaşadığında, keepalive'in halihazırda auth'lu profilini kullanması için symlink oluştur:

```bash
# MCP mevcut profilini yedekle
mv ~/.local/share/notebooklm-mcp/chrome_profile ~/.local/share/notebooklm-mcp/chrome_profile.bak

# Keepalive profiline symlink yap
ln -sf ~/.hermes/chrome_profile_notebooklm ~/.local/share/notebooklm-mcp/chrome_profile
```

**⚠️ Uyarılar:**
- İki Chrome aynı profili aynı anda kullanırsa lock çakışması olabilir. Keepalive çalışırken MCP'yi kullanmak genelde sorunsuzdur (Playwright read-only açar), ama riskli operasyonlarda önce keepalive'i durdur.
- **🚫 KRİTİK: Profil symlink'ten kaçının.** İki process aynı profil dizinine yazarsa cookie'ler karışır, session'lar çapraz gider (OpenCode Windows'ta doğrulandı). Bunun yerine **executablePath override** kullanın (aşağıdaki bölüme bak) — aynı binary, ayrı profiller, cookie'ler karışmaz.
- Symlink geri almak: `rm ~/.local/share/notebooklm-mcp/chrome_profile && mv ~/.local/share/notebooklm-mcp/chrome_profile.bak ~/.local/share/notebooklm-mcp/chrome_profile`
- npm update/upgrade symlink'i etkilemez — kalıcı çözümdür.

### 👥 Çok Profilli Mimari (pro + legacy)

Keepalive iki Google hesabını yönetir (nb_keepalive.py):

| Profil | Hesap | Açıklama |
|--------|-------|----------|
| **pro** | `kenshin4155` | Ana hesap — notebook'ların sahibi |
| **legacy** | `isimgorulsunn` | İkincil hesap |

Her iki profil sırayla kontrol edilir, TOTP ile auto-login yedeklenir. TOTP secret'ları: `~/.hermes/.nb_totp_secret_pro`, `~/.hermes/.nb_totp_secret_legacy`.

**⚠️ ÖNEMLİ:** Keepalive Chrome'u hangi profille çalışıyorsa sadece o profilin notebook'larına erişir. URL'de `?authuser=0` aktif hesabı gösterir. Erişim yoksa sayfa `/accessrequest/`'e yönlenir. Bu bir auth sorunu değil, notebook izin sorunudur.

**🔑 authuser Parametresi:** MCP'nin library.json'ındaki notebook URL'lerine doğru `authuser` parametresi eklenmelidir, yoksa yanlış profille açılır:
- `authuser=0` → birinci hesap (genelde legacy/isimgorulsunn)
- `authuser=1` → ikinci hesap (genelde pro/kenshin4155)

Tespit: Keepalive Chrome'da `Page.navigate` ile notebook URL'ine git. `/accessrequest/`'e yönleniyorsa yanlış hesap. Farklı `authuser` değerleri dene. Doğru hesap bulunca URL'yi library.json'da güncelle.

### 🍪 Cookie Kopyalama (MCP ↔ Keepalive)

İki Chrome aynı major sürümdeyse (Chromium 149.x) cookie SQLite şeması **uyumludur**. `cp` ile değil, SQL INSERT/UPDATE ile kopyalanabilir:

```python
import sqlite3
# Chrome 149 şeması: 20 kolon, creation_utc NOT NULL
src = sqlite3.connect("~/.hermes/chrome_profile_notebooklm/Default/Cookies")
dst = sqlite3.connect("~/.local/share/notebooklm-mcp/chrome_profile/Default/Cookies")
# Google/NotebookLM cookie'lerini SELECT → INSERT OR UPDATE
```

**⚠️ Sınırlama:** Hangi profilin cookie'sini kopyalarsan o profilin notebook'larına erişirsin. Legacy'den kopyalarsan legacy notebook'larına, pro'dan kopyalarsan pro notebook'larına. Sorun auth değil, notebook izinleridir.

---

### 🔧 Chromium Binary Uyumluluğu (executablePath — Kök Neden Çözümü)

Cookie şifreleme sorununun **kök nedeni**: MCP bundled Playwright Chromium'u (`~/.cache/ms-playwright/.../chrome-headless-shell`) kullanır, keepalive ise sistem Chromium'unu (`/usr/bin/chromium`). İkisi farklı **OS Crypt anahtarına** sahip olduğu için keepalive'de şifrelenen cookie'ler MCP'de çözülemez.

**Çözüm:** MCP'ye `executablePath` override ile sistem Chromium'unu kullandırtmak. Böylece:
- MCP ve keepalive **aynı binary** → **aynı OS Crypt anahtarı** → cookie'ler uyumlu ✅
- Profiller **ayrı kalır** → cookie karışması olmaz ✅
- Bir kere `re_auth` → MCP kendi profilinde kalıcı cookie üretir ✅

#### Patch Uygulama

```bash
bash ~/.hermes/scripts/mcp-chromium-patch.sh
```

Bu script:
1. `shared-context-manager.js`'e `executablePath` override ekler (`NOTEBOOKLM_CHROMIUM_PATH` env var'ından okur)
2. Wrapper'a `NOTEBOOKLM_CHROMIUM_PATH=/usr/bin/chromium` env var'ını ekler
3. npm update sonrası patch sıfırlanırsa tekrar çalıştırılır

#### Nasıl Çalışır (Kaynak Kod)

MCP `dist/session/shared-context-manager.js`'de `chromium.launchPersistentContext()` çağrısına `executablePath` parametresi eklenir:

```javascript
const nbChromiumPath = process.env.NOTEBOOKLM_CHROMIUM_PATH;
const baseLaunchOptions = {
    ...(nbChromiumPath && { executablePath: nbChromiumPath }),
    headless: shouldBeHeadless,
    // ...
};
```

#### Browser Channel Mekanizması

`chromium-fallback.js`'de iki kanal var:

| Kanal | Etki | Ne Zaman Çalışır |
|-------|------|-----------------|
| `BROWSER_CHANNEL=chrome` (default) | Sistem Chrome'unu dener | Sistemde Chrome yoksa → `isChannelFailure` → bundled Chromium'a fallback |
| `NOTEBOOKLM_CHROMIUM_PATH` (patch) | `executablePath` override | **Her zaman** — bundled'ı tamamen bypass eder |

Patch uygulandığında `BROWSER_CHANNEL`'dan bağımsız çalışır. İkisi de set edilirse `executablePath` önceliklidir.

#### npm Update Koruma

`npm install -g notebooklm-mcp@latest` yapıldığında dist dosyaları sıfırlanır. Tekrar uygulamak için:

```bash
bash ~/.hermes/scripts/mcp-chromium-patch.sh
```

---

## MCP v2.0 (Node.js — Güncel)

### Binary Yönetimi

MCP v2.0 bir npm global paketidir:
- Kurulum: `npm install -g notebooklm-mcp`
- Binary: `~/.npm-global/bin/notebooklm-mcp`
- Wrapper: `~/.local/bin/notebooklm-mcp-wrapper.sh`

Wrapper içindeki binary yolu bozulursa iki fix seçeneği var:

**🔵 SEÇENEK 1 — Symlink (ÖNERİLEN)**
Wrapper zaten `~/.local/bin/notebooklm-mcp`'yi çağırdığı için buraya symlink koymak yeterli:
```bash
ln -sf /home/ubuntu/.npm-global/bin/notebooklm-mcp /home/ubuntu/.local/bin/notebooklm-mcp
```
**Avantaj:** npm update sonrası wrapper'ın üzerine yazılsa bile symlink bozulmaz. Wrapper'ın exec satırı dokunulmadan kalır.

**🔵 SEÇENEK 2 — Exec line düzenleme**
Doğrudan binary'e yönlendir:
```bash
# YANLIŞ (binary yok):
# exec /home/ubuntu/.local/bin/notebooklm-mcp "$@"
# DOĞRU:
# exec /home/ubuntu/.npm-global/bin/notebooklm-mcp "$@"
```
**⚠️ Dezavantaj:** npm update/upgrade wrapper'ın üzerine yazarsa fix kaybolur.

Wrapper env var'ları:
```bash
export NOTEBOOKLM_COOKIES_PATH="/home/ubuntu/.notebooklm-mcp-cli/auth.json"
export NOTEBOOKLM_PERSISTENT_SESSION="true"
```

### Playwright Browser'lar

Paket kurulumu browser'ları indirmez. Ayrıca yüklenmeli:
```bash
cd /home/ubuntu/.npm-global/lib/node_modules/notebooklm-mcp
npx playwright install chromium
```
Browser'lar `~/.cache/ms-playwright/` altına iner.

### Hermes'e Ekleme

```bash
printf "Y\nY\n" | hermes mcp add notebooklm-mcp --command /home/ubuntu/.local/bin/notebooklm-mcp-wrapper.sh
```
İnteraktif soruları (overwrite + enable all) auto-yanıtlamak için `printf "Y\nY\n"` gerekir.

**Not:** "Start a new session to use these tools" mesajı normaldir — tool'lar yeni session'da görünür. Mevcut session'da `delegate_task` ile subagent'lar kullanabilir.

### Auth İşlemi (İlk ve Tek Seferlik)

MCP v2.0 auth, kendi Chrome profili üzerinden yapılır. `setup_auth` tool'u bir kere Chrome açar, login yapılır, cookie'ler profile kaydedilir:

```bash
# Sanal display'de (headless Linux'da display yoksa):
Xvfb :99 -screen 0 1024x768x24 -ac &
DISPLAY=:99 /home/ubuntu/.npm-global/bin/notebooklm-mcp
# Sonra ayrı bir terminal'den JSON-RPC ile setup_auth çağır
```

Auth durumu kontrolü: `get_health` → `authenticated: true/false`

### VNC Üzerinden re_auth (Doğrulanmış)

MCP'nin `re_auth` tool'u Google AccountChooser'ı açar — headless'ta görünmez kalır. VNC üzerinden headed modda yapılmalı:

```bash
# 1. VNC stack'in çalıştığını kontrol et
# Xvfb :99 (sanal display)
# x11vnc -display :99 -rfbport 5900 (VNC sunucusu)
# websockify 6080 127.0.0.1:5900 (noVNC web arayüzü)

# 2. MCP'yi headed modda başlat (timeout 10dk — re_auth bekler)
HEADLESS=false DISPLAY=:99 timeout 600 /home/ubuntu/.local/bin/notebooklm-mcp-wrapper.sh <<'EOF'
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"re_auth","arguments":{}}}
EOF
```

**⚠️ Timeout & Recovery:**
- `re_auth` 10 dakikaya kadar bekler ("Waiting for login (up to 10 minutes)")
- Timeout yerse (exit code 124) → MCP process'i temizlenmeli:
  ```bash
  pkill -f "notebooklm-mcp.*re_auth" 2>/dev/null; pkill -f "timeout 600.*notebooklm-mcp" 2>/dev/null
  ```
- Timeout sonrası cookie'ler profile kaydedilmez → tekrar denenmeli
- Başarılı olursa MCP otomatik kapanır, cookie'ler profile kaydedilir

**⚠️ noVNC Mobil Uyarısı:**
- `trycloudflare.com` domain'i bazı mobil ağlarda (TT, Turkcell, Vodafone) erişilemeyebilir
- Erişilemezse: bilgisayardan bağlanmayı öner, veya Edel müsait olana kadar bekle
- noVNC'yi kullanmadan önce tunnel URL'sini test et:
  ```bash
  curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:6080/vnc.html
  ```
- Cloudflared tunnel açık değilse: `cloudflared tunnel --url http://127.0.0.1:6080 --no-autoupdate`

**⚠️ re_auth öncesi kritik adımlar:**
- Keepalive Chrome'u **KAPATMA** — sadece MCP'nin browser'ı görünsün istiyorsan Edel'e sor
- noVNC'de sadece MCP'nin AccountChooser sayfası görünmeli
- Karışıklık olursa Edel doğru browser'da giriş yapamayabilir

**⚠️ Not:** `re_auth` "Waiting for login (up to 10 minutes)" mesajıyla bekler. VNC'den login yapılana kadar timeout'a düşer. Login tamamlanınca cookie'ler profile kaydedilir ve bir daha `re_auth` gerekmez.

### 💻 CDP ile Doğrudan Sorgu Gönderme (MCP ask_question Çalışmadığında)

MCP'nin `ask_question`'ı timeout yediğinde veya boş response döndüğünde, keepalive CDP üzerinden NotebookLM'e doğrudan sorgu gönderilebilir.

**İki yaklaşım:**

### Yaklaşım 1: Sleep-based (basit, hızlı, bazen kararsız)

```python
import websocket, json, time, urllib.request
# Yeni sekme aç
req = urllib.request.Request("http://127.0.0.1:18800/json/new", method="PUT")
page = json.loads(urllib.request.urlopen(req).read())
ws = websocket.create_connection(page["webSocketDebuggerUrl"])
# Navigate + sleep
ws.send(json.dumps({"id":1,"method":"Page.navigate","params":{"url":"https://notebooklm.google.com/notebook/<UUID>?authuser=1"}}))
time.sleep(10)
# Query
ws.send(json.dumps({"id":2,"method":"Runtime.evaluate","params":{"expression":"document.querySelector('textarea.query-box-input')?...'}}))
ws.recv(); time.sleep(1)
ws.close()
```

### Yaklaşım 2: Event-driven (önerilen — daha güvenilir)

```python
import websocket, json, time, urllib.request

req = urllib.request.Request("http://127.0.0.1:18800/json/new", method="PUT")
page = json.loads(urllib.request.urlopen(req).read())
ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=30)

# 1. Page event'lerini enable et
ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
ws.send(json.dumps({"id": 2, "method": "Runtime.enable"}))
time.sleep(0.5)
ws.settimeout(0.3)
try:
    while True: ws.recv()  # flush
except: pass

# 2. Navigate
ws.send(json.dumps({"id": 3, "method": "Page.navigate", "params": {
    "url": "https://notebooklm.google.com/notebook/<UUID>?authuser=1"
}}))

# 3. frameNavigated event'ini bekle (sleep yerine event-driven)
ws.settimeout(15)
loaded = False
while not loaded:
    try:
        r = json.loads(ws.recv())
        if r.get("method") == "Page.frameNavigated":
            url = r.get("params",{}).get("frame",{}).get("url","")
            if "notebooklm" in url or "signin" in url:
                loaded = True
                time.sleep(5)
    except:
        break

# 4. JS evaluate (artık sayfa hazır)
def js(expr):
    mid = int(time.time()*1000000)
    ws.send(json.dumps({"id": mid, "method": "Runtime.evaluate",
                         "params": {"expression": expr, "returnByValue": True}}))
    ws.settimeout(10)
    while True:
        try:
            d = json.loads(ws.recv())
            if d.get("id") == mid:
                return d.get("result",{}).get("result",{}).get("value","")
        except:
            break
    return ""

title = js("document.title")
print(f"Title: {title}")
ws.close()
```

Referans: `references/cdp-query-fallback.md` (sleep-based örnek içerir; event-driven için yukarıdaki kodu kullan)

MCP'nin `ask_question`'ı timeout yediğinde veya boş response döndüğünde, keepalive CDP üzerinden NotebookLM'e doğrudan sorgu gönderilebilir:

```python
import websocket, json, time, urllib.request

# 1. Yeni sayfa aç
req = urllib.request.Request("http://127.0.0.1:18800/json/new", method="PUT")
page = json.loads(urllib.request.urlopen(req).read())
ws = websocket.create_connection(page["webSocketDebuggerUrl"])

# 2. Notebook sayfasına git (doğru authuser ile)
ws.send(json.dumps({"id":1,"method":"Page.navigate","params":{
    "url":"https://notebooklm.google.com/notebook/<UUID>?authuser=1"}}))
ws.recv(); time.sleep(10)

# 3. Soruyu yaz
ws.send(json.dumps({"id":2,"method":"Runtime.evaluate","params":{"expression":"""
    var ta = document.querySelector('textarea.query-box-input');
    ta.focus(); ta.value = 'soru metni';
    ta.dispatchEvent(new Event('input', {bubbles: true}));
"""}})); ws.recv(); time.sleep(1)

# 4. Gönder (Enter)
ws.send(json.dumps({"id":3,"method":"Input.dispatchKeyEvent","params":{
    "type":"keyDown","key":"Enter","code":"Enter","windowsVirtualKeyCode":13}}))
ws.recv()

# 5. Cevabı bekle (poll)
for i in range(30):
    ws.send(json.dumps({"id":4,"method":"Runtime.evaluate","params":{"expression":
        "document.querySelector('.to-user-container:last-child .message-text-content')?.innerText?.substring(0,500) || 'yok'"}}))
    r = json.loads(ws.recv())
    text = r.get("result",{}).get("result",{}).get("value","")
    if text and text != "yok" and "yükleniyor" not in text.lower() and "thinking" not in text.lower():
        print(f"Cevap: {text}"); break
    time.sleep(3)
ws.close()
```

Referans: `references/cdp-query-fallback.md` (sleep-based). **Hazır script:** `scripts/cdp_notebooklm_query.py` — event-driven, karakter-karakter yazma, mesaj sayacı, doğrudan kullanılabilir.

### 📊 NotebookLM CDP Selector'ları (5 Tem 2026 — Doğrulanmış)

CDP ile NotebookLM'den cevap okurken doğru selector'lar:

| Selector | Çalışıyor? | Not |
|----------|:----------:|-----|
| `.message-content` | ✅ | Gerçek sohbet mesajları |
| `textarea` | ✅ | loadEventFired'dan sonra |
| `[class*=message]` | ⚠️ | Çok geniş — UI elementlerini de yakalar |
| `.message-text-content` | ❌ | Güncel arayüzde yok |
| `textarea.query-box-input` | ❌ | Eski class |

**Cevap tespiti:** Mesaj sayısı artışı (prior vs current) — `.message-content` selector ile.

**⚠️ CDP boş dönüyorsa:** Chrome uzun süredir çalışıyorsa (4+ saat) CDP Runtime.evaluate boş dönmeye başlayabilir. Sayfa yüklendi event'i gelir ama JS sonuçları hep boştur. Çözüm: Chrome'u yeniden başlat (ama ÖNCE Edel'e sor). Veya yeni bir Chrome instance'ı başlat.

NotebookLM'e sorgu göndermek için MCP'yi yeniden yapılandırma **gereksizdir**. Keepalive'nin zaten auth'lu Chrome'u CDP üzerinden kullanılabilir:

```bash
# 1. Keepalive Chrome'un çalıştığını kontrol et
curl -s http://127.0.0.1:18800/json | head -5

# 2. Yeni sekme aç (PUT gerekli, GET çalışmaz)
curl -s -X PUT http://127.0.0.1:18800/json/new
# → {"id": "...", "webSocketDebuggerUrl": "ws://127.0.0.1:18800/devtools/page/..."}

# 3. WebSocket ile CDP komutları gönder
# pip install websocket-client
import websocket, json, time
ws = websocket.create_connection("ws://127.0.0.1:18800/devtools/page/XXX")
# Navigate
ws.send(json.dumps({"id": 1, "method": "Page.navigate", "params": {"url": "https://notebooklm.google.com/notebook/<UUID>"}}))
time.sleep(8)  # Sayfanın yüklenmesini bekle
# Sayfa içeriğini oku
ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate", "params": {"expression": "document.body?.innerText?.substring(0,2000) || ''"}}))
ws.close()
```

**⚠️ Hesap uyumu (KRİTİK):** Keepalive'nin Chrome'u `pro` (kenshin4155) veya `legacy` (isimgorulsunn) profiliyle bağlı olabilir. Sayfa "Erişim izni gerekiyor" / "Access Required" derse → Chrome'daki hesabın notebook'a erişimi yok. 

Bu **auth sorunu DEĞİLDİR** — Chrome Google'a login'dir ama notebook başka bir profilin hesabına aittir. Çözüm:
- **AccountChooser:** `https://accounts.google.com/AccountChooser?continue=https://notebooklm.google.com&Email=...` ile diğer hesaba geç
- **Share:** Notebook'u NotebookLM'den diğer hesapla paylaş (Settings → Share)
- **VNC re-auth:** MCP'yi headed modda başlatıp `re_auth` ile doğru hesaba login ol

Test akışı:
```
get_health → authenticated: true/false (MCP login durumu)
Page.navigate → notebook URL → /accessrequest/ yönleniyor mu?
  Yoksa → auth tamam, notebook erişilebilir ✅
  Varsa → notebook başka hesaba ait, hesap değiştirilmeli 🔄
```

### Keepalive ile İlişkisi

Keepalive sistemsel Chromium profilini yönetir, MCP kendi profilini kullanır. Aralarında otomatik cookie paylaşımı yoktur. MCP'ye ayrı `setup_auth` gerekir. **MCP'yi sadece Edel açıkça istediğinde yeniden yapılandır.**

### Config Parametreleri

| Env Var | Default | Açıklama |
|---------|---------|----------|
| `HEADLESS` | `true` | Chrome headless |
| `ANSWER_TIMEOUT_MS` | `600000` | Cevap timeout |
| `BROWSER_TIMEOUT` | `30000` | Per-action timeout |
| `STEALTH_ENABLED` | `true` | Human-typing stealth |
| `NOTEBOOKLM_TRANSPORT` | `stdio` | `stdio` veya `http` |
| `NOTEBOOKLM_PROFILE` | `full` | Tool profile |
| `BROWSER_CHANNEL` | `chrome` | `chromium` force bundled |

---

## 🐛 Bilinen Bug'lar ve Pitfall'lar

### PermissionError: `/tmp/{pro,legacy}_dict.json` (root ownership)

**Belirti:** `cdp_extract_both.py` / `nb_keepalive.py` şu hatayı verir:
```
PermissionError: [Errno 13] Permission denied: '/tmp/pro_dict.json'
```

**Sebep:** Dosya geçmişte root olarak çalıştırılan bir process tarafından oluşturulmuş (`-rw-r--r-- 1 root root`). Ubuntu kullanıcısı overwrite edemez.

**Çözüm:** Docker container'da `sudo` yoksa root erişimi gerekir. Workaround olarak `cdp_extract_both.py` içindeki `/tmp/` yolunu `~/.hermes/tmp/` olarak değiştir. Veya container restart'ta `/tmp/` temizlenir.

**✅ FALLBACK ÇALIŞIYOR (10 Tem 2026):** Keepalive script'i PermissionError'dan sonra otomatik olarak CDP tabanlı login'e düşer (`🔄 Falling back to nlm CDP login (Network.getAllCookies)...`). Bu fallback **başarılıdır** — `✅ pro CDP login OK` ve `✅ legacy CDP login OK` mesajlarıyla sonuçlanır. MCP auth statüsü bu fallback'ten hemen etkilenmeyebilir (MCP ayrı bir cookie store kullanır), ancak keepalive'in kendi auth'u düzelir. **Hata görünce panik yapma — script kendini toparlar.**

### 🔴 Authfix Wrapper (12 Tem 2026)

`notebooklm-mcp v2.0.11`'de `_ensure_client()` `authenticate()`'i hiç çağırmaz. Çözüm olarak `~/.hermes/scripts/notebooklm_mcp_authfix.py` monkey-patch wrapper'ı kullanılır.

Wrapper, `NotebookLMFastMCP._ensure_client`'e `authenticate()` çağrısını ekler. Hermes config'inde `mcp_servers.notebooklm.command` bu wrapper'a yönlendirilir.

Detaylı bilgi: `references/python-v2.0.11-auth-bug.md`

### 🔴 Profil Locking (İki Chrome, Aynı Profil)

Keepalive Chrome ve MCP'nin undetected_chromedriver'ı AYNI profil dizinini kullanır (`~/.hermes/chrome_profile_notebooklm`). Chrome aynı profili aynı anda iki instance'a açmaz — keepalive profili lock'lar.

**Belirti:** Her iki Chrome'da da aynı 35 Google cookie var (doğrulandı), ama MCP'nin Chrome'u auth yapamaz.

**Çözümler:**
1. MCP'ye ayrı bir profil kopyası ver (cookies import edilmiş)
2. Keepalive'ı önce durdur, MCP'yi başlat, sonra keepalive'ı geri başlat (Edel'e sor)
3. Keepalive CDP'sini direkt kullan (port 18800) — MCP Chrome'u bypass et

`nb_autologin.py` (keepalive auto-login script) line 22'de `NLM_BIN = "/usr/local/bin/nlm"` yazıyordu. **Asıl kritik nokta:** Sistemde `nlm` adında iki farklı npm paketi vardı: (a) **groupon/nlm** (v5.8.0) — Node.js lifecycle manager, (b) **jacob-bd/notebooklm-mcp-cli** (v0.8.1) — NotebookLM MCP. `nlm` komutu artık NotebookLM aracı DEĞİL.

**Alınan aksiyonlar:** NotebookLM artık MCP-native çalışıyor (cookie-based, Chrome CDP). `nlm` binary'sine hiç ihtiyaç kalmadı. Tüm script'lerden nlm bağımlılığı temizlendi:
- `nb_keepalive.py` → v4.0 MCP-native, nlm kodu kaldırıldı ✅
- `nb_autologin.py` → NLM_BIN değişkeni ve nlm cookie update adımı kaldırıldı ✅
- `refresh_google_token.sh` → NotebookLM kontrolü kaldırıldı ✅
- `restore_config.py` → eski nlm referansı kaldırıldı ✅

**Kural:** Artık hiçbir script `nlm` veya `notebooklm-mcp` binary'sini doğrudan çağırmaz. NotebookLM auth'u `nb_keepalive.py` (Chrome CDP + cookie extraction) tarafından yönetilir. Yeni bir script yazarken `subprocess.run(["nlm", ...])` KULLANMA — PATH'teki `nlm` (groupon/nlm) yanlış araçtır.

**Belirti:** `Page.frameNavigated` event'i geliyor, navigasyon başarılı görünüyor, ama `Runtime.evaluate` her zaman boş (`""`) dönüyor. WebSocket'ten çok sayıda mesaj geliyor (555/15sn) ama hiçbiri evaluate yanıtı değil.

**Sebep:** Chrome uzun süredir (4+ saat) çalışıyorsa execution context bozulabilir. `Runtime.enable` yapılsa bile evaluate yanıt vermez.

**Çözüm:** Chrome'u yeniden başlat (ama ÖNCE Edel'e sor!):
```bash
bash /home/ubuntu/.hermes/scripts/start-chrome-keepalive.sh
```
Veya VNC'den manuel giriş yap.

### Binary Version Çakışması: Hermes v1 Python MCP'i Çalıştırıyor (10 Tem 2026)

**Belirti:** `hermes mcp test notebooklm-mcp` başarılı (39 tool keşfedildi) ama MCP tool'ları hala `"MCP server 'notebooklm-mcp' is not connected"` hatası veriyor. Ya da `get_health` sürekli hata dönüyor.

**Sebep:** Sistemde **iki farklı notebooklm-mcp binary'si** var:
- `/usr/local/bin/notebooklm-mcp` → **v1 Python** (`notebooklm_tools.mcp.server`), root'a ait, Hermes config'te bu path kullanılıyor
- `~/.npm-global/bin/notebooklm-mcp` → **v2 Node.js** (`dist/index.js`), npm global

Hermes config'i (`hermes mcp list` → Transport kolonu) `/usr/local/bin/notebooklm-mcp`'yi gösteriyorsa **v1 Python sürümü** çalışıyordur. Skill v2.0'ı anlatsa da sistem v1'de takılı kalabilir.

**Tanı akışı:**
```bash
# 1. Hermes'in hangi binary'i kullandığını kontrol et
hermes mcp list | grep notebooklm
# Transport: stdio → /usr/local/bin/notebooklm-mcp  ← v1 Python!

# 2. Binary'nin gerçekte ne olduğunu kontrol et
head -3 /usr/local/bin/notebooklm-mcp
# !/usr/local/bin/python3.11  ← Python = v1
# from notebooklm_tools.mcp.server import main

head -3 ~/.npm-global/bin/notebooklm-mcp
# Node.js wrapper → v2 (asıl istenen sürüm)

# 3. Symlink kontrolü (wrapper hangisine gidiyor?)
readlink -f ~/.local/bin/notebooklm-mcp
# → /usr/local/bin/notebooklm-mcp (v1!) veya ~/.npm-global/bin/notebooklm-mcp (v2)
```

**Çözüm:** Hermes config'ini v2 Node.js binary'sine yönlendir:
```bash
# 1. Symlink'i düzelt (wrapper v2'ye gitsin)
ln -sf /home/ubuntu/.npm-global/bin/notebooklm-mcp /home/ubuntu/.local/bin/notebooklm-mcp

# 2. Hermes MCP config'ini güncelle (wrapper üzerinden)
hermes mcp remove notebooklm-mcp
printf "Y\nY\n" | hermes mcp add notebooklm-mcp --command /home/ubuntu/.local/bin/notebooklm-mcp-wrapper.sh

# 3. Veya doğrudan binary path'ini ver
printf "Y\nY\n" | hermes mcp add notebooklm-mcp --command /home/ubuntu/.npm-global/bin/notebooklm-mcp
```

> **⚠️ Kritik:** `hermes mcp add` yeniden yapılandırma sayılır. Önce Edel'e sor. "MCP'yi yeniden yapılandırmam gerekiyor — sistem v1 Python sürümünü kullanıyor, v2 Node.js'e geçirmek istiyorum. Onaylıyor musun?"

### nlm `login --check` "expired" ama keepalive "Already logged in"

**Belirti:** Keepalive log'u `✅ Already logged in!` ve `✅ nlm cookies updated` diyor, ama `nlm login --check --profile pro` hala `✗ Authentication failed: Credentials have expired.` dönüyor.

**Sebep:** nlm'nin cookie expiry kontrol mekanizması ile keepalive'in CDP üzerinden aldığı cookie'ler arasında format farkı olabilir. nlm kendi `cookies.json` dosyasını kontrol eder, keepalive ise Chrome'dan canlı cookie alır. nlm dosyasındaki cookie'lerin `expiry` değeri geçmiş olabilir.

**Çözüm:** nlm check'e güvenme. Gerçek auth durumunu anlamak için:
1. Chrome'da NotebookLM sayfası açık mı? `curl -s http://127.0.0.1:18800/json | grep NotebookLM`
2. CDP ile notebook sayfasına gidip `document.title` al: "Google NotebookLM" dönüyorsa auth var
3. `nlm login --provider openclaw --cdp-url http://127.0.0.1:18800 --profile pro --force` ile nlm'yi güncelle

### nlm login --manual Netscape cookie import (10 Temmuz 2026)

Keepalive'in `/tmp/pro_dict.json` dosyasında Google auth cookie'leri bulunur (NID, APISID, PSIDCC vb.). Bu cookie'leri `nlm login --manual` ile import etmek için:

1. **Dosyayı Netscape formatına çevir:**
```python
import json
with open('/tmp/pro_dict.json') as f:
    cookies = json.load(f)
ns_lines = ["# Netscape HTTP Cookie File"]
for name, value in cookies.items():
    ns_lines.append(f".google.com\tTRUE\t/\tTRUE\t4070908800\t{name}\t{value}")
with open('/tmp/nlm_import.txt', 'w') as f:
    f.write('\n'.join(ns_lines))
```

2. **Import et:**
```bash
nlm login --manual -f /tmp/nlm_import.txt
```
`✓ Successfully authenticated!` mesajı başarıyı gösterir.

**Ne zaman kullanılır:** MCP `setup_auth` headless'ta başarısız olduğunda (`Authentication failed or was cancelled`) ve keepalive Chrome CDP çalışır durumdayken. Keepalive'in dict dosyasındaki cookie'leri nlm'ye aktarmak için en hızlı yöntemdir.

### CDP Runtime.evaluate "mesaj selinde kaybolma" (Event-Driven Pattern)

**Belirti:** `Runtime.evaluate` isteği gönderiliyor, `time.sleep` ile bekleniyor, sonra `ws.recv()` yapılıyor ama evaluate yanıtı gelmiyor. Tümüyle boş değer.

**Sebep:** WebSocket'ten sürekli event yağıyor (Page.frameNavigated, Runtime.consoleAPICalled, vs). Uzun `time.sleep` sırasında mesajlar birikiyor ve evaluate yanıtı bu selin içinde kayboluyor. `settimout` ile kısa süre dinleyince evaluate yanıtını kaçırıyorsun.

**Çözüm:** FrameNavigated event'inden **hemen sonra** evaluate gönder. Event'leri sürekli dinle, evaluate yanıtını ID'ye göre yakala. `time.sleep` kullanma:
```python
ws.settimeout(30)
while True:
    d = json.loads(ws.recv())
    if d.get('method') == 'Page.frameNavigated':
        if NOTEBOK_ID in d['params']['frame']['url']:
            ws.send(json.dumps({'id':10,'method':'Runtime.evaluate',...}))  # hemen
    
    if d.get('id') == 10:  # evaluate yanıtı
        result = d['result']['result']['value']
        break
```

## 🔴 Chrome Başlatma Sorunları (Headed Mode)

### --disable-gpu: Headi ÖLDÜRÜR

Docker container'da headed Chromium başlatırken `--disable-gpu` flag'i X11 rendering'i engeller ve Chromium hemen çıkar (6 saniyede exit 0, hiç log yok).

| Flag | Headed | Headless |
|------|:------:|:--------:|
| `--disable-gpu` | ❌ ÖLÜR | ✅ Çalışır |
| `--ozone-platform=x11` | ✅ Çalışır | — |
| Hiçbiri | ✅ Çalışır (software) | — |

**Çalışan başlangıç (headed):**
```bash
chromium \
  --no-sandbox --disable-dev-shm-usage \
  --remote-debugging-port=18800 --remote-allow-origins=* \
  --user-data-dir=$PROFILE \
  --window-size=1280,1024 \
  https://notebooklm.google.com
```

**Tanı:** Chrome hemen ölüyorsa:
```bash
# Xvfb kontrolü
DISPLAY=:99 xdpyinfo | head -3
# /tmp/.X99-lock root'a aitse docker restart gerek
ls -la /tmp/.X99-lock
# Headless modda çalışıyor mu?
timeout 5 chromium --no-sandbox --headless --dump-dom https://example.com
```

### start-chrome-keepalive.sh'te `exec` Tuzağı

`start-chrome-keepalive.sh` şu pattern'i kullanır:
```bash
exec chromium --no-sandbox ... https://notebooklm.google.com
```

`exec` mevcut shell'i chromium ile değiştirir. Bu, `terminal(background=true)` ile başlatıldığında beklenmedik davranışa yol açabilir. Eğer process hemen ölüyorsa, `exec`'i kaldırıp düz `chromium` çalıştırmayı dene.

## 🔴 Keepalive Chrome'unu ASLA Kapatma

Compass kuralı: "Kurmana gerek yok. Compass kurallarını uygula, notebooklm zaten var."

Keepalive Chrome'u (port 18800) sistemin **kalbidir.** 7/24 çalışır. Onu `pkill`/`kill` ile kapatmak:

- ❌ Session'ı düşürür
- ❌ nlm cookie'lerini geçersiz kılar
- ❌ CDP bağlantısını koparır
- ❌ Edel'in yaptığı manuel girişi boşa çıkarır
- ❌ Mekanizmanın kendini iyileştirmesini engeller

**Auth sorunu varsa Chrome'u öldürme.** Onun yerine:
1. `python3 ~/.hermes/scripts/nb_keepalive.py` çalıştır (Compass kuralı — BWS+TOTP+CDP ile auto-heal)
2. Veya BW'den kullanıcı/şifre/TOTP alıp CDP ile login yap (`nb_autologin.py --profile pro`)
3. Veya VNC'den manuel giriş yap

**Eğer Chrome crash-loop'ta veya gerçekten yeniden başlatılması gerekiyorsa:** `start-chrome-keepalive.sh` ile yeniden başlat. Ama önce `Singleton*` dosyalarını temizle.

## Sık Karşılaşılan Sorunlar

| Sorun | Sebep | Çözüm |
|-------|-------|-------|
| `get_health` → `authenticated: false` | Cookies var ama `auto_login_enabled: false` + `active_sessions: 0`. MCP henüz NotebookLM'e bağlanmadı. | Normaldir — gerçek auth `ask_question` çağrılınca belli olur. Veya keepalive CDP üzerinden çalış (port 18800). |
| `ask_question` → `"Could not find NotebookLM chat input"` | **Üç olası sebep** (5 Tem 2026 tanı akışı): <br>1. Auth yok → sayfa "Sign in" / "identifier"<br>2. Erişim izni yok → sayfa "Erişim izni gerekiyor" (notebook başka hesaba ait)<br>3. Sayfa render'lanmamış → textarea henüz DOM'da yok | **CDP tanı kodu** (bkz. `references/cdp-query-fallback.md#-could-not-find-chat-input--uclu-tani-akisi`):<br>1. `document.body.innerText` ile sayfa içeriğini oku<br>2. "Erişim izni" / "Access Required" → authuser değiştir<br>3. "Sign in" → auth yok, Chrome'da giriş yap<br>4. "NotebookLM" + textarea yok → bekle
| `ask_question` → `"Failed to authenticate session"` | Cookie'ler geçersiz veya encrypted_value boş. MCP profili ile keepalive profili farklı. | Keepalive profilini MCP'ye symlinkle: `ln -sf ~/.hermes/chrome_profile_notebooklm ~/.local/share/notebooklm-mcp/chrome_profile` |
| `ask_question` → `success: true` ama `response: ""` (boş) | Cevap alındı ama `waitForStableAnswer` metni boş döndü — selector uyumsuzluğu | CDP fallback kullan (`references/cdp-query-fallback.md`) |
| `ask_question` → timeout (180s+) | `waitForStableAnswer` polling döngüsü cevap bulamıyor, keepalive CDP çalışır | keepalive Chromium'u NotebookLM'i doğru render eder. CDP fallback kullan. |
| MCP tool'ları bu session'da görünmüyor | Config'e eklendi ama session eski | Yeni session başlat veya `delegate_task` kullan |
| `ask_question` timeout (300sn+) | Playwright binary eksik veya auth bekliyor | `npx playwright install chromium` + auth |
| `browserType.launch...: Executable doesn't exist` | Playwright browser'ları kurulmamış | Paket dizininde `npx playwright install chromium` |
| `Connection closed` MCP eklenirken | Binary path yanlış | Binary varlığını kontrol et, wrapper path'ini düzelt |
| Wrapper `not found` | `~/.local/bin/notebooklm-mcp` yok | Symlink oluştur: `ln -sf /home/ubuntu/.npm-global/bin/notebooklm-mcp /home/ubuntu/.local/bin/notebooklm-mcp` |
| Provider/Model çakışması | NotebookLM kendi Gemini'ini kullanır | Normaldir — Hermes modelinden bağımsız |

---

## MCP v1 (Python — Legacy)

Eski Python tabanlı MCP. Yerini v2.0 Node.js paketine bıraktı. Auth flow'u farklıydı:
- CLI: `nlm login --check`, `nlm login --manual -f cookies.json`
- VNC + CDP cookie export ile login
- Storage state empty trick: `{"cookies":[],"origins":[]}`
- `undetected-chromedriver` cookie limiti (`__Secure-` prefix sorunu)

**v2.0'da bu yöntemler geçerli değildir.**

---

## İlgili Yollar

- **MCP v2.0 Chrome profili:** `~/.local/share/notebooklm-mcp/chrome_profile/`
- **Keepalive Chrome profili:** `~/.hermes/chrome_profile_notebooklm`
- **Auth cookie dosyası (legacy):** `~/.notebooklm-mcp-cli/auth.json`
- **MCP npm paketi:** `/home/ubuntu/.npm-global/lib/node_modules/notebooklm-mcp/`
- **Wrapper script:** `~/.local/bin/notebooklm-mcp-wrapper.sh`
- **Playwright cache:** `~/.cache/ms-playwright/`
- **Library JSON:** `~/.local/share/notebooklm-mcp/library.json`
- **Keepalive script:** `~/.hermes/scripts/nb_keepalive.py`
- **Chromium patch script:** `~/.hermes/scripts/mcp-chromium-patch.sh` (skill: `scripts/mcp-chromium-patch.sh`)
- **CDP sorgu fallback:** `references/cdp-query-fallback.md`
- **MCP Chromium patch (re-apply):** `~/.hermes/scripts/mcp-chromium-patch.sh` (skill altında da: `scripts/mcp-chromium-patch.sh`)
- **CDP query fallback:** `references/cdp-query-fallback.md`
