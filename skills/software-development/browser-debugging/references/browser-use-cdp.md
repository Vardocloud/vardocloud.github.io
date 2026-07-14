# Browser Use CDP Remote Browser

Ücretsiz residential IP browser — Playwright CDP bağlantısı.

## Bağlantı

```python
from playwright.async_api import async_playwright

CDP_URL = "wss://<session-id>.cdp.browser-use.com"

async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp(CDP_URL)
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else await context.new_page()
    # ...
    await browser.close()
```

## Skool Login Örneği

```python
import asyncio
from playwright.async_api import async_playwright

CDP_URL = "wss://49ceed8d-ca67-4bff-be4d-91c5b7762cbe.cdp.browser-use.com"

async def skool_login():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()
        
        await page.goto("https://www.skool.com/login", wait_until="networkidle", timeout=30000)
        
        # Email
        email = await page.query_selector('input[type="email"]')
        await email.fill("isimgorulsunn@gmail.com")
        
        # Password
        pwd = await page.query_selector('input[type="password"]')
        await pwd.fill("41y%#Y8#Htts*kx3*amf5YJNU37^mn")
        
        # Submit
        btn = await page.query_selector('button[type="submit"]')
        await btn.click()
        
        await page.wait_for_load_state("networkidle", timeout=15000)
        await asyncio.sleep(3)
        
        # Verify login
        content = await page.content()
        if "Vanilla" in content:
            print("LOGIN OK")
        
        await browser.close()

asyncio.run(skool_login())
```

## API Key

Browser Use API key: `bu_med7R2iddLji52IcXBRt4KsFj4-OAq_RNfbvbDRsFaY`
- Cloud session'lar ÜCRETLI (görev başına ücret)
- CDP bağlantısı ÜCRETSİZ (sadece browser connect)
- CDP URL'si dashboard'dan alınır, değişebilir

## Pitfalls

1. **Cloud session para harcar** — `client.sessions.create()` KULLANMA
2. **CDP URL değişir** — Yeni oturum açıldığında URL değişir, dashboard'dan kontrol et
3. **Sayfa boş** — `wait_until="networkidle"` + `asyncio.sleep(3)` ekle
4. **Browser kapatma** — İşlem bitince `await browser.close()` ile bağlantıyı kapat
5. **Çoklu context** — `browser.contexts[0]` ilk context'i alır, genelde yeterli
6. **Yeni sayfa** — `context.pages[0]` varsa kullan, yoksa `await context.new_page()` ile yeni aç
