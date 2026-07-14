# CDP ile NotebookLM'e Kaynak Ekleme (10 Temmuz 2026)

MCP auth çalışmadığında CDP ile NotebookLM'e kaynak eklemek için kullanılır.

## Ön Koşul
- Keepalive Chrome çalışıyor: `http://127.0.0.1:18800`
- Chrome'da NotebookLM'e login olunmuş olmalı (keepalive bunu yönetir)

## NotebookLM DOM Yapısı (10 Tem 2026)

Notebook sayfasındaki kritik elementler:

| Element | Selector / Text | İşlev |
|---------|----------------|-------|
| "Kaynak ekle" butonu | `.add-source-button` / aria-label="Kaynak ekle" | Ana kaynak ekleme butonu |
| "Kopyalanan metin" seçeneği | `button` text `content_pasteKopyalanan metin` | İkinci dialog seçeneği |
| Metin girişi textarea | `placeholder="Metni buraya yapıştırın"` | Kopyalanan metni yapıştırma alanı |
| "Ekle" butonu | `button` text `Ekle` (başlangıçta disabled) | Kaynağı onayla/ekle |
| "Geri" butonu | `button` aria-label="Geri" | Önceki adıma dön |
| Chat textarea | Notebook sohbet alanı, `placeholder` değişken | Sorgu girişi |
| Yanıt kartları | `.to-user-message-card-content` / `.message-text-content` | NotebookLM yanıtları |

## Adım Adım Akış

```python
import json, urllib.request, websocket, time

CDP = 'http://127.0.0.1:18800'
NOTEBOOK_URL = 'https://notebooklm.google.com/notebook/<NOTEBOOK_ID>?authuser=1'

# 1. Tab bul
tabs = json.loads(urllib.request.urlopen(f'{CDP}/json').read())
for t in tabs:
    if 'notebooklm' in t.get('url',''):
        tab_id, ws_url = t['id'], t['webSocketDebuggerUrl']
        break

# 2. Bağlan + Navigate
ws = websocket.create_connection(ws_url, timeout=15)
nid = [1]
def send(m, p=None):
    nid[0] += 1; ws.send(json.dumps({'id':nid[0],'method':m,'params':p or {}}))
send('Runtime.enable'); time.sleep(0.3)
send('Page.navigate', {'url': NOTEBOOK_URL}); time.sleep(15)
ws.close(); time.sleep(1)  # Navigate sonrası RECONNECT

# 3. Reconnect
tabs2 = json.loads(urllib.request.urlopen(f'{CDP}/json').read())
for t in tabs2:
    if t.get('id') == tab_id:
        ws2 = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=10)
        break

# 4. Kaynak ekle butonuna tıkla
def ev(expr, timeout=15):
    nid[0] += 1; mid=nid[0]
    ws2.send(json.dumps({'id':mid,'method':'Runtime.evaluate',
        'params':{'expression':expr,'returnByValue':True}}))
    ws2.settimeout(timeout)
    while True:
        try:
            d=json.loads(ws2.recv())
            if d.get('id')==mid:
                r=d.get('result',{})
                if r.get('exceptionDetails'): return None
                return r.get('result',{}).get('value','')
        except: break
    return None

# 5. "Kaynak ekle" butonu
ev('document.querySelector(".add-source-button")?.click()')
time.sleep(3)

# 6. "Kopyalanan metin" seçeneği
ev("""
var btns = document.querySelectorAll('button');
for(var b of btns) {
    if(b.textContent.includes('Kopyalanan metin')) { b.click(); break; }
}
""")
time.sleep(3)

# 7. Metin textarea'sını bul ve metni yapıştır
ev("""
var inputs = document.querySelectorAll('textarea');
for(var inp of inputs) {
    if(inp.placeholder && inp.placeholder.includes('Metni buraya')) {
        inp.focus(); inp.select(); break;
    }
}
""")
time.sleep(1)

# Büyük metinler için chunked insertText
def insert_text(text):
    nid[0] += 1
    ws2.send(json.dumps({'id':nid[0],'method':'Input.insertText','params':{'text':text}}))

chunk_size = 10000
for i in range(0, len(transcript), chunk_size):
    chunk = transcript[i:i+chunk_size]
    insert_text(chunk)
    time.sleep(0.5)

# 8. "Ekle" butonuna tıkla (metin girilince enabled olur)
ev("""
var btns = document.querySelectorAll('button');
for(var b of btns) {
    var txt = (b.textContent||'').trim();
    if((txt === 'Ekle') && !b.disabled) { b.click(); break; }
}
""")

# 9. Indexleme için bekle (30-40 sn)
time.sleep(40)

# 10. Sorgu gönder
ev('document.querySelector("textarea")?.focus()')
insert_text(soru)
time.sleep(1)
# Enter tuşuna bas
for kt in ['keyDown','keyUp']:
    nid[0] += 1
    ws2.send(json.dumps({'id':nid[0],'method':'Input.dispatchKeyEvent',
        'params':{'type':kt,'key':'Enter','code':'Enter','windowsVirtualKeyCode':13}}))
    time.sleep(0.1)

# 11. Yanıtı DOM'dan oku
resp = ev("""
(function() {
    var cards = document.querySelectorAll('mat-card.mat-mdc-card');
    var last = cards[cards.length - 1];
    if(last && (last.textContent||'').trim().length > 50) return (last.textContent||'').trim().substring(0,1500);
    var msgs = document.querySelectorAll('.message-text-content');
    var lastMsg = msgs[msgs.length - 1];
    if(lastMsg) return (lastMsg.textContent||'').trim().substring(0,1500);
    return 'no response';
})()
""")
```

## Önemli Noktalar

- **"Ekle" butonu başlangıçta disabled=true.** Metin girilince otomatik enabled olur. disabled=false olduğunda tıkla.
- **Metin chunk'ları 10K altı olmalı** — daha büyük chunk'larda Input.insertText timeout atabiliyor.
- **Chunk'lar arasında 0.5sn bekle** — Chrome'un event loop'una zaman tanı.
- **Toplam metin büyüklüğü NotebookLM limitini aşmamalı.** 54K karakter sorunsuz çalıştı.
- **İkinci dialog'u bulmak için** `placeholder="Metni buraya yapıştırın"` olan textarea'yı kullan — bu ana chat'tekilerden farklı bir element.

## Referans
- Çalışan script: `/tmp/nlm_final.py` (10 Tem 2026'da Mentoring transkripti başarıyla eklendi)
- Notebook: `APA Bilgi` (c44469fe-a69a-4a86-8dd8-756c2f365109)
