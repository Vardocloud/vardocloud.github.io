---
name: meet-record
description: Google Meet ve Zoom toplantılarını headless Chrome+PulseAudio ile kaydetme — tekli ve paralel kayıt
category: productivity
trigger: >-
  Kullanıcı "toplantı kaydı", "meeting record", "Google Meet", "Zoom", "meet", "seminere gir",
  "toplantıya gir", "kayıt al", "meeting join", "paralel kayıt", "eş zamanlı" gibi ifadeler
  kullandığında otomatik yüklenir.

---

# Meet Record — Online Toplantı Ses/Video Kaydı
## Çalışan Yöntem (13 Haz 2026)

**Google hesabı girişli Chrome (port 9222, NotebookLM profili) + PulseAudio null-sink + ffmpeg ile başarılı kayıt.** NotebookLM Chrome'una yeni sekme açılır, mevcut sekmelere dokunulmaz.

### Akış

```
Bitwarden → bw_secure_get.py "gmail" → /tmp/bw_*.pwd (isteğe bağlı, login cookie kalıcı)
Chrome 9222 (NotebookLM profili, Google login hazır)
  → Puppeteer MCP ile bağlan
  → Meet URL'ine navigate et
  → "Hemen katıl" / "Katılma isteği" butonuna tıkla
  → Mikrofon izni sorarsa "Mikrofon olmadan devam et" seç
  → PulseAudio sink'e ses gider (genelde zoom_rec)
    → ffmpeg zoom_rec.monitor → MP3 (128kbit/s)
```

### Setup

```bash
# 1. PulseAudio null-sink var mı kontrol
pactl list sinks short | grep zoom

# 2. ffmpeg kaydı başlat
ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k /tmp/meet_kaydi.mp3

# 3. Chrome port 9222 (NotebookLM) — Google girişli
# Puppeteer MCP ile bağlan
mcp_puppeteer_puppeteer_connect_active_tab(debugPort=9222)
```

### Google Giriş (İlk Sefer / Cookie Süresi Dolduysa)

```bash
# Şifreyi al (DeepSeek görmez)
python3 ~/.hermes/tools/bw_secure_get.py "gmail"
# → /tmp/bw_*.pwd (600 perms)

# Secure script ile doldur
python3 /tmp/secure_google_login.py
```

Google hesap seçici sekmesi Chrome'da açık kalır. Hesap seçilir, secure script şifreyi doldurur ve Next'e tıklar.

### Meet'e Katılma

**İki tip meeting var:**

| Tip | Buton | Ne zaman |
|---|---|---|
| Herkese açık | "Hemen katıl" (Join now) | Direkt katılabilirsin |
| Host onayı gerekli | "Katılma isteği" (Ask to join) | Host kabul edene kadar bekleme odasında kalınır |

Puppeteer MCP ile buton bul:
```js
const btns = document.querySelectorAll('button');
for (const btn of btns) {
  const t = (btn.textContent || '').trim();
  if (t.includes('Hemen katıl') || t.includes('Katılma isteği')) {
    btn.click(); break;
  }
}
```

**Mikrofon izni:** "Kullanıcıların toplantıda sizi duymasını istiyor musunuz?" diye sorarsa:
```js
// En küçük elementi bul (span.mUIrbf-vQzf8d)
"Mikrofon olmadan devam et" içeren en derin elementi bul ve tıkla
```

**Kamera hatası:** "Kamera bulunamadı" uyarısı çıkar — önemsiz, kapat butonuna tıkla.

### Ses Kontrolü (KRİTİK — Atlanırsa Boş Kayıt)

ÖNCE hangi sink'e bağlı olduğunu kontrol et:
```bash
pactl list sink-inputs | grep -E "application.name|Sink:"
# → Sink: 676 → application.name = "Chromium"
```

İKİ sink olabilir:
- `zoom_rec` (ID 676) — Chromium buraya bağlı ✅
- `zoom_recording` (ID 885) — boşta 

ffmpeg'i Chrome'un bağlı olduğu sink'in monitor'ünden başlat:
```bash
# Doğru: zoom_rec.monitor (Chrome burada)
ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k /tmp/kayit.mp3

# Yanlış: zoom_recording.monitor (boş)
```

### Keepalive & Monitor

Script: `scripts/meet-monitor.py`

```bash
cd /tmp && python3 meet-monitor.py "meet.google.com/esa-jqcr-agj"
```

Her 30sn'de bir:
- Meeting sekmesi hâlâ açık mı kontrol et
- ffmpeg çalışıyor mu kontrol et, düşmüşse restart et
- Dosya büyüyor mu kontrol et

ffmpeg 86400s (24h) timeout ile başlat.

### Rejoin / Erişim Değişikliği Akışı

Meeting'den ayrıldıktan sonra "Toplantıdan ayrıldınız" ekranı gelir:
- **"Yeniden katıl"** → join sayfasına döner
- Erişim tipi değişmişse join butonu da değişir (örn. "Hemen katıl" → "Katılma isteği")

```js
// "Toplantıdan ayrıldınız" ekranından yeniden katıl
const btns = document.querySelectorAll('button');
for (const btn of btns) {
  const t = (btn.textContent || '').trim();
  if (t.includes('Yeniden katıl') || t.includes('Join again')) {
    btn.click(); break;
  }
}
```

### Re-Test / Süreklilik Testi (13 Haz 2026 — Kanıtlanmış)

User'ın "10 dk ara verip tekrar dene" talebi üzerine test edildi:

1. İlk test: 8dk 18sn kayıt ✅ → skill'e kaydedildi
2. 10dk ara → hiçbir şey resetlenmedi (Chrome 9222 ayakta, PulseAudio sink canlı)
3. İkinci test: 6dk 46sn kayıt ✅ — farklı meeting, farklı erişim tipi
4. Üçüncü test: Erişim tipi değiştirildi ("Hemen katıl" → "Katılma isteği"), yeniden join → 6dk 16sn ✅

**Sonuç:** Pipeline sürekliliği koruyor. Skill kaydı, Chrome oturumu, PulseAudio — hepsi 10dk+ boşlukta ayakta kalıyor.

### Re-Test Akışı

User "tekrar dene" dediğinde:
1. Mevcut meeting sayfasını kontrol et (hâlâ açık mı?)
2. Açık değilse → yeniden navigate et
3. Erişim tipini kontrol et (değişmiş olabilir)
4. Join + ffmpeg kayıt başlat
5. Raporla

### Erişim Tipi Değişikliği (Canlı Test — 13 Haz 2026)

Meeting sahibi **"Hemen katıl" ↔ "Katılma isteği"** arasında canlı değişiklik yapabilir. Bu durumda:

1. Sayfa yeniden yüklenince yeni buton tipi gelir
2. "Yeniden katıl" → yeni join sayfası → yeni buton tipi
3. Eskisi gibi join'le — buton metni farklı olabilir

```js
// Hangi buton tipi geldiğini algıla
const txt = document.body.innerText;
if (txt.includes('Hemen katıl')) console.log('OPEN access');
if (txt.includes('Katılma isteği')) console.log('HOST_APPROVAL access');
// Sonra uygun butona tıkla
```

### NotebookLM Chrome Kullanımı (13 Haz 2026 — Teyit Edildi)

NotebookLM'nin Chrome'u (port 9222, profil: `.notebooklm-mcp-cli/chrome-profiles/default`) Google Meet için kullanılabilir:
- **Yeni sekme açılır**, mevcut NotebookLM sekmelerine dokunulmaz
- Auth `configured` kalır, NotebookLM çalışmaya devam eder
- User "notebooklm'i bozmamışsındır" diye sordu — teyit: bozulmamıştır ✅
- Google login cookie kalıcıdır — şifreyi her seferinde girmek gerekmez

### Pitfall'lar

- **İKİ sink var:** `zoom_rec` vs `zoom_recording` — hangisine bağlı olduğunu `pactl list sink-inputs` ile kontrol et. Yanlış sink'ten kayıt = 0 byte.
- **ls size 0 gösterir:** `ls -la` çıktısı 0 byte gösterebilir ama ffmpeg aslında yazıyordur. `process poll` veya `ffprobe` ile kontrol et. `ls -la` çıktısına güvenme, ffmpeg process output'una bak.
- **NotebookLM bozulmaz:** Yeni sekme aç, mevcut NotebookLM sekmelerine dokunma. Auth "configured" kalır. Kullanıcı "notebooklm'i bozmamışsındır" diye sorar — sorun olmadığı teyit edildi.
- **Google login cookie kalıcı:** Chrome 9222 profili çerezleri tutar. Her seferinde şifre girmek gerekmez. İlk login yeterli.
- **"Katılma isteği" bekleme odası:** Host kabul edene kadar bekleme odasında kalınır. Beklerken ses gelmez. Host onaylayınca otomatik geçer.
- **Erişim tipi değişirse:** Meeting sahibi erişim tipini "Hemen katıl" ↔ "Katılma isteği" arasında değiştirebilir. Yeniden katıl butonuna basınca yeni tip algılanır.
- **Kamera hatası = safe:** Google Meet "Kamera bulunamadı" diye uyarır — kapatıp geç. Ses kaydı için önemsiz.
- **Tarayıcı uyarısı:** "Bu tarayıcı sürümü artık desteklenmiyor" — Chromium 148 eski ama çalışır, dikkate alma.

---

## Zoom Web Client ile Kayıt (CDP WebSocket Yöntemi)

Google Meet'ten farklı olarak Zoom, browser üzerinden katılım için **CDP WebSocket** kullanır (Puppeteer MCP yerine). Zoom'un PWA'sı `app.zoom.us/wc/` üzerinden çalışır.

### Akış

```
PulseAudio null-sink oluştur
→ Chrome'u PULSE_SINK=<sink> ile başlat (ayrı user-data-dir)
→ ffmpeg <sink>.monitor → MP3 başlat
→ Chrome CDP WebSocket üzerinden navigate et
→ İsim gir (input-for-name)
→ Mute + Stop Video + Join
→ Computer Audio seç (Join Audio by Computer)
→ Device uyarılarını dismiss et (Got It / Continue without)
→ Kayıt devam eder
```

### Chrome Başlatma

```bash
PULSE_SINK=zoom_rec_2 DISPLAY=:99 \
  chromium --show-component-extension-options \
    --no-default-browser-check --disable-pings --media-router=0 \
    --disable-dev-shm-usage --no-sandbox --disable-gpu \
    --remote-debugging-port=9334 --remote-allow-origins=* \
    --user-data-dir=/home/ubuntu/.hermes/chrome_profile_zoom_9334 \
    --window-size=1280,1024 \
    about:blank
```

### Zoom URL Yapısı

```bash
# Doğrudan meeting join:
https://app.zoom.us/wc/join/<MEETING_ID>?pwd=<PASSCODE>
# Alternatif:
https://miuul.zoom.us/j/<MEETING_ID>?pwd=<PASSCODE>
# (join sayfasına redirect eder)
```

### CDP WebSocket Kontrolü (Python)

Puppeteer MCP'nin aksine Zoom PWA'sı ile websocket-client kullanılır:

```python
import websocket, json

TARGET_ID = "<tab-id-from-json>"
WS_URL = f"ws://localhost:9334/devtools/page/{TARGET_ID}"

def send_cmd(ws, cmd_id, method, params=None):
    msg = {"id": cmd_id, "method": method}
    if params: msg["params"] = params
    ws.send(json.dumps(msg))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == cmd_id: return resp

ws = websocket.create_connection(WS_URL, timeout=15)
send_cmd(ws, 0, "Runtime.enable")

# Sayfada JavaScript çalıştır
r = send_cmd(ws, 1, "Runtime.evaluate", {
    "expression": "document.title",
    "returnByValue": True
})
```

### Zoom Form Alanları & Butonlar

| Element | ID/Text | İşlem |
|---------|---------|-------|
| İsim input | `input-for-name` | `inp.value = 'Name'; dispatch input+change events` |
| Ses kapat | `"Mute"` | `button.click()` |
| Video kapat | `"Stop Video"` | `button.click()` |
| Katıl | `"Join"` | `button.click()` |
| Bilgisayar ses | `"Join Audio by Computer"` veya `"Computer Audio"` | `button.click()` |
| Uyarı onay | `"Got It"` | `button.click()` |
| Mikrofonsuz devam | `"Continue without microphone and camera"` | `button.click()` |

**Önemli:** React uygulaması olduğu için input değeri native setter ile atanmalı:
```js
var nativeSetter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype, 'value'
).set;
nativeSetter.call(inp, 'Sudenaz');
inp.dispatchEvent(new Event('input', {bubbles: true}));
inp.dispatchEvent(new Event('change', {bubbles: true}));
```

### PulseAudio Sink Kontrolü

```bash
# Custom PulseAudio binary
EXTRACT=/tmp/pulseaudio_extract
export LD_LIBRARY_PATH=$EXTRACT/usr/lib/x86_64-linux-gnu:$EXTRACT/usr/lib/x86_64-linux-gnu/pulseaudio:$EXTRACT/usr/lib/pulse-17.0+dfsg1/modules
export PULSE_SERVER="unix:/tmp/pulse-PKdhtXMmr18n/native"

# Null-sink oluştur
$EXTRACT/usr/bin/pactl load-module module-null-sink sink_name=zoom_rec_2

# Sink'leri listele
$EXTRACT/usr/bin/pactl list sinks short

# Chrome'un hangi sink'e bağlı olduğunu kontrol et
$EXTRACT/usr/bin/pactl list sink-inputs | grep -E "Sink:|application.process.id"
```

### ffmpeg Kayıt

```bash
ffmpeg -y -f pulse -i zoom_rec_2.monitor -c:a libmp3lame -b:a 128k \
  -t 02:00:00 /home/ubuntu/recordings/miuul_airflow_16tem2026.mp3
```

---

## Paralel Çoklu Kayıt

Aynı anda iki farklı toplantı kaydedilebilir — her biri ayrı Chrome instance + ayrı PulseAudio null-sink + ayrı ffmpeg.

### Mimari

```
Toplantı #1 (19:30)           Toplantı #2 (20:00)
     │                              │
Chrome 9333                   Chrome 9334
PULSE_SINK=zoom_rec           PULSE_SINK=zoom_rec_2
     │                              │
     ▼                              ▼
zoom_rec (Sink 0)             zoom_rec_2 (Sink 1)
     │                              │
     ▼                              ▼
zoom_rec.monitor              zoom_rec_2.monitor
     │                              │
     ▼                              ▼
ffmpeg -> MP3#1               ffmpeg -> MP3#2
```

### Kurulum Adımları

```bash
# 1. İkinci null-sink'i ekle (birincisi zaten PulseAudio başlatılırken yüklendi)
pactl load-module module-null-sink sink_name=zoom_rec_2

# 2. İkinci Chrome'u başlat (ayrı port, ayrı user-data-dir, ayrı PULSE_SINK)
PULSE_SINK=zoom_rec_2 DISPLAY=:99 chromium --remote-debugging-port=9334 \
  --user-data-dir=~/.hermes/chrome_profile_zoom_9334 ...

# 3. İkinci ffmpeg'i başlat
ffmpeg -y -f pulse -i zoom_rec_2.monitor -c:a libmp3lame -b:a 128k \
  -t 02:00:00 /home/ubuntu/recordings/toplanti2.mp3

# 4. Chrome 9334'ü CDP WebSocket ile kontrol et
python3 /tmp/cdp_zoom_join.py
```

### Kısıtlamalar

- Chrome process'leri aynı X display'ini (:99) paylaşır — görsel karışma olabilir
- Her Chrome instance'ı ayrı PulseAudio sink'e yönlendirilir — ses ayrı kaydedilir
- ffmpeg her sink için ayrı process'tir — biri düşerse diğeri etkilenmez
- İkinci meeting için ayrı user-data-dir kullan — cookie/çakışma olmaz
- İkinci Chrome için `--disable-gpu` önerilir (kaynak tasarrufu)

### Kaynak Kullanımı (test edilen: 2 paralel kayıt)

| Bileşen | CPU | RAM |
|---------|-----|-----|
| Chrome başına | ~%3-5 | ~200-300MB |
| ffmpeg (audio) | ~%1-2 | ~50MB |
| ffmpeg (video) | ~%10-15 | ~200MB+ |
| Xvfb :99 | ~%0 | ~50MB |

### Video+Ses Paralel (Ekran Görüntüsü + Ses)

X11 ekran görüntüsü + ses aynı anda kaydedilebilir:
```bash
ffmpeg -y \
  -video_size 1280x720 -framerate 10 -f x11grab -i :99 \
  -f pulse -i zoom_rec.monitor \
  -c:v libx264 -preset ultrafast -crf 28 \
  -c:a aac -b:a 128k \
  -t 02:00:00 kayit.mp4
```

> ⚠️ x11grab tüm display'i yakalar — birden fazla Chrome penceresi varsa hepsi görünür. İstenen sink'ten ses alınır (zoom_rec — hangi Chrome bağlıysa).

---

### Referanslar

- `references/test-session-2026-06-13.md` — 3 Google Meet test meeting'inin detaylı kaydı
- `references/parallel-zoom-2026-07-16.md` — Paralel Zoom kaydı: Miuul Airflow (20:00) + 19:30 toplantısı
- `scripts/meet-monitor.py` — keepalive + ffmpeg monitor scripti
