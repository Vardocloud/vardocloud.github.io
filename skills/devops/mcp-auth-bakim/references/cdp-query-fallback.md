# CDP ile NotebookLM Sorgu Gönderme (MCP Fallback) — v5 (5 Tem 2026)

MCP `ask_question` çalışmadığında keepalive CDP (port 18800) üzerinden doğrudan NotebookLM sorgulaması.

## Çalışan Pattern (Kanıtlanmış)

```python
# Kritik: Page.enable + Runtime.enable ŞART
# Kritik: loadEventFired bekle — sayfa SPA, textarea 5sn sonra gelir
# Kritik: Input.dispatchKeyEvent ile karakter-karakter yaz
# Kritik: .message-content selector ile mesaj sayacı
```

Tam çalışan script: `scripts/cdp_notebooklm_query.py`

## "Could not find chat input" — Üçlü Tanı Akışı

MCP veya CDP'de bu hatayı aldığında sırayla kontrol et:

### 1. Sayfa içeriğini oku
```javascript
document.body?.innerText?.substring(0,500) || ''
```

### 2. Duruma göre çözüm

| Sayfa içeriği | Sorun | Çözüm |
|--------------|-------|-------|
| "Erişim izni gerekiyor" / "Access Required" | Notebook başka hesaba ait | `authuser=0` veya `authuser=1` dene. Veya notebook'u paylaş |
| "Sign in" / "identifier" | Auth yok | Keepalive'de giriş yap. `nb_autologin.py --profile pro` |
| "Google NotebookLM" + textarea yok | SPA render'lanmadı | 20-30sn bekle, loadEventFired sonrası poll et |
| "Could not find..." | Selector uyumsuz | Textarea class'ı değişmiş olabilir. `document.querySelector('textarea')` kullan |

### 3. Textarea class değişikliği (5 Tem 2026)

NotebookLM arayüzü güncellendi:
- **Eski:** `textarea.query-box-input`
- **Yeni:** `textarea.query-box-textarea` (class zinciri: `mat-mdc-input-element ... query-box-textarea`)

MCP `browser-session.js`'deki tüm `textarea.query-box-input` → `textarea.query-box-textarea` olarak güncellenmeli.

## Event-Driven Pattern (Sleep'siz, Güvenilir)

```python
# Page event'lerini enable et
ws.send(json.dumps({'id': 0, 'method': 'Page.enable'}))
ws.send(json.dumps({'id': -1, 'method': 'Runtime.enable'}))

# Navigate
ws.send(json.dumps({'id': 1, 'method': 'Page.navigate', 'params': {'url': NOTEBOOK_URL}}))

# loadEventFired bekle (frameNavigated değil!)
ws.settimeout(60)
while True:
    d = json.loads(ws.recv())
    if d.get('method') == 'Page.loadEventFired':
        time.sleep(5)  # SPA render süresi
        break

# Şimdi textarea hazır
# Soruyu Input.dispatchKeyEvent ile karakter-karakter yaz
# Enter: rawKeyDown + char + keyUp sequence
# Cevap: .message-content selector, önceki mesaj sayısına göre yeni mesaj tespit et
```

## Niye loadEventFired?

`Page.frameNavigated` sayfanın yönlendiğini söyler ama DOM henüz oluşmamıştır.
`Page.loadEventFired` tüm kaynaklar yüklendi demektir. Ama NotebookLM bir SPA — 
loadEventFired'dan sonra React/Angular component'leri mount olur. Bu ~5 saniye sürer.

Textarea loadEventFired'dan ~5 saniye sonra DOM'da belirir. 
20 saniyeye kadar beklemek gerekebilir.

## Mesaj Sayacı Tabanlı Cevap Tespiti

```python
# Önce mevcut mesaj sayısını al
prior = eval_js(ws, 'document.querySelectorAll(".message-content").length')

# Soruyu gönder...

# Poll: mesaj sayısı arttı mı?
for i in range(40):
    time.sleep(4)
    current = eval_js(ws, """
    (function(){
        var msgs = document.querySelectorAll('.message-content');
        return JSON.stringify({
            count: msgs.length,
            last: msgs.length > 0 ? msgs[msgs.length-1].innerText?.substring(0,2000)||'' : ''
        });
    })()
    """)
    if current:
        info = json.loads(current)
        if info.get('count', 0) > prior:
            return info.get('last', '')  # YENİ CEVAP!
```

## Selector Referansı

| Selector | Açıklama | Çalışıyor? |
|----------|---------|:----------:|
| `.message-content` | Gerçek sohbet mesajları | ✅ |
| `textarea` (herhangi) | Chat input | ✅ (loadEventFired'dan 5sn sonra) |
| `[class*=message]` | Çok geniş, UI elementlerini de yakalar | ⚠️ |
| `.message-text-content` | Eski arayüz | ❌ |
| `textarea.query-box-input` | Eski class (2025) | ❌ |
| `textarea.query-box-textarea` | Güncel class (Tem 2026) | ✅ |
