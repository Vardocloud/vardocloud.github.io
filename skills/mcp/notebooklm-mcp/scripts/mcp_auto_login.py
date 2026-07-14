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

def find_chrome_port():
    """MCP Chrome'un remote-debugging portunu ps aux ile bul."""
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
    resp = urllib.request.urlopen(
        "http://127.0.0.1:8087/object/item/8a95abcd-65dd-4aa5-a255-b4660182d7cf",
        timeout=10
    )
    data = json.loads(resp.read())
    return data.get("data", {}).get("login", {}).get("password", "")

def login_in_chrome(port):
    """Keepalive'daki güncel cookie'leri MCP Chrome'a yükle + login flow."""
    # Önce keepalive'dan cookie'leri al
    resp = urllib.request.urlopen(f"http://127.0.0.1:18800/json/list", timeout=5)
    ka_targets = json.loads(resp.read())
    ka_target = None
    for t in ka_targets:
        if "notebooklm" in t.get("url","") and "signin" not in t.get("url",""):
            ka_target = t
            break
    if not ka_target:
        ka_target = ka_targets[0] if ka_targets else None
    if not ka_target:
        log("❌ keepalive target bulunamadı")
        return False

    ws_ka = websocket.create_connection(
        ka_target["webSocketDebuggerUrl"], timeout=10,
        sslopt={"cert_reqs": ssl.CERT_NONE}
    )
    req = {"id": 1, "method": "Network.getAllCookies", "params": {}}
    ws_ka.send(json.dumps(req))
    time.sleep(2)
    cookies = []
    for _ in range(5):
        try:
            r = json.loads(ws_ka.recv())
            if r.get("id") == 1:
                cookies = r.get("result", {}).get("cookies", [])
                break
        except:
            break
    ws_ka.close()
    log(f"🍪 {len(cookies)} cookie alındı")

    # MCP Chrome'a bağlan
    resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=5)
    targets = json.loads(resp.read())
    target = None
    for t in targets:
        url = t.get("url", "")
        if "signin" in url or "accountchooser" in url:
            target = t
            break
    if not target:
        target = targets[0] if targets else None
    if not target:
        log("❌ MCP target bulunamadı")
        return False

    ws = websocket.create_connection(
        target["webSocketDebuggerUrl"], timeout=10,
        sslopt={"cert_reqs": ssl.CERT_NONE}
    )

    # Cookie'leri yükle
    seen = set()
    unique = []
    for c in cookies:
        key = (c.get("domain", ""), c.get("name", ""))
        if key not in seen:
            seen.add(key)
            unique.append(c)
    req = {"id": 2, "method": "Network.setCookies", "params": {"cookies": unique}}
    ws.send(json.dumps(req))
    time.sleep(1)
    log(f"✅ {len(unique)} cookie yüklendi")

    # AccountChooser mı kontrol et
    req = {"id": 3, "method": "Runtime.evaluate", "params": {"expression": """
        JSON.stringify({
            chooser: !!document.querySelector('[data-identifier]'),
            url: window.location.href.substring(0,80)
        })
    """}}
    ws.send(json.dumps(req))
    time.sleep(2)
    page_info = "?"
    for _ in range(3):
        try:
            r = json.loads(ws.recv())
            if r.get("id") == 3:
                page_info = r.get("result",{}).get("result",{}).get("value","?")
                break
        except:
            break

    if "chooser" in str(page_info):
        # AccountChooser'da hesap seç
        req = {"id": 4, "method": "Runtime.evaluate", "params": {"expression": """
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
        time.sleep(4)
        log("✅ Hesap seçildi")

    # Şifre sayfası
    password = get_password()
    if not password:
        log("❌ Şifre alınamadı")
        ws.close()
        return False

    req = {"id": 5, "method": "Runtime.evaluate", "params": {"expression": f"""
        (() => {{
            const inp = document.querySelector('input[type="password"]');
            if (!inp) return JSON.stringify({{state:'no pw', url: window.location.href.substring(0,60)}});
            const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            s.call(inp, {json.dumps(password)});
            inp.dispatchEvent(new Event('input', {{bubbles: true}}));
            inp.dispatchEvent(new Event('change', {{bubbles: true}}));
            return JSON.stringify({{state:'filled'}});
        }})()
    """}}
    ws.send(json.dumps(req))
    time.sleep(2)
    log("✅ Şifre girildi")

    # Enter tuşu
    for ev_type in ["keyDown", "keyUp"]:
        req = {"id": 6, "method": "Input.dispatchKeyEvent", "params": {
            "type": ev_type, "key": "Enter", "code": "Enter",
            "windowsVirtualKeyCode": 13
        }}
        ws.send(json.dumps(req))
        time.sleep(0.5)
    log("✅ Enter gönderildi")

    time.sleep(5)
    ws.close()
    log("✅ Login işlemi tamamlandı")
    return True

def main():
    log("=" * 40)
    log("🚀 MCP auto-login başlatılıyor...")

    # MCP'yi başlat
    proc = subprocess.Popen(
        ["notebooklm-mcp", "--config", CONFIG, "test", "-n", NOTEBOOK_ID],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    # Chrome portunu bul (30sn timeout)
    port = None
    for i in range(30):
        port = find_chrome_port()
        if port:
            log(f"🔍 Chrome port {port} ({(i+1)}s)")
            break
        time.sleep(1)

    if not port:
        log("❌ Chrome port bulunamadı")
        return 1

    time.sleep(3)
    login_in_chrome(port)

    proc.wait(timeout=30)
    log("✅ MCP test tamamlandı")
    return 0

if __name__ == "__main__":
    sys.exit(main())
