---
name: meet-bot
description: "Google Meet ve Zoom toplantılarına otomatik katılım, transkripsiyon ve ses kaydı. meeting-bot skill'ini absorbe etti."
version: 1.9.0
metadata:
  hermes:
    category: meet-bot
---

# Meet-Bot Skill

Google Meet ve Zoom toplantılarına otomatik katılım, transkripsiyon ve ses kaydı.

---

## 🏆 Birincil Yöntem: Direkt `meet_join` Tool'u (CRON DEĞİL)

**Hermes'in resmi `google_meet` plugin'i** kullanılıyor. Plugin Google Meet'in kendi altyazılarını DOM'dan okuyarak transkripsiyon yapar. Ses kaydı veya Whisper gerekmez.

### Kurulum

```bash
hermes plugins enable google_meet
hermes meet install              # pip deps + Chromium
hermes meet setup                # preflight checks
hermes meet auth                 # opsiyonel — guest lobby'yi atlar
```

### Auth — Google'a Giriş Yapma

**Edel her zaman Gmail hesabıyla auth'lu giriş yapar — guest mod kullanılmaz.** auth.json'daki cookie'ler sayesinde lobby'de "Ask to join" beklemeden doğrudan toplantıya girilir.

#### 🏆 Öncelikli Yöntem: ~/.config/chromium/ Profilini Kullan (WSL/lokal PC)

`~/.config/chromium/` profilinde Edel'in `isimgorulsunn@gmail.com` hesabı **zaten login durumda**. SID, HSID, SAPISID, SSID, __Secure-1PSID gibi tüm auth cookie'leri mevcut. Bu profil kullanıldığında **hiçbir 2FA gerekmez** — direkt Meet'e giriş yapılır.

**Pre-flight check:**
```bash
# Cookie'leri doğrula (≥5 Google cookie olmalı)
sqlite3 ~/.config/chromium/Default/Cookies "SELECT COUNT(*) FROM cookies WHERE host_key LIKE '%google.com' AND name IN ('SID','HSID','SSID','APISID','SAPISID','__Secure-1PSID','__Secure-3PSID');" 2>/dev/null

# Hesap adını doğrula
chromium --user-data-dir=/home/ubuntu/.config/chromium --headless=new --dump-dom "https://myaccount.google.com/" 2>/dev/null | grep -oP 'isimgorulsunn|@gmail.com'
```

**Meet'e direkt giriş:**
```bash
chromium --user-data-dir=/home/ubuntu/.config/chromium --headless=new --no-sandbox --disable-gpu "https://meet.google.com/"
```
Not: Hermes browser_* araçları Playwright'un kendi izole profilini kullanır, Edel'in profilini kullanmaz. Meet join için **ya meet_join aracını** (cookie export gerektirir) **ya da direkt chromium komutunu** kullan.

⚠️ **5 Temmuz 2026 dersi:** Önceki session Playwright'un varsayılan anonim profilini kullandı, 2FA'da takıldı, toplantı kaçtı. **Edel'in profilini kullan — ilk seferde çalışır.** Detay: `references/chromium-profile-auth.md`

Dört yöntem, sırayla dene:

| Sıra | Yöntem | Ne Zaman | Açıklama |
|------|--------|----------|----------|
| 0 | **~/.config/chromium/ profili** | WSL/lokal PC'de İLK DENE | Edel'in hesabı zaten login, 2FA gerekmez |
| 1 | **`meet_join`** | Yöntem 0 çalışmazsa | Plugin dener. Başarısız olursa joinedAt=null kalır |
| 2 | **Bitwarden ile browser auth** | Cookie'ler expire olmuşsa | `bw-serve` API'den password + TOTP al, browser'da giriş yap, cookie tazele |
| 3 | **Cookie Export** | Üçü de başarısızsa | Edel'den yeni cookie iste (`references/cookie-export-auth.md`) |

**Pre-flight check (join öncesi ZORUNLU):** Auth durumunu doğrula. Şu sırayla kontrol et:

**1. ~/.config/chromium/ profili (en hızlı):**
```bash
# Cookie sayısını kontrol et
sqlite3 ~/.config/chromium/Default/Cookies "SELECT COUNT(*) FROM cookies WHERE host_key LIKE '%google.com' AND name IN ('SID','HSID','SSID','APISID','SAPISID');" 2>/dev/null
# → 5+ ise direkt kullan, 2FA gerekmez
```

**2. auth.json (meet_join için):**
```bash
python3 -c "import json, time; d=json.load(open('$HOME/.hermes/workspace/meetings/auth.json')); cookies=d.get('cookies',[]); print(f'{len(cookies)} cookie'); [print(f'{\"❌\" if c.get(\"expiry\",0) and c[\"expiry\"] < time.time() else \"✅\"} {c.get(\"name\",\"?\")}') for c in cookies]"
```

**⏰ 5 Temmuz 2026 dersi:** auth.json cookie'leri expire olabilir. Join başarısız olursa (`joinedAt=null, error=null`), önce cookie'leri kontrol et. Eski ise:
   1. Bitwarden ile browser auth dene (Yöntem 2)
   2. Olmazsa Edel'den cookie export iste (Yöntem 3)

**Not:** auth.json zaten mevcutsa (`~/.hermes/workspace/meetings/auth.json`), yeniden auth yapmaya gerek yok — cookie'ler geçerliyse direkt join yapılabilir.

**Auth doğrulama:** `auth.json`'da 5+ Google cookie olmalı:
```bash
python3 -c "import json; d=json.load(open('$HOME/.hermes/workspace/meetings/auth.json')); print(len([c for c in d.get('cookies',[]) if 'google' in c.get('domain','')]), 'Google cookies')"
# → 5+ varsa başarılı
```

**WSL'de (lokal PC):** `hermes meet auth` headed browser ile çalışır. PC başında değilsen:
- **Bitwarden ile browser auth** (Yöntem 2): `bw-serve` (port 8087) → Google hesap item'ı → password + TOTP → browser'da giriş yap
- **Cookie export** ile Edel'in cihazından (`references/cookie-export-auth.md`)
- **Remote node** ile kendi Mac'inden join
- **WARP+ proxy** ile IP maskele (`../devops/warp-proxy/SKILL.md`)

#### 🔐 Yöntem 2: Bitwarden ile Browser Auth (Cookie Tazeleme)

Bu yöntemi `meet_join` joinedAt=null kaldığında ve auth.json cookie'leri expire olduğunda dene.

**bw-serve API (Bitwarden) ile Google hesap bilgilerini al:**
- Port 8087'de auto-started (entrypoint.sh)
- Status kontrol: `GET /status` → "unlocked" olmalı
- Item'ları listele: `GET /list/object/items` → "Google-isimgorulsunn" item'ını bul
- Password ve TOTP: `GET /object/item/{id}` → `login.password` ve `login.totp` field'ları
- TOTP secret varsa: `pyotp.TOTP(secret).now()` ile anlık kod üret

**Browser giriş akışı:**
1. `browser_navigate("https://accounts.google.com/signin")`
2. Email gir (`isimgorulsunn@gmail.com`) → Next
3. Password gir (Bitwarden'dan) → Next
4. 2FA gelirse:
   - TOTP secret varsa → kod üret, gir, Next
   - Yoksa → "Try another way" → "Authenticator app" → Edel'den kod iste
5. **Google Prompt (telefon bildirimi) gelirse:**
   - ⚠️ **EKRANDA BİR SAYI GÖRÜNÜR** — bu sayıyı **HEMEN** Edel'e yaz, telefonda onaylaması için
   - 30 saniye içinde onaylamazsa sayfa düşer, yeniden başlatmak gerekir
   - "Telefonunda şu sayıyı görüyor musun? → [SAYI] → Onayla" şeklinde mesaj at
6. "Couldn't sign you in" hatası:
   - Google browser'ı tanımaz. **accounts.google.com'dan değil, workspace.google.com (Gmail) yolunu dene.**
   - `browser_navigate("https://mail.google.com")` → "Sign into Gmail" linkini tıkla → email/password gir
   - workspace.google.com üzerinden giriş Google Prompt'u tetikler (telefon bildirimi), bot detection'ı atlar
   - Bildirimi onaylamasını iste. Olmazsa cookie export'a geç.

**`host denied admission` hatası:** Bu genelde false positive'dir. Asıl sebep expire olmuş cookie'ler veya bot detection. joinedAt=null + error="host denied admission" → cookie tazele (Yöntem 2 veya 3).

### Join Komutları

```bash
# Basit join (transcribe mode):
hermes meet join "https://meet.google.com/abc-defg-hij" --guest-name Sudenaz

# Headed mod (hata ayıklama):
hermes meet join "https://meet.google.com/abc-defg-hij" --headed

# Realtime mode (bot konuşsun):
hermes meet join "https://meet.google.com/abc-defg-hij" --mode realtime

# Remote node ile (başka makineden):
hermes meet join "https://meet.google.com/abc-defg-hij" --node my-mac

# Süre sınırlı:
hermes meet join "https://meet.google.com/abc-defg-hij" --duration 30m
```

### Vanitas için Doğal Dil Triggerları

- "meeting başladı"
- "toplantı başladı"
- "gir <URL>"
- "katıl <URL>"
- "seminer"
- Herhangi bir meet.google.com URL'i

### Kullanılabilir Tool'lar

| Tool | Ne işe yarar | Parametreler |
|------|-------------|--------------|
| `meet_join` | Toplantıya katıl + transkript başlat | `url` (zorunlu), `mode`, `guest_name`, `duration`, `headed`, `node` |
| `meet_status` | Bot canlı mı, transkript ilerliyor mu? | `node` |
| `meet_transcript` | Transkripti oku | `last=N`, `node` |
| `meet_leave` | Toplantıdan ayrıl | `node` |
| `meet_say` | (Realtime mode) Bot konuşsun | `text`, `node` |

### `meet_say` ile Bot Konuşturma (Realtime Mode)

`--mode realtime` ile join edilmiş toplantıda bot konuşabilir:

```bash
hermes meet say "Merhaba, ben not tutan botum."
```

**Gereksinimler:**
- `OPENAI_API_KEY` veya `HERMES_MEET_REALTIME_KEY` `.env`'de tanımlı
- PulseAudio null-sink kurulu (`hermes meet install --realtime`)
- **Maliyet:** OpenAI Realtime per-audio-minute ücretlidir

### Remote Node (v3) — Uzak Makineden Join

Gateway (headless sunucu) yerine kullanıcının kendi Mac'inde çalıştırma:

**Mac'te (Chrome girişli):**
```bash
pip install playwright websockets && python -m playwright install chromium
hermes plugins enable google_meet
hermes meet node run --display-name my-mac    # sunucu başlar, token verir
```

**Gateway'de (Vanitas'ın çalıştığı yer):**
```bash
hermes meet node approve my-mac ws://<mac-ip>:18789 <token>
hermes meet node ping my-mac                   # erişim testi
hermes meet join <URL> --node my-mac           # remote join
```

### Mimari

```
Hermes Agent -> google_meet plugin -> Playwright Chromium (headless)
  -> meet.google.com -> caption DOM scraping -> transcript.txt
  -> AI agent post-processing (özet, aksiyon maddeleri)
```

### Transkript Konumu

`~/.hermes/workspace/meetings/<meeting-id>/transcript.txt`

### Otomatik Session Cleanup

Session sona erdiğinde bot otomatik toplantıdan ayrılır — orphan Chrome kalmaz.

---

## 🌐 Google Cloud IP Engellemesi

**Google, veri merkezi IP'lerinden TÜM hizmetlerine otomatik erişimi engelliyor.** Bu sadece Meet değil, YouTube, yt-dlp dahil her şey için geçerli.

| Hizmet | Engel | Hata |
|--------|-------|------|
| Google Meet | Giriş + join | `Couldn't sign you in` |
| YouTube (yt-dlp) | Video/audio indirme | `Sign in to confirm you're not a bot` |
| YouTube Transcript API | Altyazı çekme | `IP blocked` |

**Çözümler (zorluk sırasına göre):**
1. **Cookie Export** — Edel'in kendi cihazından (`references/cookie-export-auth.md`)
2. **WARP+ SOCKS5 Proxy** — IP maskeleme (`../devops/warp-proxy/SKILL.md`)
3. **Remote Node** — kullanıcının Mac'inden join (yukarıya bak)

---

## 🔄 Hermes Browser Tools ile Join (Fallback)

**Birincil yöntem her zaman `meet_join` tool'udur.** Aşağıdaki durumlarda browser_* araçları fallback olarak kullanılabilir:
- `meet_join → joinedAt=null, error=null` (sessiz başarısızlık)
- Toplantı "open to anyone" (host onayı gerekmez)
- WSL/lokal PC'de çalışıyorsan (cloud IP engeli yok)

### Browser Join Flow (WSL/lokal PC'de çalışır)

1. `browser_navigate(meet_url)` — pre-join sayfasını açar
2. "Do you want people to see and hear you?" dialog'u gelir → "Continue without microphone and camera" tıkla
3. "Sign in with your Google account" dialog'u gelirse → "Got it" tıkla
4. `browser_type` ile isim gir (guest name)
5. "Join now" butonu aktif olur → tıkla
6. Başarılı: toplantıya katılırsın. Başarısız: "You can't join this video call" hatası (host çıkmış/toplantı bitmiş)

**Sınırlamalar:**
- Cloud/veri merkezi IP'lerinde Chromium blocklanır (`workspace.google.com` yönlenmesi)
- Guest olarak katılırsın (host kabul etmeyebilir)
- auth.json cookie'leri browser_* ile paylaşılmaz

---

## 🧯 Legacy Fallbacks (Plugin Çalışmazsa)

Aşağıdaki yöntemler google_meet plugin'i başarısız olursa devreye girer.

### Camoufox (Firefox Fork) ⭐

Camoufox, C++ seviyesinde anti-detection patch'leri olan bir Firefox fork'udur. ARM64'te Google Meet'in pre-join sayfasını gösterebilen tek tarayıcıdır.

```bash
pip install camoufox
# ~700MB Firefox fork indirir
```

```python
from camoufox import Camoufox

FIREFOX_PREFS = {
    "permissions.default.microphone": 1,
    "permissions.default.camera": 1,
    "media.navigator.permission.disabled": True,
    "media.navigator.streams.fake": True,
    "media.getusermedia.insecure.enabled": True,
}

with Camoufox(headless=True, firefox_user_prefs=FIREFOX_PREFS) as browser:
    page = browser.new_page()
    page.goto(MEET_URL, wait_until="domcontentloaded", timeout=60000)
    # ... join flow
```

**Bilinen sorun:** "Ask to join" tıklamasından sonra Playwright `FFBrowserContext` crash'i — join ZATEN başarılı olmuştur, crash beklenir.

### Chrome CDP via Puppeteer MCP (Port 9222)

NotebookLM Chrome profili (zaten Google hesabına girişli) üzerinden:
1. Port 9222'deki Chrome'a bağlan
2. Meet URL'ini yeni sekmede aç
3. Account chooser'da hesabı seç
4. Join flow'unu tamamla

**⚠️ KRİTİK:** Zoom ve Meet sayfalarında `puppeteer_evaluate` CSP nedeniyle `undefined` döner. Form doldurma için **CDP WebSocket** kullan.

Detaylı workflow ve kod: skill içindeki eski bölümlerde mevcut.

### Firefox Workaround

Chromium blocklanınca Playwright Firefox'a geç:
```python
browser = pw.firefox.launch(headless=not headed)
```

Firefox'a özel davranışlar:
- "Getting ready..." spinner'ı 5-15sn bekler
- "Click Allow" izin dialog'unu kapat
- `permissions` context arg'ında "microphone" desteklenmez

### browser-browserbase Plugin

```bash
hermes plugins enable browser-browserbase
```
Cloud browser + residential proxy ile stealth. Google Meet ile test edilmedi.

---

## 💾 Ses Kaydı Doğrulama (ffmpeg Silence Detection)

```bash
ffmpeg -i kayit.mp3 -af "volumedetect" -f null /dev/null 2>&1 | grep -E "max_volume|mean_volume"
```

| Değer | Anlamı |
|-------|--------|
| `mean_volume: -91.0 dB` | **TAMAMEN SESSİZ** (null sink gürültüsü) |
| `mean_volume: -30.0 dB` | Normal konuşma seviyesi ✅ |
| `max_volume: 0.0 dB` | Clipping var, çok yüksek |

**Pitfall:** PulseAudio null sink + ffmpeg her zaman veri üretir (~256K/10sn sessizde). Dosya boyutu büyümesi toplantıda olunduğu anlamına gelmez.

---

## 🚨 Zoom Desteği

Zoom için Hermes plugin'i YOKTUR. Ayrı skill: `productivity/zoom-recording`

**Özet:** headless Chrome + PulseAudio + ffmpeg ile ses kaydı çalışıyor:
- `--use-fake-device-for-media-stream` ile getUserMedia bypass
- PulseAudio null sink → ffmpeg MP3 kaydı
- CDP WebSocket ile kontrol

Detay: `productivity/zoom-recording/SKILL.md`

## ⏰ No-Agent Join Cron + Fail-Safe Bildirim (Google Meet İçin)

**Bu plan Zoom için olduğu kadar Google Meet için de geçerlidir.** 
Aynı 3 katmanlı sistem Meet join'lerine de uygulanmalıdır:

1. **Todo listesi** — tüm Meet toplantıları adımlara bölünür
2. **No-Agent cron (join'den 10dk önce)** — `meet_join` tool'u ile join dener
   - Başarılı → sessiz
   - Başarısız → Edel'e 🚨 bildirim
3. **Saat başı proaktif kontrol** — her saat başı sıradaki görev sorgulanır

**⚠️ Fark:** Meet join için `meet_join` Hermes tool'u kullanılır (Zoom'daki gibi CDP+Chrome yerine). 
Bu nedenle no-agent script ile değil, **LLM'li cron** ile yapılması gerekir (meet_join tool'una sadece LLM erişebilir).
Ya da browser_* araçları ile browser join flow'u kullanılır.

**Önerilen:** Meet join için de `zoom_autojoin.py` benzeri bir script yazılabilir — 
browser ile Meet sayfasına gidip join flow'unu otomatikleştirir.

---

## Pitfalls

| Hata | Anlamı | Çözüm |
|------|--------|-------|
| `hermes meet auth` headless'ta çalışmaz | X server yok | WARP+, cookie export veya remote node kullan |
| `meet_join → joinedAt=null, error=null` | Plugin join flow'u sessiz başarısız | Camoufox veya Chrome CDP dene. WSL/lokal PC'de browser_* ile join dene |
| `host denied admission` | Host reddetti veya false positive | `status.json` kontrol et. Gerçekten red mi, yoksa browser unsupported mu? |
| `lobby timeout` | Host 5dk içinde kabul/ret etmedi | Host'un toplantıda olduğundan emin ol |
| `browser_navigate → workspace.google.com` | Chromium blocklandı | Camoufox/Firefox kullan |
| `auth.json` confusion | `~/.hermes/auth.json` (credential pool) vs `workspace/meetings/auth.json` (storage state) farklı | Plugin kullanır: `workspace/meetings/auth.json` |
| `Couldn't sign you in` | Google Cloud IP'den otomatik tarayıcı tespiti | Cookie export veya WARP+ proxy |
| "Bu tarayıcı sürümü artık desteklenmiyor" banner'ı | Chromium 148 nightly | Join hala çalışır, banner'ı kapat |
| Chrome zygote crash (~30dk) | ARM64'te headless Chrome periyodik çöker | Crash Recovery Protocol (bkz: zoom-recording skill) |
| `"You can't join this video call"` hatası | Host toplantıdan çıktı veya toplantı kilitlendi | Toplantı bitmiş — kurtarma mümkün değil. Kullanıcıya bildir |
| `Cron one-shot schedule "once at DATE TIME"` | Geçersiz format — `next_run_at: null` olur | ISO formatı kullan: `"2026-07-05T20:25:00+03:00"` |
| ❌ **Playwright anonim profili kullanma** | Edel'in ~/.config/chromium/ profili varken Playwright'un varsayılan izole profilini kullanmak → 2FA takılma | **Önce ~/.config/chromium/ profilini dene** — zaten login, 2FA gerekmez |
| ❌ **Google Prompt sayısını paylaşmama** | 2FA tetiklendiğinde ekrandaki doğrulama sayısını Edel'e söylememek → telefon onayı alınamaz | **EKRANDAKİ SAYIYI HEMEN MESAJ YAZ** — "Telefonunda [SAYI] görünüyor mu? Onayla" |

---

## NotebookLM Arşiv Fallback

notebook: `6c7f3daa-1640-4fad-9917-ec44bc432e58` | label: "Yapay Zeka Araçları"

Bilgi eksikse: `cross_notebook_query("Meet bot cookie ayarları", notebook_names="6c7f3daa")`
