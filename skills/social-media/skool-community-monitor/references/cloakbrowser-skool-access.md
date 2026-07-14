# CloakBrowser ile Skool Erişimi

Browserbase (engine: auto) timeout verdiğinde alternatif olarak local CloakBrowser kullan.

## Kurulum

CloakBrowser zaten yüklü: `/data/ubuntu/hermes-agent/venv/lib/python3.12/site-packages/cloakbrowser/`

Güncelleme:
```bash
pip install --upgrade cloakbrowser
```

## Güncel API (v2+)

Eski `PlaywrightCloudflareStealth` sınıfı kalktı. Yeni API:

```python
from cloakbrowser import launch_async

async def fetch_skool():
    browser = await launch_async()
    page = await browser.new_page()
    
    # Login
    await page.goto("https://www.skool.com/login", wait_until="networkidle", timeout=60000)
    await page.fill('input[type="email"]', EMAIL)
    await page.fill('input[type="password"]', PASSWORD)
    await page.click('button:has-text("LOG IN")')
    await page.wait_for_timeout(3000)
    
    # Community'ye git
    await page.goto(COMMUNITY_URL, wait_until="networkidle", timeout=60000)
    await page.wait_for_timeout(3000)
    
    # İçerik çek
    title = await page.title()
    url = page.url
    text = await page.evaluate("() => document.body.innerText")
    links = await page.evaluate("""
        () => Array.from(document.querySelectorAll('a'))
            .map(a => ({text: a.innerText.substring(0,100), href: a.href}))
            .filter(x => x.text || x.href)
    """)
    
    await browser.close()
```

## Önemli Noktalar

1. **Her session'da login gerekir** — CloakBrowser epheméral cookie saklamaz.
2. **Şifre environment variable'dan geçirilir** — asla koda gömme:
   ```bash
   SKOOL_PASSWORD="..." python3 script.py
   ```
3. **Stealth** — CloakBrowser Cloudflare bypass'ı yapar, WARP gibi ek proxy genelde gerekmez.
4. **Timeout** — 60sn yeterli olmazsa 90sn dene.
5. **Başarısız login** — Her login'den sonra sayfa URL'ini kontrol et:
   - Hala `/login` ise → login başarısız
   - Community sayfasında ise → başarılı
