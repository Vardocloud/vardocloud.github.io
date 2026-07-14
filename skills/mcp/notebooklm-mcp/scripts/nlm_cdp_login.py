#!/usr/bin/env python3
"""NotebookLM'de oturum aç — keepalive Chrome CDP üzerinden.
Bitwarden'dan Google şifresini alır, Playwright ile login formunu doldurur.
"""

import json, sys, time, os

CDP_URL = "http://127.0.0.1:18800"
BW_ITEM_ID = "8a95abcd-65dd-4aa5-a255-b4660182d7cf"  # Google-isimgorulsunn
NOTEBOOKLM_URL = "https://notebooklm.google.com"
LOG_FILE = os.path.expanduser("~/.hermes/logs/nlm_cdp_login.log")

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def get_password():
    import urllib.request
    url = f"http://127.0.0.1:8087/object/item/{BW_ITEM_ID}"
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read())
    pw = data.get("data", {}).get("login", {}).get("password", "")
    if not pw:
        log("❌ Şifre alınamadı!")
        sys.exit(1)
    return pw

def main():
    log("🔐 NotebookLM CDP Login başlıyor...")
    password = get_password()
    log("✅ Şifre alındı")
    email = "isimgorulsunn@gmail.com"

    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp(CDP_URL)
    ctx = browser.contexts[0] if browser.contexts else browser.new_context()
    page = ctx.new_page()
    log("🌐 Yeni sekme açıldı")

    page.goto(NOTEBOOKLM_URL, wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    current_url = page.url
    log(f"📍 URL: {current_url[:120]}")

    if "accounts.google.com" in current_url or "signin" in current_url:
        log("🔑 Login sayfası — form dolduruluyor...")
        email_input = page.locator('input[type="email"], input[name="identifier"], #identifierId').first
        email_input.wait_for(timeout=10000)
        email_input.fill(email)
        log(f"✉️ Email: {email}")
        time.sleep(1)
        next_btn = page.locator('button:has-text("İleri"), button:has-text("Next"), #identifierNext').first
        next_btn.wait_for(timeout=5000)
        next_btn.click()
        log("👉 İleri tıklandı")
        time.sleep(3)

        # "Diğer oturum açma seçenekleri" → "Şifre ile giriş yap"
        try:
            other_opts = page.locator('text=Diğer oturum açma seçenekleri, text=Other sign-in options').first
            if other_opts.is_visible(timeout=2000):
                log("🔀 Diğer seçenekler bulundu")
                pw_opt = page.locator('text=Şifre ile giriş yap, text=Use your password').first
                if pw_opt.is_visible(timeout=2000):
                    pw_opt.click()
                    log("🔑 Şifre ile giriş seçildi")
                    time.sleep(2)
        except:
            log("ℹ️ Direkt şifre ekranı")

        pw_input = page.locator('input[type="password"], input[name="Passwd"]').first
        pw_input.wait_for(timeout=10000)
        pw_input.fill(password)
        log("🔑 Şifre girildi")
        time.sleep(1)
        next_btn2 = page.locator('button:has-text("İleri"), button:has-text("Next"), #passwordNext').first
        next_btn2.wait_for(timeout=5000)
        next_btn2.click()
        log("👉 İleri tıklandı (şifre)")
        time.sleep(5)

        try:
            page.wait_for_url("**notebooklm.google.com/**", timeout=30000)
            log("✅ NotebookLM'e yönlendirildi!")
        except:
            log(f"⚠️ Son URL: {page.url[:120]}")
            page.screenshot(path="/tmp/nlm_login_result.png")
    else:
        log("✅ Zaten NotebookLM'de")

    cookies = page.context.cookies()
    nlm_c = [c for c in cookies if "notebooklm" in c.get("domain", "")]
    log(f"🍪 NotebookLM cookie: {len(nlm_c)}")

    page.close(); browser.close(); pw.stop()
    log("✅ Tamamlandı")
    return 0

if __name__ == "__main__":
    sys.exit(main())
