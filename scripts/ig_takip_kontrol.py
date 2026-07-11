#!/usr/bin/env python3
"""
IG Takip Kontrolü — Token harcamaz (no_agent).
SADECE durum değişirse stdout'a yazar, değişmezse sessiz.

Kullanılan cookie: @melkora_ (ID: 65631980467)
Hedef: @minipak3223 (ID: 74806716932)
"""
import subprocess, json, os, sys

USER_ID = "74806716932"
USERNAME = "minipak3223"
EXPECTED_DS_USER = "65631980467"  # melkora_ user ID

# DÜZELTME: Bardopsikoloji değil, Melkora cookie'si kullanılacak
COOKIE_FILE = os.path.expanduser("~/.hermes/melkora_cookies.txt")
STATE_FILE = os.path.expanduser("~/.hermes/cron/ig_takip_durumu.json")
CURL = "/usr/bin/curl"

def parse_netscape_cookies(path):
    """Netscape cookie jar'dan dict çıkar."""
    cookies = {}
    try:
        with open(path) as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.strip().split("\t")
                if len(parts) >= 7:
                    cookies[parts[5]] = parts[6]
    except FileNotFoundError:
        return None
    return cookies

def verify_cookie():
    """Cookie'nin @melkora_ hesabına ait olduğunu doğrula."""
    cookies = parse_netscape_cookies(COOKIE_FILE)
    if cookies is None:
        return False
    ds_user = cookies.get("ds_user_id", "")
    return ds_user == EXPECTED_DS_USER

def check_friendship():
    if not verify_cookie():
        return None
    
    cookies = parse_netscape_cookies(COOKIE_FILE)
    csrf = cookies.get("csrftoken", "")
    
    cmd = [
        CURL, "-s", "--socks5", "127.0.0.1:1080",
        "-b", COOKIE_FILE,
        "-H", f"X-CSRFToken: {csrf}",
        "-H", "X-IG-App-ID: 936619743392459",
        "-H", "X-Requested-With: XMLHttpRequest",
        "-H", "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
        "-w", "\n%{http_code}",
        f"https://www.instagram.com/api/v1/friendships/show/{USER_ID}/",
        "--max-time", "20"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=25, env={**os.environ, "ALL_PROXY": ""})
    
    if result.returncode != 0 or not result.stdout.strip():
        return None
    
    # Parse: son satır HTTP kodu, öncesi JSON
    lines = result.stdout.strip().split("\n")
    http_code = lines[-1].strip()
    json_str = "\n".join(lines[:-1])
    
    if http_code != "200":
        return None
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None

# --- Ana akış ---
data = check_friendship()

if data is None:
    sys.exit(0)  # API hatası → sessiz

current = {
    "following": data.get("following", False),
    "followed_by": data.get("followed_by", False),
    "outgoing_request": data.get("outgoing_request", False),
    "is_private": data.get("is_private", False),
}

# Önceki durumu oku
prev = {}
if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE) as f:
            prev = json.load(f)
    except (json.JSONDecodeError, IOError):
        pass

# Durumu kaydet
os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
with open(STATE_FILE, "w") as f:
    json.dump(current, f)

# İlk çalıştırma → sessiz
if not prev:
    sys.exit(0)

# Durum değişikliği kontrolü
was_pending = prev.get("outgoing_request") is True
now_accepted = current.get("followed_by") is True
now_rejected = (current.get("outgoing_request") is False 
               and current.get("followed_by") is False 
               and prev.get("outgoing_request") is True)

if was_pending and now_accepted:
    print(f"🎯 TAKİP KABUL EDİLDİ! {USERNAME} seni takip etmeye başladı. DM zamanı!")
elif now_rejected:
    print(f"❌ Takip isteği reddedildi veya geri çekildi: {USERNAME}")
else:
    pass  # Değişiklik yok → sessiz
