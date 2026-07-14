---
name: zoom-recording
description: Zoom toplantılarını kaydetme — Chrome+CDP+PulseAudio yöntemi (headless ARM64 ve WSL/lokal PC)
category: productivity
trigger: >-
  Kullanıcı "Zoom", "zoom toplantı", "zoom kaydı", "zoom meeting", "seminer",
  "seminer var" gibi ifadeler kullandığında veya herhangi bir zoom.us URL'i
  paylaştığında otomatik yüklenir.
---

# Zoom Recording — Headless/Yerel Ses Kaydı

## ✅ ÇALIŞAN YÖNTEM (13 Haz 2026 — Kanıtlanmış)

**Zoom web client'a Chrome + PulseAudio + fake media device ile başarılı katılım ve MP3 kaydı.** 🎉

**Not:** Bu skill hem headless ARM64 (Oracle Cloud) hem de WSL/lokal PC (x86_64) ortamlarında çalışır. WSL'de DISPLAY ortam değişkeni ve PulseAudio yapılandırması farklılık gösterebilir — gerekirse `/mnt/c/` altındaki Windows araçları da kullanılabilir.

Başarılı test: 2 YouTube videosu aynı anda oynatılırken 30+ dk kesintisiz kayıt. Transkript: Pollinations whisper-1.

### Çekirdek Mimari

```
Chrome 9333 (--use-fake-device-for-media-stream)
  → PulseAudio null-sink (zoom_rec)
    → ffmpeg (zoom_rec.monitor → MP3)
```

### ffmpeg Background Pattern — `nohup` ile (3 Tem 2026) ⭐

`terminal(background=true)` ile ffmpeg başlatırken env değişkenleri (PULSE_SERVER) kaybolur ve ffmpeg exit 254 alır. Çözüm: ffmpeg'i `nohup` ile sarmala:

**⚠️ 10 Tem 2026 — Docker container'ında farklı yöntem gerekir:**
`cap_drop=ALL` olan Docker container'ında (Debian Trixie) `nohup` + `background=true` da çalışmaz
— ffmpeg hemen exit 254 alır veya hiç başlamaz. Çalışan yöntem: **`delegate_task` ile subagent'te çalıştır.**

Detaylı kod: `references/docker-bootstrap-python.md` (ffmpeg delegate_task bölümü).

```bash
# Doğru:
nohup ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k \
  -t 01:05:00 /home/ubuntu/recordings/dosya.mp3 > /tmp/ffmpeg.log 2>&1 &

# Yanlış (env kaybı):
terminal(background=true, command="ffmpeg -y -f pulse -i zoom_rec.monitor ...")
```

**Wrapper script pattern (argümanlı):**

```bash
#!/bin/bash
SOCK=$(find /tmp -name "native" -type s 2>/dev/null | head -1)
export PULSE_SERVER="unix:$SOCK"
LABEL="${1:-seminer}"
DURATION="${2:-01:05:00}"
nohup ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k \
  -t "$DURATION" "/home/ubuntu/recordings/${LABEL}.mp3" > /tmp/ffmpeg_${LABEL}.log 2>&1 &
```

Mevcut script: `scripts/zoom_switch.sh` (saatlik geçişler için).

### Setup (Her Oturum)

> PulseAudio yoksa (`pactl: command not found`), önce `references/pulseaudio-bootstrap-sid.md`'deki adımları uygula, ardından `scripts/start_pulseaudio.sh` ile başlat.
> 
> **ÖNEMLİ:** pulseaudio extract edilmiş binary'lerle çalışıyorsan, `LD_LIBRARY_PATH`'e modules dizinini de ekle:
> ```bash
> export LD_LIBRARY_PATH=/tmp/pulseaudio_extract/usr/lib/x86_64-linux-gnu:/tmp/pulseaudio_extract/usr/lib/x86_64-linux-gnu/pulseaudio:/tmp/pulseaudio_extract/usr/lib/pulse-17.0+dfsg1/modules
> ```

### 🐳 Docker Container Bootstrap (10 Tem 2026)

Mevcut shell script'ler (`start_pulseaudio.sh`, `zoom-chrome-9333.sh`) Oracle Cloud ARM64
gibi systemd'li ortamlarda çalışır. Docker container'ında (Debian Trixie, cap_drop=ALL)
D-Bus system bus olmadığı için **farklı bir yöntem** gerekir:

1. D-Bus session bus `--fork` veya `background=true` ile başlatılamaz
2. Chrome `exec` + `background=true` ile başlatılamaz (process tree zombie olur)
3. Çözüm: **Python `subprocess.Popen` + `start_new_session=True`**

Detaylı adımlar ve çalışan Python kodu: `references/docker-bootstrap-python.md`

```bash
# 1. PulseAudio null-sink
pactl load-module module-null-sink sink_name=zoom_rec

# 2. Chrome başlat (KRİTİK: disable-gpu KULLANMA!)
# İki alternatif Chrome binary'si:
#   - Playwright: /data/ubuntu/cache/ms-playwright/chromium-1223/chrome-linux/chrome
#   - Sistem: /usr/bin/chromium (debian/ubuntu)
# İkisi de aynı flag'lerle çalışır. Hangisi varsa kullan.
PULSE_SINK=zoom_rec DISPLAY=:99 \
  /data/ubuntu/cache/ms-playwright/chromium-1223/chrome-linux/chrome \
  --no-sandbox --remote-debugging-port=9333 --remote-allow-origins=* \
  --user-data-dir=/tmp/zoom_profile --no-first-run \
  --no-default-browser-check --disable-features=TranslateUI \
  --ozone-platform=x11 --window-size=1280,720 \
  --use-fake-device-for-media-stream --use-fake-ui-for-media-stream &

# 3. ffmpeg kaydı başlat (önce başla ki lobby sesi kaçmasın)
ffmpeg -y -f pulse -i zoom_rec.monitor \
  -c:a libmp3lame -b:a 128k /home/ubuntu/seminer_kaydi.mp3 &
```

### Saatlik Bölünmüş Kayıt (2 Tem 2026) ⭐

Aynı Zoom linki üzerinden saat başı farklı seminerler yayınlandığında kullanılır.
Her seminer için ayrı MP3 dosyası gerekir. Detaylı pattern: `references/per-hour-split-recording.md`

Özet:
- Her saat başı cron job'u → eski ffmpeg'i kill et → yeni ffmpeg başlat (`-t 01:05:00`)
- Chrome tüm gün açık kalır, sadece ffmpeg değişir
- Tek seferlik (`deliver: local`) cron job'ları ile zamanlanır

### Paralel Çoklu Kayıt (17 Haz 2026 — Kanıtlanmış) ⭐

Aynı anda birden fazla Zoom toplantısı kaydetmek için **her toplantıya ayrı Chrome + ayrı PulseAudio sink + ayrı ffmpeg** gerekir.

**Mimari (2 toplantı için):**

```
Toplantı 1:  Chrome :9333 → PULSE_SINK=zoom_rec   → ffmpeg → meeting1.mp3
Toplantı 2:  Chrome :9334 → PULSE_SINK=zoom_rec_2 → ffmpeg → meeting2.mp3
```

**Neden ayrı Chrome şart:** Tek Chrome'da iki Zoom sekmesi aynı PULSE_SINK'e ses gönderir — kayıtlar birbirine karışır. Her Chrome kendi `PULSE_SINK` env değişkeniyle başlatılmalı.

**Setup (her ek toplantı için):**

```bash
# 1. Yeni PulseAudio null-sink
pactl load-module module-null-sink sink_name=zoom_rec_2

# 2. Yeni Chrome profili + başlat (farklı port ve PULSE_SINK)
# Sistem chromium (/usr/bin/chromium) veya Playwright chromium ikisi de çalışır
mkdir -p /tmp/zoom_profile2/Default
# Preferences dosyasına media pre-grant ekle (setup_recording.sh'teki gibi)

PULSE_SINK=zoom_rec_2 DISPLAY=:99 \
  /data/ubuntu/cache/ms-playwright/chromium-1223/chrome-linux/chrome \
  --no-sandbox --remote-debugging-port=9334 --remote-allow-origins=* \
  --user-data-dir=/tmp/zoom_profile2 --no-first-run \
  --no-default-browser-check --disable-features=TranslateUI \
  --ozone-platform=x11 --window-size=1280,720 \
  --use-fake-device-for-media-stream --use-fake-ui-for-media-stream &

# 3. Yeni ffmpeg (farklı monitor)
ffmpeg -y -f pulse -i zoom_rec_2.monitor \
  -c:a libmp3lame -b:a 128k /home/ubuntu/recordings/zoom_meeting2.mp3 &
```

**Önemli kurallar:**
- Her Chrome farklı `--user-data-dir` kullanmalı (profil çakışmasını önler)
- Her Chrome farklı `--remote-debugging-port` kullanmalı (9333, 9334, 9335...)
- `DISPLAY=:99` tüm Chrome'lar tarafından paylaşılabilir
- ffmpeg'ler birbirinden bağımsızdır — birini durdurmak diğerini etkilemez

### Join Flow (CDP ile — Kanıtlanmış Sıra, 13 Haz 2026)

**Kullanılacak isim:** Toplantıya göre değişir — Edel belirtir. Varsayılan: `Sudenaz`. Alternatif: `Berkcan Ulucan`. (Vanitas DEĞİL — toplantılarda bot ismi görünmez)

**URL Seçimi:**
- `https://app.zoom.us/wc/join/MEETING_ID` — direkt join formu (tercih edilen)
- `https://us05web.zoom.us/j/MEETING_ID?pwd=...` — landing page, "Join from Browser" tıkla
- `https://custom.zoom.us/w/ID?tk=TOKEN` — **webinar** (özel domain, bkz. aşağı)

**Webinar (zoom.us/w/) Join (17 Haz 2026):**

APA gibi kurumsal Zoom hesapları `zoom.us/w/ID?tk=TOKEN` formatında webinar linkleri kullanır.
Bu linkler landing page'e yönlendirir ve "Join from Browser" butonu içerir.

**İki alt varyant:**

**Varyant A — Token'sız / registration gerekli:** Webinar sayfası `zoom.us/webinar/register/...` kayıt formuna yönlendirir. Önce kayıt doldurulur, sonra landing page → "Join from Browser" akışı devam eder.

**Varyant B — Token+passcode (30 Haz 2026):** URL `custom.zoom.us/w/ID?tk=TOKEN&pwd=...&uuid=...` formatındadır. Kayıt formu atlanır, direkt landing page'e düşer. "Join from Browser" tıklanınca PWA iframe (`<iframe id="webclient">`) içinde meeting açar. İframe'de sadece passcode sorulur (`input-for-pwd`). Token kimlik bilgisini taşır — ayrıca isim istenmez.

⚠️ **KRİTİK — PWA iframe:** Varyant B'de meeting client bir `<iframe id="webclient">` içinde yüklenir. CDP ile etkileşim için `document` yerine `iframe.contentDocument` veya `iframe.contentWindow.document` kullanılmalıdır:
```python
idoc = iframe.contentDocument || iframe.contentWindow.document;
pwd = idoc.getElementById('input-for-pwd');
```

Passcode başarılı girilince **bekleme odasına** düşülür ("Please wait, the webinar will begin soon"). Normal meeting'lerdeki gibi ikinci bir Join tıklaması gerekmez.

```python
# 1. Önce landing page URL'i ile git (token gerekli olabilir)
navigate_to_url(CHROME_PORT, FULL_URL_WITH_TOKEN)
time.sleep(8)

# 2. "Join from Browser" linkini bul ve tıkla
cdp_evaluate(ws, '''
  (function() {
    var btns = document.querySelectorAll("button");
    for (var i = 0; i < btns.length; i++) {
      if (btns[i].textContent.trim() === "Join from browser") {
        btns[i].click(); return "clicked button";
      }
    }
    var links = document.querySelectorAll("a");
    for (var i = 0; i < links.length; i++) {
      if (links[i].textContent.includes("Join from Browser")) {
        links[i].click(); return "clicked link";
      }
    }
    return "not found";
  })()
''', user_gesture=True)
time.sleep(6)

# 3. Webinar'da genelde passcode OLMAZ — sadece isim istenir
# input-for-name varsa doldur, yoksa ilk text input'u bul
```

**Webinar vs Normal Meeting Farkları:**
- Webinar'da passcode alanı (`input-for-pwd`) genelde yoktur
- Landing page'ten "Join from Browser" tıklanarak join formuna geçilir
- Tab ID değişimi daha sık olur — her adımda `get_zoom_tab()` ile yeniden bul
- `direct join URL` (app.zoom.us/wc/join/ID) webinar'larda çalışmayabilir
- **Bazı kurumsal Zoom webinarları (APA vb.) kayıt sayfasına yönlendirir** — önce kayıt formu doldurulmalı, sonra "Join from Browser" çıkar

**Webinar Registration Form Fields (APA Pattern):**
Bazı Zoom webinarları `zoom.us/webinar/register/...` sayfasına yönlendirir. Form alanları:
- `question_first_name` (text) — "Berkcan"
- `question_last_name` (text) — "Ulucan"
- `question_email` (text) — Edel'in Gmail'i kullanılır
- `question_org` (text, opsiyonel) — "Bardo Psychology"
- `question_job_title` (text, opsiyonel) — "Clinical Psychology Graduate"
- `input[placeholder*="state"]` (text, opsiyonel) — "İstanbul"
- Submit butonu: text "Register and Join" içerir

Kayıt tamamlandıktan sonra landing page'e döner ("Join from Browser"). Normal join flow devam eder.

**Form Doldurma — Hermes `browser_console` ile JS (2 Tem 2026, CDP alternatifi) ⭐**

CDP WebSocket timeout verdiğinde veya Puppeteer CSP'ye takıldığında,
Hermes'in `browser_console` aracı (port 9222) Zoom formlarını doldurmak için
güvenilir bir alternatiftir:

```javascript
// 1. Input'ları bul
// browser_console(expression: "document.querySelectorAll('input')...")

// 2. Native setter + dispatchEvent ile doldur (React state için ZORUNLU)
var setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
var nameInput = document.getElementById('input-for-name');
setter.call(nameInput, 'Sudenaz');
nameInput.dispatchEvent(new Event('input', {bubbles: true}));
nameInput.dispatchEvent(new Event('change', {bubbles: true}));

// 3. Join butonuna tıkla
document.querySelectorAll('button')[2].click(); // Join = index 2
```

**Avantajı:** Hermes'in CDP supervisor'ı Zoom CSP'sinden etkilenmez.
**Dezavantajı:** browser_* (9222) ses kaydetmez — Custom Chrome'da (9333)
ayrıca join gerekir.

**Input ID'leri:** `input-for-name` (isim), `input-for-pwd` (passcode)

```python
# 1. Navigate to direct join page
target_url = f"https://app.zoom.us/wc/join/MEETING_ID"
# Title "Zoom meeting on web" olana kadar bekle (SPA, 8-10sn)

# 2. Form doldur (native setter + input/change — React için ZORUNLU)
setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set
nameInput = document.getElementById('input-for-name')
setter.call(nameInput, "Sudenaz")
nameInput.dispatchEvent(new Event('input', {bubbles: true}))
nameInput.dispatchEvent(new Event('change', {bubbles: true}))

pwdInput = document.getElementById('input-for-pwd')
setter.call(pwdInput, PAROLA)
pwdInput.dispatchEvent(new Event('input', {bubbles: true}))
pwdInput.dispatchEvent(new Event('change', {bubbles: true}))

# 3. Join butonuna tıkla (userGesture=True — autoplay için ŞART)
document.querySelector('button').click()

# 4. BEKLE 8-10sn → preview session açılır ama overlay kalır
# İKİNCİ KEZ Join tıkla — overlay kalkar
document.querySelector('button').click()  # userGesture=True ile

# 5. BEKLE 5sn → Title "Sudenaz Zoom Toplantısı" ✅
```

**Join Sonrası Doğrulama (Checklist):**
- [ ] Title: `"Sudenaz Zoom Toplantısı"` (host ismi) — toplantıda
- [ ] Body <100 chars — minimal meeting UI
- [ ] `"Unmute"` butonu — mikrofonda mute ✅
- [ ] `"Leave"` butonu — toplantıda olduğumuzu teyit
- [ ] `"Participants"` — katılımcı paneli
- [ ] `"2"` — host + bot = 2 katılımcı
- [ ] Tab URL: `wc/MEETING_ID/join` (join DEĞİL, meeting client) 
- [ ] Blob worker'lar: `WCL_VIDEO_ENCODE`, `WCL_VIDEO_DECODE`, `zoom-tp`

### Ses Doğrulama

```bash
# Kayıtta ses var mı?
ffmpeg -i kayit.mp3 -af "volumedetect" -f null - 2>&1 | grep -E "mean_volume|max_volume"
# -91.0 dB = SESSİZLİK (sorun var)
# -6.9 dB veya daha yüksek = ✅ SES VAR
```

**⏱️ Timing Uyarısı:** Join'den hemen sonra yapılan ses kontrolü **yalancı sessizlik** gösterebilir. Join sonrası Chrome → WebRTC → PulseAudio pipeline'ının oturması 2-3 dakika alır. İlk 3 dakikada -80 dB civarı ölçüm alırsan panik yapma — 6. dakikada tekrar kontrol et. Toplantı içinde host konuşurken yapılan ölçüm en güveniliridir.

### Transkript — Groq Whisper (birincil), Pollinations (yedek)

**Yerel Whisper KULLANMA.** Türkçe kalitesi düşüktür.

**Birincil — Groq Whisper:** Edel tercihi. Groq API key'i `GROQ_API_KEY` olarak BWS'de (Bitwarden Secrets Manager) saklanır. `~/.hermes/bin/bws secret list` ile bul, ID ile al.

- **Endpoint:** `https://api.groq.com/openai/v1/audio/transcriptions`
- **Model:** `whisper-large-v3` (Türkçe için en iyisi)
- **Auth:** `Authorization: Bearer $GROQ_API_KEY`
- **Format:** multipart/form-data
- **Dil:** `tr` zorunlu
- **Komut:**
  ```bash
  curl -s -X POST "https://api.groq.com/openai/v1/audio/transcriptions" \
    -H "Authorization: Bearer *** \
    -F "file=@chunk.mp3" \
    -F "model=whisper-large-v3" \
    -F "language=tr"
  ```
- **Rate limit:** Chunk'lar arasında 2 sn bekle

**Yedek — Pollinations whisper (Groq kapalıysa veya bakiye yetersizse):**

- **Endpoint:** Pollinations proxy (localhost, port 19999)
- **Model:** `whisper-1`
- **Dosya boyutu sınırı:** 25MB üstü böl
- **⚠️ Bilinen sorun:** Pollinations "pollen" bakiye sistemi kullanır. Bakiye tükenirse `PAYMENT_REQUIRED: Insufficient balance` hatası alınır (30 Haz 2026: 0.0012 pollen kalmıştı). Bu durumda Groq'a geç.
- **Bakiye kontrol:** Küçük bir sessizlik MP3'ü ile test: `curl -s -X POST http://localhost:19999/v1/audio/transcriptions -F "file=@test.mp3" -F "model=whisper-1" -F "language=tr"`. 402 dönerse bakiye bitmiş.

### Cron ile Zamanlanmış Join (17 Haz 2026) ⭐

> ⚠️ **Edel'in Tercihi (2 Tem 2026): Cron KULLANMA, manuel takip et.**
> Edel, kayıt takibi için cron job'larına güvenmez. Geçmişte cron'un
> takip etmediği bir kayıt sorun yaratmıştır.
> **Bunun yerine:** 20:00'ye kadar aktif seste kal, her saat başı manuel
> ffmpeg değiştir. Arada Chrome tab'larını ve ses seviyesini kontrol et.
> Cron job'ları sadece Edel açıkça istediğinde kullan.

Setup'ı toplantıdan çok önce yap, join'i cron ile tetikle. Bu sayede:
- PulseAudio/Chrome/ffmpeg başlatma gecikmeleri yaşanmaz
- Join anında sadece CDP komutları çalışır (hızlı, güvenilir)
- Paralel toplantılarda her join bağımsız cron job olarak planlanır

```bash
# Setup: toplantıdan 15-30dk önce manuel başlat
bash setup_recording.sh  # Chrome + PulseAudio + ffmpeg

# Cron: join anı için one-shot cron
cronjob create \
  --name "Zoom Join - Meeting X" \
  --schedule "2026-06-17T19:25:00" \
  --prompt "python3 /path/to/join_script.py" \
  --deliver origin
```

**Cron Join Script Pattern:** Self-contained Python script olmalı:
1. Chrome port'una bağlan (zaten çalışıyor)
2. ffmpeg kontrol et
3. Join sayfasına git
4. Form doldur + join butonu (2 kez)
5. Durum kontrolü yap
6. Sonucu bildir

Script örneği: `references/cdp-websocket-join.py` temel alınarak toplantıya özel yazılır.

### 📋 Transkripsiyon Retry Pattern (30 Haz 2026) ⭐

Post-recording cron job'ı, seminer hâlâ devam ederken (ffmpeg canlı) çalışırsa, kaydı KESME. Bunun yerine:

**ÖNCE DOĞRULA — ffmpeg canlı mı, yoksa sadece çalışıyor mu?** ffmpeg'in çalışıyor olması tek başına yeterli değildir — Chrome çökmüş ve toplantı bitmiş olabilir, ffmpeg o zaman sessizlik kaydeder. Adımları sırayla uygula:

```bash
# 1. ffmpeg canlı mı kontrol et
pgrep -f "ffmpeg.*zoom_rec" && echo "KAYIT DEVAM EDİYOR" || echo "KAYIT BİTTİ"

# 2. Chrome tab'larını kontrol et — toplantı gerçekten devam ediyor mu?
for port in 9333 9334; do
  echo "=== Port $port ==="
  tabs_json=$(curl -sf http://localhost:$port/json 2>/dev/null)
  if [ -n "$tabs_json" ]; then
    echo "$tabs_json" | grep -o '"title":"[^"]*"' | head -5
    echo "$tabs_json" | grep -o '"url":"[^"]*zoom\.us[^"]*"' | head -3
  else
    echo "  Chrome port $port yanıt vermiyor"
  fi
done
# 🔍 Eğer Chrome tab'ları artık meeting URL'i göstermiyor veya port ölüyse
# toplantı bitmiş demektir → ffmpeg'i kill et ve transkripsiyona başla

# 3. ffprobe ile dosya süresini al (status raporu için)
ffprobe -hide_banner /home/ubuntu/recordings/seminer_kaydi.mp3 2>&1 | grep -E "Duration"

# 4. Kayıt devam ediyorsa → retry cron oluştur (relative time)
hermes cron create \
  --name "Transkript Retry - Meeting" \
  --deliver origin \
  --skill "zoom-recording" \
  "30m" \
  "Aynı transkripsiyon görevini tekrar dene."

# 5. Alternatif: exact time schedule
hermes cron create \
  --name "Transkript Retry - Meeting" \
  --deliver origin \
  --skill "zoom-recording" \
  "2026-06-30T22:45:00" \
  "Aynı transkripsiyon görevini tekrar dene."
```

**Kurallar:**
- **ffmpeg canlıyken ASLA `pkill -f ffmpeg` ÇALIŞTIRMA** — bu kaydı yarıda keser
- Retry schedule'ı: `"30m"`, `"15m"`, `"2h"` gibi relative format veya `"2026-06-30T22:45:00"` exact time
- Her retry cron'u kendi bağımsız job ID'sini alır — önceki job'ın durmasını engellemez
- Retry sayısını sınırlamak için `--repeat 5` eklenebilir (maksimum 5 deneme sonra bildirimle dur)
- Retry cron prompt'u mümkün olduğunca **self-contained** olmalı — tüm görev adımlarını içermeli, sadece skill'e güvenmemeli
- Eğer Chrome port'u yanıt vermiyor ama ffmpeg çalışıyorsa → **önce Chrome'u restart et** (Crash Recovery Protocol), eğer restart sonrası toplantı tab'ı yoksa ffmpeg kill edilebilir

**Durum Raporu Formatı (cron delivery):** ffmpeg canlı bulunduğunda, retry cron'u oluştur ve şu formatta raporla:
```
📼 Seminer Kayıt Durumu — [TARİH, SAAT]

| Seminer | Dosya | Boyut | Süre | ffmpeg | Chrome |
|---------|-------|-------|------|--------|--------|
| 📘 [İSİM 1] | [dosya.mp3] | [XX MB] | [ffprobe süresi] | ✅ Canlı | ✅ Port X |
| 📗 [İSİM 2] | [dosya2.mp3] | [XX MB] | [ffprobe süresi] | ✅ Canlı | ✅ Port X |

**ffmpeg durumu:** [açıklama]
**Chrome durumu:** [hangi port'ta hangi meeting açık]
**Yapılan:** [SAAT]'te tekrar denemek üzere retry cron oluşturuldu.
```

> **İpucu:** ffprobe süresi için: `ffprobe -hide_banner dosya.mp3 2>&1 | grep "Duration"`

### 📺 YouTube Canlı Yayın Kaydı (10 Tem 2026) ⭐

YouTube canlı yayınlarını (live stream) kaydetmek için iki yöntem:

**Yöntem A — yt-dlp + ffmpeg (tavsiye edilen):**
```bash
# 1. Canlı formatları listele
export PATH=$PATH:/home/ubuntu/.local/bin
yt-dlp -F --extractor-args "youtube:player_client=android" "URL"

# 2. m3u8 URL'ini al
M3U8_URL=$(yt-dlp -f 91 --get-url --extractor-args "youtube:player_client=android" "URL")

# 3. ffmpeg ile MP3'e çevirerek indir
nohup ffmpeg -y -i "$M3U8_URL" -vn -c:a libmp3lame -b:a 128k \
  -t 02:00:00 "kayit.mp3" > /tmp/yt_ffmpeg.log 2>&1 &
```

**Yöntem B — Browser ile PulseAudio üzerinden kayıt (Zoom ile aynı yöntem):**
- Chrome'da YouTube sayfasını aç (PULSE_SINK=zoom_rec_2 ile)
- ffmpeg ile zoom_rec_2.monitor'den kaydet
- Zoom paralel kaydıyla aynı prensipler

**⚠️ Önemli:** yt-dlp JS runtime gerektirir. `--extractor-args youtube:player_client=android`
olmadan format alınamaz. Canlı yayın henüz başlamamışsa `ERROR: This live event will begin in N minutes` hatası alınır — yayın başlayana kadar bekle, sonra dene.

### 📋 No-Agent Sağlık Kontrolü (10 Tem 2026 — Uzun Kayıtlar İçin) ⭐

Uzun süren kayıtlarda (paralel seminerler, tüm gün etkinlikler) ffmpeg sessizce ölebilir.
Çözüm: **no-agent cron + periyodik health check shell script.**

**Pattern:**
```bash
# ~/.hermes/scripts/healthcheck_seminer.sh
#!/bin/bash
FFPID=$(pgrep -f "ffmpeg.*zoom_rec" | head -1)
if [ -n "$FFPID" ]; then
    echo "✅ ffmpeg PID=$FFPID çalışıyor"
else
    echo "❌ ffmpeg ölü! Chrome canlı mı kontrol et, yeniden başlat."
    # Chrome canlıysa ffmpeg'i yeniden başlat
    nohup ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k \
      -t 00:30:00 "kayit_partN.mp3" > /tmp/ffmpeg_N.log 2>&1 &
fi
```

**Cron kurulumu (no_agent=True):**
```bash
cronjob action=create \\
  name="📼 Sağlık Kontrolü" \\
  schedule="5m" \\
  script="healthcheck_seminer.sh" \\
  repeat=30 \\
  no_agent=True \\
  deliver=origin
```

**Kurallar:**
- `no_agent=True` = LLM çağrısı yok, direkt shell script. Provider limitinden etkilenmez.
- `repeat=N` ile maksimum tekrar sayısı (örn. 30 × 5dk = 2.5 saat)
- Script içinde `nohup ... &` kullan (direkt terminal'de çalışır, `background=true` gerekmez)
- Her part ayrı dosyaya yaz (`part1.mp3`, `part2.mp3`, ...) — ffmpeg crash'inde tüm kayıt gitmez
- **Edel notu:** Sağlık kontrolü cron'ları Edel'in istediği takip mekanizmasıdır. "kaydın düzenli kontrol edilmeli, sorun varsa acil müdahale" talebini karşılar.

**ffmpeg'i `nohup` ile başlatma (önemli nüans):**
- ✅ `terminal("nohup ffmpeg ... &")` → ÇALIŞIR (direkt komut)
- ❌ `terminal(background=true, command="bash script_icinde_nohup.sh")` → ÇALIŞMAZ (env kaybı + exec sorunu)
- ✅ Wrapper script'te `nohup ... &` + `wait $!` → script foreground'da çalışıyorsa çalışır
- ✅ `delegate_task` ile subagent'te ffmpeg başlatmak → en güvenilir yöntem (subagent terminal timeout'u 300sn olsa bile ffmpeg başarıyla tamamlanır)

### ⏰ No-Agent Join Cron + Fail-Safe Bildirim (10 Tem 2026 — KRİTİK DERS) ⭐

**10 Temmuz 2026'da Çocuk Çizim Testleri webinarı kaçırıldı.** 
Kök neden: 3 seminerlik sette 1. ve 2. seminer başarıyla kaydedildi, 3. seminerin join saati
(21:30) unutuldu çünkü:
1. Seminer linki todo listesine dönüştürülmedi
2. Saat 21:00-21:30 arası bekleme moduna geçildi (aktif takip yok)
3. Join anında tetikleyici mekanizma yoktu

**Çözüm — 3 Katmanlı Otomatik Join Sistemi:**

**Katman 1: 📋 Todo Listesi**
Her seminer setinde tüm adımları `todo()` aracına gir. Her adım tamamlanınca sıradakine otomatik geç.

**Katman 2: ⏰ No-Agent Join Cron (join saatine 10dk kala ⭐)**
```bash
# ~/.hermes/scripts/zoom_autojoin.py (self-contained Python script)
# Kullanım:
cronjob action=create \
  name="Join - Seminer Adı" \
  schedule="2026-07-10T21:27:00+03:00" \
  script="zoom_autojoin.py" \
  no_agent=True \
  deliver=origin
# Script çıktısı:
#   OK     → join başarılı, sessiz kal
#   FAIL|. → join başarısız, sebep ile birlikte Edel'e bildirim gider
```

🚨 **Fail-Safe Bildirim formatı (join başarısız olursa Edel'e gider):**
```
🚨 [Seminer Adı]'na giriş YAPILAMADI
⏰ Saat: 21:30
❌ Sebep: Chrome port 9333 ölü / Toplantı bitmiş / PulseAudio yok

Ne yapmalısın: Linki kontrol et veya manuel join dene
```

**Katman 3: 🕐 Saat Başı Proaktif Kontrol**
Bekleme moduna geçme. Her saat başı şu sorguyu otomatik yap:
- "Sıradaki görev ne?"
- "Tüm seminer join'leri için cron kurulu mu?"
- "Chrome/PulseAudio canlı mı?"

**Script: `scripts/zoom_autojoin.py`** (skill altında) — Chrome + PulseAudio kontrolü, tab açma,
Join from Browser tıklama, PWA iframe passcode/isim doldurma, çift join tıklama,
meeting durumu doğrulama. Başarılı → OK, başarısız → FAIL|sebep.

### No-Agent Provider Resilience (2 Tem 2026 — KRİTİK) ⭐

Provider limiti bittiğinde (rate limit, bakiye, model kapalı) LLM çağrısı gerektiren işlemler (cron job prompt) **çalışmaz**. Edel 2 Tem 2026'da deepseek-v4-flash limiti bittiğinde bu sorun yaşandı.

**Çözüm:** Kritik zamanlı işlemlerde `no_agent=True` cron job'ları kullan. Bunlar LLM çağrısı yapmaz, direkt shell script çalıştırır.

```bash
# No-agent cron job oluşturma
cronjob action=create \
  name="📹 Seminer - noagent" \
  schedule="2026-07-02T18:00:00" \
  script="zoom_seminer2.sh"
  no_agent=True \
  deliver=origin
```

**Ne zaman kullanılır:**
- Provider limiti riski varsa (free tier, düşük bakiye)
- Edel'in LLM session'ı aktif olmayabilir
- 20:00'ye kadar süren uzun kayıt seansları

**Wrapper script pattern (argüman iletmek için):**
```bash
# ~/.hermes/scripts/zoom_seminer2.sh
#!/bin/bash
exec /home/ubuntu/.hermes/scripts/zoom_seminer_switch.sh seminer2_1800
```

**Önemli kurallar:**
- `no_agent=True` → script çıktısı doğrudan Edel'e iletilir, LLM yorumu olmaz
- Script'ler **executable** olmalı (`chmod +x` unutulursa cron hata verir)
- Script path ~/.hermes/scripts/ altında, sadece filename
- Argüman geçilemez — ayrı wrapper script yazılmalı
- Edel, no-agent cron'ları **yedek** olarak tercih eder — birincil takip manuel

### ⏱️ Aktif İzleme Zorunluluğu (30 Haz 2026 — KRİTİK DERS)

**ffmpeg çalışıyor olması seminerin devam ettiği anlamına gelmez.** ffmpeg, Chrome çökse veya toplantı bitmiş olsa bile sessizlik kaydetmeye devam eder. Bu, 3+ saatlik gereksiz kayıt dosyalarına yol açar.

**Yapılması gerekenler:**

**1. Join sonrası bir SONRAKİ TUR'DA mutlaka durum raporu ver.** Edel'e şu bilgileri içeren bir özet gönder:
   - Hangi seminere katıldın (hangisi beklemede, hangisi içeride)
   - ffmpeg kayıt durumu
   - Tahmini bitiş saati (başlangıç saatine +1.5-2 saat ekle)

**2. Seminerin ortasında (başladıktan ~1 saat sonra) Chrome tab'larını kontrol et.**
   ```bash
   for port in 9333 9334; do
     curl -sf http://localhost:$port/json 2>/dev/null | \
       python3 -c "import sys,json;[print(f'Port {port}: {t.get(\"title\",\"?\")[:60]}') for t in json.load(sys.stdin) if 'zoom' in t.get('url','')]"
   done
   ```
   - Eğer title "Zoom" veya "Zoom meeting on web" ise → toplantı devam ediyor
   - Eğer title farklıysa veya port yanıt vermiyorsa → toplantı bitmiş olabilir

**3. ffmpeg süresini takip et.** `ffprobe` ile kayıt süresini al:
   ```bash
   ffprobe -hide_banner /home/ubuntu/recordings/seminer_kaydi.mp3 2>&1 | grep Duration
   ```
   Seminer başlangıcına göre makul süreyi aştıysa (örn. 2.5 saat geçtiyse 1.5 saatlik seminer için) → toplantının bittiğini varsay.

**4. Seminer bittiğinde (kullanıcı söylemese bile fark et):**
   - ffmpeg'i kill et (gereksiz sessizlik kaydını durdur)
   - Chrome'ları kapat
   - PulseAudio temizliği yap
   - Transkripsiyona başla
   - Edel'e "Seminerler bitti, kayıtlar hazır, transkript alınıyor" diye bildir

**5. Paralel kayıtlarda HER BİR SEMİNERİ ayrı takip et.** Biri erken bitebilir, diğeri devam edebilir.

ARM64 headless Chrome ~30 dk'da bir zygote crash'i ile sessizce ölür. Toplantı ortasında bu olduğunda:

```
1. TESPİT: curl -sf localhost:PORT/json/version → "ÖLÜ"
2. RESTART: Chrome'u background=true ile aynı parametrelerle başlat
3. DOĞRULA: sleep 5 && curl -sf localhost:PORT/json/version
4. REJOIN: Yeni tab aç → form doldur → çift join (join flow'un aynısı)
5. DEVAM: ffmpeg zaten çalışıyor, restart gerekmez
```

**Önemli:** Crash sadece o port'taki Chrome'u etkiler. Paralel toplantı varsa diğer port etkilenmez.
Kayıtta ~45 sn sessizlik boşluğu olur — kabul edilebilir.

### Kayıt Sonrası Prosedür

⚠️ **ÖNCE KONTROL ET:** `pgrep -f "ffmpeg.*zoom_rec"` ile ffmpeg'in gerçekten öldüğünden emin ol.
Eğer ffmpeg hâlâ canlıysa (seminer devam ediyor), `pkill -f ffmpeg` KAYDI YARIDA KESER.
Canlı kayıt için **Transkripsiyon Retry Pattern**'i uygula, cleanup'i seminer bitince yap.

```bash
# 1. Chrome ve ffmpeg kill
pkill -f "chrome.*remote-debugging-port=9333" || true
pkill -f "ffmpeg.*pulse" || true

# 2. PulseAudio temizlik
pactl list short modules | grep zoom_rec | awk '{print $1}' | xargs pactl unload-module

# 3. Geçici profili temizle
rm temp profile under /tmp/zoom_profile*

# 4. Kayıt dosyasını ~/recordings/ altına taşı
mkdir -p ~/recordings
mv kayit.mp3 ~/recordings/
```

### Browser Tool vs Custom Chrome Ayrımı (KRİTİK)

| Tool | Chrome | Port | Ses Yönlendirme | Kullanım |
|------|--------|------|-----------------|----------|
| Hermes `browser_*` | Playwright (varsayılan) | 9222 | PULSE_SINK yok | Sayfa inceleme ama ses YAKALAYAMAZ |
| Custom Chrome (bu skill) | Manuel başlatma | **9333** | PULSE_SINK=zoom_rec | Ses kaydı için ZORUNLU |

- `browser_*` araçları default Chrome 9222'de çalışır — ses yakalamaz
- Custom 9333 Chrome ffmpeg kaydı için şart — CDP WebSocket veya MCP Puppeteer ile kontrol et

**Custom Chrome'u Kontrol Etme Yöntemleri:**

**Yöntem 1 — CDP WebSocket (Python, TAVSİYE EDİLEN) ⭐:**

**KRİTİK TÜYO — WebSocket URL'i `tab['webSocketDebuggerUrl']`'den al.**
Manuel URL (`ws://localhost:9333/devtools/page/{TAB_ID}`) timeout verebilir.
Doğru kullanım:
```python
from websocket import create_connection
import json, urllib.request

tabs = json.loads(urllib.request.urlopen(f'http://localhost:{PORT}/json').read())
tab = tabs[0]  # veya zoom tab'ını bul
ws = create_connection(tab['webSocketDebuggerUrl'], timeout=15)
# Sonra Runtime.evaluate ile JS çalıştır
```

⚠️ **`Page.enable` ÇAĞIRMA** — gereksizdir ve response dönmeyebilir. Direkt `Runtime.evaluate` ile başla.

Çalışan implementasyon: `references/cdp-websocket-join.py`

**Yöntem 2 — Hermes browser_* araçları (CDP Fallback, 2 Tem 2026) ⭐**
CDP WebSocket timeout verdiğinde veya başka bir sorun olduğunda:
1. Hermes'in kendi browser_* araçlarını (port 9222) UI etkileşimi için kullan
2. Custom Chrome (9333) sadece ses kaydı sağlar — join işlemini ayrıca Custom Chrome'da da tekrarla
3. İki Chrome da aynı Zoom meeting'ine farklı kullanıcılar olarak katılır

```bash
# Adım 1: Hermes browser ile Zoom sayfasına git
# (browser_navigate → form doldur → join)

# Adım 2: Custom Chrome'da yeni tab aç
curl -X PUT "localhost:9333/json/new?https://app.zoom.us/wc/join/MEETING_ID"

# Adım 3: Custom Chrome'da da aynı join flow'u CDP ile tekrarla
python3 join_script.py --port 9333
```

Bu yaklaşımın avantajı: browser_* araçları Zoom CSP'sinden etkilenmez (Hermes'in CDP supervisor'ı çalışır). Detaylı pattern için: `references/dual-browser-strategy.md`

**Yöntem 3 (eski) — MCP Puppeteer (SADECE NAVIGASYON İÇİN):**
```python
mcp_puppeteer_puppeteer_connect_active_tab(debugPort=9333)
mcp_puppeteer_puppeteer_navigate(url="...")
```
⚠️ **KRİTİK: Zoom sayfasında `puppeteer_evaluate` HER ZAMAN `undefined` döner!**
Zoom'un CSP header'ı Playwright/Puppeteer'ın `page.evaluate()` çağrılarını bloklar.
**Form doldurma için MUTLAKA CDP WebSocket veya browser_* kullan.**

**Yöntem 4 — HTTP REST (basit kontroller için):**
```bash
curl http://localhost:9333/json            # Tab listesi
curl http://localhost:9333/json/version     # Browser bilgisi
curl -X PUT "localhost:9333/json/new?URL"  # Yeni tab
```

## Ek Referanslar

- `references/per-hour-split-recording.md` — **Saatlik bölünmüş kayıt pattern'i** (2 Tem 2026): Aynı Zoom linki üzerinden saat başı seminerler için cron tabanlı ayrı kayıt stratejisi.
- `references/dual-browser-strategy.md` — **Dual-browser pattern** (2 Tem 2026): CDP WebSocket timeout verdiğinde Hermes browser_* araçlarını UI fallback'i olarak kullanma stratejisi. browser_* (9222) ile join + Custom Chrome (9333) ile ses kaydı.
- `references/cdp-websocket-join.py` — **ÇALIŞAN CDP WebSocket join implementasyonu** (16 Haz 2026). Puppeteer CSP sorununu aşar, doğrudan websocket-client ile Runtime.evaluate
- `references/live-test-tips.md` — bot detection bypass, real-time audio verification, CDP quirks, puppeteer MCP
- `references/pwa-iframe-join-pattern.md` — **PWA iframe join pattern** (30 Haz 2026): Modern Zoom web client'ı `#webclient` iframe'i içinde yükler. CDP ile iframe'e erişim, iki alt pattern (passcode-only / isim+passcode), örnek kod.
- `scripts/transcribe-all.py` — **Batch transcription** (17 Haz 2026): splits large MP3 recordings into whisper-compatible chunks and transcribes via local Pollinations proxy. `python3 scripts/transcribe-all.py [m1] [m2]`
- `scripts/zoom_switch.sh` — **Saatlik kayıt değiştirici** (3 Tem 2026): no-agent cron job'ları için ffmpeg geçiş script'i. Kullanım: `zoom_switch.sh <label> <süre>` (örn. `zoom_switch.sh seminer2_1800 01:05:00`). Eski ffmpeg'i kill edip yenisini başlatır.
- `scripts/start_pulseaudio.sh` — **PulseAudio bootstrap** (18 Haz 2026): D-Bus + PulseAudio başlatma script'i. Extract'ten çalıştırır, socket'i bulur.
- `scripts/zoom-chrome-9333.sh` — **Custom Chrome 9333 wrapper** (2 Tem 2026): PULSE_SINK=zoom_rec + media pre-grant + doğru flag'ler ile Chrome başlatır. `background=true` için idealdir.
- `references/healthcheck-and-failsafe.md` — **No-Agent sağlık kontrolü + fail-safe join bildirim** (10 Tem 2026): ffmpeg periyodik kontrol, join cron+notification pattern, 3 katmanlı seminer takip sistemi.
- `references/docker-bootstrap-python.md` — **Docker container bootstrap** (10 Tem 2026): PulseAudio 17 + D-Bus + Chrome'u Python subprocess + `start_new_session=True` ile başlatma yöntemi. Shell script'lerin çalışmadığı Docker ortamları için.
- `scripts/zoom_autojoin.py` — **No-Agent join + fail-safe bildirim script** (10 Tem 2026): Chrome+PulseAudio kontrol, CDP join, meeting doğrulama. OK/FAIL çıktısı ile cron dostu.

### Pitfalls

| Sorun | Çözüm |
|-------|-------|
| `--disable-gpu` → ses servisi başlamaz, getUserMedia timeout | ASLA kullanma |
| Fresh Chrome profile → join formu render etmez | NotebookLM profilini kopyala (`/tmp/zoom_profile`) |
| getUserMedia timeout (PulseAudio source bulamaz) | `--use-fake-device-for-media-stream` şart |
| Mic permission headless'ta prompt gösteremez | Preferences'a content_settings pre-grant |
| "Automated bots aren't allowed" hatası | Zoom bot koruması. Her host'ta farklı. Mevcut tab'ı kapat, yeni tab aç + UA override ile dene. Bazı meeting'lerde kalıcı olur — host ayarlarına bağlı |
| "This meeting link is invalid (3001)" | Meeting henüz başlamamış — host'a haber ver, başlatmasını bekle |
| "Join from browser" butonu tıklanmıyor (`browser_click`) | CDP veya puppeteer kullan — Hermes browser_click tetiklemez |
| Join sonrası "Unmute" var ama form hâlâ görünüyor | Join butonuna İKİNCİ KEZ tıkla — overlay kalkar |
| Tab ID değişiyor (SPA navigation) | SPA cross-origin navigation'dan sonra CDP target ID değişir. `curl /json` ile yeni ID'yi bul |
| AudioContext "suspended" kalıyor | Runtime.evaluate'de `userGesture: True` ekle |
| ffmpeg önce başlatılmazsa lobby sesi kaçar | Join'den ÖNCE başlat |
| PulseAudio module ID her seferde değişir | `pactl list short modules \| grep zoom_rec` ile ID'yi bul |
| CDP WebSocket 404/500 | Tab kapandı veya ID değişti. `/json` ile mevcut tab'ları tara |
| `input.value='x'` React state'i tetiklemez | Native setter + dispatchEvent(input + change) ZORUNLU |
| Sayfa body çok kısa (<100 chars) | Normal — meeting UI yüklenmiş demektir. Title kontrol et |
| Title "Error - Zoom" | Meeting başlamamış veya link geçersiz |
| `window.location.href` undefined (puppeteer) | CSP veya cross-origin iframe. CDP Runtime.evaluate kullan |
| **Chrome background process sessiz çıkış (16 Haz)** | `terminal(background=true)` ile başlatılan Chrome bazen exit code 0 ile sessizce çıkar, port 9333 dinlenmez. Çözüm: `sleep 5` sonrası `curl /json/version` ile doğrula. Çalışmazsa tekrar başlat (2-3 deneme normaldir) |
| **Chromium 148 ARM64 ~30dk zygote crash'i (17 Haz)** | Chrome ~30dk'da bir zygote/GPU hatasıyla çöküyor. Belirti: `WebRTC SSRC` hataları + `GpuControl.CreateCommandBuffer transient failure`. ffmpeg kaydı sürüyor ama ses akışı duruyor. **Geçici çözüm:** join script'inde Chrome health check + auto-restart. **Kalıcı çözüm:** Chromium downgrade, snd-aloop, veya alternatif tarayıcı araştırılacak. |
| **Puppeteer evaluate daima undefined (16 Haz)** | Zoom CSP'si Playwright evaluate'ı bloklar. BU NORMALDİR. Form işlemleri için CDP WebSocket kullan, Puppeteer'ı sadece navigate için kullan |
| **Audio auto-joins — "Join Audio" gerekmez (16 Haz)** | Zoom web client join sonrası sesi OTOMATİK bağlar. "Join Audio by Computer" butonu genelde çıkmaz. İkinci Join tıklaması overlay'i kaldırmak için yeterlidir |
| **Custom domain Zoom URL'leri landing page gösterir** | `miuul.zoom.us/j/ID?pwd=...` gibi URL'ler landing page'e yönlendirir. "Join from browser" butonuna tıklamak gerekir. Mümkünse direkt `app.zoom.us/wc/join/ID` kullan |
| **Paralel kayıtta sesler karışıyor (17 Haz)** | Tek Chrome'da iki Zoom sekmesi aynı PULSE_SINK'e yazar. Çözüm: Her toplantı için ayrı Chrome + ayrı PULSE_SINK + ayrı port. |
| **Webinar join formunda passcode alanı yok (17 Haz)** | APA vb. webinar'larda sadece isim istenir. `input-for-pwd` bulunamazsa hata değil — normaldir. İlk text input'una isim yaz, join butonuna tıkla. |
| **Webinar'da "Join from Browser" tıklanmıyor** | Landing page'teki link bazen `button` değil `a` elementidir. `querySelectorAll('a')` ile tara, `textContent.includes("Join from Browser")` ile bul. |
| **Paralel toplantıda ilk kayıt yanlışlıkla durduruluyor (17 Haz)** | Meeting 2 join script'i meeting 1'in ffmpeg'ini KILL ETMEMELİ. Her ffmpeg farklı monitor'den okur (`zoom_rec.monitor` vs `zoom_rec_2.monitor`). Doğrulama: `pgrep -f "ffmpeg.*zoom_rec"` her ikisini de göstermeli. |
| **Chrome ARM64 zygote crash — ~30 dk'da sessiz ölüm (17 Haz)** | Chrome çalışır durumdayken ~30 dk sonra WebRTC `SSRC which doesn't exist` + zygote `NOTREACHED` hatalarıyla exit code 0 ile çıkar. Port yanıt vermez, ffmpeg sessizlik kaydeder. **BU NORMALDIR — ARM64 headless'ta tekrarlayan bir pattern.** Çözüm: Crash Recovery Protocol (aşağıya bak). En kötü ~45 sn boşlukla toparlanır. **Diğer port'taki Chrome (9334) etkilenmez** — sadece crash olanı restart et. |
| **Toplantı ortasında Chrome restart + rejoin (17 Haz)** | Crash sonrası recovery akışı: (1) `curl localhost:PORT` ile ölüyü tespit et, (2) `background=true` ile aynı parametrelerle Chrome'u yeniden başlat, (3) `sleep 5 && curl` ile canlıyı doğrula, (4) yeni tab aç + form doldur + çift join (tam join flow'un aynısı). ffmpeg restart GEREKMEZ — kayıt aynı dosyaya devam eder, sadece crash-boşluk arası sessizlik olur. |
| **Chrome `/json/close/` sonrası çöküyor (17 Haz)** | Zoom tab'ını `/json/close/TAB_ID` ile kapatmak bazen Chrome'u komple çökertir (port yanıt vermez olur). Çözüm: Tab kapatma yerine **yeni tab aç** (`/json/new?URL`). Eski tab'ı olduğu gibi bırak, Chrome kendi temizler. Chrome çökerse: `pkill -f "chrome.*remote-debugging-port=9333"` + yeniden başlat. **Diğer port'taki Chrome'ları (9334) etkilemez.** |
| **Webinar registration form — APA kurumsal (17 Haz 2026)** | Token'lı webinar URL'i bazen doğrudan "Join from Browser" göstermez, `zoom.us/webinar/register/...` sayfasına yönlendirir. `question_first_name`, `question_last_name`, `question_email` alanlarını doldur, "Register and Join" butonuna tıkla. Kayıttan sonra landing page'e döner, normal flow devam eder. |
| **Test join sonrası form state'i bozuluyor (17 Haz)** | Test amaçlı join yapıp Leave ile çıktıktan sonra aynı tab'a tekrar join URL'i gitmek form input'larını render etmez (NO_INPUT hatası). Çözüm: Her join denemesi için **yeni temiz tab** aç. Eski Zoom tab'larını `/json` ile listele ama `/json/close/` KULLANMA — sadece yeni tab aç. |
| **PULSE_SINK env background'da kaybolur (30 Haz)** | `terminal(background=true)` env değişkenlerini miras almaz. Chrome'u wrapper script ile başlat (`#!/bin/bash` içinde `export PULSE_SINK=...`). Doğrulama: `pactl list sink-inputs` ile sink ID'sini kontrol et. |
| **CDP WebSocket URL manuel yazınca timeout (2 Tem)** | `ws://localhost:9333/devtools/page/{TAB_ID}` yerine `tab['webSocketDebuggerUrl']` kullan. HTTP `/json` endpoint'inden dönen URL her zaman doğrudur. |
| **CDP `Page.enable` response dönmez (2 Tem)** | `Page.enable` gereksizdir. Direkt `Runtime.evaluate` ile başla — CDP herhangi bir initialization gerektirmez. |
| **browser_* ile join yapınca Custom Chrome'da da ayrıca join gerekir (2 Tem)** | browser_* (9222) Hermes'in varsayılan Chrome'udur, ses KAYDETMEZ. Custom Chrome'da (9333) da aynı join flow'u tekrarlamazsan ffmpeg sessizlik kaydeder. Dual-browser pattern'ini uygula. |
| **PulseAudio setup script'inde `mkdir` + `set -e` çakışması (2 Tem)** | `set -e` aktifken `mkdir /tmp/dizin` (zaten var) script'i sessizce öldürür. Her zaman `mkdir -p` kullan. |
| **Seminer bittiğini takip etmezsen (30 Haz — KRİTİK)** | ffmpeg çalışıyor diye seminer devam etmiyordur. Join sonrası 1 saat içinde Chrome tab'larını kontrol et. ffprobe ile kayıt süresini izle. Edel'e durum raporu vermeyi unutma. |
| **Kayıt dosyası gereksiz uzar (30 Haz)** | `-t SÜRE` parametresiz ffmpeg sonsuza kadar kaydeder. Tahmini süre + 30dk ekle. Bilinmiyorsa cron retry mekanizması kullan. | | Token+passcode webinar'da meeting `<iframe id="webclient">` içinde yüklenir. CDP için `iframe.contentDocument` kullan. |
| **PulseAudio bg env kaybı (30 Haz)** | `background=true` ile PULSE_SINK env kaybeder. Wrapper script kullan. |
| **Ses doğrulama yalancı sessizlik (30 Haz)** | Join'den hemen sonra volumedetect -80 dB gösterir. Audio pipeline'ın oturması için 3-5 dk bekle, sonra tekrar kontrol et. |
| **`/json/new` PUT ister (17 Haz)** | Chrome `/json/new?URL` icin **PUT** metodu bekler. Dogrusu: `curl -X PUT localhost:9333/json/new?URL`. |
| **D-Bus session bus calismiyor (10 Tem)** | Docker'da `dbus-daemon --fork` calismaz, `exec` + `background=true` da calismaz. Cozum: Python `subprocess.Popen(["dbus-daemon", "--session", ...], start_new_session=True)`. |
| **Chrome zombie oluyor (10 Tem)** | Chrome `exec` ile `background=true` da baslatilinca parent exit 0 döner, child zombie olur. Cozum: Python `subprocess.Popen(start_new_session=True)`. |
| **PulseAudio 17 D-Bus system bus istiyor (10 Tem)** | Session bus baslat, system bus degil. `DBUS_SESSION_BUS_ADDRESS` dogru ayarla. `dbus-daemon --session` kullan. |
| **Seminer join kaçırıldı (10 Tem)** | Bekleme moduna geçince saat fark edilmedi. Çözüm: Her join için 10dk önce no-agent cron kur (scripts/zoom_autojoin.py). Sağlık kontrolü cron'ları ile ffmpeg canlılığını izle. 3 katmanlı sistemi kullan: (1) todo listesi, (2) join cron'u (10dk önceden), (3) saat başı proaktif sorgu. | `module-native-protocol-unix.so` yüklenirken `LD_LIBRARY_PATH`e modul dizinini de ekle: `.../pulse-17.0+dfsg1/modules`. |

## 🔒 Gizlilik ve Güvenlik (17 Haz 2026)

Tüm kayıtlar **tamamen yerel** çalışır — hiçbir bulut servisine upload yapılmaz.

```bash
# Kayıt dosyalarını kilitle (sadece sahibi okuyabilir)
chmod 600 /home/ubuntu/recordings/zoom_meeting*.mp3

# Doğrulama
ls -la /home/ubuntu/recordings/
# -rw------- 1 ubuntu ubuntu ... (600 = sadece ubuntu)
```

**Kurallar:**
- Kayıtlar `/home/ubuntu/recordings/` altında, `chmod 600` ile saklanır
- Transkript sadece Edel istediğinde alınır — otomatik değil
- Toplantıda kullanılan isim Edel'in gerçek adı DEĞİLDİR (Sudenaz / Berkcan Ulucan vb.)
- Kayıt pipeline'ı: PulseAudio → ffmpeg → yerel disk. Cloud servisi YOK
- Kayıtlar transkript alındıktan sonra silinebilir (Edel'in kararı)

### 🚨 KRİTİK DERSLER (16 Haz 2026, güncelleme: 3 Tem 2026)

### 🥉 Üçüncü Altın Kural: Background Process'ler Env Miras Almaz

`terminal(background=true)` ile başlatılan process'ler, shell ortam değişkenlerini (PULSE_SINK, LD_LIBRARY_PATH vb.) **devralmaz**. Bu, paralel Chrome örneklerinde PULSE_SINK'in yanlış sink'e ses göndermesine yol açar.

**Çözüm:** Chrome'u hazır wrapper script'ler ile başlat:
```bash
# 1. Chrome için:
~/.hermes/scripts/zoom-chrome-1.sh --remote-debugging-port=9333 ...

# 2. Chrome için:
~/.hermes/scripts/zoom-chrome-2.sh --remote-debugging-port=9334 ...
```

Script'ler PULSE_SINK + DISPLAY export'u içerir, `background=true` ile çağrılabilir:
```bash
# Örnek kullanım:
terminal(f"~/.hermes/scripts/zoom-chrome-1.sh --no-sandbox --remote-debugging-port=9333 ...", background=True)
```

**⚠️ GEÇMİŞ NOT (2 Tem 2026): `~/.hermes/scripts/zoom-chrome-1.sh` ve `zoom-chrome-2.sh` script'lerinde `--disable-gpu` flag'i VARDI.**\n2 Temmuz 2026'da düzeltildi. Artık doğru flag'leri (`--use-fake-device-for-media-stream`, `--ozone-platform=x11`, vb.) içeriyorlar.\nGüvenle kullanabilirsin.

**Doğrulama:** Join sonrası hangi sink'te olduğunu kontrol et:
```bash
pactl list sink-inputs | grep -E "Sink Input|Sink:|application.process.id"
# Sink: 0 = zoom_rec, Sink: 1 = zoom_rec_2
```

Aynı sorun PulseAudio başlatma için de geçerlidir (LD_LIBRARY_PATH wrapper script ile verilmelidir).

### 🥇 3 Temmuz 2026 — Kampüsten Sahaya Zirvesi Kayıt Dersleri

**Olay:** 4 seminerlik etkinlikte 1. ve 2. seminer başarılı (57dk, 60dk), 3. seminer yarım (8dk), 4. seminer ve Vimeo kaydı hiç başlamadı.

**Kök neden analizi:**

| Sorun | Sebep | Çözüm |
|-------|-------|-------|
| 19:00 kaydı 8dk'da koptu | Chrome zygote crash veya session kesintisi | `-t` parametresi ekle, ffmpeg süre sınırı koy |
| 20:00 geçişi tetiklenmedi | Saatlik cron'lar no-agent çalışmadı | Saatlik geçişlerde no-agent cron + wrapper script **test et** |
| pactl çalışmadı | PulseAudio extract'te LD_LIBRARY_PATH eksik | Alternatif kontrol: `lsof`, `ffprobe` |
| Vimeo kaydı başlamadı | Çift kanal setup'ı tamamlanamadı | Paralel kayıtta önce her iki Chrome'u başlat, sonra her iki ffmpeg'i |
| Session koptu, takip kalmadı | Model switch/provider limiti | Kritik anlarda no-agent cron yedekle |

**Eklenen pitfall'lar:**

| Sorun | Çözüm |
|-------|-------|
| **PulseAudio extract pactl çalışmıyor** | `LD_LIBRARY_PATH`'e modules dizinini ekle: `export LD_LIBRARY_PATH=/tmp/pulseaudio_extract/usr/lib/x86_64-linux-gnu:/tmp/pulseaudio_extract/usr/lib/x86_64-linux-gnu/pulseaudio:/tmp/pulseaudio_extract/usr/lib/pulse-17.0+dfsg1/modules`. Alternatif: `lsof \| grep pulse` ile socket'i bul |
| **ffmpeg -t parametresi yoksa sonsuz kayıt** | `ffmpeg -t 01:05:00` ekle (tahmini süre + 5dk). Bilinmiyorsa 2 saat |
| **Saatlik geçiş cron'u test edilmemiş** | Her geçiş öncesi son kontrol yap: Chrome port canlı mı? ffmpeg çalışıyor mu? |
| **No-agent cron argument geçilemez** | `script="zoom_switch.sh seminer2_1800 01:05:00"` çalışmaz — argümanlar script path'in parçası sayılır. **Her seminer için ayrı wrapper script yaz:** `zoom_s2.sh`, `zoom_s3.sh`, `zoom_s4.sh` gibi, içinde sabit label+path olsun |
| **Chrome crash tespiti gecikmeli** | `curl -sf localhost:9333/json/version` ile her 5dk'da heartbeat |
| **Chrome wrapper script'te `--ozense` typo (3 Tem)** | `--ozense-platform=x11` yazarsan Chrome flag parse edemez, başlamaz. Doğrusu: `--ozone-platform=x11`. `zoom-chrome-9333.sh`'de bulundu ve düzeltildi |
| **mkdir -p unutulursa ffmpeg çıktı hatası (3 Tem)** | ffmpeg öncesi `mkdir -p ~/recordings/klasor_adi` ile çıktı dizinini oluştur. Yoksa ffmpeg "Error opening output: No such file or directory" ile exit 254 alır |
| **No-agent cron'a argüman geçilmez (3 Tem)** | `script="zoom_switch.sh seminer2_1800"` yazarsan hermes tüm string'i script adı sanar. Çalışmaz. Çözüm: Her job için ayrı wrapper script yaz (`zoom_s2.sh`, `zoom_s3.sh`). Argümansız, sadece script adı |
| **Cron one-shot schedule geçersiz format** | `once at 2026-07-05 20:25` yazma — next_run_at: null kalır, tetiklenmez. ISO formatı kullan: `2026-07-05T20:25:00+03:00` |
| **CDP WebSocket response timeout (3 Tem)** | Bazen CDP istekleri response dönmese bile komutlar çalışır. Join script'inde "fire and forget" yap: isteği gönder, response bekleme, 5sn bekle, sonra title kontrol et |

**Kesin kural (3 Tem 2026):** Kayıt başlatırken MUTLAKA `ffmpeg -t` parametresi kullan. Süre bilinmiyorsa `-t 02:00:00` (2 saat) varsayılan.

### 🥇 Periyodik Ses Kontrolü (1 Temmuz 2026 — OTOMATİK)

30 Haz 2026'da Miuul kaydı 179MB sessizlikle sonuçlandı. Bunu erken tespit etmek için hazır script:

```bash
python3 ~/.hermes/scripts/zoom-audio-check.py <kayit_dosyasi.mp3>
```

**Exit code'lar:**
- `0` ✅ Ses normal (> -30 dB)
- `1` ⚠️ Düşük ses (-60 dB ile -30 dB arası)
- `2` ❌ Sessiz kayıt (< -60 dB)
- `3` Hata

**Önerilen kullanım:** Kayıt başladıktan 3 dk sonra, her 5 dk'da bir kontrol et
```bash
sleep 180  # 3 dk bekle (audio pipeline otursun)
python3 ~/.hermes/scripts/zoom-audio-check.py /home/ubuntu/recordings/seminer_kaydi.mp3
if [ $? -eq 2 ]; then
  echo "🔴 SESSİZ KAYIT! Müdahale et!"
fi
```

### 🥉 Kayıt Süresi Yönetimi (30 Haz 2026)

ffmpeg'e `-t SÜRE` parametresi eklemezsen, Chrome kapansa bile kayda devam eder ve dosya sessizlikle şişer. 30 Haz 2026'da seminer bitmesine rağmen 3+ saat kayıt alındı.

**Çözüm:** ffmpeg başlatırken tahmini süreye +30dk ekleyerek `-t` parametresi kullan:
```bash
# 1.5 saatlik seminer için: 2 saat kayıt yeter
ffmpeg -y -f pulse -i zoom_rec.monitor -t 02:00:00 \
  -c:a libmp3lame -b:a 128k kayit.mp3
```

Eğer süre bilinmiyorsa, cron tabanlı transkripsiyon retry mekanizması kullan (yukarıdaki Transkripsiyon Retry Pattern).
Bu skill'i `skill_view` ile yüklediğinde, içindeki adımları OKUMADAN alternatif bir yönteme atlama.
16 Haz 2026'da Camoufox'a geçtim — Chrome+CDP daha hızlı çalışacakken 20 dakika kaybettim.
**Sıra:** Skill'i yükle → Oku → Takip et. Sadece skill'deki yöntem başarısız olursa alternatif ara.

### 🥈 İkinci Altın Kural: Linked Files'ı Kontrol Et
Skill_view() çıktısında `linked_files` varsa, özellikle `references/` altındaki dosyaları da oku.
29 Haz 2026'da pulseaudio kurulumu için references/pulseaudio-bootstrap-sid.md zaten vardı ama atlandı — 30+ tool call kaybı.
**Sıra:** Skill'i yükle → linked_files'ı tara → ilgili referansları oku → uygula.

### 🚫 Camoufox Kullanma (Zoom İçin)
Camoufox (Firefox fork) Zoom'da ÇALIŞMAZ. Landing page'de "Join from browser" tıklanınca
Playwright `FFBrowserContext` bilinen bir crash ile çöker:
```
TypeError: Cannot read properties of undefined (reading 'url')
    at FFBrowserContext.<anonymous>
```
Navigation başarılı olur ama Playwright bağlantısı kopar. Çözüm: Chrome+CDP'ye geç.
Camoufox sadece Google Meet için geçerli bir alternatiftir (meet-bot skill'inde belirtilir).

### 🧩 Skill İsmi Çakışması Çözümü
`skill_view("zoom-recording")` ambiguous hata verirse (2 eşleşme):
- ✅ Asıl Zoom skill'i: `zoom-recording` (productivity klasörü)
- ❌ `meet-bot/references/zoom-recording.md` — Google Meet skill'inin içindeki bir referans notu, skill değil
Google Meet skill'i ayrıdır: **`meet-bot`**

### 🎯 Google Meet Skill'i (Hatırlatma)
Google Meet için ayrı bir skill vardır: **`meet-bot`**
- Google Meet katılımı, transkripsiyon, kayıt
- İçinde Zoom ile ilgili bir referans notu barındırır (meet-bot/references/zoom-recording.md)
- Ama bu bir referanstır, skill değildir. Zoom için `zoom-recording` (productivity) kullan.

## 🔍 Alternatif Araştırması (13 Haz 2026)
**Mevcut yöntem çalışıyor — alternatifler blokaj durumunda devreye girecek.**

### Seçenek A — Zoom RTMS (Resmi Çözüm) 🥇
- Zoom'un bot/notetaker için **resmi ürünü**
- Canlı audio/video/transcript WebSocket üzerinden, Python SDK var
- **SORUN:** Sadece `linux-x64` ve `darwin-arm64` — `linux-arm64` yok (GitHub issue #90)
- Intel/AMD sunucu gerektirir

### Seçenek B — Meeting SDK
- **Bot için resmen yasak:** *"reserved for human use cases"* — hesap askıya alınabilir 🚫

### Seçenek C — py-zoom-meeting-sdk (noah-duncan)
- Meeting SDK Linux Python bindings, coveraj 36/235, erken aşama, ToS riski

### Seçenek D — Redroid (Android Container) ⭐
- Container-based Android, ARM64 native, Zoom APK + ADB ile kontrol
- Araştırılacak: GPU gereksinimi, PulseAudio routing

### Seçenek E — VoIP Telefon (PSTN)
- Bot detection sıfır, ~$0.01/dk. Edel bütçe ayırmadı — rafa kalktı
