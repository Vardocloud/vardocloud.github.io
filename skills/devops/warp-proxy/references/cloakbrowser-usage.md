# CloakBrowser Kullanımı (9 Haz 2026)

Cloudflare korumalı sitelere (Skool, vb.) erişim için alternatif browser engine.

## Kurulum

```bash
pip install cloakbrowser
playwright install chromium  # Playwright Chromium gerekli
```

## Güncel API (v2+)

**⚠️ Eski API kalktı:** `from cloakbrowser import PlaywrightCloudflareStealth` artık çalışmaz.

**Yeni API:**

```python
import asyncio
from cloakbrowser import launch_async

async def main():
    browser = await launch_async()
    page = await browser.new_page()
    await page.goto("https://example.com", wait_until="networkidle")
    # ... işlemler ...
    await browser.close()

asyncio.run(main())
```

Standart Playwright API'si ile birebir uyumlu — page.goto, page.fill, page.click, page.evaluate, page.screenshot vb. hepsi çalışır.

## Skool Erişimi için

CloakBrowser + WARP birlikte çalışır:

```python
import os, asyncio
from cloakbrowser import launch_async

async def fetch_skool():
    browser = await launch_async()
    page = await browser.new_page()
    
    # Login
    await page.goto("https://www.skool.com/login", wait_until="networkidle", timeout=60000)
    await page.fill('input[type="email"]', 'hesap@email.com')
    await page.fill('input[type="password"]', 'sifre')
    await page.click('button:has-text("LOG IN")')
    await page.wait_for_timeout(3000)
    
    # Topluluk sayfası
    await page.goto("https://www.skool.com/<slug>", wait_until="networkidle", timeout=60000)
    
    title = await page.title()
    text = await page.evaluate("() => document.body.innerText.substring(0, 10000)")
    
    await browser.close()
```

**Not:** CloakBrowser, Browserbase'den farklı olarak local Chromium kullanır. Bu nedenle:
- Cloudflare bazen daha agresif davranabilir (datacenter IP)
- WARP proxy ile kombine edilince daha başarılı
- Browserbase'den yavaş olabilir (ilk startup)
- Login sonrası cookie'ler local'de kalır — aynı session'da sayfalar arası geçişte kaybolmaz

## API Değişiklik Geçmişi

| Tarih | Değişiklik |
|-------|-----------|
| 9 Haz 2026 | `PlaywrightCloudflareStealth` kaldırıldı, `launch_async` birincil API oldu |

## Ne Zaman Kullanılır

| Durum | Öneri |
|-------|-------|
| Browserbase timeout veriyor | CloakBrowser dene |
| Cloudflare 403/block | CloakBrowser + WARP dene |
| Hızlı script gerekiyor | CloakBrowser (doğrudan Python) |
| Puppeteer MCP login çalışmıyor | CloakBrowser dene |
