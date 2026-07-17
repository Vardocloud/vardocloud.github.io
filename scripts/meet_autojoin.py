#!/usr/bin/env python3
"""
meet_autojoin.py — Google Meet otomatik katılım + transkript scripti.

Kullanım:
  python3 meet_autojoin.py <meet_url> [guest_name]

Yöntem sırası:
  1. Chromium profili → auth.json export → meet_join dene
  2. Chrome CDP (port 18800) → Companion mode → caption language Türkçe → transkript

Gereksinimler:
  - playwright (pip install playwright)
  - Chrome port 18800'de çalışıyor olmalı (NotebookLM MCP)
"""
import sys, time, os, json, subprocess, sqlite3

# === CONFIG ===
MEET_URL = sys.argv[1] if len(sys.argv) > 1 else None
GUEST_NAME = sys.argv[2] if len(sys.argv) > 2 else "Berkcan"
OUT_DIR = os.path.expanduser("~/.hermes/workspace/meetings")
CHROME_COOKIES_DB = os.path.expanduser("~/.config/chromium/Default/Cookies")
AUTH_JSON = os.path.expanduser("~/.hermes/workspace/meetings/auth.json")

# === HELPERS ===
def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def extract_meeting_id(url):
    """meet.google.com/xxx-yyyy-zzz → xxx-yyyy-zzz"""
    return url.rstrip("/").split("/")[-1].split("?")[0]

# === METHOD 1: Chromium Cookie Export → auth.json ===
def export_chromium_cookies():
    """Chromium profilinden Google cookie'lerini auth.json'a export et."""
    if not os.path.exists(CHROME_COOKIES_DB):
        return False
    
    try:
        c = sqlite3.connect(CHROME_COOKIES_DB)
        cookies = []
        for row in c.execute("""
            SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly, samesite, priority
            FROM cookies 
            WHERE host_key LIKE '%google.com' 
            AND name IN ('SID','HSID','SSID','APISID','SAPISID','__Secure-1PSID','__Secure-3PSID','__Secure-1PSIDTS','__Secure-3PSIDTS','OTZ','NID','__Secure-ENID')
        """):
            host_key, name, value, path, expires_utc, is_secure, is_httponly, samesite, priority = row
            if expires_utc and expires_utc > 0:
                expiry = expires_utc / 1000000 - 11644473600
            else:
                expiry = time.time() + 86400 * 30
            
            cookie = {
                "name": name, "value": value, "domain": host_key, "path": path,
                "expires": int(expiry) if expiry > time.time() else int(time.time()) + 86400 * 30,
                "httpOnly": bool(is_httponly), "secure": bool(is_secure),
                "sameSite": ["unspecified","lax","strict","no_restriction"][samesite] if samesite else "lax",
                "priority": ["low","medium","high"][priority] if priority else "medium",
            }
            cookies.append(cookie)
        c.close()
        
        auth = {"cookies": cookies, "origins": [{"origin": "https://meet.google.com", "localStorage": []}]}
        os.makedirs(os.path.dirname(AUTH_JSON), exist_ok=True)
        with open(AUTH_JSON, 'w') as f:
            json.dump(auth, f, indent=2)
        
        log(f"✅ {len(cookies)} cookie export edildi → auth.json")
        return True
    except Exception as e:
        log(f"⚠️ Cookie export hatası: {e}")
        return False

# === METHOD 2: Chrome CDP + Companion Mode ===
def join_via_chrome_cdp():
    """Chrome CDP (port 18800, Edel'in hesabı) ile Companion mode join + transkript."""
    from playwright.sync_api import sync_playwright
    
    meeting_id = extract_meeting_id(MEET_URL)
    transcript_path = os.path.join(OUT_DIR, meeting_id, "transcript.txt")
    os.makedirs(os.path.join(OUT_DIR, meeting_id), exist_ok=True)
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:18800")
        except Exception as e:
            log(f"❌ Chrome CDP bağlantı hatası: {e}")
            return False
        
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()
        
        log("Navigating to meeting...")
        page.goto(MEET_URL, wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        
        body = page.evaluate("document.body.innerText").lower()
        if "can't join" in body:
            log("❌ Toplantıya erişilemiyor (meeting bitti/kilitlendi)")
            page.close()
            return False
        
        # Dismiss dialogs (TR/EN)
        for label in ["continue without microphone", "got it", "devam et", "anladim", "tamam"]:
            try:
                for b in page.query_selector_all('button'):
                    t = (b.text_content() or '').lower()
                    aria = (b.get_attribute('aria-label') or '').lower()
                    if label in t or label in aria:
                        if b.is_visible():
                            b.click()
                            time.sleep(0.5)
                            break
            except: pass
        
        time.sleep(2)
        
        # Fill name if empty
        try:
            inp = page.query_selector('input[type="text"]')
            if inp:
                inp.fill(GUEST_NAME)
                log(f"Name: {GUEST_NAME}")
                time.sleep(0.5)
        except: pass
        
        # Companion mode join
        for label in ["other ways", "diger", "diğer"]:
            try:
                for b in page.query_selector_all('button'):
                    if label in (b.text_content() or '').lower():
                        b.click(); time.sleep(1); break
            except: pass
        
        for label in ["companion", "eslik", "eşlik"]:
            try:
                for b in page.query_selector_all('button'):
                    if label in (b.text_content() or '').lower():
                        b.click(); time.sleep(3); break
            except: pass
        
        time.sleep(3)
        body = page.evaluate("document.body.innerText").lower()
        if "can't join" in body:
            log("❌ Companion mode başarısız")
            page.close()
            return False
        
        log("✅ TOPLANTIDA!")
        
        # Turn on captions (TR/EN)
        page.evaluate("""() => {
            for (const b of document.querySelectorAll('button')) {
                const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                const text = (b.textContent || '').toLowerCase();
                if ((aria.includes('altyaz') && aria.includes('aç')) || 
                    (aria.includes('turn on captions')) ||
                    (text.includes('closed_caption_off'))) {
                    b.click(); return;
                }
            }
        }""")
        log("Captions toggled")
        time.sleep(2)
        
        # Switch language to Turkish
        page.evaluate("""() => {
            // Find language combobox
            const combo = document.querySelector('[role="combobox"][aria-label*="language" i], [role="combobox"][aria-label*="dil" i]');
            if (combo) {
                combo.click();
                setTimeout(() => {
                    const options = document.querySelectorAll('[role="option"]');
                    for (const opt of options) {
                        if (opt.textContent.includes('Turkish')) { opt.click(); break; }
                    }
                }, 500);
            }
        }""")
        log("Language switched to Turkish")
        time.sleep(3)
        
        # Main caption poll loop
        log("Starting caption poll...")
        seen = set()
        last_log = time.time()
        
        try:
            while True:
                caps = page.evaluate("""() => {
                    const found = [];
                    const cr = document.querySelector('[role="region"][aria-label*="aption" i]');
                    if (cr) {
                        cr.querySelectorAll(':scope span').forEach(s => {
                            const t = (s.textContent||'').trim();
                            if (t.length > 3) found.push(t);
                        });
                    }
                    document.querySelectorAll('[aria-live="polite"]').forEach(el => {
                        const t = (el.textContent||'').trim();
                        if (t.length > 5) found.push(t);
                    });
                    return [...new Set(found)];
                }""")
                
                if isinstance(caps, list):
                    for c in caps:
                        if c not in seen:
                            seen.add(c)
                            ts = time.strftime('%H:%M:%S')
                            with open(transcript_path, "a") as f:
                                f.write(f"[{ts}] {c}\n")
                            print(f"[CAPTION] {c}", flush=True)
                
                now = time.time()
                if now - last_log >= 60:
                    log(f"Alive: {len(seen)} lines captured")
                    last_log = now
                time.sleep(3)
        except KeyboardInterrupt:
            log("Stopped")
        except Exception as e:
            log(f"Poll error: {repr(e)}")
        
        log(f"Done. {len(seen)} lines → {transcript_path}")
        return True

# === MAIN ===
if __name__ == "__main__":
    if not MEET_URL:
        print("Usage: python3 meet_autojoin.py <meet_url> [guest_name]")
        sys.exit(1)
    
    log(f"Meet AutoJoin — {MEET_URL} as {GUEST_NAME}")
    
    # Method 1: Cookie export + meet_join
    cookie_ok = export_chromium_cookies()
    if cookie_ok:
        log("Cookies exported. Would call meet_join here (tool not available from script).")
        log("Falling through to Method 2: Chrome CDP...")
    
    # Method 2: Chrome CDP
    log("Method 2: Chrome CDP + Companion mode...")
    success = join_via_chrome_cdp()
    
    if not success:
        log("❌ Tüm yöntemler başarısız.")
        print("\n📋 Ne yapmalı:")
        print("  1. Edel'e bildir: 'Toplantıya otomatik katılamadım'")
        print("  2. Manuel dene: browser_navigate → Companion mode")
        print("  3. Remote node ile dene (Edel'in Mac/PC'sinden)")
    else:
        log("✅ Script tamamlandı.")
