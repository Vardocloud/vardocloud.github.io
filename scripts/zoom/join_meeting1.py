#!/usr/bin/env python3
"""
Zoom CDP WebSocket join — Meeting 1
Cron ile 19:25'te tetiklenir. Chrome 9333'te çalışıyor olmalı.
"""
import json, urllib.request, urllib.parse, time, sys, os
from websocket import create_connection

MEETING_ID = "81345287700"
PASSCODE = "600297"
NAME = "Berkcan Ulucan"
CHROME_PORT = 9333
JOIN_URL = f"https://app.zoom.us/wc/join/{MEETING_ID}"

def get_tabs(port):
    return json.loads(urllib.request.urlopen(f'http://localhost:{port}/json').read())

def get_zoom_tab(port):
    tabs = get_tabs(port)
    for t in tabs:
        url = t.get('url', '')
        if 'app.zoom.us' in url:
            return t
    for t in tabs:
        if 'zoom.us' in t.get('url', ''):
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
    if 'value' in result:
        return result['value']
    return result

def navigate_via_cdp(port, url):
    """CDP ile yeni tab aç veya mevcut tab'ı navigate et"""
    tabs = get_tabs(port)
    # Boş tab bul
    for t in tabs:
        if t.get('url', '') in ('about:blank', '', 'chrome://newtab/'):
            ws = create_connection(t['webSocketDebuggerUrl'], timeout=10)
            cdp_evaluate(ws, f'window.location.href = "{url}"', user_gesture=True)
            ws.close()
            time.sleep(3)
            return True
    # Yeni tab oluştur
    try:
        urllib.request.urlopen(
            f'http://localhost:{port}/json/new?{urllib.parse.quote(url)}'
        )
        time.sleep(5)
        return True
    except:
        return False

def main():
    log = lambda msg: print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    
    log("=== Zoom Join - Meeting 1 ===")
    log(f"URL: {JOIN_URL}")
    log(f"Name: {NAME}")
    
    # Chrome çalışıyor mu?
    try:
        ver = json.loads(urllib.request.urlopen(f'http://localhost:{CHROME_PORT}/json/version').read())
        log(f"Chrome: {ver.get('Browser', 'ok')}")
    except Exception as e:
        log(f"HATA: Chrome port {CHROME_PORT} yanıt vermiyor: {e}")
        sys.exit(1)
    
    # ffmpeg çalışıyor mu?
    ffmpeg_running = os.system('pgrep -f "ffmpeg.*zoom_rec.monitor" > /dev/null 2>&1') == 0
    log(f"ffmpeg kaydı: {'✅ çalışıyor' if ffmpeg_running else '⚠️ ÇALIŞMIYOR!'}")
    
    # Navigate to join page
    log("Join sayfasına gidiliyor...")
    navigate_via_cdp(CHROME_PORT, JOIN_URL)
    time.sleep(6)  # SPA yüklenmesini bekle
    
    # Tab'ı bul
    tab = get_zoom_tab(CHROME_PORT)
    if not tab:
        log("HATA: Zoom tab'ı bulunamadı")
        sys.exit(1)
    
    log(f"Tab bulundu: {tab.get('title', '?')}")
    ws = create_connection(tab['webSocketDebuggerUrl'], timeout=15)
    
    # Form: İsim doldur
    fill_name_js = f'''
    (function() {{
        var inp = document.getElementById("input-for-name");
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
    
    # Form: Şifre doldur
    fill_pwd_js = f'''
    (function() {{
        var inp = document.getElementById("input-for-pwd");
        if (!inp) return "NO_INPUT";
        var ns = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
        ns.call(inp, "{PASSCODE}");
        inp.dispatchEvent(new Event("input", {{bubbles: true}}));
        inp.dispatchEvent(new Event("change", {{bubbles: true}}));
        return "pwd filled";
    }})()
    '''
    result = cdp_evaluate(ws, fill_pwd_js)
    log(f"Passcode: {result}")
    
    # İlk Join tıklaması
    click_join_js = '''
    (function() {
        var btns = document.querySelectorAll("button");
        for (var i = 0; i < btns.length; i++) {
            var t = btns[i].textContent.toLowerCase();
            if (t.includes("join")) {
                btns[i].click();
                return "clicked: " + btns[i].textContent.trim();
            }
        }
        return "NO_JOIN_BTN";
    })()
    '''
    result = cdp_evaluate(ws, click_join_js, user_gesture=True)
    log(f"Join 1: {result}")
    
    time.sleep(8)
    
    # Tab ID değişmiş olabilir
    tab = get_zoom_tab(CHROME_PORT)
    if tab:
        ws = create_connection(tab['webSocketDebuggerUrl'], timeout=15)
    
    # İkinci Join tıklaması (overlay için)
    result = cdp_evaluate(ws, click_join_js, user_gesture=True)
    log(f"Join 2: {result}")
    
    time.sleep(4)
    
    # Durum kontrolü
    check_state_js = '''
    (function() {
        return JSON.stringify({
            title: document.title,
            hasUnmute: document.body.innerText.includes("Unmute"),
            hasLeave: document.body.innerText.includes("Leave"),
            bodyLen: document.body.innerText.length,
            url: window.location.href
        });
    })()
    '''
    state = cdp_evaluate(ws, check_state_js)
    log(f"State: {state}")
    
    ws.close()
    
    # Başarı kontrolü
    if state and '"hasLeave":true' in str(state):
        log("✅ TOPLANTIDA! Ses kaydı devam ediyor.")
        # Kayıt dosyasını log'a yaz
        try:
            with open('/tmp/zoom_rec_file.txt') as f:
                log(f"Kayıt dosyası: {f.read().strip()}")
        except:
            pass
    else:
        log("⚠️ Join durumu belirsiz — manuel kontrol et")
    
    log("=== Join tamam ===")

if __name__ == '__main__':
    main()
