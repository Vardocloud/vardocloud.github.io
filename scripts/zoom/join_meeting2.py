#!/usr/bin/env python3
"""
Zoom Meeting 2 — APA Webinar Join + Recording Switch
20:55'te cron tetikler. Eski ffmpeg'i durdurur, yenisini başlatır, join yapar.
"""
import json, urllib.request, urllib.parse, time, sys, os, subprocess

MEETING_URL = "https://apa-org.zoom.us/w/94249463797?tk=qPUwbLU8hl1ryGiz5dLZSUN4BLoPvWYmmDUwCqzidQE.DQkAAAAV8bSv9RZvMEM4cUN6LVEwNjBlb3MyS3lGNDV3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA&uuid=WN_XTPBWAw5Rcu18lqjRfUKvQ"
DIRECT_JOIN_URL = "https://apa-org.zoom.us/wc/join/94249463797"
NAME = "Berkcan Ulucan"
CHROME_PORT = 9334  # Meeting 2 ayrı Chrome'da (9333 = meeting 1)

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def get_tabs(port):
    return json.loads(urllib.request.urlopen(f'http://localhost:{port}/json').read())

def get_zoom_tab(port):
    tabs = get_tabs(port)
    for t in tabs:
        url = t.get('url', '')
        if 'zoom.us' in url:
            return t
    return None

def cdp_evaluate(ws, expression, user_gesture=False, timeout=15):
    ws.send(json.dumps({
        'id': int(time.time() * 1000) % 100000,
        'method': 'Runtime.evaluate',
        'params': {
            'expression': expression,
            'returnByValue': True,
            'userGesture': user_gesture,
        }
    }))
    ws.settimeout(timeout)
    resp = json.loads(ws.recv())
    result = resp.get('result', {}).get('result', {})
    return result.get('value', result)

def stop_old_ffmpeg():
    """Eski ffmpeg kaydını durdur, dosyayı bildir"""
    log("Eski ffmpeg durduruluyor...")
    os.system('pkill -f "ffmpeg.*zoom_rec.monitor" 2>/dev/null || true')
    time.sleep(2)
    # Eski kayıt dosyası
    try:
        with open('/tmp/zoom_rec_file.txt') as f:
            old_file = f.read().strip()
            if old_file and os.path.exists(old_file):
                size_mb = os.path.getsize(old_file) / (1024*1024)
                log(f"Meeting 1 kaydı: {old_file} ({size_mb:.1f}MB)")
    except:
        pass

def start_new_ffmpeg():
    """Yeni ffmpeg kaydı başlat"""
    log("Yeni ffmpeg başlatılıyor...")
    new_file = f"/home/ubuntu/recordings/zoom_meeting2_{time.strftime('%Y%m%d_%H%M')}.mp3"
    
    proc = subprocess.Popen([
        'ffmpeg', '-y', '-f', 'pulse', '-i', 'zoom_rec.monitor',
        '-c:a', 'libmp3lame', '-b:a', '128k', new_file
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(2)
    with open('/tmp/zoom_rec_file.txt', 'w') as f:
        f.write(new_file)
    log(f"Kayıt başladı: {new_file} (PID: {proc.pid})")
    return new_file

def navigate_to_url(port, url):
    """CDP ile URL'e git"""
    tabs = get_tabs(port)
    # Boş tab bul veya Zoom tab'larını kapat
    for t in tabs:
        t_url = t.get('url', '')
        if 'zoom.us' in t_url:
            # Mevcut Zoom tab'ını kapatıp yeni aç
            try:
                urllib.request.urlopen(f'http://localhost:{port}/json/close/{t["id"]}')
                log(f"Eski Zoom tab'ı kapatıldı: {t['id']}")
            except:
                pass
    
    time.sleep(1)
    # Yeni tab aç
    try:
        encoded_url = urllib.parse.quote(url, safe='')
        urllib.request.urlopen(f'http://localhost:{port}/json/new?{encoded_url}')
        log("Yeni tab açıldı")
        time.sleep(8)
        return True
    except Exception as e:
        log(f"Tab açma hatası: {e}")
        return False

def main():
    log("=== Zoom Meeting 2 — APA Webinar ===")
    log(f"URL: {MEETING_URL[:80]}...")
    
    # 1. Chrome kontrol — ölüyse restart et
    chrome_alive = False
    try:
        ver = json.loads(urllib.request.urlopen(f'http://localhost:{CHROME_PORT}/json/version').read())
        log(f"Chrome: {ver.get('Browser', 'ok')}")
        chrome_alive = True
    except:
        pass
    
    if not chrome_alive:
        log(f"⚠️ Chrome {CHROME_PORT} ölü, restart ediliyor...")
        import subprocess
        subprocess.Popen([
            '/data/ubuntu/cache/ms-playwright/chromium-1223/chrome-linux/chrome',
            '--no-sandbox', f'--remote-debugging-port={CHROME_PORT}',
            '--remote-allow-origins=*', '--user-data-dir=/tmp/zoom_profile2',
            '--no-first-run', '--no-default-browser-check',
            '--disable-features=TranslateUI', '--ozone-platform=x11',
            '--window-size=1280,720', '--use-fake-device-for-media-stream',
            '--use-fake-ui-for-media-stream'
        ], env={**dict(os.environ), 'PULSE_SINK': 'zoom_rec_2', 'DISPLAY': ':99'})
        # Chrome'un hazır olmasını bekle
        for i in range(20):
            time.sleep(1)
            try:
                json.loads(urllib.request.urlopen(f'http://localhost:{CHROME_PORT}/json/version').read())
                log(f"Chrome restart OK ({i+1}s)")
                chrome_alive = True
                break
            except:
                pass
        
        if not chrome_alive:
            log("HATA: Chrome restart başarısız!")
            sys.exit(1)
    
    # 2. ffmpeg kontrol (zaten çalışıyor olmalı)
    ffmpeg_running = os.system('pgrep -f "ffmpeg.*zoom_rec_2.monitor" > /dev/null 2>&1') == 0
    if ffmpeg_running:
        log("ffmpeg meeting 2: ✅ çalışıyor")
    else:
        log("⚠️ ffmpeg meeting 2 çalışmıyor, başlatılıyor...")
        rec_file = f"/home/ubuntu/recordings/zoom_meeting2_{time.strftime('%Y%m%d_%H%M')}.mp3"
        subprocess.Popen([
            'ffmpeg', '-y', '-f', 'pulse', '-i', 'zoom_rec_2.monitor',
            '-c:a', 'libmp3lame', '-b:a', '128k', rec_file
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        log(f"Yeni kayıt: {rec_file}")
    
    # 4. Navigate — önce landing page'i dene
    log("Join sayfasına gidiliyor (landing page)...")
    navigate_to_url(CHROME_PORT, MEETING_URL)
    
    # 5. Tab'ı bul
    from websocket import create_connection
    tab = get_zoom_tab(CHROME_PORT)
    if not tab:
        # Landing page başarısız olduysa direkt join dene
        log("Landing page'te Zoom tab'ı yok, direkt join deneniyor...")
        navigate_to_url(CHROME_PORT, DIRECT_JOIN_URL)
        tab = get_zoom_tab(CHROME_PORT)
    
    if not tab:
        log("HATA: Zoom tab'ı bulunamadı!")
        log("Mevcut tablar:")
        for t in get_tabs(CHROME_PORT):
            log(f"  {t.get('title','?')[:50]} — {t.get('url','?')[:80]}")
        sys.exit(1)
    
    log(f"Tab: {tab.get('title', '?')[:60]}")
    ws = create_connection(tab['webSocketDebuggerUrl'], timeout=15)
    
    # 6. Landing page'te "Join from Browser" butonu var mı kontrol et
    check_page_js = '''
    (function() {
        var body = document.body ? document.body.innerText : "";
        return JSON.stringify({
            hasJoinFromBrowser: body.includes("Join from Browser") || body.includes("Tarayıcıdan Katıl"),
            hasJoinButton: body.toLowerCase().includes("join"),
            title: document.title,
            bodyPreview: body.substring(0, 200)
        });
    })()
    '''
    page_info = cdp_evaluate(ws, check_page_js)
    log(f"Sayfa: {page_info}")
    
    # Landing page -> "Join from Browser" tıkla
    click_browser_js = '''
    (function() {
        var body = document.body.innerText;
        if (body.includes("Join from Browser")) {
            var links = document.querySelectorAll("a");
            for (var i = 0; i < links.length; i++) {
                if (links[i].textContent.includes("Join from Browser")) {
                    links[i].click();
                    return "clicked join from browser";
                }
            }
        }
        if (body.includes("Tarayıcıdan Katıl")) {
            var links = document.querySelectorAll("a");
            for (var i = 0; i < links.length; i++) {
                if (links[i].textContent.includes("Tarayıcıdan")) {
                    links[i].click();
                    return "clicked tarayıcıdan katıl";
                }
            }
        }
        return "no browser join link";
    })()
    '''
    
    if page_info and ('"hasJoinFromBrowser":true' in str(page_info)):
        result = cdp_evaluate(ws, click_browser_js, user_gesture=True)
        log(f"Browser join: {result}")
        time.sleep(6)
    
    # Tab ID değişmiş olabilir
    tab = get_zoom_tab(CHROME_PORT)
    if tab:
        ws = create_connection(tab['webSocketDebuggerUrl'], timeout=15)
    
    # 7. İsim doldur (webinar'da sadece isim isteyebilir)
    fill_name_js = f'''
    (function() {{
        // Önce input-for-name dene
        var inp = document.getElementById("input-for-name");
        if (!inp) {{
            // Alternatif: ilk text input'u bul
            var inputs = document.querySelectorAll('input[type="text"]');
            inp = inputs[0];
        }}
        if (!inp) return "NO_INPUT";
        var ns = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
        ns.call(inp, "{NAME}");
        inp.dispatchEvent(new Event("input", {{bubbles: true}}));
        inp.dispatchEvent(new Event("change", {{bubbles: true}}));
        return "filled: " + inp.value;
    }})()
    '''
    result = cdp_evaluate(ws, fill_name_js)
    log(f"Name: {result}")
    
    # 8. Passcode varsa doldur (webinar'da olmayabilir)
    fill_pwd_js = '''
    (function() {
        var inp = document.getElementById("input-for-pwd");
        if (!inp) return "no pwd field (webinar)";
        var ns = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
        ns.call(inp, "");
        inp.dispatchEvent(new Event("input", {bubbles: true}));
        return "pwd exists but empty";
    })()
    '''
    result = cdp_evaluate(ws, fill_pwd_js)
    log(f"Passcode: {result}")
    
    # 9. Join butonu
    click_join_js = '''
    (function() {
        var btns = document.querySelectorAll("button");
        for (var i = 0; i < btns.length; i++) {
            var t = btns[i].textContent.toLowerCase();
            if (t.includes("join") || t.includes("katıl")) {
                btns[i].click();
                return "clicked: " + btns[i].textContent.trim();
            }
        }
        // Link tipi join?
        var links = document.querySelectorAll("a");
        for (var i = 0; i < links.length; i++) {
            var t = links[i].textContent.toLowerCase();
            if (t.includes("join") || t.includes("katıl")) {
                links[i].click();
                return "clicked link: " + links[i].textContent.trim();
            }
        }
        return "NO_JOIN_BTN";
    })()
    '''
    result = cdp_evaluate(ws, click_join_js, user_gesture=True)
    log(f"Join 1: {result}")
    
    time.sleep(8)
    
    # Tab yeniden bul
    tab = get_zoom_tab(CHROME_PORT)
    if tab:
        ws = create_connection(tab['webSocketDebuggerUrl'], timeout=15)
    
    # İkinci join (overlay)
    result = cdp_evaluate(ws, click_join_js, user_gesture=True)
    log(f"Join 2: {result}")
    
    time.sleep(4)
    
    # Durum kontrolü
    check_state_js = '''
    (function() {
        return JSON.stringify({
            title: document.title,
            hasUnmute: document.body ? document.body.innerText.includes("Unmute") : false,
            hasLeave: document.body ? document.body.innerText.includes("Leave") : false,
            bodyLen: document.body ? document.body.innerText.length : 0,
            url: window.location.href
        });
    })()
    '''
    state = cdp_evaluate(ws, check_state_js)
    log(f"State: {state}")
    
    ws.close()
    
    if state and '"hasLeave":true' in str(state):
        log("✅ WEBINAR'DA! Ses kaydı devam ediyor.")
    else:
        log("⚠️ Join durumu belirsiz — manuel kontrol et")
    
    log("=== Meeting 2 join tamam ===")

if __name__ == '__main__':
    main()
