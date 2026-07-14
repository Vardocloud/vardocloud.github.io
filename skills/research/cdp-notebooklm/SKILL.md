---
name: cdp-notebooklm
description: "CDP (Chrome DevTools Protocol) ile NotebookLM'e bağlanan Python client. YEDEK/YARA durumunda kullanılır. Birincil araç: jacob-bd/notebooklm-mcp-cli (39 tool, full Studio desteği). Keepalive Chrome (port 18800) üzerinden çalışır."
tags: [notebooklm, cdp, chrome-devtools, query, login]
version: "1.3"
---

# CDP NotebookLM Client

CDP (Chrome DevTools Protocol) üzerinden NotebookLM'e bağlanıp soru-cevap yapan Python client.
MCP'ye alternatif olarak, keepalive Chrome'un CDP port'u üzerinden doğrudan çalışır.

## Trigger
NotebookLM ile etkileşim gerektiğinde **ÖNCE MCP'yi dene** (`notebooklm-mcp` skill). CDP'yi sadece MCP çalışmazsa veya aşağıdaki durumlarda kullan:
- MCP `studio_create` çalışmıyor (nadir)
- Manuel DOM kontrolü gerekiyor
- Login/auth sorunu

## Gereksinimler
- Keepalive Chrome çalışıyor olmalı: `http://127.0.0.1:18800`
- `websocket-client` ve `pyotp` Python paketleri
- BWS'den credential'lar (bw-serve HTTP API port 8087)
- `/tmp/get_creds.py` helper script

## MCP Server Auth Limitation (KRİTİK — 12 Tem 2026)

NotebookLM MCP server (`notebooklm-mcp server --transport stdio --headless`) çalışır ama **chat/query işlemleri kalıcı olarak başarısız olur** çünkü:

**Kök neden (2 katmanlı):**

1. **Selenium add_cookie kırılması:** MCP server'ın `_load_cookies()` methodu önce `driver.get('https://notebooklm.google.com')` ile sayfaya gider, SONRA cookie ekler. Sayfa yüklenirken Google eskimiş çerezleri görür ve **hemen `accounts.google.com/CookieMismatch`'e redirect eder**. Artık accounts.google.com domain'indeyken notebooklm.google.com veya google.com domain'li çerezler Selenium `add_cookie` ile eklenemez (domain mismatch). Kritik auth cookie'leri sessizce skip edilir. (client.py L183-207)

2. **Session state eksikliği:** Google, cookie'lere ek olarak service worker, IndexedDB, storage API gibi ek browser state'leri kullanır. httpx ile AYNI cookieler gönderilse bile Google CookieMismatch döndürür — aynı cookie + farklı tarayıcı = farklı session. Keepalive Chrome (port 18800) çalışır çünkü full browser state korunur.

**Notebooklm-mcp v2.0.11 ek detay:**
- **client.py L90:** `self.driver = uc.Chrome(options=options, version_main=149, headless=False)` — `headless=False` **hardcoded**. CLI'da `--headless` geçmek sadece UI'ı gizler, undetected_chromedriver yine GUI modunda Chrome başlatır.
- Config'de `auth.cookies_path: null` → storage_state.json'dan okur (format: `{"cookies": [...]}`). NLM CLI profilleri (`cookies.json`, format: `[...]`) AYNI format değildir.

**Sonuç:** MCP server'ın kendi Chrome'u ASLA keepalive'daki oturumu kopyalayamaz. Keepalive Chrome (port 18800) TEK güvenilir auth kaynağıdır.

### Recovery Prosedürü (Restart Sonrası)

Restart sonrası keepalive Chrome ölür, çerezler eskimeye başlar. MCP server'ın kendi Chrome'u da çalışmaz. Adımlar:

1. **VNC üzerinden manuel login:** `http://localhost:6080/vnc.html` → NotebookLM'i aç → oturum aç
2. **Keepalive çalıştır:** `python3 ~/.hermes/scripts/nb_keepalive.py` — CDP'den taze çerezleri çeker
3. **Storage state sync:** CDP çerezlerini MCP'nin `~/.notebooklm/profiles/default/storage_state.json`'a da yaz (format dönüşümü gerekir: NLM CLI listesi → `{"cookies": [...]}`)
4. **Gateway restart:** `pkill -f "hermes gateway"` → entrypoint auto-restart eder, MCP yeni storage_state ile başlar
5. **Test:** `mcp_notebooklm_navigate_to_notebook()` ✅ çalışır ama `mcp_notebooklm_chat_with_notebook()` ❌ çalışmaz — bu beklenen bir limitation.

**Not:** Keepalive autologin (`nb_autologin.py`) RotateCookiesPage'e takılırsa veya "Too many failed attempts" hatası alırsa manuel VNC login tek çözümdür.

## Auth Sorunları

### RotateCookiesPage — En Sık Karşılaşılan Blocker

Google periyodik olarak tüm Chrome session'larının çerezlerini geçersiz kılıp `RotateCookiesPage`'e yönlendirir. Bu durumda:

- MCP healthcheck → `authenticated: false`
- Keepalive logs → `✅ CDP cookie extraction succeeded` (YANILTICI — teknik olarak extraction başarılı ama çekilen cookie'ler geçersiz)
- Chrome tab URL'leri `RotateCookiesPage` içerir
- Cookie dosyalarında auth cookie'si sıfırlanır

**Keepalive Tuzağı:** Keepalive loop'u 20 dk'da bir dener, "successful" raporlar, ama değersiz çerezleri çeker. Loop çalışıyor görünse de gerçekte auth yoktur.

**Tek çözüm:** Edel tarayıcıda `notebooklm.google.com`'u açıp `kenshin4155@gmail.com` ile manuel re-login yapmalıdır. Keepalive otomatik toparlayamaz.

**Tespit için:** `/tmp/{p}_dict.json` dosyalarında auth cookie sayısını kontrol et. 0 auth cookie = RotateCookiesPage durumu.

### Keepalive Auto-Heal (Chrome Crash)

Keepalive loop Chrome crash'lerini otomatik tespit edip restart edebilir. Log'da şu pattern aranır:
```
Chrome CDP not responding, attempting restart...
Chrome restarted successfully
```
Bu mekanizma RotateCookiesPage'i çözemez — sadece fiziksel Chrome crash'lerini düzeltir.

### chrome-port-map.json Stale Problem

Keepalive Chrome yeniden başladığında debug port'u değişebilir. `~/.notebooklm-mcp-cli/chrome-port-map.json` eski PID'leri tutar. Gerçek port'ları bulmak için `ps aux` ile `remote-debugging-port` parametresini ara.

## MCP Server Management

NotebookLM MCP server öldüğünde Hermes MCP manager otomatik restart etmeyebilir.

**Kontrol:**
- `ps aux | grep notebooklm-mcp` — process live mı?
- MCP healthcheck → `authenticated: false` ise: auth sorunundan mı yoksa process ölüden mi? (CDP bağlantısı varsa auth, yoksa process restart gerekir)

**Restart:**
1. `kill <PID>` — eski MCP process'ini öldür
2. Bekle 10sn — Hermes bazen restart eder
3. Restart etmezse gateway restart gerekir
4. Auth reset sonrası (Edel re-login): MCP'yi öldür + gateway restart

## Kritik Kurallar

### 1. Unique Message ID'ler
Chrome DevTools Protocol'de HER mesaj için UNIQUE integer ID kullanılmalı.
Aynı ID'yi tekrar kullanmak `"Message must have integer 'id' property"` hatası verir.

```python
gid = [1]
def nid():
    gid[0] += 1
    return gid[0]
```

### 2. Navigate Sonrası Reconnect (EN KRITIK)
Page.navigate sonrası WebSocket mesajları karışır ve Runtime.evaluate cevap vermez.
Navigate'ten sonra MUTLAKA:
1. `time.sleep(12)` bekle
2. `ws.close()` — WebSocket'i KAPAT
3. Aynı tab ID'si ile YENİ WebSocket bağlantısı aç
4. `Runtime.enable` gönder (unique ID ile!)
5. drain()
6. Şimdi Runtime.evaluate çalışır

```python
def reconnect(tab_id):
    tabs = json.loads(urllib.request.urlopen(f'{CDP}/json').read())
    for t in tabs:
        if t.get('id') == tab_id:
            ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=30)
            ws.send(json.dumps({'id':nid(),'method':'Runtime.enable'}))
            time.sleep(0.3); drain(ws)
            return ws
    return None
```

### 3. Tab ID'sini Sakla
Her `json/new` bir tab ID'si döner. Bu ID'yi sakla — reconnect için gerekli.

### 4. eval_js Fonksiyonu
```python
def ev(ws, expr, timeout=10):
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
```

### 5. Account Click (Google Login)
Account chooser'da hesaba tıklamak için:
```javascript
document.querySelector('[data-identifier*="kenshin"]')?.click()
```

### 6. Klavye Girişi (Input.enable)
Klavye girişi yapmadan hemen önce `Input.enable` gönder (unique ID ile).
Her `send_keys` çağrısından önce Input.enable gerekli.

## Dosyalar
- `/tmp/get_creds.py` — bw-serve'den email/şifre/TOTP çeker
- `/tmp/nlm_v2.py` — Tam login + test script'i (referans implementasyon)

## Pitfalls
- ❌ `id:0` birden fazla kez kullanma — Chrome ikinciyi reddeder
- ❌ Navigate sonrası aynı WebSocket'te eval yapma — cevap gelmez, reconnect şart
- ❌ `try: while True: ws.recv()` tek satırda Python'da çalışmaz — `drain()` fonksiyonu kullan
- ❌ `time.sleep(15)` WebSocket buffer taşması yapabilir — 12sn ideal
- ❌ `Input.enable` olmadan `Input.dispatchKeyEvent` çalışmaz
- ❌ `nb_autologin.py` account chooser'da selector uyumsuzluğu nedeniyle takılır — bu CDP client'ı kullan

## İki Hesap Mimarisi

NotebookLM'e iki Google hesabıyla erişilir:

| Hesap | authuser | Email | Rol |
|-------|----------|-------|-----|
| **Pro** | `?authuser=0` | kenshin4155@gmail.com | Ana hesap, Studio'ya tam erişim |
| **Legacy** | `?authuser=1` | isimgorulsunn@gmail.com | İkincil hesap, Studio'ya tam erişim |

**6 Tem 2026 doğrulaması:** Her iki hesap da Studio'ya FULL erişime sahiptir. Studio panelinde 9 farklı artifact türü bulunur.

CDP üzerinden istediğin authuser'a navigate edebilirsin:
```python
nb_url = f'https://notebooklm.google.com/notebook/{NOTEBOOK_ID}?authuser={0 veya 1}'
```

## 🔴 KRİTİK: HER ZAMAN İKİ HESABI DA TEST ET (6 Tem 2026 — Hata Dersi)

**5 Temmuz 2026'da "Pro hesap login'i yok" denildi ama aslında vardı. Bu hata TEKRARLANMAYACAK.**

### Hatanın Kök Nedenleri
1. **Varsayımsal analiz** — Chrome tab'larına bakıp "authuser=0 ana sayfada, demek ki login yok" dedim, fiilen kontrol etmedim
2. **CDP reconnect zorluğundan kaçınma** — Navigate sonrası reconnect sorunu yaşadığım için authuser=0 notebook sayfasına gitmeyi denemedim
3. **Tek authuser'a odaklanma** — Sadece authuser=1 (legacy) sayfasını test ettim, Pro'yu atladım

### Zorunlu Kontrol Listesi (NotebookLM İşlemleri İçin)
- [ ] authuser=0 (Pro/kenshin4155) sayfasını kontrol ettin mi?
- [ ] authuser=1 (Legacy/isimgorulsunn) sayfasını kontrol ettin mi?
- [ ] İkisini de test etmeden "yok" demedin mi?
- [ ] "Yok" dediysen en az 2 farklı method ile doğruladın mı? (CDP + MCP + browser)

### Kural
Bir özelliğin "yok" demek için EN AZ 2 farklı yöntemle test et:
1. Mevcut CDP tab'larında kontrol et
2. Yeni tab açıp o sayfaya navigate et (reconnect ile)
3. Emin değilsen "kontrol edeyim" de, "yok" deme

## Studio Paneli — CDP ile Haritalandırma

Studio, NotebookLM notebook sayfasında `H2: Studio` başlığı altında bulunan bir paneldir. Doğrudan CDP ile kontrol edilebilir.

### Panel Bulma

```python
def find_studio_panel(ws):
    """Studio panelini DOM'da bul, görünür mü kontrol et."""
    return ev(ws, """
    (function(){
        var headings = document.querySelectorAll('h2');
        var panel = null;
        headings.forEach(function(h){
            if((h.textContent||'').trim() === 'Studio') {
                var p = h.closest('[class*=\"studio\" i]') || h.parentElement;
                while(p && !p.className.includes('studio') && p !== document.body) 
                    p = p.parentElement;
                if(p !== document.body) panel = p;
            }
        });
        return JSON.stringify({
            found: !!panel,
            visible: panel ? panel.offsetParent !== null : false,
            html: panel ? panel.outerHTML.substring(0,200) : ''
        });
    })()
    """)
```

### Artifact Buton Haritası (6 Tem 2026)

Studio panelinde bulunan 9 artifact türü:

| # | İkon | Buton Text | aria-label | CSS Class |
|---|------|-----------|------------|-----------|
| 1 | 🎧 | `audio_magic_eraser Sesli Özet chevron_forward` | `"Sesli Özet"` | `blue create-artifact-button-container` |
| 2 | ✏️ | `chevron_forward` (özelleştir) | `"Sesli Özet'i özelleştir"` | `edit-artifact-button` |
| 3 | 📊 | `tablet Slayt Sunusu chevron_forward` | `"Slayt Sunusu"` | `create-artifact-button-container` |
| 4 | ✏️ | `chevron_forward` (özelleştir) | `"Slayt sunusunu özelleştir"` | `edit-artifact-button` |
| 5 | 🎬 | `subscriptions Videolu Özet chevron_forward` | `"Videolu Özet"` | `green create-artifact-button-container` |
| 6 | 🧠 | `flowchart Zihin Haritası chevron_forward` | `"Zihin Haritası"` | `create-artifact-button-container` |
| 7 | 📑 | `auto_tab_group Raporlar chevron_forward` | `"Raporlar"` | `create-artifact-button-container` |
| 8 | 🃏 | `cards_star Bilgi kartları chevron_forward` | `"Bilgi kartları"` | `create-artifact-button-container` |
| 9 | ❓ | `quiz Test chevron_forward` | `"Test"` | `cyan create-artifact-button-container` |
| 10 | 📈 | `stacked_bar_chart İnfografik chevron_forward` | `"İnfografik"` | `create-artifact-button-container` |
| 11 | 📋 | `table_view Veri Tablosu chevron_forward` | `"Veri Tablosu"` | `blue create-artifact-button-container` |

Ayrıca:
- **Daralt** butonu: `dock_to_left` / aria-label `"Stüdyo panelini daralt"`
- Her artifact'in sağında `chevron_forward` özelleştirme butonu (tooltip: `"[Tür]'i özelleştir"`)

### Buton Bulma ve Tıklama

```python
def click_studio_button(ws, aria_label_substring):
    """Studio panelinde aria-label'ı belirtilen metni içeren butona tıkla."""
    return ev(ws, f"""
    (function(){{
        var btns = document.querySelectorAll('button, [role="button"]');
        for(var b of btns){{
            var aria = b.getAttribute('aria-label') || '';
            if(aria.includes('{aria_label_substring}')) {{
                b.click();
                return 'clicked: ' + aria;
            }}
        }}
        // Alternatif: text content ara
        var all = document.querySelectorAll('[class*="create-artifact"]');
        for(var el of all){{
            var t = el.textContent || '';
            if(t.includes('{aria_label_substring}')) {{
                el.querySelector('button')?.click();
                return 'clicked via container';
            }}
        }}
        return 'not found';
    }})()
    """)
```

### Audio Overview (Sesli Özet) CDP ile Test

```python
# Studio panelinde Sesli Özet butonunu bul
btn_info = ev(ws, """
(function(){
    var all = document.querySelectorAll('[class*="create-artifact-button"]');
    for(var el of all){
        var t = el.textContent || '';
        var aria = el.getAttribute('aria-label') || '';
        if(t.includes('Sesli Özet') || aria.includes('Sesli Özet')){
            // Buton div'in içindeki asıl button'u bul ve tıkla
            var btn = el.querySelector('button') || el;
            btn.click();
            return JSON.stringify({
                clicked: true, 
                text: t.substring(0,100),
                aria: aria
            });
        }
    }
    return JSON.stringify({clicked: false});
})
""")
```

### CDP Query Pattern (10 Tem 2026)

MCP auth çalışmadığında CDP ile doğrudan NotebookLM'e soru sorulabilir.

```python
# Keepalive Chrome (port 18800) üzerinden NotebookLM'e bağlan
# 1. Tab bul → 2. Navigate → 3. Reconnect → 4. insertText + Enter → 5. DOM'dan yanıt oku
```

Detaylı çalışan kod için `references/cdp-query-pattern.md` dosyasına bak.

### CDP ile Kaynak Ekleme (10 Tem 2026)

MCP `source_add` çalışmadığında CDP ile NotebookLM'e metin kaynağı eklenebilir. Akış:

1. "Kaynak ekle" butonuna tıkla (`.add-source-button`)
2. "Kopyalanan metin" seçeneğini seç (`button` text `Kopyalanan metin`)
3. Açılan textarea'ya (`placeholder="Metni buraya yapıştırın"`) metni yapıştır (chunked, max 10K/chunk)
4. "Ekle" butonuna tıkla (metin girilince otomatik enabled olur)
5. Indexleme için 30-40sn bekle
6. Sorgu gönder ve DOM'dan yanıt oku

Detaylı adımlar ve DOM selector'ları için: `references/cdp-add-source.md`

### Studio vs MCP — Ne Zaman Hangisi? (10 Tem 2026 Güncellemesi)

**MCP (jacob-bd/notebooklm-mcp-cli) artık Studio için BİRİNCİL araçtır.** CDP sadece yedek/YARA durumunda kullanılır.

| Senaryo | Kullan | 
|---------|--------|
| Studio artifact oluşturma (sesli özet, slayt, quiz, vb.) | **MCP** (`studio_create`) veya CLI (`nlm quiz create ...`) |
| Soru-cevap (chat) | **MCP** (`notebook_query`) veya CLI (`nlm query`) | **CDP query** — keepalive Chrome textarea'ya soru yaz + DOM'dan oku (`references/cdp-query-pattern.md`) |
| Kaynak ekleme (URL/metin) | **MCP** (`source_add`) veya CLI (`nlm source add`) | **CDP add-source** — DOM butonlarına tıkla + text yapıştır (`references/cdp-add-source.md`) |
| MCP Studio çalışmıyorsa yedek | **CDP Studio** — Studio butonlarına DOM'dan tıkla |

## Doğrulanmış Akış
1. `json/new` → tab oluştur, tab_id sakla
2. Page.enable + Runtime.enable (unique ID'lerle)
3. drain()
4. Page.navigate → 12sn bekle → ws.close()
5. reconnect(tab_id) → Runtime.enable → drain()
6. Runtime.evaluate → ÇALIŞIR
7. Gerekirse Input.enable → send_keys → Enter
8. Studio paneli için: mevcut notebook tab'ını kullan (yeni navigate gerekmez)
