# Zoom Meeting Recording (Headless Server)

Google Meet'in aksine Zoom'un Hermes plugin'i yoktur. Kayıt için manuel headless browser pipeline'ı gerekir.

## Stack

- **PulseAudio null sink**: Sanal ses cihazı, tarayıcı sesini yakalar
- **Xvfb**: Sanal ekran (headless'ta browser için zorunlu)
- **Chromium (Playwright)**: `--remote-debugging-port` ile CDP kontrolü
- **ffmpeg/parec**: PulseAudio monitor'dan MP3 kaydı

## Kurulum

```bash
# 1. PulseAudio null sink oluştur
pulseaudio --start 2>/dev/null
pactl load-module module-null-sink sink_name=zoom_recording

# 2. Xvfb sanal ekran
Xvfb :99 -screen 0 1280x720x16 -ac &

# 3. Chromium'u ses + ekran yönlendirmesiyle başlat
DISPLAY=:99 PULSE_SINK=zoom_recording /usr/local/bin/chromium \
  --remote-debugging-port=9333 \
  --remote-allow-origins=* \
  --no-first-run --disable-background-networking \
  --disable-sync --no-startup-window \
  --user-data-dir=/tmp/zoom_profile \
  --disable-dev-shm-usage --no-sandbox --disable-gpu 2>/dev/null &

# 4. SES KAYDINI BASLAT (join'i bekleme — meeting'de ses varsa yakalanir)
ffmpeg -y -f pulse -i zoom_recording.monitor -c:a libmp3lame -b:a 128k /tmp/zoom_recordings/seminar.mp3 2>/tmp/ffmpeg.log &

# 5. CDP uzerinden Zoom URL'ine git
websocket_url = f"ws://127.0.0.1:9333/devtools/page/{tab_id}"
# Page.navigate ile Zoom meeting URL'ini ac

# 6. Join butonlarina tikla (guest adi + sifre)
# Page.click, Page.type ile form doldur
```

## CDP WebSocket 403 Pitfall (Chrome 148+)

`--remote-allow-origins=*` flag'i Chrome 148'de **çalışmaz** — WebSocket bağlantıları hala 403 Forbidden döner. **2026-06-12 test:** Python websocket-client ile `header={"Origin": "..."}` eklenmesi de çözmedi. HTTP POST `/devtools/page/{tab_id}/page/navigate` endpoint'i de boş dönüyor olabilir.

**Çalışan yaklaşım:** `execute_code` içinden Python `websocket` modülü ile ayrı bir WebSocket bağlantısı kur. `timeout=10` ve `ws.settimeout(5)` ayarlarıyla kısa süreli bağlantılar yap. Uzun `time.sleep()`'ler bağlantı timeout'una neden olur — her `sleep`'ten sonra yeniden bağlan.

```python
import json, websocket
ws = websocket.create_connection(f"ws://127.0.0.1:9333/devtools/page/{tab_id}", timeout=15)
def send_cmd(method, params=None):
    msg = {"id": 1, "method": method, "params": params or {}}
    ws.send(json.dumps(msg))
    ws.settimeout(5)
    return json.loads(ws.recv())
```

**Port çakışması:** NotebookLM Chrome'u port 9222'yi kullanır. Zoom için FARKLI port seç (9333, 9444).

**Alternatif: Hermes browser tool'ları** — `browser_navigate`, `browser_click` Playwright kullanır ve SPA'larla daha iyi başa çıkabilir. Ancak PulseAudio ses yönlendirmesi için manuel Chromium başlatmak şart.

## Meeting Join Flow

Zoom web arayüzünde join akışı:
1. Meeting URL → "Launch Meeting" butonu (veya doğrudan join sayfası)
2. "Open Zoom Meetings?" dialog'u → "Cancel" + "Join from Browser" linki
3. İsim gir (guest name) → "Join" butonu
4. Meeting şifresi (varsa) → "Join Meeting"

Tam otomasyon için CDP ile adım adım:
1. `Page.navigate` → Zoom URL
2. `Runtime.evaluate` → "Join from Browser" linkini bul ve tıkla
3. `Runtime.evaluate` → isim input'una guest name yaz
4. `Runtime.evaluate` → Join butonuna tıkla
5. Eğer istemiyorsa: aynı flow ile şifre input'una parolayı yaz

## Kayit: Dogrudan ffmpeg (parec'siz)

```bash
# Dogrudan PulseAudio null sink monitor'dan MP3 kaydi
ffmpeg -y -f pulse -i zoom_recording.monitor -c:a libmp3lame -b:a 128k /tmp/zoom_recordings/seminar.mp3 2>/tmp/ffmpeg.log
```

`parec | ffmpeg` pipeline'ina gerek yok — ffmpeg PulseAudio input'u dogrudan destekler. `-b:a 128k` sohbet kalitesi icin yeterli, seminer/sunum icin 192k kullan.

⚠️ **Kayit join'den ONCE baslatilmalidir.** Kullanici "ses kaydi al yeter" dediginde meeting'e giremesen bile ses varsa kaydedilir.

## Zoom SPA Headless Uyumsuzlugu

Zoom web client (`app.zoom.us/wc/`) React tabanli bir SPA'dir. Headless Chrome'da su sorunlar gorulebilir:

- **Bos sayfa**: `document.body.innerText` bos doner, input'lar gorunmez. React app render edemiyor olabilir.
- **iframe karmasasi**: Zoom PWA wrapper sayfasi (`zoom.us/j/`) bir iframe icinde `app.zoom.us/wc/`'i yukler. Iframe cross-origin olabilir.
- **medya izni**: `--use-fake-ui-for-media-stream` flag'i medya izin dialog'unu atlar ama ses cihazi routing'i etkilemez.

**Cozum stratejisi:**
1. Kaydi BASLAT (join'i bekleme)
2. Sayfa yuklenmesini bekle (SPA'lar 10-15s surebilir)
3. `document.querySelector('#webclient')` ile iframe'i bul
4. Iframe `contentDocument`'ine eris (genelde same-origin)
5. Form elementlerini iframe icinde ara
6. Basarisiz olursa: dogrudan `app.zoom.us/wc/join/<meeting_id>` URL'ine git

SPA tamamen yuklenmezse alternatif: Zoom desktop client'a gec veya telefon dial-in kullan.

## Çoklu Meeting

İki Zoom toplantısını aynı anda kaydetmek için:
- İki farklı PulseAudio null sink (sink_name=zoom1, zoom2)
- İki ayrı Xvfb display (:99 ve :100)
- İki ayrı Chromium portu (9333 ve 9444)
- `delegate_task()` ile paralel başlat

## Browser Tool ile Join (CDP'siz — Tercih Edilen)

CDP WebSocket bağlantı sorunları yaşanıyorsa **Hermes'in kendi browser tool'ları** (`browser_navigate`, `browser_click`, `browser_type`) çok daha güvenilirdir. Tek dezavantaj: browser tool'un Chromium'u PulseAudio'ya yönlendirilemez (ses yakalama olmaz).

**Join akışı (browser tool ile, 12 Haz 2026'da test edildi):**
1. `browser_navigate(url="https://app.zoom.us/wc/{meetingId}/join")`
2. `browser_click(ref="e4")` — "Continue without microphone and camera" (bazen 2 kez gerekir)
3. `browser_type(ref="e3", text="Adınız")` — isim gir (passcode isteniyorsa önce passcode)
4. `browser_type(ref="e4", text="Adınız")` — isim (passcode yoksa)
5. `browser_click(ref="e2")` — "Join" butonu
6. Toplantı içinde: `browser_snapshot(full=true)` ile katılımcı listesi, host bilgisi, Cloud Recording durumu kontrol et

**Meeting metadata extraction (browser console):**
```javascript
// Meeting başlığı (sayfa HTML'inde gömülü)
document.body.innerText.substring(0, 500)
// Medya elementleri
document.querySelectorAll('audio, video').length
// Cloud Recording kontrolü
[...document.querySelectorAll('*')].filter(e => e.textContent.includes('Cloud Recording'))
```

## Parola (Passcode) Nüansları

- **URL'de gömülü pwd:** `?pwd=XCRr7YWvZJKJMG9v4So0phqAYCQkyH.1` — Zoom otomatik olarak passcode'u alır, join sayfasında sorulmaz
- **Ayrı passcode:** URL'de `pwd` yoksa join sayfasında "Meeting Passcode" alanı çıkar
- **Kayıt passcode'ları:** `/rec/` path'indeki kayıtlar CANLI toplantıdan farklı passcode kullanabilir. "478716" canlı toplantıda çalışan passcode, kayıt sayfasında "Wrong passcode" verebilir
- **Passcode yanlışsa:** Browser snapshot'ta "Incorrect Password" veya "Wrong passcode" alert'i görünür — hemen farklı passcode dene

## Cloud Recording Recovery Path

Toplantıda "Cloud Recording is in progress" yazısı görünüyorsa **host zaten kaydediyordur**. Ses yakalayamasan bile:
1. Edel'e "Cloud Recording aktif, host kaydediyor" bildir
2. Meeting ID, host adı, katılımcı sayısını not al
3. Host'tan kaydı talep etmek için bilgileri sakla

## Headless Ses Yakalama Başarısızlığı (12 Haz 2026)

**Tam reproduction recipe:**
```bash
# Ortam: Oracle Cloud ARM64 (Ampere), Ubuntu 24.04, kernel 6.17
# Hiçbir ALSA ses cihazı yok: /proc/asound/cards BOŞ

pulseaudio --start
pactl load-module module-null-sink sink_name=zoom_recording
pactl set-default-sink zoom_recording
Xvfb :99 -screen 0 1280x720x16 -ac &

PULSE_SINK=zoom_recording DISPLAY=:99 chromium \
  --remote-debugging-port=9333 --remote-allow-origins=* &

# Chromium Zoom'da toplantıda, ses var (görsel olarak ses var) ama:
pactl list sink-inputs short  # → BOŞ! Chromium PulseAudio'ya bağlanmamış
ffmpeg -f pulse -i zoom_recording.monitor test.mp3  # → 0 byte MP3
```

**Kök neden:** Chromium, ALSA seviyesinde hiç ses cihazı bulamayınca ses pipeline'ını tamamen kapatır. `PULSE_SINK` env değişkeni ALSA cihazı yokluğunu override etmez — Chromium önce bir ALSA cihazı bulmalı, sonra PulseAudio'ya yönlendirebilir. `snd-aloop` veya `snd-dummy` kernel modülü olmadan çalışmaz.

## Troubleshooting

| Sorun | Çözüm |
|-------|-------|
| PulseAudio "Connection refused" | `pulseaudio -k; pulseaudio --start` |
| Chromium snap hataları | `/usr/local/bin/chromium` (Playwright) kullan, snap chromium-browser DEĞİL |
| ffmpeg 0 byte MP3 | `pactl list sink-inputs` BOŞSA → ses cihazı yok. `arecord -l` ile kontrol et. `snd-aloop` gerek |
| Xvfb "cannot open display" | `ps aux | grep Xvfb` ile çalıştığını doğrula |
| Zoom "Unable to connect audio" | Web client audio ayarlari -> "Call using Internet Audio" |
| Port 9222 zaten kullanimda | NotebookLM Chrome'u 9222'yi kullanir — **9333 veya 9444** port sec |
| Zoom sayfasi bos (SPA) | React yuklenmesini bekle (15s), iframe'e erismeyi dene, alternatif: direkt `app.zoom.us/wc/join/ID` |
| CDP WebSocket timeout | Uzun `time.sleep()`'ler baglantiyi koparir — her beklemeden sonra yeniden baglan |
| CDP WebSocket 403 Forbidden | `--remote-allow-origins=*` Chrome 148'de güvenilir değil. Browser tool kullan |
| "Incorrect Password" | URL'deki `pwd=` parametresini kullan veya doğru passcode'u Edel'den iste |
| "Wrong passcode" (kayıt) | Kayıt passcode'u canlı toplantıdan farklı olabilir |
