# Studio Artifact CDP Referansı

NotebookLM Studio paneli, keepalive Chrome (port 18800) CDP'si üzerinden doğrudan kontrol edilebilir. `nlm` CLI'ın çalışmadığı veya auth sorunu olduğu durumlarda CDP yedek yöntemdir.

## CDP Studio Kullanımı

```python
import websocket, json, time, urllib.request

CDP = 'http://127.0.0.1:18800'
gid = [1]
def nid(): gid[0] += 1; return gid[0]

# Mevcut notebook tab'ını bul (authuser=0 veya =1)
tabs = json.loads(urllib.request.urlopen(f'{CDP}/json').read())
target = None
for t in tabs:
    url = t.get('url','') or ''
    if 'notebooklm.google.com/notebook' in url:
        target = t; break

ws = websocket.create_connection(target['webSocketDebuggerUrl'], timeout=30)
ws.send(json.dumps({'id':nid(),'method':'Runtime.enable'}))
time.sleep(0.3)
# drain
ws.settimeout(0.5)
try:
    while True: ws.recv()
except: pass

def ev(expr, timeout=8):
    mid = nid()
    ws.send(json.dumps({'id':mid,'method':'Runtime.evaluate',
        'params':{'expression':expr,'returnByValue':True}}))
    ws.settimeout(timeout)
    while True:
        try:
            d = json.loads(ws.recv())
            if d.get('id') == mid:
                r = d.get('result',{})
                if r.get('exceptionDetails'): return 'ERR'
                return r.get('result',{}).get('value','')
        except: break
    return None

# Studio panelini bul
studio = ev("""
(function(){
    var headings = document.querySelectorAll('h2');
    for(var h of headings){
        if((h.textContent||'').trim() === 'Studio'){
            var panel = h.closest('[class*=\"studio\"]') || h.parentElement;
            while(panel && !panel.className.includes('studio') && panel !== document.body)
                panel = panel.parentElement;
            return panel ? panel.outerHTML.substring(0,500) : 'not found';
        }
    }
    return 'no Studio heading';
})()
""")
```

## Artifact Türleri ve aria-label'lar

| Artifact | aria-label | DOM Text |
|----------|------------|----------|
| Sesli Özet | `"Sesli Özet"` | `audio_magic_eraser Sesli Özet` |
| Slayt Sunusu | `"Slayt Sunusu"` | `tablet Slayt Sunusu` |
| Videolu Özet | `"Videolu Özet"` | `subscriptions Videolu Özet` |
| Zihin Haritası | `"Zihin Haritası"` | `flowchart Zihin Haritası` |
| Raporlar | `"Raporlar"` | `auto_tab_group Raporlar` |
| Bilgi kartları | `"Bilgi kartları"` | `cards_star Bilgi kartları` |
| Test | `"Test"` | `quiz Test` |
| İnfografik | `"İnfografik"` | `stacked_bar_chart İnfografik` |
| Veri Tablosu | `"Veri Tablosu"` | `table_view Veri Tablosu` |

## Butona Tıklama

```python
def click_artifact(ws, artifact_name):
    """Studio panelinde artifact butonuna tıkla."""
    return ev(ws, f"""
    (function(){{
        var containers = document.querySelectorAll('[class*="create-artifact"]');
        for(var c of containers){{
            var t = c.textContent || '';
            var aria = c.getAttribute('aria-label') || '';
            if(t.includes('{artifact_name}') || aria.includes('{artifact_name}')){{
                var btn = c.querySelector('button') || c;
                btn.click();
                return 'clicked: ' + aria;
            }}
        }}
        return 'not found: {artifact_name}';
    }})()
    """)
```

## Özelleştirme Butonu

Her artifact'in sağında `chevron_forward` ikonlu bir özelleştirme butonu vardır (aria-label: `"[Tür]'i özelleştir"`). Buton class: `edit-artifact-button`.

## Notlar

- CDP ile Studio, sayfa zaten yüklüyse navigate gerektirmez — mevcut tab'ı kullan
- Özelleştirme butonları genelde `mdc-icon-button` class'ına sahip
- Panel daraltma: `dock_to_left` butonu / aria-label `"Stüdyo panelini daralt"`
- Tüm Studio butonları görünür (scroll gerekmez) — panel genelde sağ tarafta açılır
- Authuser fark etmez — her iki hesap da (authuser=0 ve authuser=1) Studio'ya tam erişimlidir
