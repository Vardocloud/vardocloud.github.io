# NotebookLM Auth Repair Workflow — Headless CDP

`nlm login --cdp-url` ile headless sunucuda auth yenileme.

**İKİ YÖNTEM:**
1. ✅ **ÖNCELİKLİ — Headless-only** (Playwright Chromium, `--headless=new`, X server GEREKMEZ)
2. ❌ **ESKİ/LEGACY — Xvfb + Snap Chromium** (X11 authority sorunlu, kaçın)

---

## YÖNTEM 1: Headless-Only (ÖNCELİKLİ) 🏆

X server, DISPLAY, Xauthority — hiçbiri gerekmez. `--headless=new` modunda çalışır.

### 1. Playwright Chromium'u Bul

```bash
# Genelde burada
~/.cache/ms-playwright/chromium-1223/chrome-linux/chrome

# Tam yol
find ~/.cache/ms-playwright -name "chrome" -path "*/chrome-linux/*" 2>/dev/null
```

### 2. Headless Chrome'u CDP ile Başlat

```bash
~/.cache/ms-playwright/chromium-1223/chrome-linux/chrome \
  --headless=new \
  --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --remote-debugging-port=9222 \
  --user-data-dir=/home/ubuntu/snap/chromium/common/chromium/nlm_profile \
  --no-first-run --disable-default-apps \
  about:blank 2>/dev/null &
```

**ARM64 uyumlu:** Playwright Chromium ARM64 için derlenmiştir (snap chromium'daki X11 authority sorunu yok).

### 3. CDP Hazır mı Kontrol Et

```bash
sleep 8
curl -s http://127.0.0.1:9222/json/version | head -5
```

Başarılı çıktı:
```json
{"Browser": "Chrome/148.0.7778.0", ...}
```

### 4. nlm login

```bash
nlm login --cdp-url http://127.0.0.1:9222 --force
```

Başarılı çıktı:
```
Successfully authenticated!
Profile: default
Cookies: ~60 extracted
CSRF Token: Yes
Account: isimgorulsunn@gmail.com
```

### 5. auth.json'u Güncelle (MCP Server İçin)

```python
import json, os
NLM_DIR = os.path.expanduser('~/.notebooklm-mcp-cli')
PROFILE_DIR = os.path.join(NLM_DIR, 'profiles', 'default')
with open(os.path.join(PROFILE_DIR, 'cookies.json')) as f: cookies = json.load(f)
with open(os.path.join(PROFILE_DIR, 'metadata.json')) as f: metadata = json.load(f)
auth = {
    'cookies': cookies,
    'csrf_token': metadata.get('csrf_token', ''),
    'session_id': metadata.get('session_id', ''),
    'build_label': metadata.get('build_label', ''),
    'extracted_at': metadata.get('extracted_at', '')
}
with open(os.path.join(NLM_DIR, 'auth.json'), 'w') as f: json.dump(auth, f, indent=2)
```

### 6. Gateway'i Restart Et

```bash
pkill -f hermes-gateway
sleep 3
systemctl --user start hermes-gateway
```

### 7. Doğrula

```bash
# CLI
nlm login --check
# → "Authentication valid!"

# MCP ile canlı test (en güvenilir)
# → notebook_list çalışıyorsa auth sağlamdır
```

---

## YÖNTEM 2: Xvfb + Snap Chromium (LEGACY — Kaçın)

Snap chromium (`/usr/bin/chromium-browser`) headless sunucuda X11 authority sorunu verir:
- "Authorization required, but no authorization protocol specified"
- `sudo snap connect chromium:x11` çözmez
- Gateway restart'ı Xvfb authority dosyasını değiştirir (eski yol geçersiz)

**Sadece Yöntem 1 çalışmazsa dene.** Xvfb + DISPLAY=:99 + xhost gerektirir.

---

## Otomatik Script

`~/.nlm/refresh_cookies.py` ve `~/.nlm/check_auth.sh` bu iş akışını otomatikleştirir:

- **Her 12 saatte bir** cron job (`NotebookLM Cookie Auto-Refresh`) çalışır
- Headless Chrome başlatır → `nlm login --cdp-url` → auth.json günceller
- Başarısız olursa Telegram alert gönderir

**Script path:** `~/.hermes/scripts/nlm-auth-refresh.sh`

---

## Auth Status & Heuristic

| Gösterge | Anlamı | Gerçek Durum |
|----------|--------|--------------|
| `server_info: "stale"` | Cookie yaşı 7+ gün | **⚠️ Gerçek expired olabilir** — write test yapmadan emin olma |
| `nlm login --check` valid | CLI testi geçti | ✅ Sadece okuma token'ı geçerli — yazma ayrı test edilmeli |
| `notebook_list` 30+ notebook | Read ops çalışıyor | ✅ En azından okuma çalışıyor |
| `studio_create` başarılı | Write ops çalışıyor | ✅ Tam yetkili, gerçek auth sağlam |
| `nlm report create` başarılı | CLI write testi | ✅ En güvenilir test |
| `refresh_auth: "expired"` | MCP server cookie cache'i | ⚠️ **DİKKAT:** Bu artık sadece cache değil, gerçek expired olabilir |

## Auth Asimetrisi (8 Haz 2026 — KRİTİK)

NotebookLM'in okuma ve yazma token'ları **farklı sürelere sahiptir**. Yazma token'ı daha hızlı expire olur.

| İşlem Tipi | Çalışır? | Açıklama |
|------------|----------|----------|
| `notebook_list`, `notebook_query` | ✅ | Read ops — genelde çalışır |
| `source_add(type="text")`, `source_add(type="url")` | ✅ | Source ekleme — çalışır |
| `nlm login --check` | ✅ | CLI read testi — geçer |
| `studio_create` (slide_deck, audio, report, video) | ❌ | "auth is not valid (reason: expired)" |
| `nlm report create` | ❌ | "PERMISSION_DENIED (code 7)" |
| `nlm video create`, `nlm audio create` | ❌ | Aynı şekilde bloke |

**Sonuç:** `nlm login --check` valid gösterse de yazma işlemleri çalışmayabilir. CLI ve MCP aynı auth token setini kullanır.

**Doğrulama prosedürü:**
```bash
# 1. CLI read test — yetersiz
nlm login --check
# → "Authentication valid!"

# 2. CLI write test — ZORUNLU
nlm report create <NOTEBOOK_ID> --format "Briefing Doc" --confirm -y
# → "PERMISSION_DENIED" alırsan yazma kapalı
```

## WebSocket CDP 403 Hatası (Chrome 148+, 8 Haz 2026)

`--remote-allow-origins=*` flag'i Chrome 148'de WebSocket için **yetersiz kalır**:

```bash
# BU ÇALIŞMAZ:
CHROME=~/.cache/ms-playwright/chromium-1223/chrome-linux/chrome
$CHROME --headless=new --no-sandbox --disable-gpu \\
  --remote-debugging-port=9222 --remote-allow-origins=* \\
  ... about:blank

# Puppeteer bağlanmaya çalışınca:
# WebSocketBadStatusException: Handshake status 403 Forbidden
```

Bu Chrome'un kendi güvenlik kısıtlaması — origin check'i bypass edilemez.

**Çözüm:** CDP'yi tamamen atla, doğrudan `nlm login --manual -f cookies.json` kullan. Kullanıcıdan fresh cookie export iste, elle import et. Bu her zaman çalışır.

---

## Pitfalls

- **Headless Chrome profili önemli:** `--user-data-dir` ile belirtilen profilde daha önce Google oturumu açılmış olmalı. İlk seferde `about:blank` açılır, nlm login Chrome'un cache'lediği cookie'leri kullanır. Profil boşsa login başarısız olur (önce bir kere manuel login gerekir).
- **Playwright Chromium versiyonu:** `chromium-1223` altındaki Chrome binary'si. `npx playwright install chromium` ile güncellenebilir.
- **Gateway restart'ı sırasında session kesilir:** `pkill -f hermes-gateway` çalıştırdığında mevcut Hermes oturumun sonlanır. Önce işlemleri bitir.
- **ARM64 uyumluluğu:** Google Chrome'un ARM64 için resmi .deb'i yoktur. Playwright Chromium ARM64'te çalışan tek headless Chrome seçeneğidir.
