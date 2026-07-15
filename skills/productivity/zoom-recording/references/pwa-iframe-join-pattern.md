# PWA Iframe Join Pattern (30 Haz 2026)

Modern Zoom web client (2026) meeting join sayfasını bir **PWA wrapper** içinde `#webclient` iframe'i olarak yükler. Bu pattern, eski direkt join sayfasının yerini almıştır.

## Tespit

Bir Zoom URL'ine gidildiğinde:
1. Landing page (`zoom.us/j/ID` veya `zoom.us/w/ID`) → "Join from Browser" tıkla
2. Yönlenen URL: `https://app.zoom.us/wc/MEETING_ID/join?ref_from=launch&...`
3. Sayfa yapısı:
   ```html
   <div id="root">
     <div class="pwa-webclient">
       <iframe id="webclient" src="..."></iframe>
     </div>
   </div>
   ```
4. `document.body.innerText` boş (`bodyLen=0`) — tüm içerik iframe içinde

## CDP ile İframe'a Erişim

Normal `document.getElementById('input-for-name')` çalışmaz çünkü input'lar iframe içinde. **İframe'in contentDocument'ına erişmek gerekir:**

```javascript
var iframe = document.getElementById('webclient');
var idoc = iframe.contentDocument || iframe.contentWindow.document;

// Artık idoc üzerinden sorgula
var nameInput = idoc.getElementById('input-for-name');
var pwdInput = idoc.getElementById('input-for-pwd');
var buttons = idoc.querySelectorAll('button');
```

## İki Alt Pattern

### Pattern A — Passcode + Bekleme (APA Webinar)
**Belirtiler:** `input-for-pwd` var, `input-for-name` yok. Passcode girilince direkt bekleme odası.

```
Sayfa: "Enter Meeting Info" + "Meeting Passcode" input + "Join" button
→ Passcode gir → Join → "Please wait. The webinar will begin soon"
```

**Akış:**
1. iframe içinde `input-for-pwd`'ye passcode'u yaz (native setter + dispatchEvent)
2. "Join" butonuna tıkla (userGesture=True)
3. 8-10sn bekle → waiting room (başlık: "Zoom meeting on web")

### Pattern B — İsim + Passcode (Normal Meeting)
**Belirtiler:** `input-for-name` ve `input-for-pwd` (veya sadece `input-for-name`).

```
Sayfa: "Your Name" input + "Meeting Passcode" input + "Join" button
→ İsim gir → Passcode gir → Join (2 kez) → toplantı içi
```

**Akış:**
1. iframe içinde `input-for-name`'e isim yaz
2. Varsa `input-for-pwd`'ye passcode yaz
3. "Join" butonuna tıkla (userGesture=True)
4. 8-10sn bekle
5. İkinci kez "Join" butonuna tıkla (overlay kaldırma)
6. 5sn bekle — toplantı içinde: "Unmute" + "Leave" butonları görünür

## CSP ve Güvenlik

- Zoom'un CSP'si iframe'e erişimi engellemez (aynı origin)
- `iframe.contentDocument` erişimi için **cross-origin değil** — `app.zoom.us` içindeki iframe aynı domain
- `try/catch` ile erişim dene, cross-origin hatası alınırsa farklı bir pattern var demektir
- Runtime.evaluate her zaman çalışır (Puppeteer evaluate'ın aksine CSP'den etkilenmez)

## Örnek CDP Kodu

```python
import json, time
from websocket import create_connection

# Tab'a bağlan
ws = create_connection(tab_ws_url, timeout=10)

# İframe içinde input doldur
FILL_IFRAME_NAME = '''
(function() {
    var iframe = document.getElementById('webclient');
    if (!iframe) return "no iframe";
    var idoc = iframe.contentDocument || iframe.contentWindow.document;
    if (!idoc) return "no iframe doc";
    var inp = idoc.getElementById('input-for-name');
    if (!inp) return "no name input in iframe";
    var ns = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    ns.call(inp, 'Sudenaz');
    inp.dispatchEvent(new Event('input', {bubbles: true}));
    inp.dispatchEvent(new Event('change', {bubbles: true}));
    return 'filled: ' + inp.value;
})()
'''

# İframe durumunu kontrol et
CHECK_IFRAME = '''
(function() {
    var iframe = document.getElementById('webclient');
    try {
        var idoc = iframe.contentDocument || iframe.contentWindow.document;
        return JSON.stringify({
            title: idoc.title,
            bodyLen: idoc.body.innerText.length,
            hasUnmute: idoc.body.innerText.includes('Unmute'),
            hasLeave: idoc.body.innerText.includes('Leave'),
            buttons: Array.from(idoc.querySelectorAll('button')).map(b => b.textContent.trim()).filter(t => t)
        });
    } catch(e) { return 'error: ' + e.message; }
})()
'''
```

## Önemli Notlar

- Tab ID **değişebilir** — "Join from Browser" tıklaması bazen eski tab'ı bırakıp **yeni bir tab/window açar**. Her adımda `/json` ile tab'ları tara, `app.zoom.us/wc/` içeren URL'den doğru tab'ı bul
- Join sonrası iframe title'ı "Zoom meeting on web" → webinar adına döner
- Waiting room'da body'de "Please wait. The webinar will begin soon" yazar
- Başlamış toplantıda "The host muted you" mesajı ve "Unmute" butonu görünür
- "You are unmuted" mesajı görünüyorsa → ses bağlantısı aktif, kayıt alınıyor
- "Waiting for the host to start the meeting" mesajı görünüyorsa → join başarılı, host bekleniyor (scheduled meeting, host henüz katılmamış)
- "Host Sign in" butonu görünüyorsa → toplantı scheduled durumda, host'un kendi hesabıyla giriş yapıp başlatması gerekiyor
