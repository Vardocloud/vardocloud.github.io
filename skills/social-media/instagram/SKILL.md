---
name: instagram
description: "Instagram entegrasyonu — auth, Graph API, cookie yönetimi, Reels indirme + transkripsiyon. instagram-reel-indirme skill'ini absorbe etti."
version: 3.0.0
metadata:
  hermes:
    tags: [instagram, social-media, auth, graph-api, n8n, credentials]
    category: social-media
---

# Instagram Entegrasyonu

Hermes üzerinden Instagram yönetimi için auth yöntemleri, credential güvenliği, ve entegrasyon pattern'leri.

## Auth Yöntemleri (5 seçenek)

### 0. Cookie Refresh Cron (Otomatik Bakım) ⭐

Instagram cookie'lerinin sürekli taze kalması için **no_agent cron job** kullan. Haftada bir Playwright ile Instagram'ı ziyaret eder, yeni cookie'leri alır ve API testi yapar.

**Kurulum (tek seferlik):**
```bash
cronjob(action='create',
  name='Instagram Cookie Refresh',
  schedule='0 10 * * *',    # Her gün 10:00 (Edel tercihi)
  script='instagram_cookie_refresh.sh',
  no_agent=True)
```

**Script:** `scripts/instagram_cookie_refresh.sh` — Playwright + WARP ile otomatik refresh.
**Dökümantasyon:** `references/cookie-cron-refresh.md`

**PITFALL — sessionid kaybı:** Script çalıştığında sessionid kaybolursa (Instagram login sayfasına düşmüş demektir) script hata verir ve mevcut cookie'leri korur. Bu durumda Chrome'dan manuel export gerekir.

### 1. Cookie + WARP Direct API (En Pratik) ⭐

Instagram web API'sine cookie tabanlı direkt istek. MCP kurulumu gerektirmez, sadece curl + cookie + WARP.

**Gerekenler:**
- WARP SOCKS5 proxy (warp:1080, `warp=plus`)
- Cookie dosyası Netscape formatında (`~/.hermes/instagram_cookies.txt`, chmod 600)
- Mobile User-Agent (desktop reddedilir)

**Çalışan endpoint:**
```
GET /api/v1/users/web_profile_info/?username=<username>  → profil bilgisi
GET /api/v1/feed/user/<user_id>/?count=6                  → son postlar
GET /api/v1/friendships/show/<user_id>/                    → takip durumu (following, followed_by, outgoing_request, is_private)
```

**Tüm istekler WARP üzerinden gitmeli:**
```bash
curl -s --socks5 warp:1080 \
  -b ~/.hermes/instagram_cookies.txt \
  -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)" \
  -H "X-CSRFToken: <csrftoken>" \
  -H "X-IG-App-ID: 936619743392459" \
  -H "X-Requested-With: XMLHttpRequest" \
  "https://www.instagram.com/api/v1/..."
```

**Gerekli header'lar:** X-CSRFToken (cookie'den), X-IG-App-ID (936619743392459), X-Requested-With (XMLHttpRequest), mobile User-Agent.

**WARP'sız istek → `checkpoint_required` hatası, bot detection tetiklenir!**

### Cookie Preflight Check (API Öncesi ZORUNLU)

API isteğine atlamadan ÖNCE cookie'nin geçerli olduğunu doğrula:

```bash
# 1. Cookie dosyası var mı?
test -f ~/.hermes/instagram_cookies.txt || echo "COOKIE YOK"

# 2. csrftoken içeriyor mu?
grep -q 'csrftoken' ~/.hermes/instagram_cookies.txt || echo "CSRFTOKEN EKSIK"

# 3. sessionid içeriyor mu?
grep -q 'sessionid' ~/.hermes/instagram_cookies.txt || echo "SESSIONID EKSIK"

# 4. Expired mi? (timestamp kontrol)
awk '{if($5 ~ /^[0-9]+$/ && $5 < systime()) print "EXPIRED: "$6}' ~/.hermes/instagram_cookies.txt
```

Herhangi biri eksikse → Cookie Refresh işlemini çalıştır.

### Cookie Lokasyon Fallback

Cookie şu yollardan birinde olabilir:
- `~/.hermes/instagram_cookies.txt` (standart)
- `~/instagram_cookies_netscape.txt` (alternatif — eski export)
- `~/ig_session_from_cookies.json` (JSON format)
- `~/ig_session.json` (JSON format)

Kullanmadan önce kontrol et, bulunanı `~/.hermes/instagram_cookies.txt`'e kopyala.

### Cookie Refresh (Playwright ile csrftoken Çekme)

Cookie'de `sessionid` var ama `csrftoken` yoksa, veya cookie süresi dolduysa:

1. Playwright ile cookie'leri yükle
2. `instagram.com`'u aç (sayfa otomatik yeni cookie'ler set eder)
3. Tüm cookie'leri `ctx.cookies()` ile çek
4. Netscape formatında kaydet (csrftoken dahil)

```python
from playwright.sync_api import sync_playwright

def parse_netscape_cookies(path):
    cookies = []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip(): continue
            parts = line.strip().split("\t")
            if len(parts) >= 7:
                cookies.append({"name": parts[5], "value": parts[6],
                    "domain": parts[0], "path": parts[2],
                    "secure": parts[3] == "TRUE", "httpOnly": False})
    return cookies

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    ctx = browser.new_context(
        proxy={"server": "socks5://warp:1080"},
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) ..."
    )
    ctx.add_cookies(parse_netscape_cookies("~/.hermes/instagram_cookies.txt"))
    page = ctx.new_page()
    page.goto("https://www.instagram.com/", wait_until="networkidle")

    # Tüm cookie'leri al ve Netscape formatında yaz
    fresh_cookies = ctx.cookies()
    with open("~/.hermes/instagram_cookies.txt", "w") as f:
        f.write("# Netscape HTTP Cookie File\n")
        for c in fresh_cookies:
            f.write(f"{c['domain']}\t{'TRUE' if c['domain'].startswith('.') else 'FALSE'}\t"
                    f"{c['path']}\t{'TRUE' if c['secure'] else 'FALSE'}\t"
                    f"{int(c.get('expires', 2147483647))}\t{c['name']}\t{c['value']}\n")
    browser.close()
```

### Pitfall — sessionid kaybı: Refresh sırasında Instagram oturum açık değilse (login sayfası), sessionid cookie'si kaybolur ve yenisi alınamaz. Refresh sonrası kontrol et:
```bash
grep -q 'sessionid' ~/.hermes/instagram_cookies.txt && echo "✅ sessionid var" || echo "❌ sessionid kayboldu"
```
sessionid kaybolduysa → Chrome'dan manuel cookie export gerekir (EditThisCookie).

### No-Agent Cron ile Otomatik Refresh

Haftalık/günlük otomatik refresh için no_agent cron pattern'i:

```bash
cronjob(action='create', name='IgCookieRefresh', schedule='0 10 * * *',
  script='instagram_cookie_refresh.sh', no_agent=True, deliver='origin')
```

Script `instagram_cookie_refresh.sh`: Playwright ile Instagram'ı açar, yeni cookie'leri alır, API testi yapar. Detay: `references/cookie-cron-refresh.md`

**PITFALL — Desktop viewport gerekli:** Mobile viewport ile cookie'ler tanınmayabilir. Desktop viewport + Windows Chrome UA kullan:
```python
ctx = browser.new_context(
    proxy={"server": "socks5://warp:1080"},
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    viewport={"width": 1280, "height": 800}
)
```

**ÖNEMLİ:** Refresh sonrası Instagram API rate-limit yiyebilir ("Please wait a few minutes"). 2-3 dakika bekle, tekrar dene.

### 2. instagrapi (Mobil API — En Hızlı Login) ⚡

Python kütüphanesi, Instagram'ın gerçek mobil API'sini kullanır. Playwright'tan hızlıdır,
session dump/load ile tekrar login gerektirmez. Çoğu challenge tipini otomatik çözer.

**Gerekenler:**
- `pip install instagrapi` (kurulu: venv'de)
- WARP SOCKS5 proxy
- Kullanıcı adı + şifre

**Temel kullanım:**
```python
from instagrapi import Client
cl = Client()
cl.set_proxy("socks5://warp:1080")
cl.login("kullanici", "sifre")
cl.dump_settings("/tmp/session.json")  # tekrar login gerektirmez
```

**PITFALL — `STEP_NAME` / `redirect.async` challenge'ı:**
instagrapi bu yeni Polaris auth challenge'ını çözemez (`ChallengeUnknownStep`).
Belirti: `step_name: "STEP_NAME"`, `bloks_action: "com.bloks.www.ig.challenge.redirect.async"`.
Çözüm: Playwright'a geç, 2FA sayfasında cihaz onayı bekle.

**Cookie dönüştürme:** instagrapi session → Netscape cookie: `references/instagrapi-auth.md`

### 3. Facebook Graph API (Resmi) ⭐

Instagram Business Account üzerinden Graph API ile etkileşim. Reels yükleme, yorum yönetimi, medya listeleme, istatistik çekme.

**Gerekenler:**
- Instagram Business Account ID (örn: `17841478124961208`)
- Facebook Access Token (Graph API Explorer'dan alınır)
- `instagram_basic`, `instagram_content_publish`, `pages_read_engagement` izinleri

**Ön koşullar (ZORUNLU):**
- Instagram hesabı **Business veya Creator** olmalı (kişisel hesapla çalışmaz)
- Instagram hesabı bir **Facebook Page'e bağlı** olmalı
- **Meta Developer hesabı** (ücretsiz)

**Kurulum Adımları (özet):**
1. [developers.facebook.com](https://developers.facebook.com) → **Create App** → **Business** türü seç
2. App Dashboard'da **Add Product** → **Instagram** → **Set Up**
3. İki yöntem: *Instagram Login* (direkt hesap bağlama) veya **Facebook Login** ⭐ (Page bağlantılı — önerilen)
4. Instagram hesabını ekle (public olmalı)
5. Graph API Explorer'da token al → **Exchange for Long-Lived Token** (60 gün)
6. Instagram Business Account ID bul: `/PAGE_ID?fields=instagram_business_account`
7. Token'ı güvenli sakla: `~/.hermes/instagram_graph_token.txt` (chmod 600)

**Token debug:** Token alınca `/debug_token?input_token=$TOKEN` ile doğrula: `is_valid`, `expires_at`, `scopes` (izin listesi), `granular_scopes` (hedef ID'ler) kontrol et.

**Gerekli izinler (scopes):**
| İzin | Kullanım |
|------|----------|
| `instagram_basic` | Temel erişim |
| `instagram_content_publish` | Post/Reels/karusel yayınlama |
| `instagram_manage_comments` | Yorum yönetimi |
| `instagram_manage_insights` | İstatistik |
| `pages_manage_posts` | Sayfa post yönetimi |
| `publish_video` | Video yükleme |
| `instagram_manage_messages` | DM (App Review gerekli) |

**Detaylı kurulum rehberi:** `references/facebook-graph-api-setup.md`

**🔴 CONFIRMED (10 Tem 2026):** Token `expires_at = 0` (süresiz) olsa bile Facebook güvenlik politikası gereği günler/haftalar içinde 190/460 hatası verebilir. "Never expire" garantisi yoktur. Long-lived token (60 gün) yenileme akışını düzenli yapmak gerekir.

### 4. MCP Chrome Session (Cookie tabanlı)

Instagram web'ine Chrome'dan giriş yapıp session cookie'lerini MCP server'a ver. Token süresi derdi yok, gerçek kullanıcı gibi davranır.

**MCP Sunucuları:**
- [`instagram-server-next-mcp`](https://mcp.so/server/instagram-server-next-mcp) — Chrome login session kullanır
- [`ig-mcp`](https://github.com/jlbadano/ig-mcp) — Graph API wrapper, production-ready

**Avantaj:** Token yenileme yok, Instagram bot detection'ına karşı daha dayanıklı (gerçek tarayıcı fingerprint'i).

**Dezavantaj:** Periyodik cookie export gerekebilir (Instagram session süresine bağlı).

### 5. Üçüncü Parti (Postiz / Composio / Genviral)

Hermes'e MCP olarak bağlanan hazır servisler.

- **Composio:** [Instagram MCP for Hermes](https://composio.dev/toolkits/instagram/framework/hermes-agent)
- **Postiz:** [Social Media CLI for Hermes](https://postiz.com/hermes-agent) — 30+ platform
- **Genviral:** [Hermes ile Instagram postlama](https://genviral.io/)

**Dezavantaj:** Genelde ücretli, harici servise bağımlılık.

## Credential Çıkarma (n8n Workflow JSON)

n8n workflow JSON export'undan hassas bilgileri çıkarma pattern'i:

```python
import json, re

with open("workflow.json") as f:
    data = json.load(f)

secrets = {}

for node in data["nodes"]:
    params = node.get("parameters", {})
    params_str = json.dumps(params)

    # API keys (general pattern)
    for m in re.finditer(r'[Ss][Kk]_[a-zA-Z0-9]{20,60}', params_str):
        secrets["API_KEY"] = m.group()

    # Header-based API keys
    for hp in params.get("headerParameters", {}).get("parameters", []):
        if "Authorization" in hp.get("name", ""):
            # Extract Bearer token
            pass

    # Query parameter tokens
    for qp in params.get("queryParameters", {}).get("parameters", []):
        if qp.get("name") == "access_token":
            secrets["FB_ACCESS_TOKEN"] = qp["value"]

# Güvenli sakla
with open(".env", "w") as f:
    for k, v in secrets.items():
        f.write(f'{k}="{v}"\n')
os.chmod(".env", 0o600)

# Orijinal JSON'u güvenli sil
# shred -u workflow.json  (Linux)
```

**Güvenlik adımları:**
1. Hassas bilgileri `.env` dosyasına yaz, chmod 600
2. Orijinal JSON'u `shred -u` ile sil (kurtarılamaz)
3. API key'leri asla log/terminal çıktısında gösterme, maskeli kullan

**ZORUNLU — Çıkan token'ı hemen test et:**
Facebook/Instagram Graph API token'ı çıktıysa, süresi dolmuş olabilir (190/460). `curl` ile Graph API'ye `/ME` endpoint'ine test isteği yap. Yanıtta `"error"` varsa token geçersizdir:
- `code: 190, error_subcode: 460` → Token expired (şifre değişmiş veya FB güvenlik nedeniyle sonlandırmış)
- `code: 190, error_subcode: 463` → Token logged out
- Geçerliyse `"name"` ve `"id"` döner

## DM "Görüldü" Yapmadan Okuma (API Inbox Yöntemi)

Instagram'ın `/api/v1/direct_v2/inbox/` endpoint'i thread listesini ve son mesaj önizlemesini verir. Thread açılmadığı için **"Seen" tetiklenmez.**

```bash
curl -s --socks5 warp:1080 \
  -b ~/.hermes/instagram_cookies.txt \
  -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)" \
  -H "X-CSRFToken: <csrftoken>" \
  -H "X-IG-App-ID: 936619743392459" \
  -H "X-Requested-With: XMLHttpRequest" \
  "https://www.instagram.com/api/v1/direct_v2/inbox/?limit=5"
```

**Güvenli mesaj okuma akışı:**
1. API inbox → thread listesi + son mesaj önizlemesi → **SEEN YOK**
2. Önizleme yeterliyse buradan karar ver
3. Tam mesaj lazımsa Playwright ile thread'i aç → Seen OLUR → ama bu noktada zaten cevap yazacaksın

**Alternatif:** Instagram mobil uygulamasında Ayarlar → Gizlilik ve güvenlik → Okundu bilgisi → KAPAT. Sadece mobilde çalışır, web'de yok.

## Web/Mobil Senkronizasyon Gecikmesi (PITFALL)

Instagram web ve mobil arayüzü arasında durum senkronizasyonu gecikebilir. Takip isteği mobilde kabul edilmiş görünürken web'de dakikalarca "Requested" kalabilir. Teyit için:
- Önce mobil uygulamadan kontrol et
- Web'de `following` sayısındaki değişimi izle (düşüş = etkileşim var)
- 5-10 dakika sonra web'i tekrar kontrol et

## n8n Instagram Pipeline Mimarisi

Tipik bir Instagram Reels pipeline'ı (n8n referans workflow):

```
Google Sheets (konu havuzu) → Idea Refiner (AI) → Görsel Üretimi
→ Video Oluşturma (ASS/FFmpeg) → Seslendirme (ElevenLabs TTS) → Telegram Onay
→ Cloudinary Upload → Instagram Graph API (container → publish) → Google Drive Yedek
```

Instagram API akışı:
1. `POST /{ig-user-id}/media` — video container oluştur (media_type=REELS)
2. Status polling — container hazır olana kadar bekle (~2 dk)
3. `POST /{ig-user-id}/media_publish` — creation_id ile yayınla

## ⚠️ ZORUNLU — Fallback Zinciri (Hata Durumunda Alternatif)

Bir yöntem hata verdiğinde ASLA pes etme. Aşağıdaki sırayı takip et:

### Vision/Fallback (browser_vision 401 Authentication Required)

```browser_vision 401 → ALTERNATİF 1: browser_snapshot(full=true) ile metin analizi
                   → ALTERNATİF 2: easyocr ile OCR (yerel, binary gerekmez)
                   → ALTERNATİF 3: Groq Vision (llama-3.2-11b-vision-preview) — API key ✅ var
                   → HİÇBİRİ ÇALIŞMAZSA: kullanıcıya "vision şu anda çalışmıyor, metin bazlı analiz yaptım" de
```

**Adım adım:**

1. **ALTERNATİF 1 — Snapshot metin analizi** (vision tamamen çalışmazsa)
   - `browser_snapshot(full=True)` ile tüm StaticText'leri oku
   - Caption, yorumlar, profil adı, süre bilgisi snapshot'ta her zaman var
   - Yorumlar içeriğin doğasını ortaya çıkarır (olumlu/olumsuz/şüpheci oranı)

2. **ALTERNATİF 2 — easyocr ile OCR** (görselden metin çıkarma)
   ```python
   import easyocr; reader=easyocr.Reader(['tr','en'])
   [print(r[1]) for r in reader.readtext('screenshot.png')]
   ```

### yt-dlp Hata Durumunda Alternatif

| yt-dlp Hatası | Sebep | Ne Yapmalı |
|--------------|-------|-----------|
| `No video formats found` | Post image-only karusel | **ALTERNATİF 1:** Browser ile slaytları tara. **ALTERNATİF 2:** Instagram API'den medya bilgisi çek (curl + WARP). |
| `only available for registered users` | Private/restricted hesap | Browser snapshot ile caption ve yorumları oku. Video içeriğini vision ile analiz et. |
| `Private account` | Hesap gizli | Sadece profil adı + fotoğraf görünür. Daha fazlası için takip gerekir. |

**Alternatif — Instagram API ile karusel görsel URL'lerini çek:**
```bash
curl -s --socks5 warp:1080 \
  -b ~/.hermes/instagram_cookies.txt \
  -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)" \
  -H "X-CSRFToken: $(grep 'csrftoken' ~/.hermes/instagram_cookies.txt | awk '{print $7}')" \
  -H "X-IG-App-ID: 936619743392459" \
  -H "X-Requested-With: XMLHttpRequest" \
  "https://www.instagram.com/api/v1/media/DZH17vTDPvU/info/" 2>/dev/null | python3 -m json.tool
```
Bu endpoint media_id veya shortcode ile çalışır. Yanıtta `carousel_media` dizisindeki her bir öğenin `image_versions2.candidates[0].url` alanı karusel slaytlarının görsel URL'lerini verir.

**⚠️ PITFALL:** Instagram API endpoint'leri değişkendir. Yukarıdaki endpoint çalışmazsa dene:
- `https://www.instagram.com/api/v1/media/{media_id}/info/`
- `https://i.instagram.com/api/v1/media/{shortcode}/info/`
- Browser'daki network isteklerini taklit et (en güvenilir)

### Alternatif Araştırma Prensibi (ZORUNLU — Tüm Skill'ler İçin Geçerli)
**⚠️ İSTİSNA — Karusel görsel üretimi:** Bu genel fallback kuralı karusel görsel üretimi için GEÇERLİ DEĞİLDİR. Karusel görselleri SADECE NotebookLM Studio slide_deck ile üretilir, alternatif araç kullanılmaz. Aşağıdaki adımlar karusel dışındaki tüm işlemler için geçerlidir.

Bir araç/yöntem çalışmadığında izlenecek adımlar SIRAYLA:

1. **DUR —** Hatanın ne olduğunu anla. Hata mesajını oku, hangi adımda koptuğunu tespit et.
2. **DÜŞÜN —** Skill'de bu hata için bir pitfall/çözüm var mı? Varsa uygula.
3. **ALTERNATİF ARA —** Aynı amaca ulaşmak için 3 farklı yol dene:
   - Aynı aracın farklı parametreleri (--cookies, -o, format seçenekleri)
   - Farklı bir araç (yt-dlp → curl + API → browser)
   - Farklı bir yöntem (API → browser → screenshot → vision)
4. **KOMBİNE ET —** Araçları birleştir: yt-dlp video indir → ffmpeg ses çıkar → Groq Whisper transcribe
5. **RAPORLA —** Hangi yöntemlerin çalıştığını/çalışmadığını kullanıcıya belirt. Çalışan yöntemin çıktısını sun.

**Kesinlikle YAPMA:**
- ❌ "Çalışmıyor" deyip geçme
- ❌ Alternatif denemeden pes etme
- ❌ "Manuel yap" önerme (Edel bunu istemez)
- ❌ Hatanın sebebini anlamadan başka yönteme atlama

**Kesinlikle YAP:**
- ✅ Her hata için en az 2 alternatif dene
- ✅ Hatanın sebebini tespit et (log oku, hata kodunu kontrol et)
- ✅ Çalışan yöntemi skill'e ekle / skill'i güncelle
- ✅ Kullanıcıya net rapor ver: hangi yöntemler denendi, hangisi çalıştı

---

## Reels İndirme & Transkripsiyon Pipeline

`instagram-reel-indirme` skill'inden absorbe edildi.

### İndirme (yt-dlp + cookie) — Hata Durumları ve Alternatifler

**Ön koşul — Cookie Preflight Check (ZORUNLU):**
```bash
grep -q 'sessionid' ~/.hermes/instagram_cookies.txt || echo "SESSIONID EKSIK — browser anonymous analiz kullan"
grep -q 'csrftoken' ~/.hermes/instagram_cookies.txt || echo "CSRFTOKEN EKSIK"
```
sessionid yoksa → `references/reel-anonymous-analysis.md`'deki browser + snapshot yöntemine geç.

**İndirme komutu:**
```bash
# Binary PATH'teyse (tercih edilen):
yt-dlp --cookies ~/.hermes/instagram_cookies.txt -o "/tmp/reel_%(id)s.%(ext)s" "REEL_URL"

# Binary yoksa Python module fallback'i:
python3 -m yt_dlp --cookies ~/.hermes/instagram_cookies.txt -o "/tmp/reel_%(id)s.%(ext)s" "REEL_URL"
```
İndirme başarılı olursa video + ses ayrı ayrı gelir, yt-dlp otomatik merge eder.

⚠️ **HATA — `yt-dlp: command not found`:**
```bash
# Binary yoksa Python module ile dene:
python3 -m yt_dlp --cookies ... 
# O da yoksa pip install yt-dlp ile kur:
pip install yt-dlp
# Kurulu ama PATH'te görünmüyorsa:
~/.local/bin/yt-dlp ...
```
⚠️ **HATA — `No video formats found`:**
Bu post **image-only karusel** (içinde video yok, sadece resimler var). yt-dlp bu formatı indiremez.
**Ne YAPMALI:**
1. Browser'da post'u aç → karuselin tüm slaytlarını "Next" butonu ile tara
2. Her slayt için snapshot'taki `img[alt*="Photo by"]` veya `button "Photo by..."` açıklamalarını oku
3. Alternatif: Instagram API ile görsel URL'lerini çek (curl + WARP, `/api/v1/media/{shortcode}/info/`)
4. img_index parametresini kontrol et (linkte `?img_index=6` varsa 6. slaytı hedef al)
⚠️ **HATA — `only available for registered users`:** Hesap **private** veya takip şartı var. Cookie'de sessionid olsa bile bu reeli indiremezsin. Fallback: browser snapshot + vision.
⚠️ **HATA — `Private account`:** Hesap gizli. Sadece profil adı + fotoğraf görünür. Takip gerekir.
✅ **Public reeller valid cookie ile %100 iner.** Cookie'deki expiry=-1 uyarıları (WARNING: skipping cookie file entry due to invalid expires at -1) zararsızdır — Instagram oturum cookie'leri expiry=0/-1 olabilir. Asıl kontrol `sessionid` varlığıdır.
✅ **WARP gerekmez:** yt-dlp + cookie doğrudan çalışır, WARP proxy'siz de public reeller iner.

### Ses → Transkripsiyon (ZORUNLU Sıralama)

1. 🥇 **Groq Whisper `whisper-large-v3-turbo`** (BİRİNCİL) — hızlı, ücretsiz tier, Türkçe desteği yüksek. API key: BWS → `GROQ_API_KEY` → config'de `stt.groq.api_key_env` veya `$GROQ_API_KEY` env. Endpoint: `https://api.groq.com/openai/v1/audio/transcriptions`
   ```python
   import requests
   resp = requests.post("https://api.groq.com/openai/v1/audio/transcriptions",
       files={"file": open("audio.m4a","rb")},
       data={"model":"whisper-large-v3-turbo","language":"tr","response_format":"text"},
       headers={"Authorization": f"Bearer {api_key}"})
   ```

2. 🥈 **Yerel faster-whisper** (İKİNCİL) — `pip install faster-whisper`, model=`small`, device=`cpu`. Groq çalışmazsa kullanılır.

### Görsel Analiz (Kritik Anlar) — Groq Vision / easyocr / vision_analyze

Ses transkriptindeki kritik anlara göre kare seç, ffmpeg `fps=1` ile çıkar. Görsel analiz sırası:

1. 🥇 **vision_analyze** — birincil, zaten çalışıyor (auxiliary vision model ayarlı)
2. 🥈 **Groq Vision** (llama-3.2-11b-vision-preview) — API key BWS'de (GROQ_API_KEY). Ücretsiz. Çok hızlı.
   ```python
   import requests
   resp = requests.post(
       "https://api.groq.com/openai/v1/chat/completions",
       json={"model": "llama-3.2-11b-vision-preview",
             "messages": [{"role": "user", "content": [
                 {"type": "text", "text": "Bu görselde ne var? Türkçe açıkla."},
                 {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
             ]}]
       },
       headers={"Authorization": "Bearer $GROQ_API_KEY"}
   )
   ```
3. 🥉 **easyocr** (yerel) — binary gerekmez, Türkçe destekli, yavaş ama her zaman çalışır

**ÖNEMLİ:** Pollinations describeImage/chatCompletion kullanılamaz — terk edildi.

**⚠️ ÖNEMLİ — browser_vision/vision_analyze 401 Sorunu (ÇÖZÜLDÜ ✅):**
config.yaml'da `auxiliary.*.api_key` ile ilgili ayar. Fix: `hermes config set auxiliary.vision.api_key '<API_KEY>'` (ve approval, curator, mcp, web_extract için de aynısı).
**Artık browser_vision ve vision_analyze çalışıyor.**

**OCR Alternatifi (Yerel, binary gerekmez):**
- ❌ `mcp_local_secure_secure_vision` → tesseract binary gerekli (kurulu değil)
- ❌ `pytesseract` → binary gerekli
- ✅ **easyocr** (1.7.2 kurulu): `python3 -c "import easyocr; reader=easyocr.Reader(['tr','en']); [print(r[1]) for r in reader.readtext('img.png')]"`
- 🔧 Tesseract binary: `apt install tesseract-ocr tesseract-ocr-tur` (root)

### Hesap
- @bardopsikoloji (ds_user_id: 78089668165)
- Cookie: `~/.hermes/instagram_cookies.txt` (600, Kasım 2026)

### NotebookLM Kayıt
Notebook `6ea985e1-aef3-4c6a-ba0b-fd80b5da32e6` ("🎬 Medya Öğrenme (Reels)")

---

## Karusel Post Analizi (Başkalarının Karusellerini Okuma)

Bir Instagram karusel post'unu (`/p/...` linki) analiz ederken:

### Adım Adım Protokol

1. **Linki browser'da aç** → `browser_navigate(url)` ile sayfayı yükle.
   - Linkte `?img_index=N` varsa (örn. `?img_index=6`), bu **N. slayda direkt gitme isteğidir**. Önce o slayda git, sonra başa dönüp tüm slaytları tara.
   
2. **Login pop-up'ını kapat** → "Close" butonuna tıkla, sayfanın asıl içeriğini görünür hale getir.

3. **İlk slaydın caption'ını oku** → Snapshot'taki StaticText'lerden post açıklamasını, hashtag'leri, etiketlenen hesapları oku.

4. **TÜM slaytları tara** → Snapshot'ta "Next" butonu (`button "Next"`) veya tıklanabilir `listitem` elementleri varsa, her birine tıkla ve her slaytın içeriğini oku:
   - `browser_click(ref="...")` ile "Next" butonuna tıkla
   - Her tıklamadan sonra `browser_snapshot` al, yeni slaydın içeriğini oku
   - Karusel toplam kaç slayttan oluşuyor not et
   - Her slaytta `img[alt*="Photo by"]` açıklaması (alt text) varsa onu da oku
   - **img_index=6 ise 6. slayda özellikle dikkat et** — kullanıcı o slaydı hedef gösteriyordur

5. **Yorumları tara** → "Load more comments" butonu varsa tıkla, yorumların tonunu ve içeriğini analiz et.

6. **Profil bilgisi** → Hesap adı, verified durumu snapshot'tan okunabilir.

7. **Eğer post image-based karuselse** (yt-dlp "No video formats") → alternatif olarak Instagram API'den görsel URL'lerini çek:
   ```bash
   curl -s --socks5 warp:1080 \
     -b ~/.hermes/instagram_cookies.txt \
     -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)" \
     -H "X-CSRFToken: $(grep 'csrftoken' ~/.hermes/instagram_cookies.txt | awk '{print $7}')" \
     -H "X-IG-App-ID: 936619743392459" \
     -H "X-Requested-With: XMLHttpRequest" \
     "https://www.instagram.com/api/v1/media/{shortcode}/info/" 2>/dev/null
   ```

### İletilen Linkleri Teker Teker İşleme (Forwarded Link Protocol)

Edel Instagram/YouTube/diğer linkleri forwarladığında:

**ZORUNLU KURAL — Linki her zaman göster:**
Her linki işlemeye başlarken, linkin kendisini ve hangi sıradaki link olduğunu belirt. "Şu an Link X/Y: [link]" formatını kullan. Edel hangi linkten bahsettiğini bilmeli.

**Sıralı işleme akışı:**
1. Linkleri say — toplam kaç link geldiğini söyle
2. Sıradaki linki URL'siyle birlikte göster: "Link X/Y: https://..."
3. Browser'da aç, analiz et, özet çıkar
4. Sonraki linke geçmeden önce Edel'in yönlendirmesini bekle
5. Her link için: hesap adı, post türü (karusel/reel/video), ana konu, önemli alıntılar

### PITFALL'lar

| Hata | Çözüm |
|------|-------|
| "Next" butonu snapshot'ta görünmüyor | Sayfa yeterince yüklenmemiş olabilir. `browser_snapshot(full=true)` ile tekrar dene. Bazı karusellerde "Next" butonu `listitem` içinde gömülü olabilir. |
| Slayt değişince snapshot aynı kalıyor | Instagram karusel slaytları bazen aynı DOM elementini günceller. `browser_vision` ile screenshot al veya `browser_console(expression="document.querySelector('img[alt*=\"Photo\"]').src")` ile görsel URL'sini oku. |
| img_index parametresi ise yaramıyor | Browser URLye direkt ?img_index=N ekleyerek acmak her zaman calismayabilir. Next butonu ile manuel ilerle. Detayli adim-adim pattern icin: references/karusel-analizi-navigasyon.md |
| img alt text çok kısa/kör | Instagram otomatik alt text üretir. Gerçek içerik için vision analizi gerekir. |
| API `carousel_media` boş dönüyor | Endpoint çalışmıyor olabilir. Browser snapshot + "Next" tıklama yöntemine dön. |

---

## Karusel İçerik Üretimi (Instagram Carousel)

---

## NotebookLM Arşiv Fallback
notebook: `6c7f3daa-1640-4fad-9917-ec44bc432e58` | label: "Dijital Platformlar"

Bilgi eksikse: `cross_notebook_query("LinkedIn post kuralları", notebook_names="6c7f3daa")`

Cookie + WARP yeterli olmadığında (görsel içerik okuma, etkileşim, JS render gerektiren sayfalar), Playwright ile headless browser kullan. Gerçek Chromium tarayıcısı başlatır, Instagram bot detection'ına karşı cookie + WARP ile dayanıklıdır.

### Mimari

```
Vanitas → Playwright → Chromium → SOCKS5 Proxy (WARP) → Instagram
```

### Kurulum

Bkz. `references/playwright-setup.md` — Playwright, Chromium, WARP proxy kontrolü.

### Cookie Yükleme (Netscape → Playwright)

Bkz. `references/playwright-cookie-format.md` — Netscape cookie jar parse ve Playwright context'e yükleme.

### Temel Kullanım

```python
from playwright.sync_api import sync_playwright

def parse_netscape_cookies(path):
    cookies = []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 7:
                cookies.append({
                    "name": parts[5], "value": parts[6],
                    "domain": parts[0], "path": parts[2],
                    "secure": parts[3] == "TRUE", "httpOnly": False,
                })
    return cookies

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        proxy={"server": "socks5://warp:1080"}
    )
    ctx.add_cookies(parse_netscape_cookies("~/.hermes/instagram_cookies.txt"))
    page = ctx.new_page()
    page.goto("https://www.instagram.com/KULLANICI/", wait_until="networkidle")
    # Screenshot, içerik okuma, scroll...
    browser.close()
```

**ÖNEMLİ: Instagram form alanları:** Login formu `name='email'` (kullanıcı adı/e-posta) ve `name='pass'` (şifre) kullanır. `name='username'` yoktur. Submit için `button[type="submit"]` çalışmaz — `page.press('input[name="pass"]', "Enter")` kullanılır.

### Instagram Login (Playwright)

Yeni hesaba giriş yapmak için tam çalışan pattern. Cookie yoksa bu kullanılır:

```python
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        proxy={"server": "socks5://warp:1080"},
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
    )
    page = ctx.new_page()
    page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle", timeout=30000)
    time.sleep(3)
    page.fill('input[name="email"]', "KULLANICI_ADI")
    page.fill('input[name="pass"]', "SIFRE")
    page.press('input[name="pass"]', "Enter")
    time.sleep(8)
    # Check page.url — if challenge page, handle 2FA
```

### 2FA / Challenge Handling

Instagram girişlerinde karşılaşılabilecek doğrulama tipleri:

| Challenge Tipi | Belirti | Çözüm |
|---------------|---------|-------|
| Cihaz onayı | "Check your notifications on another device" | Telefondan onayla veya "Try another way" → e-posta/SMS |
| E-posta kodu | "Enter the 6-digit code we sent" | Gmail API'den kodu oku, `page.fill()` ile gir |
| `redirect.async` (instagrapi) | `step_name: "STEP_NAME"`, `ChallengeUnknownStep` hatası, `challenge` key'i yok, `last_json`'da sadece `bloks_action` + `challenge_context` var | instagrapi bu tipi çözemez → Playwright'a geç. Playwright 2FA sayfası başlangıçta boş (0 tıklanabilir element). 15-20sn bekle VEYA telefondan onayla. |
| Rate-limit | Login sayfasına geri dönme | 5+ dk bekle, tekrar dene |

### DM Gönderme (İki Aşamalı — ZORUNLU)

Instagram API'si `direct_v2/create_group_thread` ile thread oluşturur ama **mesaj gönderemez** — `broadcast/text` endpoint'i `useragent mismatch` hatası verir. Bu yüzden:

1. **API ile thread oluştur** → thread_id al
2. **Playwright ile mesajı yazıp gönder** → `instagram.com/direct/t/{thread_id}/`

Tam script ve curl komutları: `references/playwright-dm-send.md`

### API vs Browser

| Yöntem | Hız | Görsel | Etkileşim | DM |
|--------|-----|--------|-----------|----|
| API (curl + WARP) | Hızlı | Yok | Yok | Sadece thread oluşturma |
| Playwright | Yavaş | Var (screenshot) | Tam (like, save, comment) | ✅ Tam DM

### Pitfalls

| Hata | Çözüm |
|------|-------|
| Profil açılıyor ama içerik yok | Cookie süresi dolmuş — önce Cookie Preflight Check yap, sonra Cookie Refresh ile yenile |
| `inner_text()` boş | Sayfa JS render bekliyor — `wait_until="networkidle"` kullan |
| Postlar görünmüyor | Lazy loading — `page.evaluate("window.scrollBy(0, 800)")` |
| WARP'sız istek → `checkpoint_required` | TÜM istekler WARP'tan geçmeli, SOCKS5 proxy konfigürasyonunu kontrol et |
| `input[name="username"]` bulunamadı | Instagram `name="email"` ve `name="pass"` kullanır |
| `button[type="submit"]` timeout | Submit butonu JS ile yükleniyor — `page.press('input[name="pass"]', "Enter")` kullan |
| Login sonrası sayfa boş/login'e döndü | Rate-limit — 5+ dk bekle |
| `page.evaluate` → "context was destroyed" | Sayfa navigation oldu — `wait_for_load_state("networkidle")` sonrası evaluate et |
| Playwright EPIPE / TargetClosedError | `--no-sandbox` ekle (Snap Chromium), detay: `references/playwright-setup.md` |
| Login: `input[name="username"]` bulunamadı | Instagram login formu `name="email"` ve `name="pass"` kullanır |
| Login: submit butonu görünmüyor | `input[name="pass"].press("Enter")` kullan, butona tıklama |
| Login: boş beyaz sayfa (bot detection) | Headless mod tespit edildi → Chrome'dan cookie export et |

### Login Pitfall — Bot Detection

Playwright headless modda (WARP olsa bile) Instagram login formu submit edildiğinde
bot detection tetiklenir. Sonuç: boş beyaz sayfa, login başarısız.

**Çözüm:** Chrome'dan manuel cookie export. Kullanıcı Chrome'da Instagram'a giriş yapar →
EditThisCookie extension → Netscape formatında export → dosyaya kaydedilir.

Bu yöntem bot detection'ı tamamen bypass eder ve her zaman çalışır.
| `broadcast/text` → `useragent mismatch` | **API ile mesaj gönderilemez.** Thread'i API ile oluştur, mesajı Playwright ile gönder. Bkz. `references/playwright-dm-send.md` |
| `create_group_thread` → mesaj görünmüyor | `text` parametresi thread oluştururken mesajı iletmez. Ayrıca Playwright ile göndermek gerekir. |
| `friendships/{id}/following/` → boş liste | **Karşılıklı takip şart.** Takip etmediğin birinin takip listesini API göstermez (özellikle gizli hesaplarda). Karşılıklı takipleşme sonrası çalışır. |
| **API rate-limit (refresh sonrası)** | Refresh sonrası ilk API isteğinde `"Please wait a few minutes before you try again."` alınırsa → rate-limit. 2-3 dk bekle, tekrar dene. Rate-limit geçicidir, cookie geçersiz değildir. |
| **Cookie farklı lokasyonda** | Cookie `~/.hermes/instagram_cookies.txt`'de yoksa `~/instagram_cookies_netscape.txt`, `~/ig_session.json` veya `~/ig_session_from_cookies.json`'a bak. Bulunanı `~/.hermes/` altına kopyala. |
| **DM "Seen" receipt kaçınılmaz** | Instagram web'de DM thread'i açıldığı an "Görüldü" otomatik işaretlenir. Web'de bunu engellemenin güvenilir yolu yoktur (mobil uçak modu taktiği web'de çalışmaz). Strateji: "Görüldü"yü kabullen, zamanlamayla yönet — 2-5 dk içinde cevap ver. 1 saat sessiz kalma. | |

## Karusel İçerik Üretimi (Instagram Carousel)

Pipeline: **NotebookLM/Wiki kaynak** → **NotebookLM Studio slide_deck** → **PDF→PNG** → **Vision doğrulama** → **Graph API karusel container** → **Edel onayı → Publish**

### Kesinti Sonrası Devam (PDF Review & Resume)

Kullanıcı hazır bir karusel PDF'i gönderdiğinde veya geçmiş bir karusel projesine döndüğünde, pipeline'a sıfırdan başlamadan içeriği değerlendir ve kaldığın yerden devam et.

**Adım 1 — PDF'i oku** (varsa): PyMuPDF (`fitz`) ile sayfaları PNG'ye çevir, `vision_analyze` ile her slaytın metnini oku.
```
python3 -c "import fitz; doc=fitz.open('karusel.pdf'); [page.get_pixmap().save(f'/tmp/karusel_s{i+1}.png') for i,page in enumerate(doc)]"
```

**Adım 2 — Görsel durumunu belirle:**
- ✅ **Metin hazır** → Hangi pipeline aşamasındayız? (görsel üretildi mi, sadece yayın kaldı mı?)
- ✅ **Görseller var mı?** PDF image-based mi → NotebookLM çıktısı olabilir, görseller yeniden üretilmeli
- ✅ **Eksik slayt var mı?** `references/karusel-yazim-krokisi.md`'deki yapıyla karşılaştır
- ✅ **Dosya sisteminde görselleri ara:** `~/instagram_karusel/`, `/tmp/`, `~/*karusel*`, `~/*slayt*` gibi kalıplarla png/jpg tara. Bulamazsan session search ile 'görsel gönder', 'MEDIA', 'karusel foto' terimlerini dene.
- ⚠️ **Görseller Telegram MEDIA ile gönderildiyse:** Geçici dosyalar session'lar arası kalıcı olmaz. En güvenilir çözüm kullanıcıdan tekrar göndermesini istemektir.

**Adım 3 — Nerede kalmıştık?** Session search ile geçmişi tara:
- Farklı terim varyasyonları dene (karusel, sınav kaygısı, yayın, cloud — AND/OR kombinasyonları)
- **Cron job session'larını filtrele:** session_search sık sık cron skill yükleme session'larını döndürür. Gerçek kullanıcı konuşmalarını ayırt etmek için `source` alanına bak (`cron` kaynaklı olanları atla).
- **Farklı topic/profil'leri dene:** Edel farklı Telegram topic'lerinde farklı konular konuşur. Eğer Instagram konusu farklı bir topic'te geçtiyse session_search bulamayabilir. Bu durumda kullanıcıya net sor: "Bu konuyu hangi başlık altında konuşmuştuk?"
- **HİÇBİR ŞEY bulamazsan:** Kullanıcıya "Geçmiş konuşmada bulamadım, hangi gün/hangi başlıkta konuşmuştuk? Bir ipucu verirsen daha daraltabilirim" diye sor. Asla "hiçbir şey hatırlamıyorum" deme — kullanıcıyı sinirlendirir.

**Pitfall — Kullanıcının "hafıza sorunu" tepkisi:**
Kullanıcı daha önce verdiği bir bilgiyi unuttuğunda "hafıza sorunu ne ya" gibi tepki verebilir. Bunu önlemek için:
- Her karusel projesinde görselleri kalıcı bir klasöre kaydet: `mkdir -p ~/instagram_karusel/<tarih>/`
- Görselleri MEDIA ile gönderirken bile kalıcı klasöre kopyala
- Session search'i hızlıca (tek sorguyla, 3 sonuç limit) yap, uzun süre bekletme

**Adım 4 — Kalan adımları tamamla:**
- Önceki pipeline aşamasından itibaren devam et (görsel üretimi → vision doğrulama → cookie pre-check → yayın)
- Vision doğrulamada metin okunabilirliğine özellikle dikkat et (Türkçe karakterler, kontrast)
- Cloud sorunu yaşanmışsa cookie pre-check atlama — cookie de etkilenmiş olabilir

**Adım 5 — Kullanıcıya raporla:**
- Şu an hangi aşamada olduğumuzu özetle
- Eksik adımları listele (görsel üretimi, cookie yenileme, manuel paylaşım)
- "Yayına hazır mı, yoksa hâlâ eksik adımlar mı var?" diye sor

**Pitfall:** Vision doğrulamada model bazen tekrarlayan çıktı verebilir (özellikle NotebookLM çıktılarında). Her sayfayı ayrı vision_analyze ile oku, gruplama yapma.

> 📝 **Yazım Krokisi (Content Blueprint):** Karusel metnini yazmadan önce `references/karusel-yazim-krokisi.md`'yi kullan. Orada: slayt yapısı (7-9 slayt), bilgi sunum tekniği (Duygu/Problem → Açıklama → Örnek → Farkındalık), başlık/kapanış kalıpları, hashtag stratejisi var. Bu görsel üretimden ÖNCEKİ içerik stratejisi katmanıdır.

### Konsept

Instagram karusel = 3-10 slaytlık kaydırmalı post formatı. Metin + görsel birleşir. Ses/kamera gerekmez — karusel tamamen yazı ve görselle yapılır.

### ⚠️ ZORUNLU KURAL — Görsel Kaynağı

**Karusel görselleri SADECE NotebookLM Studio slide_deck ile üretilir.**
- ❌ **Pollinations, seedream-pro, flux, veya herhangi bir dış görsel üretim aracı KULLANILMAZ**
- ❌ **Pollinations ile üretilmiş karusel görselleri varsa, NotebookLM Studio'da yeniden oluşturulmalıdır**
- ✅ NotebookLM Studio slide_deck → PDF → PNG pipeline'ı TÜM karusel görselleri için geçerlidir
- ✅ Bu kuralın istisnası yoktur — konu ne olursa olsun (psikoloji, ekonomi, duyuru)

Edel bu kuralı defalarca vurgulamıştır. Atlanması güven kaybına yol açar.

### Pipeline (Adım Adım)

1. **Kaynak topla** → NotebookLM'e konuyla ilgili kaynakları yükle (makaleler, videolar, notlar)
2. **İçerik analizi** → NotebookLM'den notebook_query ile ana temaları çıkar (konu, slayt başlıkları, madde işaretleri)
3. **Slayt yapısı** → Her slayt için: başlık + 3-5 kısa madde işareti (Türkçe, anlaşılır dil). `references/karusel-yazim-krokisi.md`'deki yapıyı kullan (7-9 slayt: hook → içerik → kapanış).
4. **Kaynakları NotebookLM'e yükle** → Web'den ilgili makaleleri, wiki notlarını veya YouTube URL'lerini NotebookLM notebook'una ekle (`mcp_notebooklm_mcp_source_add`).
5. **NotebookLM Auth Pre-check** → Studio oluşturmadan ÖNCE `mcp_notebooklm_mcp_server_info` ile auth_status kontrol et. "stale" veya "expired" dönerse: önce `python3 ~/.hermes/scripts/nb_keepalive.py` çalıştır (nlm login DEĞİL — headless'te crash), ardından `mcp_notebooklm_mcp_refresh_auth` ile token'ları yenile. Auth "configured" olana kadar Studio adımına geçme.
6. **NotebookLM Studio ile slide_deck oluştur** → `mcp_notebooklm_mcp_studio_create` ile:
   - artifact_type: "slide_deck"
   - slide_format: "detailed_deck"
   - detail_level: "standard"
   - focus_prompt: "Bardo Psikoloji Instagram karuseli. Pastel/sakin tonlar. Her slayt KENDİ rengini alır. Türkçe, anlaşılır dil. Slayt yapısı: 1) Hook/kapak 2-3) Konu tanımı 4-6) Temel bilgiler + örnekler 7) Günlük hayata uyarlama 8-9) Özet + kapanış."
   - confirm: True
   - ⚠️ **Rate-limit durumu:** Studio "Rate limited" (code 8) hatası dönerse SAKIN PIL, Pollinations veya başka bir dış araçla görsel üretmeye kalkma. Bunun yerine:
     1. 2-5 dk bekle, tekrar dene
     2. Hâlâ rate-limit'teyse Edel'e durumu bildir, ne zaman denememi istediğini sor
     3. Edel ne derse onu yap — kendi başına alternatif çözüm üretme, bu kuralın istisnası yoktur
7. **PDF'i indir ve PNG'ye çevir** → Studio hazır olana kadar bekle. İki yöntem:
   - **Poll yöntemi (kısa işlemler):** `mcp_notebooklm_mcp_studio_status` ile periyodik kontrol et. Studio generation 2-10 dk sürebilir.
   - **Cron tetikleyici (önerilen — async):** Studio oluşturmayı başlattıktan sonra, 10 dk sonra çalışacak tek seferlik bir cron job oluştur. Cron job: studio_status kontrol et → hazırsa PDF indir + PNG'ye çevir + Edel'e göster. Bu yöntemle sürekli poll etmek yerine işlem bitince haberdar olursun. Cron job'u silmeyi unutma (repeat=1 veya manuel remove).
   
   Hazır olunca:
   - `mcp_notebooklm_mcp_download_artifact` ile slide_deck'i PDF olarak indir (slide_deck_format: "pdf")
   - PyMuPDF (`fitz`) ile her sayfayı 200 DPI PNG'ye çevir
   - `~/instagram_karusel/<tarih>/` klasörüne kalıcı kaydet
   
   **Görsel boyutlandırma (landscape→portrait):** Studio slide_deck 16:9 (3823x2134) landscape üretir. Instagram karusel 4:5 (1080x1350) portrait ister. PNG'ye çevirdikten sonra PIL ile yeniden boyutlandır:
   ```python
   from PIL import Image
   img = Image.open("slayt.png")
   target_w, target_h = 1080, 1350
   scale = target_w / img.width
   new_w, new_h = int(img.width*scale), int(img.height*scale)
   img_resized = img.resize((new_w, new_h), Image.LANCZOS)
   if new_h < target_h:
       canvas = Image.new("RGB", (target_w, target_h), "#F5F0EB")
       canvas.paste(img_resized, (0, (target_h - new_h)//2))
       img_resized = canvas
   elif new_h > target_h:
       crop_top = (new_h - target_h) // 2
       img_resized = img_resized.crop((0, crop_top, target_w, crop_top + target_h))
   img_resized.save("slayt.jpg", "JPEG", quality=92)
   ```
8. **Vision doğrulama** → Her slaytı `vision_analyze` ile kontrol et:
   - Türkçe metinler okunabiliyor mu? (karakterler net, kontrast yeterli)
   - Tasarım psikoloji temasına uygun mu?
   - NotebookLM Studio bazen uzun metinleri kırpabilir — her slaytı tek tek kontrol et
9. **Karuseli yayınla (Graph API — BİRİNCİL YÖNTEM)**:
   - **Gerekenler:** Instagram Business Account ID, Graph API token (`instagram_content_publish` scope'lu)
   - **Adımlar:**
     a) Görselleri herkese açık URL'ye yükle. **Cloudinary unsigned upload preset (ÖNERİLEN):** WSL/Docker'da Catbox/0x0.st/Imgur çalışmayabilir. Cloudinary'de unsigned preset ayarlayıp kullan (`POST` ile `upload_preset` parametresi, API secret gerekmez). Detay: `references/cloudinary-upload.md`. Alternatif: `python3 -m http.server` ile geçici serve (WSL'de çalışmaz).
     b) `POST /v24.0/{ig-id}/media` ile her görsel için IMAGE container oluştur (media_type=IMAGE, image_url=...)
     c) `POST /v24.0/{ig-id}/media` ile CAROUSEL container oluştur (media_type=CAROUSEL, children=[id1,id2,...], caption=...)
     d) Container FINISHED olana kadar poll et (`GET /{container-id}?fields=status_code`)
     e) `POST /v24.0/{ig-id}/media_publish` ile yayınla (creation_id=karusel_container_id)
   - ⚠️ Image URL herkese açık olmalı — local file path çalışmaz
   - **Alternatif — Kullanıcıya gönder (manuel):** Görselleri MEDIA: ile Telegram'a gönder (01_slayt, 02_slayt... diye sıralı), kullanıcı Instagram uygulamasından seçip paylaşır

### Cron Otomasyonu (Günde 2 Karusel)

Bardo Psikolojisi için otomatik karusel üretimi. LinkedIn pipeline'ına benzer yapıda.

**Cron Job'ları:**
- `karusel_sabah` — her gün **10:00**
- `karusel_aksam` — her gün **19:00**

Her ikisi de aynı pipeline'ı çalıştırır: NotebookLM/Wiki kaynak → Studio slide_deck → PDF→PNG → hosting upload → Graph API container → Edel'e onay. ASLA otomatik yayınlama — onay akışı zorunlu.

**Arşiv:** `~/.hermes/data/karusel_arsiv.json` — duplicate kontrolü için. status=pending_approval veya posted olan konular tekrar işlenmez.

### Kullanıcı "cookie vermiştim / cookie ile girmiştik" Dediğinde

Bu, Instagram'a daha önce cookie ile giriş yapıldığını gösterir. Akış:
1. Cookie preflight check yap (csrftoken + sessionid kontrolü)
2. sessionid kaybolmuşsa (skill'deki "Cookie'de sessionid eksik" hatası): kullanıcıya Chrome'dan EditThisCookie ile Netscape formatında cookie export etmesini söyle
3. Cookie export adımlarını sırala: Chrome'da Instagram'a git → EditThisCookie extension → Export → Netscape formatında kaydet → dosyayı paylaş
4. sessionid varsa: WARP üzerinden API ile test et, profile info sorgula

### Onay Akışı (ZORUNLU — Kullanıcı Onaysız Yayın Yok)

Karusel hazırlandıktan sonra kullanıcıya göster, onay al, SONRA yayınla. Asla otomatik yayınlama.

**Adım 1 — İçerik + caption hazırlığı:** Slayt başlıklarını, sıralamayı ve caption'ı kullanıcıya göster, onay al
**Adım 2 — Görsel hazırlık:** Studio slide_deck'ten çevrilen PNG'leri kalıcı klasöre kaydet, vision ile doğrula
**Adım 3 — Onay için gönder:** Görselleri MEDIA: ile sırayla gönder + caption + hashtag. "Onaylıyorsan 'yayınla' yaz" ekle
**Adım 4 — Yayınla (Graph API):** Kullanıcı "yayınla" deyince:
   - `POST /v24.0/{ig-id}/media` ile her görsel için IMAGE container oluştur (image_url olarak imgur/cloudinary veya geçici HTTP server URL'si kullan)
   - `POST /v24.0/{ig-id}/media` ile CAROUSEL container oluştur (children=[id1,id2,...])
   - Container FINISHED olana kadar poll et
   - `POST /v24.0/{ig-id}/media_publish` ile yayınla
**Adım 5 — Arşive kaydet:** `karusel_arsiv.json`'a status="posted" olarak işaretle

### Caption Yapısı (Karuseller İçin)

- **Giriş:** Hook — merak uyandıran soru veya yaygın bir his
- **Detay + Örnek:** Psikolojik terimler günlük dile çevrilir
- **Özet + Soru:** Farkındalık oluşturan kapanış
- **Kural:** ASLA promosyon/reklam dili yok
- **Hashtag (ÖNEMLİ):** Marka/hesap adı içeren etiketler (#bardopsikoloji) keşfedilebilirliğe katkı sağlamaz. Sadece içerikle ilgili tutarlı etiketler kullan: #psikoloji #yalnızlık #ruhSağlığı #farkındalık gibi. 3-4 hashtag yeterli.
- **Ton:** Sıcak, anlaşılır, günlük Türkçe

### Görsel Stili — NotebookLM Studio Slide Deck

NotebookLM Studio slide_deck ile karusel görselleri otomatik oluşturulur. Görsel stili `focus_prompt` parametresiyle kontrol edilir.

**`focus_prompt` içinde belirtilmesi gerekenler:**
- **Ton:** Profesyonel psikoloji içeriği, sade ve anlaşılır dil
- **Renkler:** Pastel/sakin tonlar — her slayt KENDİ rengini alır (tekrar eden renk yok): adaçayı yeşili, lavanta, şeftali, gök mavisi, krem/bej, soft mercan, pudra pembesi
- **Tipografi:** Sans-serif, başlıklar kalın, yüksek kontrast
- **Slayt yapısı:** 7-9 slayt (hook → içerik → kapanış), `references/karusel-yazim-krokisi.md`'deki akış
- **Dil:** Türkçe, anlaşılır, psikolojik terimler günlük dile çevrilmiş
- **Boyut:** Studio slide_deck PDF → PyMuPDF ile 200 DPI PNG'ye çevrilir. Her sayfa ayrı slayt olur.

**⚠️ Pitfall:** NotebookLM Studio bazen uzun metinleri slaytlarda kırpabilir. Her slaytı vision_analyze ile kontrol et.

**⚠️ Pitfall:** Studio generation 2-10 dakika sürebilir (yoğunlukta 10+ dk). `studio_status` ile poll et, sabırlı ol.

### Studio `focus_prompt` Şablonu

NotebookLM Studio'da slide_deck oluştururken `focus_prompt` parametresiyle stil ve içerik kontrol edilir:

```
Bardo Psikoloji Instagram karuseli için [KONU] temalı 7-9 slaytlık bir slide deck hazırla.
- Slayt 1: Dikkat çeken başlık / problem cümlesi (hook)
- Slayt 2-3: Konu tanımı + neden önemli
- Slayt 4-6: 2-3 temel bilgi + örnekler + yanlış inanışlar
- Slayt 7: Günlük hayata uyarlama / mini farkındalık
- Slayt 8-9: Özet + kapanış sorusu / düşündürücü cümle
- Renkler: Pastel/sakin tonlar, her slayt KENDİ rengini alsın
- Dil: Türkçe, anlaşılır, psikolojik terimler günlük dile çevrilmiş
- Profesyonel psikoloji estetiği
```

### Format İpuçları

| Slayt | İçerik | Uzunluk |
|-------|--------|---------|
| 1 (kapak) | Soru + alt başlık, dikkat çekici | 4 madde |
| 2-4 (içerik) | Her slayt bir alt konu | 3 madde |
| 5 (kapanış) | Özet + güçlü bitiş | 4 madde |

### Vision Doğrulama Soru Şablonu

Her slayt `vision_analyze` ile kontrol edilir:
- "Bu Instagram karusel slaydı. Türkçe metinler okunabiliyor mu? Karakterler net, kontrast yeterli mi?"
- "Tasarım psikoloji temasına uygun mu? Pastel tonlar var mı?"
- "Slayttaki metin kırpılmış mı? (NotebookLM Studio bazen taşan metni kesebilir)"

Metin okunamıyorsa → Studio'da focus_prompt'u sadeleştir, slayt başına daha az metin iste, yeniden oluştur.

### Cookie Pre-check (Paylaşım Öncesi ZORUNLU)

```bash
echo "=== Cookie durumu ==="
ls -la ~/.hermes/instagram_cookies.txt
echo "=== CSRF + SessionID kontrolü ==="
grep -q 'csrftoken' ~/.hermes/instagram_cookies.txt && echo "csrftoken: ✅" || echo "csrftoken: ❌"
grep -q 'sessionid' ~/.hermes/instagram_cookies.txt && echo "sessionid: ✅" || echo "sessionid: ❌"
grep -q 'ds_user_id' ~/.hermes/instagram_cookies.txt && echo "ds_user_id: ✅" || echo "ds_user_id: ❌"
```

### Pitfalls (Karusel Üretimi)

- ⚠️ **KRITIK — Cron job'lar da kurala tabi:** Otomatik karusel cron job'ları da NotebookLM Studio kuralına uymak zorundadır. Cron, MCP auth başarısız olduğunda PIL/başka bir araçla görsel üretmeye kalkmamalıdır. Eğer Studio çalışmıyorsa, cron rapor vermeli ve atlamalıdır — alternatif araçla görsel üretmek yok. Bu kuralın cron için istisnası yoktur.
- ⚠️ **KRITIK — Gorsel kaynagi:** Karusel görselleri SADECE NotebookLM Studio slide_deck ile üretilir. **Pollinations, seedream-pro, flux veya baska bir dis gorsel araci KULLANMA.** Bu kuralin istisnasi yoktur. Edel icin bu, pipeline'in temel prensibidir — atlanmasi guven kaybina yol acar.
- ⚠️ **KRITIK — Studio yoksa karusel yapma:** NotebookLM Studio kullanılamıyorsa (MCP tool yok, auth expired/expired, CDP bağlantısız, rate-limit) **SAKIN PIL, Pollinations, Photoshop veya başka bir dış araçla görsel üretme.** PIL ile manuel karusel yapmak da bu kuralın kapsamındadır. Çözüm: Karusel işlemini durdur. Edel'e "Studio şu anda kullanılamıyor, auth yenilenince tekrar denerim" diye bildir. Cron job'larda: sessizce skip et, hata bildirme — bir sonraki tick'te tekrar dener. **Bu kuralın istisnası yoktur** (11 Temmuz 2026'da PIL ile karusel üretildi, Edel tarafından reddedildi).
- ⚠️ **Studio rate-limit'te alternatif kullanma:** NotebookLM Studio "Rate limited" (code 8) hatası verdiğinde SAKIN PIL, Pollinations, Photoshop veya başka bir dış araçla görsel üretme. PIL ile manuel karusel yapmak da bu kuralın kapsamındadır. Çözüm: 2-5 dk bekle, tekrar dene. Hâlâ çalışmazsa Edel'e bildir, ne zaman denemek istediğini sor. Asla kendi başına alternatif çözüm üretme. Bu hata 2 Temmuz 2026'da yaşandı ve Edel tarafından düzeltildi — tekrarlama.
- ⚠️ **KRITIK — Asla manuele kacma:** Upload servisi calismazsa, token hata verirse veya bir adim takilirsa, ASLA "manuel paylas" veya "kullanici yapsin" onerme. Otomasyonun anlami budur. Alternatif teknigi arastir (Cloudinary dokumantasyonu, farkli auth yontemi, farkli endpoint). Pes etmek yok.
- ⚠️ **Hashtag kurali:** Marka/hesap adi iceren etiketler (#bardopsikoloji) kesfedilebilirlige katki saglamaz. Sadece icerikle ilgili tutarli etiketler kullan: #psikoloji #yalnizlik #ruhSagligi #farkindalik gibi.
- ⚠️ **Async pattern (sürekli poll etme):** Studio slide_deck oluşturma emri verdikten sonra sürekli `studio_status` poll etme. Tetikleyici cron job kur (`schedule='10m', repeat=1`) — işlem bitince kontrol etsin. Beklerken başka iş yap. Edel: "Sürekli çıktı yapman gerekmiyor."
- ⚠️ **WSL upload kisiti:** Catbox.moe, 0x0.st, imgur Docker/WSL'de çalışmayabilir (DNS, proxy, dosya yolu sorunları). Cloudinary unsigned upload preset en güvenilir çözüm. Detay: `references/cloudinary-upload.md`.
- ⚠️ **Auth refresh donusu:** download "Google sign-in sayfasi" donerse (auth stale) → nb_keepalive.py + refresh_auth + tekrar dene.
- ⚠️ **Studio landscape cikti:** Studio 16:9 (3823x2134) uretir. Instagram portrait 4:5 (1080x1350) gerektirir. PIL ile resize sart.
- ⚠️ **Image-based PDF:** Studio image-based PDF uretir, metin cikarilamaz. Vision analizi gerekir.
- Instagram karusel formatı **kamera gerektirmez** — tamamen yazılı ve görsel içerik
- NotebookLM Studio generation 3-7 dakika sürebilir (genelde 5-7 dk). SAKIN poll'layarak bekleme — cron tetikleyici kur (`schedule='10m', repeat=1`), o hazır olunca kontrol etsin.
- Studio bazen uzun metinleri slaytlarda kırpabilir — her slaytı vision_analyze ile tek tek kontrol et
- Studio slide_deck PDF olarak gelir — PyMuPDF ile PNG'ye çevirirken 200 DPI kullan, yeterli kalite
- PDF'ten çevrilen slaytlar farklı boyutlarda olabilir (landscape) — PIL ile 1080×1350'ye yeniden boyutlandırıp padding ekle
- **Görsel kalıcılığı — temp cleanup riski:** `~/instagram_karusel/` altındaki eski karusel klasörleri temp cleanup script'i tarafından silinebilir. Özellikle günlük cron job'lar arasında eski karusellerin görselleri kaybolur. **Önlem:** Görselleri Telegram MEDIA ile gönderdikten sonra bile kalıcı bir kopyayı `~/wiki/karusel_arsivi/<tarih>/` gibi temp cleanup'in dokunmadığı bir yerde sakla. Session'lar arası görsel kurtarma için tek güvenilir kaynak ya bu kalıcı kopya ya da Telegram mesaj geçmişidir (MEDIA ile gönderilen dosyalar).
- **Kesinti sonrası dönüş:** Kullanıcı geçmiş bir karusel projesine döndüğünde session search ile hızlıca tara, cron session'larını filtrele, bulamazsan kullanıcıya spesifik soru sor (hangi gün/konu başlığı). Asla hicbir sey hatirlamiyorum deme — bu kullaniciyi sinirlendirir.
- **Karusel arşivindeki eski görseller:** `~/.hermes/data/karusel_arsiv.json`'daki `status: pending_approval` kayıtlarının görselleri eski yöntemle (Pollinations) üretilmiş olabilir. Bunları yayınlamadan ÖNCE NotebookLM Studio'da slide_deck olarak yeniden oluştur. Arşivdeki `hosted_urls`'e güvenme — sil baştan yap.
- **Karusel cron job'ları PIL kullanmamalı:** Cron job içinde `studio_create` MCP aracı çalışmazsa (auth expired, tool not found), cron PIL ile görsel üretmeye kalkmamalıdır. Bunun yerine: (1) auth sorununu raporla, (2) karuseli atla, (3) bir sonraki tick'te dene. PIL karusel = kural ihlali = Edel'in güven kaybı.
- **Auth stale → download hatası:** studio_status "completed" gösterse bile MCP download_artifact "Download failed" dönebilir. curl ile indirirsen Google login sayfası gelir. Çözüm: `nb_keepalive.py` → `refresh_auth` → tekrar download.
- **PDF landscape çıkar (3823x2134):** Studio slide_deck landscape (16:9) üretir. Instagram karusel portrait (4:5 = 1080x1350) gerektirir. PyMuPDF ile PNG'ye çevirdikten sonra PIL ile resize et:
  ```python
  from PIL import Image
  img = Image.open("slayt.png").resize((1080, 1350), Image.LANCZOS)
  img.save("slayt.jpg", "JPEG", quality=85)
  ```
- **Image-based PDF:** Studio slide_deck image-based PDF üretir — metin çıkarılamaz. Doğrulama için vision_analyze gerekir.
- **Studio otomatik başlık:** focus_prompt'ta net başlık versen bile Studio kendi başlığını koyabilir. İçerik doğru olur, PDF adını etkiler — sorun değil.
- **Görsel yükleme sorunu (WSL):** Catbox, 0x0.st, imgur gibi upload servisleri WSL/Docker'dan çalışmayabilir. Alternatif: kullanıcıya MEDIA olarak gönder (manuel paylaşım) veya Google Drive'a yükle (yazma izni gerektirir).
  ```python
  known_sizes = {
      55382: "01 Kapak",
      101366: "02 Bilgi Var Kaygi Blokluyor",
      116349: "03 Kaygi mi Bilgi Eksikligi mi",
      115612: "04 Bedenin Savas Kac Tepkisi",
      81306:  "05 Zihnin Kurdugu Tuzaklar",
      76428:  "06 Kayginin Ideal Dozu",
      91731:  "07 Zihni Sakinlestirme Adimlari"
  }
  ```
  Bu yöntem kullanıcının aynı görselleri tekrar göndermesi durumunda çalışır.
- **Playwright + WARP = CDN blokajı:** WARP SOCKS5 proxy üzerinden Playwright ile Instagram açıldığında CDN kaynakları (static.cdninstagram.com) `ERR_CONNECTION_CLOSED` ve `ERR_PROXY_CONNECTION_FAILED` hataları veriyor. Sayfa yüklenemiyor veya JS render olmuyor. **Çözüm:** Playwright'ı WARP'sız kullan (sadece sayfa yüklemek için), API isteklerini ayrıca WARP üzerinden curl ile yap. Detay: `references/playwright-karusel-upload-broken-2026.md`
- **Instagram web 2026'da post oluşturma broken:** Sidebar'da `[aria-label="New post"]` butonu çalışıyor, popup açılıyor, "Post" seçeneği görünüyor ama file dialog tetiklenmiyor. Bu Instagram'ın web sürümünde yaptığı bir değişiklik. Karusel yayınlamak için tek güvenilir yöntem: manuel (kullanıcıya gönder).
- **Auth expiration -> download failure:** Studio slide_deck generation "completed" olur ama `mcp_notebooklm_mcp_download_artifact` hata verir (auth expired). Çözüm: `python3 ~/.hermes/scripts/nb_keepalive.py` çalıştır -> `mcp_notebooklm_mcp_refresh_auth` yap -> download'ı tekrar dene. Keepalive her 2 saatte bir otomatik çalışır (nb_keepalive_2h cron) ama generation uzun sürerse aradaki auth düşebilir.
- **Image-based PDF (no extractable text):** NotebookLM Studio image-based PDF üretir - PyMuPDF `page.get_text()` boş döner. Metin kontrolü için `vision_analyze` gerekir. Alternatif: tesseract OCR kullan (`apt install tesseract-ocr tesseract-ocr-tur`). Slayt sayısını fitz ile PNG'ye çevirerek sayabilirsin.
- **Skill'i kontrol etmeden "bu tanımlanmamış" deme:** Kullanıcıya "bu konuşulmadı / tanımlanmamış" demeden ÖNCE skill'in tüm ilgili bölümünü oku. SkillView ile full içeriği getir, references/ dosyalarını da kontrol et. Emin değilsen session_search ile geçmiş konuşmaları tara. Kullanıcı "hepsi skill'de yazıyor" dediğinde güven kaybı yaşanır — bu hatayı tekrarlama.

## Companion Skills

- **`instagram-operasyonu`** — DM operational protocol: elicitation tactics (FBI/psychology-backed), deflection arsenal, human-like Turkish (linguistics-researched), OPSEC rules, approval flow, multi-message handling, conversation context management. Load this before any DM intelligence-gathering operation.

## Investigation & Reconnaissance

Profil keşfi, burner hesap tespiti ve sosyal mühendislik için: `references/investigation-reconnaissance.md`

### Burner Hesap Tespiti (Hızlı)
5 işaret: `is_private=true` + `follower=0` + `following≥25` + `full_name=""` + `biography=""` + `media=0` → %95 burner.

### Profil Fotoğrafı Kontrolü
Profil fotoğrafı **varsayılan Instagram ikonu** (insan silueti) görünüyorsa:
- Kullanıcı fotoğrafını kaldırmış olabilir
- Cookie'siz bakıldığında Instagram placeholder gösterebilir — doğrulama için Playwright ile cookie'li aç
- screenshot'ta avatar kontrolü: `img[alt*="profile picture"]` elementinin src'si default avatar URL'sine mi bakıyor kontrol et

### Cookie'siz Profil Görüntüleme Limiti
Instagram web'i cookie'siz açıldığında profil sayfasında "See full profile in the app" mesajı gösterir — profil fotoğrafı default placeholder olur, bio görünmez. Bu görüntü **gerçek durumu yansıtmaz**. Her zaman cookie'li Playwright ile doğrula.

### Instagram CDN Görsel Erişimi (PITFALL)
`scontent-*.cdninstagram.com` URL'leri direkt erişime 403 döner — WARP ile bile. Görsel için Playwright browser automation şart.

## Pitfalls

- **Playwright login (mobile web):** Instagram mobil login'de `button[type="submit"]` bulunamaz. Formu doldurduktan sonra `password_field.press("Enter")` kullan. Yine de timeout/EPIPE riski var — en güvenilir yöntem Chrome cookie export.
- **API login (`accounts/login/ajax/`):** Boş yanıt dönebilir. WARP üzerinden login endpoint'i güvenilir değil. Cookie export tercih et.
- **yt-dlp hata ayıklama:** `--cookies` ile public reeller %100 iner. `only available for registered users` → hesap private/restricted. `No video formats found` → image-only karusel (video yok). Her iki durumda da browser snapshot + navigasyon ile metin analizi yap.
- **Token geçersiz (190/460):** Kullanıcı şifre değiştirmiş veya Facebook session'ı security nedeniyle sonlandırmış. Recovery:
  1. `developers.facebook.com` → Tools → Graph API Explorer
  2. Instagram Business hesabını seç, `instagram_basic`, `instagram_content_publish`, `pages_read_engagement` izinlerini ekle
  3. Generate Access Token → Exchange for long-lived token (60 gün)
  4. `.env`'deki `FACEBOOK_ACCESS_TOKEN`'ı güncelle
  5. n8n workflow'unda da güncelle (eğer kullanılıyorsa)
  Ayrıca n8n workflow JSON'unda hardcoded token varsa (`queryParameters` içinde `access_token`), onu da yenile.
- **Container silinemiyor (Graph API):** `DELETE /{container-id}` işlemi desteklenmez (error_subcode: 33, "Unsupported delete request"). Sadece **yayınlanmış** postlar silinebilir. Container oluşturulup publish edilmemişse, container Facebook tarafında kalır ama zararsızdır — otomatik expire olur. Container ID'yi arşive kaydet, tekrar deneme.
- **API versiyonu:** Graph API versiyonları sık değişir. v23.0'dan v24.0'a geçişte endpoint'leri kontrol et.
- **Cookie süresi:** Instagram session cookie'leri ~6 ay geçerli. Süre dolunca Chrome'dan yeniden export et.
- **Yanıltıcı `require_login: true`:** API `{"message":"Please wait a few minutes","require_login":true}` döndüğünde cookie geçersiz OLABİLİR veya rate-limit yemiş olabilirsin. Önce Cookie Preflight Check yap — cookie'de csrftoken+sessionid varsa rate-limit'tir, 2-3dk bekle tekrar dene.
- **WARP zorunlu:** Oracle Cloud IP'si Meta tarafından bot olarak işaretlenir. Tüm Instagram isteklerinde WARP SOCKS5 proxy kullan.
- **One-shot cron job'ları temizle:** Tek seferlik araştırma/rapor cron job'ları işi bitince silinmeli. "Konu kapandı ama hâlâ bildirim geliyor" → en sık karşılaşılan hata. Cron job'ı `pause` veya `remove` yapmayı unutma.
- **Tekrarlayan API kontrolü → no_agent script:** Takip isteği, DM kontrolü gibi periyodik durum poll'ları LLM/token harcamamalı. Python + curl + state file ile `no_agent=true` cron job kullan. Bkz. `references/no-agent-polling.md`

## Bitwarden Serve ile Credential Çekme (bw-serve)

## Bitwarden Credential Çekme (bw-serve + bws)

Bazı servislerin (Cloudinary, Deepgram, vb.) API bilgileri Bitwarden'da saklanır. İki ayrı Bitwarden servisi var:

### 1. bw-serve (Password Manager) — ÖNCELİKLİ ✅

Container başlangıcında otomatik başlar, `unlocked` durumdadır, REST API sunar (localhost:8087). Daha güvenilirdir.

**Endpoints:**
- `GET /status` — bağlantı durumu, kullanıcı email, unlock status
- `GET /list/object/items` — tüm item'ları listele

**Cloudinary credential çekme:** `GET /list/object/items` yanıtında `name` alanında "cloud" geçen item'ı bul. `login.username` = cloud_name, `login.password` = api_secret. Custom fields'da api_key de olabilir. Yanıtı Python veya jq ile parse et.

### 2. bws (Secrets Manager) — Yedek

`bws` binary'si `~/.hermes/bin/bws` konumundadır (PATH'te değilse direkt yol ile çağır).

**Kullanım:**
```bash
export PATH="$HOME/.hermes/bin:$PATH"
bws secret list
bws secret get <SECRET_ID>
```

**PITFALL — Maskelenmiş secret:** BWS `bws secret get` çıktısında `value` alanı `**********` olarak maskelenebilir (Cloudinary URL gibi formatlı değerlerde). Bu durumda gerçek secret'ı `bw-serve` üzerinden çek. Asla `**********` değerini gerçek secret sanıp kullanma!

**PITFALL — `bws` PATH yok:** `bws: command not found` hatası alırsan `~/.hermes/bin/bws` yolunu dene (export PATH ekiyle).

## Bitwarden Credential Çekme (bw-serve + bws)

API bilgileri (Cloudinary, Deepgram, vb.) Bitwarden'da saklanir. İki ayri Bitwarden servisi var:

### 1. bw-serve (Password Manager) — ÖNCELİKLİ

Container'da otomatik baslar (port 8087), `unlocked` durumda.

**Endpoints:**
- `GET /status` — kullanici email, unlock status
- `GET /list/object/items` — tum item'lari listele

**Cloudinary credential çekme:** `GET /list/object/items` yanıtında `name` alanında "cloud" geçen item'ı bul. `login.username` = cloud_name, `login.password` = api_secret.

### 2. bws (Secrets Manager) — Yedek

Binary: `~/.hermes/bin/bws` (PATH'te degilse direkt yol ile cagir).

```bash
export PATH="$HOME/.hermes/bin:$PATH"
bws secret list                              # listele
bws secret get <SECRET_ID>                   # detay
```

**PITFALL — Maskelenmis secret:** BWS value alanini `**********` olarak maskeleyebilir (Cloudinary URL gibi formatli degerlerde). Gercek degeri `bw-serve` uzerinden cek. Maskelenmis degeri gercek secret sANma.

**PITFALL — `bws` PATH yok:** `bws: command not found` hatasi alirsan `~/.hermes/bin/bws` yolunu dene (export PATH ekleyerek).

## References

- `references/n8n-credential-extraction.md` — n8n JSON'dan credential çıkarma detaylı rehber
- `references/api-endpoints.md` — Cookie + WARP ile çalışan API endpoint'leri ve test sonuçları
- `references/cookie-setup.md` — Chrome'dan cookie alma ve Netscape formatına çevirme
- `references/playwright-setup.md` — Playwright + Chromium + WARP kurulum (headless browser automation)
- `references/playwright-cookie-format.md` — Netscape cookie jar formatı ve Python parse kodu
- `references/playwright-login-save.md` — Playwright ile Instagram login + Netscape cookie kaydetme script'i (2FA handling dahil)
- `references/playwright-dm-send.md` — **İki aşamalı DM gönderme** (API thread oluştur + Playwright mesaj gönder)
- `references/investigation-reconnaissance.md` — Profil keşfi, burner hesap tespiti, sosyal mühendislik cover story tasarımı
- `references/humint-elicitation.md` — DM'de bilgi çıkarma: elicitation teknikleri, deflection, cover story, burner tespiti
- `references/dm-humanize-taktikleri.md` — DM'de doğal insan gibi yazma: İnce İşler 9 adım, Gen Z Türk DM dili, 10 humanize taktiği
- `references/instagrapi-auth.md` — instagrapi login + challenge handling + `STEP_NAME` pitfall + cookie dönüştürme
- `references/no-agent-polling.md` — **Token harcamayan API polling pattern'i** — Python + curl + state file + cron no_agent
- `references/reel-anonymous-analysis.md` — **Login'siz Reel analizi** — Browser + Vision ile anonim içerik çözümleme
- `references/karusel-yazim-krokisi.md` — **Karusel yazım krokisi** — psikoloji Instagram karuselleri için bilgi sunum yapısı, slayt akışı, başlık/kapanış kalıpları, hashtag stratejisi.
- `references/playwright-karusel-upload-broken-2026.md` — **Playwright ile karusel upload BROKEN (2026)** — Instagram web değişikliği, denenen yöntemler, neden çalışmadığı, alternatifler.
- `references/cookie-cron-refresh.md` — **Cookie refresh cron setup** — no_agent script, cron kurulumu, pitfall'lar, schedule kararlari
- `references/cloudinary-upload.md` — **Cloudinary upload rehberi** — unsigned upload preset kurulumu, Basic Auth ile signed upload, imza hataları, görsel optimizasyonu (landscape→portrait).
- `scripts/instagram_cookie_refresh.sh` — **Otomatik cookie refresh scripti** — Playwright + WARP ile haftalık bakım
