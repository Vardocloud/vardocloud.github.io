# Playwright ile Instagram DM Gönderme

## Genel Bakış

Instagram API'si ile thread oluşturulabilir ama mesaj gönderme (`broadcast/text`) `useragent mismatch` hatası verir. Çözüm: API ile thread oluştur, Playwright ile mesajı yazıp gönder.

## İki Aşamalı Akış

### Aşama 1: API ile Thread Oluştur (curl)

```bash
ALL_PROXY=socks5://127.0.0.1:1080 CSRF=$(grep csrftoken ~/.hermes/instagram_cookies.txt | head -1 | awk '{print $NF}') && \
curl -s --max-time 20 \
  -b ~/.hermes/instagram_cookies.txt \
  -H 'User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)' \
  -H "X-CSRFToken: $CSRF" \
  -H 'X-IG-App-ID: 936619743392459' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
  -d "recipient_users=[\"TARGET_USER_ID\"]&text=ilk-mesaj&_csrftoken=${CSRF}&_uuid=$(python3 -c 'import uuid;print(uuid.uuid4())')" \
  'https://www.instagram.com/api/v1/direct_v2/create_group_thread/'
```

Yanıttan `thread_id` al. Örn: `340282366841710301244259173000696496060`

### Aşama 2: Playwright ile Mesaj Gönder

```python
import builtins, time, os

# Cookie'leri parse et
cookie_path = os.path.expanduser("~/.hermes/instagram_cookies.txt")
cookies = []
with builtins.open(cookie_path) as f:
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

from playwright.sync_api import sync_playwright

thread_id = "THREAD_ID_FROM_API"  # Aşama 1'den al

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        proxy={"server": "socks5://127.0.0.1:1080"},
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    )
    ctx.add_cookies(cookies)
    page = ctx.new_page()
    
    # Direkt thread'e git
    page.goto(f"https://www.instagram.com/direct/t/{thread_id}/", wait_until="networkidle", timeout=25000)
    time.sleep(3)
    
    # Mesaj yaz
    msg_area = page.locator('[contenteditable="true"], [role="textbox"], textarea').first
    msg_area.click()
    time.sleep(0.5)
    msg_area.fill("MESAJ_BURAYA")
    time.sleep(1)
    
    # Gönder (Send butonu veya Enter)
    send_btn = page.locator('button:has-text("Send"), button:has-text("Gonder")').first
    if send_btn.is_visible(timeout=2000):
        send_btn.click()
    else:
        msg_area.press("Enter")
    
    time.sleep(2)
    browser.close()
```

## Kullanıcı ID'si Bulma

```bash
ALL_PROXY=socks5://127.0.0.1:1080 curl -s --max-time 15 \
  -b ~/.hermes/instagram_cookies.txt \
  -H 'User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)' \
  -H 'X-IG-App-ID: 936619743392459' \
  -H 'X-Requested-With: XMLHttpRequest' \
  'https://www.instagram.com/api/v1/users/web_profile_info/?username=KULLANICI_ADI' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['user']['id'])"
```

## Pitfalls

| Hata | Çözüm |
|------|-------|
| `broadcast/text` → `useragent mismatch` | API ile mesaj gönderilemez. Playwright kullan. |
| `create_group_thread` → `text` parametresi mesajı göndermez | Sadece thread oluşturur. Mesaj için Playwright gerek. |
| Playwright'ta "Message" butonu görünmüyor | Kendi profiline mesaj atamazsın. Thread ID ile direkt `/direct/t/{id}` git. |
| Profil sayfasında "Follow" var, "Message" yok | Takip etmediğin kişiye direkt DM atamazsın. API ile thread oluştur, sonra Playwright. |
