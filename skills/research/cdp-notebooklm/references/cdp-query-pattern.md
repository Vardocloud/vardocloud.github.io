# CDP Query Pattern — NotebookLM Soru Sorma (10 Tem 2026)

## Ne Zaman Kullanılır

MCP server authenticated değilse (`get_health` → `authenticated: false`) ama keepalive Chrome çalışıyorsa (port 18800), CDP ile NotebookLM'e doğrudan soru sorulabilir.

## Ön Koşullar

- Keepalive Chrome çalışıyor: `curl http://127.0.0.1:18800/json/version` → 200
- Notebook tab'ı zaten açık (keepalive login yapmış olmalı)
- `python3` + `websocket-client` kurulu

## Çalışan Pattern

```python
import json, urllib.request, websocket, time

CDP = 'http://127.0.0.1:18800'
NOTEBOOK_URL = 'https://notebooklm.google.com/notebook/{NOTEBOOK_ID}?authuser={1}'

# 1. Keepalive Chrome'da NotebookLM tab'ını bul
tabs = json.loads(urllib.request.urlopen(f'{CDP}/json').read())
target = None
for t in tabs:
    if 'notebooklm' in t.get('url',''):
        target = t
        tab_id = t['id']
        ws_url = t['webSocketDebuggerUrl']
        break

# 2. WebSocket bağlantısı kur
ws = websocket.create_connection(ws_url, timeout=15)
nid = [5000]

def send(method, params=None):
    nid[0] += 1
    ws.send(json.dumps({'id': nid[0], 'method': method, 'params': params or {}}))

send('Runtime.enable')
time.sleep(0.3)

# 3. Notebook sayfasına navigate et
send('Page.navigate', {'url': NOTEBOOK_URL})
time.sleep(15)  # Sayfanın yüklenmesi için bekle (JS-heavy)

# 4. KRITIK: Navigate sonrası reconnect (eski WebSocket ölür)
ws.close()
time.sleep(1)
tabs2 = json.loads(urllib.request.urlopen(f'{CDP}/json').read())
ws2 = None
for t in tabs2:
    if t.get('id') == tab_id:
        ws2 = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=10)
        break

nid2 = [6000]
def send2(m, p=None):
    nid2[0] += 1
    ws2.send(json.dumps({'id': nid2[0], 'method': m, 'params': p or {}}))

def eval2(expr, timeout=15):
    nid2[0] += 1
    mid = nid2[0]
    ws2.send(json.dumps({'id':mid,'method':'Runtime.evaluate',
        'params':{'expression':expr,'returnByValue':True}}))
    ws2.settimeout(timeout)
    while True:
        try:
            d = json.loads(ws2.recv())
            if d.get('id') == mid:
                r = d.get('result',{})
                if r.get('exceptionDetails'):
                    return None
                return r.get('result',{}).get('value','')
        except:
            break
    return None

send2('Runtime.enable')
time.sleep(0.5)

# 5. Soru gönder
question = "What are the key points from the APA guide on navigating AI-generated advice?"
eval2('document.querySelector("textarea")?.focus()')
time.sleep(0.3)
nid2[0] += 1
ws2.send(json.dumps({'id': nid2[0], 'method': 'Input.insertText',
    'params': {'text': question}}))
time.sleep(0.5)

# Enter tuşuna bas
for ev_type in ['keyDown', 'keyUp']:
    nid2[0] += 1
    ws2.send(json.dumps({'id': nid2[0], 'method': 'Input.dispatchKeyEvent',
        'params': {'type': ev_type, 'key': 'Enter', 'code': 'Enter',
                   'windowsVirtualKeyCode': 13}}))
    time.sleep(0.1)

# 6. Cevabı bekle ve al
time.sleep(20)  # NotebookLM yanıt süresi
result = eval2("""
(function() {
    var all = document.querySelectorAll('*');
    var results = [];
    for(var el of all) {
        var text = (el.textContent || '').trim();
        var cls = el.className || '';
        if(text.length > 50 && 
           (cls.includes('message') || cls.includes('response') || cls.includes('answer'))) {
            results.push({tag: el.tagName, text: text.substring(0,200)});
        }
    }
    return JSON.stringify(results.slice(-5));
})()
""")
```

## Doğrulanan Bilgiler

- Keepalive Chrome'da açık NotebookLM tab'ı (`?authuser=0`) üzerinden sorgu yapılabiliyor
- Navigate sonrası 15sn bekle + reconnect pattern çalışıyor
- `Input.insertText` textarea'ya metin yazmak için çalışıyor
- `Input.dispatchKeyEvent` Enter göndermek için çalışıyor
- NotebookLM'in chat response'u `to-user-message-card-content` class'lı `mat-card` içinde geliyor
- authuser=1 (legacy/isimgorulsunn@gmail.com) ile APA Bilgi notebook'u açılabiliyor

## Sınırlamalar

- NotebookLM yanıt süresi değişken (10-30sn arası)
- Chat response DOM selector'ları NotebookLM güncellemeleriyle değişebilir
- `Input.insertText` bazen son karakteri düşürebilir — ek `time.sleep` ile kontrol et
- Uzun script'leri terminal'de tek satırda çalıştırmak tırnak sorunu çıkarır — her zaman .py dosyasına yaz
