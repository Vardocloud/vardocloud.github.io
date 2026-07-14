# CDP Query Fallback — Proven Pattern

MCP `ask_question` çalışmadığında (auth, selector, şifreleme sorunu), CDP üzerinden
keepalive Chrome'una doğrudan bağlanarak NotebookLM sorgusu yapılabilir.

## Ne Zaman Kullanılır

- MCP `ask_question` → `"Could not find chat input"` / boş cevap / timeout
- Cookie şifreleme uyumsuzluğu (bundled vs sistem Chromium)
- Auth sorunu ama keepalive Chrome'unda oturum açık

## Kritik CDP Deseni: `eval_js` ve Mesaj Yönetimi

### eval_js Helper (Kanıtlanmış, 5 Tem 2026)

```python
def eval_js(ws, expr, timeout=10):
    mid = int(time.time() * 1000000)
    ws.send(json.dumps({'id': mid, 'method': 'Runtime.evaluate',
                         'params': {'expression': expr, 'returnByValue': True}}))
    ws.settimeout(timeout)
    while True:
        try:
            d = json.loads(ws.recv())
            if d.get('id') == mid:
                r = d.get('result', {})
                if r.get('exceptionDetails'):
                    return "ERR:" + str(r['exceptionDetails'].get('text','?'))
                return r.get('result', {}).get('value', '')
        except:
            break
    return None
```

### PITFALL: `sleep + drain` Pattern FAILS

```python
# ❌ ÇALIŞMAZ — eval_js None döner
go(ws, url, wait=10)  # navigate + sleep(10) + drain
url = eval_js(ws, "window.location.href")  # → None

# ✅ ÇALIŞIR — mesajları tek tek oku
ws.send(json.dumps({'id': 1, 'method': 'Page.navigate', 'params': {'url': url}}))
# Mesajları TEK TEK oku, loadEventFired'ı bekle
ws.settimeout(15)
for _ in range(30):
    d = json.loads(ws.recv())
    if d.get('method') == 'Page.loadEventFired':
        time.sleep(3)
        break
# Şimdi eval_js çalışır
url = eval_js(ws, "window.location.href")  # → "https://..."
```

**Nedeni:** `Page.navigate` sonrası 30+ mesaj gelir (frame navigations, execution context
changes, subframe loads). `drain()` hepsini yer ama `Runtime.evaluate` yanıtı ya kaçar
ya da WebSocket buffer'ı bozulur. Mesajları sırayla okumak her durumda çalışır.

### PITFALL: `websocket.TimeoutError` Yok

```python
# ❌ AttributeError
except websocket.TimeoutError:  # BU SINIF YOK

# ✅ Doğru
except websocket.WebSocketTimeoutException:
    pass
# Veya bare except (cdp_notebooklm_query.py bu şekilde)
except:
    pass
```

## Navigate + Settle Deseni

Sayfanın tamamen yüklenmesini beklemenin en güvenilir yolu:

```python
def navigate_and_settle(ws, url, settle_time=8):
    ws.send(json.dumps({'id': 1, 'method': 'Page.navigate', 'params': {'url': url}}))
    ws.settimeout(3)
    last_event_time = time.time()
    for _ in range(60):
        try:
            d = json.loads(ws.recv())
            method = d.get('method', '')
            if method in ('Page.loadEventFired', 'Page.frameStoppedLoading'):
                last_event_time = time.time()
        except:
            if time.time() - last_event_time > 3:
                break  # 3 saniyedir event yok → sayfa yüklendi
    time.sleep(settle_time)
    # Drain remaining
    ws.settimeout(0.3)
    try:
        while True: ws.recv()
    except: pass
    return eval_js(ws, "window.location.href") or ''
```

## Tam Sorgu Akışı

```python
# 1. Keepalive Chrome'a bağlan
req = urllib.request.Request('http://127.0.0.1:18800/json/new', method='PUT')
page = json.loads(urllib.request.urlopen(req).read())
ws = websocket.create_connection(page['webSocketDebuggerUrl'], timeout=30)

# 2. Domain'leri enable et
for m in ['Page.enable', 'Runtime.enable', 'Input.enable']:
    ws.send(json.dumps({'id': 0, 'method': m}))
time.sleep(0.3)
drain(ws)  # Enable yanıtlarını temizle

# 3. Notebook'a git (authuser=1 legacy, authuser=0 pro)
url = navigate_and_settle(ws, 
    f'https://notebooklm.google.com/notebook/{NB_ID}?authuser=1')

# 4. Auth kontrol
if url and 'accounts.google' in url:
    # Auth yok → login gerekli (VNC veya autologin)
    return None

# 5. Önceki mesaj sayısını al
prior = eval_js(ws, "document.querySelectorAll('.message-content').length") or 0

# 6. Textarea'ya yaz
eval_js(ws, "var t=document.querySelector('textarea'); if(t)t.focus()")
time.sleep(0.3)

for ch in question:
    ws.send(json.dumps({'id': 99, 'method': 'Input.dispatchKeyEvent', 'params': {
        'type': 'keyDown' if ch != ' ' else 'rawKeyDown',
        'key': ch, 'text': ch,
        'windowsVirtualKeyCode': ord(ch.upper()) if ch.isalpha() else 32}}))
    time.sleep(0.03)

# 7. Enter
for evt in ['rawKeyDown', 'char', 'keyUp']:
    ws.send(json.dumps({'id': 99, 'method': 'Input.dispatchKeyEvent', 'params': {
        'type': evt, 'key': 'Enter', 'code': 'Enter',
        'windowsVirtualKeyCode': 13, 'text': '\r'}}))
    time.sleep(0.1)

# 8. Cevap bekle
drain(ws)  # Gönderim event'lerini temizle
for i in range(25):
    time.sleep(4)
    cur = eval_js(ws, """(function(){
        var ms=document.querySelectorAll('.message-content');
        return JSON.stringify({c:ms.length, l:ms.length>0?ms[ms.length-1].innerText?.substring(0,2000)||'':''});
    })()""")
    if cur:
        info = json.loads(cur)
        if info.get('c', 0) > prior:
            return info.get('l', '')  # Cevap alındı!
```

## Çalışan Script

Kanıtlanmış sorgu script'i: `~/.hermes/scripts/cdp_notebooklm_query.py`

Kullanım:
```bash
python3 cdp_notebooklm_query.py "sorunuz" [notebook_id]
# notebook_id: "bdt" (varsayılan) veya tam notebook ID
```

## Auth Olmadan Çalışmaz

CDP sorgusu, keepalive Chrome'unda aktif Google oturumu gerektirir.
Oturum expired ise (`accounts.google.com/sessionexpired`):

1. `python3 ~/.hermes/scripts/nb_keepalive.py` çalıştır (TOTP auto-login dener)
2. Keepalive takılırsa: VNC ile manuel login (`https://<tunnel>/vnc.html`)
3. Chrome restart son çare (31+ tab, hepsi sessionexpired ise)

## NotebookLM Selector Güncellemeleri

| Tarih | Eski | Yeni |
|-------|------|------|
| 5 Tem 2026 | `textarea.query-box-input` | `textarea.query-box-textarea` |

CDP sorguda selector kullanılmaz — direkt `document.querySelector('textarea')` yeterlidir.
Ama MCP'de bu değişiklik `browser-session.js`'de patch gerektirir.
