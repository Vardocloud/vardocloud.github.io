# Instagram Automation — Kurulum

## Playwright Kurulumu

```bash
pip install playwright --break-system-packages
```

> `--break-system-packages`: PEP 668 korumasını aşmak için. Sunucuda venv yerine sistem Python'u kullanıldığında gerekli.

## Chromium

Mevcut binary: `/usr/bin/chromium-browser` (snap)

Playwright kendi Chromium'unu da kullanabilir:
```bash
playwright install chromium
```

### ⚠️ --no-sandbox ZORUNLU (Oracle Cloud / Snap Chromium)

Snap Chromium, headless modda sandbox hatası verir (`EPIPE`, `TargetClosedError`).
Tüm `chromium.launch()` çağrılarında `--no-sandbox` kullan:

```python
browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
```

Bu olmadan Playwright ya hiç başlamaz ya da ilk `page.goto()`'da EPIPE ile çöker.
Test komutu:
```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox'])
    ctx = b.new_context(proxy={'server': 'socks5://127.0.0.1:1080'})
    page = ctx.new_page()
    page.goto('https://httpbin.org/ip', timeout=15000)
    print(page.inner_text('body'))
    b.close()
    print('OK')
"
```

## WARP Proxy

Zaten kurulu ve çalışıyor olmalı. Kontrol:
```bash
curl -x "socks5h://127.0.0.1:1080" "https://www.cloudflare.com/cdn-cgi/trace" | grep warp
# Çıktı: warp=plus  → OK
```

Proxy adresi: `socks5://127.0.0.1:1080`

## Cookie Dosyası

Konum: `~/.hermes/instagram_cookies.txt`
İzin: `chmod 600`
Format: Netscape cookie jar (TAB ayrımlı)

## Güvenlik Kontrol Listesi

- [ ] Cookie dosyası oluşturuldu ve `chmod 600`
- [ ] WARP proxy çalışıyor (`warp=plus`)
- [ ] Chromium mevcut (`which chromium-browser`)
- [ ] Playwright kurulu (`python3 -c "import playwright"`)
