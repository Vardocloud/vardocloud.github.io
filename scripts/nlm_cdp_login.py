#!/usr/bin/env python3
"""NotebookLM'de oturum aç — keepalive Chrome CDP üzerinden.
Bitwarden'dan Google şifresini alır, login formunu doldurur.
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
    """Bitwarden'dan şifreyi al."""
    import urllib.request
    url = f"http://127.0.0.1:8087/object/item/{BW_ITEM_ID}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    pw = data.get("data", {}).get("login", {}).get("password", "")
    if not pw:
        log("❌ Şifre alınamadı!")
        sys.exit(1)
    return pw

def main():
    log("🔐 NotebookLM CDP Login başlıyor...")

    # 1. Şifreyi al
    log("📦 Bitwarden'dan şifre alınıyor...")
    password = get_password()
    log("✅ Şifre alındı")
    email = "isimgorulsunn@gmail.com"

    # 2. Playwright ile keepalive Chrome'a bağlan
    log(f"🔗 Keepalive Chrome'a bağlanılıyor ({CDP_URL})...")
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp(CDP_URL)
    log(f"✅ Bağlantı başarılı — {len(browser.contexts)} context")

    # 3. Yeni sayfa aç
    ctx = browser.contexts[0] if browser.contexts else browser.new_context()
    page = ctx.new_page()
    log("🌐 Yeni sekme açıldı")

    # 4. notebooklm.google.com'a git
    log(f"📂 {NOTEBOOKLM_URL} açılıyor...")
    page.goto(NOTEBOOKLM_URL, wait_until="domcontentloaded", timeout=30000)

    # Sayfanın yüklenmesini bekle
    time.sleep(3)

    current_url = page.url
    log(f"📍 Mevcut URL: {current_url[:120]}")

    # 5. Login sayfası mı kontrol et
    if "accounts.google.com" in current_url or "signin" in current_url:
        log("🔑 Login sayfası tespit edildi, form dolduruluyor...")

        # 5a. Email gir
        try:
            # Email input'unu bekle
            email_input = page.locator('input[type="email"], input[name="identifier"], #identifierId').first
            email_input.wait_for(timeout=10000)
            email_input.fill(email)
            log(f"✉️ Email girildi: {email}")

            # "İleri" / "Next" butonuna tıkla
            time.sleep(1)
            next_btn = page.locator('button:has-text("İleri"), button:has-text("Next"), #identifierNext, [jscontroller="soHxf"]').first
            next_btn.wait_for(timeout=5000)
            next_btn.click()
            log("👉 'İleri' tıklandı")
            time.sleep(3)

            # 5b. "Diğer oturum açma seçenekleri" kontrolü
            current_url2 = page.url
            log(f"📍 URL: {current_url2[:120]}")

            # Eğer "diğer seçenekler" sayfası geldiyse, "Şifre ile giriş yap" seç
            try:
                other_options = page.locator('text=Diğer oturum açma seçenekleri, text=Other sign-in options, [jsname="Cuz2Ue"]').first
                if other_options.is_visible(timeout=2000):
                    log("🔀 'Diğer oturum açma seçenekleri' bulundu")
                    # "Şifre ile giriş yap" seçeneğini tıkla
                    pw_option = page.locator('text=Şifre ile giriş yap, text=Use your password, [jsname="V9tsb"]').first
                    if pw_option.is_visible(timeout=2000):
                        pw_option.click()
                        log("🔑 'Şifre ile giriş yap' seçildi")
                        time.sleep(2)
            except Exception:
                log("ℹ️ 'Diğer seçenekler' sayfası yok, direkt şifre ekranı")

            # 5c. Şifre gir
            pw_input = page.locator('input[type="password"], input[name="Passwd"]').first
            pw_input.wait_for(timeout=10000)
            pw_input.fill(password)
            log("🔑 Şifre girildi")

            time.sleep(1)
            next_btn2 = page.locator('button:has-text("İleri"), button:has-text("Next"), #passwordNext, [jscontroller="soHxf"]').first
            next_btn2.wait_for(timeout=5000)
            next_btn2.click()
            log("👉 'İleri' tıklandı (şifre sonrası)")

            # 5d. Yönlendirmeyi bekle
            time.sleep(5)

            # Sayfanın notebooklm'a yönlenmesini bekle
            try:
                page.wait_for_url("**/notebook/**", timeout=30000)
                log("✅ NotebookLM'e yönlendirildi!")
            except:
                log(f"⚠️ Son URL: {page.url[:120]}")
                # Belki başka bir ekran (2FA, vs)
                try:
                    page.wait_for_url("**notebooklm.google.com**", timeout=15000)
                    log("✅ NotebookLM'e ulaşıldı!")
                except:
                    log("⚠️ Zaman aşımı — manuel kontrol gerekebilir")

        except Exception as e:
            log(f"❌ Hata: {e}")
            # Son durumu göster
            log(f"📍 Son URL: {page.url[:120]}")
            try:
                page.screenshot(path="/tmp/nlm_login_error.png")
                log("📸 Ekran görüntüsü: /tmp/nlm_login_error.png")
            except:
                pass
    else:
        log("✅ Zaten NotebookLM'de görünüyor — auth geçerli olabilir")

    # 6. Cookie durumunu kontrol et
    cookies = page.context.cookies()
    google_cookies = [c for c in cookies if "google.com" in c.get("domain", "")]
    nlm_cookies = [c for c in cookies if "notebooklm" in c.get("domain", "")]
    log(f"🍪 Google cookie: {len(google_cookies)}, NotebookLM cookie: {len(nlm_cookies)}")

    # 7. Bağlantıları temizle
    page.close()
    browser.close()
    pw.stop()

    log("✅ İşlem tamamlandı")
    return 0

if __name__ == "__main__":
    sys.exit(main())
