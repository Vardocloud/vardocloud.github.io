#!/usr/bin/env python3
"""MCP Chrome'unda otomatik login — CDP ile email+şifre gir.
MCP test çalıştırılır, Chrome açılır, bu script login yapar.
"""
import json, urllib.request, websocket, ssl, time, sys, os, subprocess

CONFIG = "/tmp/mcp_config.json"
NOTEBOOK_ID = "24d50377-8c14-4851-bcc2-b2d67b039041"
LOG_FILE = os.path.expanduser("~/.hermes/logs/mcp_auto_login.log")

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def find_chrome_port(target_port=None):
    """Chrome'un remote-debugging portunu bul."""
    if target_port:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{target_port}/json/version", timeout=2)
            return target_port
        except:
            pass
    
    # ps aux ile ara
    import subprocess
    result = subprocess.run(
        ["ps", "aux"], capture_output=True, text=True, timeout=5
    )
    for line in result.stdout.split("\n"):
        if "remote-debugging-port=" in line and "18800" not in line and "chromium" in line:
            for part in line.split():
                if "remote-debugging-port=" in part:
                    port = part.split("=")[1]
                    return int(port)
    return None

def get_password():
    resp = urllib.request.urlopen("http://127.0.0.1:8087/object/item/8a95abcd-65dd-4aa5-a255-b4660182d7cf", timeout=10)
    data = json.loads(resp.read())
    return data.get("data", {}).get("login", {}).get("password", "")

def login_in_chrome(port):
    """Chrome'da login yap."""
    resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=5)
    targets = json.loads(resp.read())
    
    # En uygun target'ı bul (signin/accountchooser)
    target = None
    for t in targets:
        url = t.get("url", "")
        if "signin" in url or "accountchooser" in url:
            target = t
            break
    if not target:
        for t in targets:
            if "google" in t.get("url", "") or "accounts" in t.get("url", ""):
                target = t
                break
    if not target:
        target = targets[0] if targets else None
    if not target:
        log("❌ Target bulunamadı")
        return False
    
    ws_url = target["webSocketDebuggerUrl"]
    log(f"🔗 Bağlanıldı: {target.get('url','?')[:60]}")
    ws = websocket.create_connection(ws_url, timeout=10, sslopt={"cert_reqs": ssl.CERT_NONE})
    
    # Sayfa durumu
    req = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": "document.querySelector('input[type=\"email\"]') ? 'email' : document.querySelector('[data-identifier]') ? 'chooser' : window.location.href.substring(0,60)"}}
    ws.send(json.dumps(req))
    time.sleep(2)
    page_state = "?"
    for _ in range(3):
        try:
            r = json.loads(ws.recv())
            if r.get("id") == 1:
                page_state = r.get("result",{}).get("result",{}).get("value","?")
                break
        except:
            break
    log(f"📋 Sayfa: {page_state[:60]}")
    
    # Accountchooser ise hesap seç
    if "chooser" in str(page_state):
        req = {"id": 2, "method": "Runtime.evaluate", "params": {"expression": """
            (() => {
                const btns = document.querySelectorAll('[data-identifier]');
                for (const btn of btns) {
                    if (btn.getAttribute('data-identifier') === 'isimgorulsunn@gmail.com') {
                        btn.click(); return 'clicked';
                    }
                }
                return 'not found';
            })()
        """}}
        ws.send(json.dumps(req))
        time.sleep(3)
        log("✅ Hesap seçildi")
    
    # Email sayfası ise email gir
    if "email" in str(page_state):
        req = {"id": 3, "method": "Runtime.evaluate", "params": {"expression": """
            (() => {
                const inp = document.querySelector('input[type="email"]');
                if (!inp) return 'no email field';
                const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                s.call(inp, 'isimgorulsunn@gmail.com');
                inp.dispatchEvent(new Event('input', {bubbles: true}));
                document.querySelector('#identifierNext')?.click();
                return 'email sent';
            })()
        """}}
        ws.send(json.dumps(req))
        time.sleep(3)
        log("✅ Email girildi")
    
    # Şifre sayfası için bekle
    time.sleep(3)
    password = get_password()
    if not password:
        log("❌ Şifre alınamadı")
        return False
    
    req = {"id": 4, "method": "Runtime.evaluate", "params": {"expression": f"""
        (() => {{
            const inp = document.querySelector('input[type="password"]');
            if (!inp) return JSON.stringify({{state: 'no pw field', url: window.location.href.substring(0,60)}});
            const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            s.call(inp, {json.dumps(password)});
            inp.dispatchEvent(new Event('input', {{bubbles: true}}));
            inp.dispatchEvent(new Event('change', {{bubbles: true}}));
            const nextBtn = document.querySelector('#passwordNext');
            if (nextBtn) {{ nextBtn.click(); return JSON.stringify({{state:'next clicked'}}); }}
            inp.dispatchEvent(new KeyboardEvent('keydown', {{key:'Enter', keyCode:13}}));
            return JSON.stringify({{state:'enter sent'}});
        }})()
    """}}
    ws.send(json.dumps(req))
    time.sleep(5)
    log("✅ Şifre girildi, Enter gönderildi")
    
    # Enter tekrar (bazen gerekli)
    time.sleep(3)
    req = {"id": 5, "method": "Input.dispatchKeyEvent", "params": {"type": "keyDown", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13}}
    ws.send(json.dumps(req))
    time.sleep(1)
    
    # Son kontrol
    ws.close()
    time.sleep(5)
    
    # URL kontrol
    try:
        resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=5)
        targets = json.loads(resp.read())
        for t in targets:
            url = t.get("url", "")
            if "notebooklm.google.com/notebook" in url:
                log(f"✅✅✅ NOTEBOKLM\'E GİRİŞ BAŞARILI! {url[:60]}")
                return True
    except:
        pass
    
    return True  # İşlem tamam, MCP test etsin

def main():
    # 1. MCP'yi başlat
    log("🚀 MCP test başlatılıyor...")
    proc = subprocess.Popen(
        ["notebooklm-mcp", "--config", CONFIG, "test", "-n", NOTEBOOK_ID],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    
    # 2. Chrome portunu bul (en fazla 30sn bekle)
    port = None
    for i in range(30):
        port = find_chrome_port()
        if port:
            log(f"🔍 Chrome port {port} bulundu ({(i+1)*1}s)")
            break
        time.sleep(1)
    
    if not port:
        log("❌ Chrome port bulunamadı")
        return 1
    
    # 3. Login yap
    time.sleep(3)
    login_in_chrome(port)
    
    # 4. MCP'nin bitmesini bekle
    proc.wait(timeout=30)
    log("✅ MCP test tamamlandı")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
