# No-Agent API Polling Pattern (Token-Free)

Instagram API'sini tekrarlayan şekilde kontrol etmek için LLM/token harcamayan
Python script pattern'i. `no_agent=true` cron job olarak çalışır.

## Ne Zaman Kullanılır?

- Periyodik durum kontrolü (takip isteği, DM, like, vs.)
- Cevap gerektirmeyen, sadece "değişiklik var mı?" sorusu
- LLM reasoning'i gereksiz — API yanıtı deterministik

## Mimari

```
Cron (every 30m) → Python script → curl + WARP → Instagram API
                                     ↓
                              State file (JSON)
                                     ↓
                         Değişiklik var mı?
                         ├─ Hayır → sessiz (stdout boş)
                         └─ Evet → mesaj yaz → Telegram'a iletilir
```

## Script Şablonu

```python
#!/usr/bin/env python3
"""No-agent polling script. SADECE durum değişirse stdout'a yazar."""
import subprocess, json, os, sys

# --- CONFIG ---
STATE_FILE = os.path.expanduser("~/.hermes/cron/durum.json")
COOKIE_FILE = os.path.expanduser("~/.hermes/instagram_cookies.txt")
CURL = "/usr/bin/curl"  # Tam path ZORUNLU (cron PATH sınırlı)

def parse_cookies(path):
    """Netscape cookie jar → {name: value}"""
    cookies = {}
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 7:
                cookies[parts[5]] = parts[6]
    return cookies

def api_call(url):
    cookies = parse_cookies(COOKIE_FILE)
    csrf = cookies.get("csrftoken", "")
    result = subprocess.run([
        CURL, "-s", "--socks5", "127.0.0.1:1080",
        "-b", COOKIE_FILE,
        "-H", f"X-CSRFToken: {csrf}",
        "-H", "X-IG-App-ID: 936619743392459",
        "-H", "X-Requested-With: XMLHttpRequest",
        "-H", "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
        "-w", "\n%{http_code}",
        url, "--max-time", "20"
    ], capture_output=True, text=True, timeout=25,
       env={**os.environ, "ALL_PROXY": ""})  # ALL_PROXY="" ZORUNLU

    if result.returncode != 0:
        return None
    lines = result.stdout.strip().split("\n")
    http_code = lines[-1].strip()
    if http_code != "200":
        return None
    try:
        return json.loads("\n".join(lines[:-1]))
    except json.JSONDecodeError:
        return None

# --- Ana Akış ---
data = api_call("https://www.instagram.com/api/v1/...")
if data is None:
    sys.exit(0)  # API hatası → sessiz

current = extract_relevant_fields(data)  # projeye özel

# Önceki durumu oku
prev = {}
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        prev = json.load(f)

# Durumu kaydet
os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
with open(STATE_FILE, "w") as f:
    json.dump(current, f)

# İlk çalıştırma → sessiz (state yeni oluştu)
if not prev:
    sys.exit(0)

# Değişiklik kontrolü
if state_changed(prev, current):
    print("🔔 Durum değişti: ...")  # stdout → Telegram'a gider
else:
    pass  # sessiz
```

## Kritik Noktalar (PITFALLS)

| Pitfall | Çözüm |
|---------|-------|
| `curl` bulunamadı (cron PATH) | `/usr/bin/curl` tam path kullan |
| ALL_PROXY çakışması | `env={**os.environ, "ALL_PROXY": ""}` |
| HTTP 403/401 sessizce geçilmeli | HTTP kodu kontrolü, 200 değilse `sys.exit(0)` |
| İlk çalıştırmada false alarm | `if not prev: sys.exit(0)` → state'i kaydeder ama mesaj atmaz |
| State dosyası yok → hata | `os.makedirs(os.path.dirname(...), exist_ok=True)` |
| Cron job delivery hedefi | no_agent script'lerde deliver otomatik — stdout Telegram'a gider |

## Mevcut Implementasyon

`~/.hermes/scripts/ig_takip_kontrol.py` — Instagram takip isteği durumunu 30dk'da bir kontrol eder.
Cron job: `e7458e949c41`, deliver: Operasyon Karargahı (thread 16).
