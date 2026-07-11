import asyncio
from playwright.async_api import async_playwright

async def login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            proxy={"server": "socks5://127.0.0.1:1080"},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        page = await ctx.new_page()
        
        # Stealth script
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
        """)
        
        await page.goto("https://sso.apa.org/apasso/idm/apalogin?ERIGHTS_TARGET=https://www.apa.org", timeout=30000)
        await page.wait_for_timeout(4000)
        
        inputs = await page.query_selector_all("input")
        print(f"Input sayısı: {len(inputs)}")
        
        if len(inputs) < 2:
            body = await page.text_content("body") or ""
            print(f"Body: {body[:300]}")
            await browser.close()
            return
        
        await inputs[0].fill("isimgorulsunn@gmail.com")
        await inputs[1].fill("*^7ghUEYTxTSk5UcRvGJn3UkzWNd55")
        print("✅ Form dolduruldu")
        
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(6000)
        
        url = page.url
        print(f"URL: {url}")
        
        if "sso.apa.org" not in url:
            import json, os
            cookies = await ctx.cookies()
            os.makedirs("/home/ubuntu/.hermes/secrets", exist_ok=True)
            with open("/home/ubuntu/.hermes/secrets/apa_cookies.json", "w") as f:
                json.dump(cookies, f, indent=2)
            print(f"✅ BAŞARILI! {len(cookies)} cookie kaydedildi")
        else:
            body = await page.text_content("body") or ""
            print(f"Başarısız. Body: {body[:300]}")
        
        await browser.close()

asyncio.run(login())
