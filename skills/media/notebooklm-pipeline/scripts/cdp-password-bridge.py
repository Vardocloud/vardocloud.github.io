#!/usr/bin/env python3
"""
CDP Password Bridge — Web form → CDP → Chrome.
Password never touches disk, is never logged, exists only in RAM.

Usage:
  python3 cdp-password-bridge.py [--port 7777] [--cdp-port 37000]

The user opens http://localhost:PORT (or via tunnel), pastes their Google
password, clicks Submit. The bridge types it into Chrome via CDP and
clicks "Next".

Security:
  - Password is received in an HTTP POST handler, immediately forwarded
    to Chrome via CDP WebSocket, then discarded.
  - No logging of the password value.
  - HTTPS tunnel (Serveo/localhost.run) encrypts the web form traffic.
"""

import json, http.server, urllib.request, asyncio, websockets

CDP_PORT = 37000
BRIDGE_PORT = 7777


def get_cdp_ws():
    """Get the first usable CDP WebSocket URL from Chrome."""
    resp = urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json", timeout=5)
    tabs = json.loads(resp.read())
    for t in tabs:
        if "devtools" in t.get("webSocketDebuggerUrl", "") and "newtab" not in t.get("url", "").lower():
            return t["webSocketDebuggerUrl"]
    return tabs[0]["webSocketDebuggerUrl"]


HTML_PAGE = """<!DOCTYPE html>
<html lang="tr">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Google Giriş</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;align-items:center;justify-content:center}
.card{background:#fff;border-radius:20px;padding:40px;width:420px;max-width:90vw;box-shadow:0 20px 60px rgba(0,0,0,.15)}
.logo{text-align:center;margin-bottom:24px;font-size:28px}
h1{font-size:20px;text-align:center;color:#1a1a2e;margin-bottom:8px}
.email{text-align:center;color:#666;font-size:14px;margin-bottom:28px;padding:8px 16px;background:#f5f5f5;border-radius:8px}
label{display:block;font-size:14px;font-weight:500;color:#333;margin-bottom:6px}
.pwd-wrapper input{flex:1;padding:14px 16px;border:2px solid #e0e0e0;border-radius:10px;font-size:16px;outline:none}
.pwd-wrapper input:focus{border-color:#667eea}
.btn-group{display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap}
.btn{flex:1;padding:10px 16px;border:none;border-radius:8px;font-size:13px;font-weight:500;cursor:pointer;min-width:80px}
.btn-paste{background:#e8f0fe;color:#1a73e8}
.btn-toggle{background:#f5f5f5;color:#333}
.btn-clear{background:#fce8e6;color:#d93025}
.submit{width:100%;padding:14px;background:#1a73e8;color:#fff;border:none;border-radius:10px;font-size:16px;font-weight:500;cursor:pointer}
.submit:hover{background:#1557b0}.submit:disabled{background:#ccc;cursor:not-allowed}
#status{margin-top:16px;padding:12px;border-radius:8px;font-size:13px;display:none;text-align:center}
#status.success{background:#e6f4ea;color:#137333;display:block}
#status.error{background:#fce8e6;color:#c5221f;display:block}
#status.info{background:#e8f0fe;color:#1a73e8;display:block}
.footer{text-align:center;margin-top:20px;font-size:11px;color:#999}
.spinner{display:inline-block;width:16px;height:16px;border:2px solid #ccc;border-top-color:#1a73e8;border-radius:50%;animation:spin .6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
</style></head>
<body>
<div class="card">
<div class="logo">🔑</div>
<h1>Google Giriş</h1>
<div class="email">📧 isimgorulsunn@gmail.com</div>
<form id="pwdForm">
<label for="password">Google şifren</label>
<input type="password" id="password" placeholder="Şifreni yapıştır veya yaz" autocomplete="off" spellcheck="false" style="width:100%;padding:14px 16px;border:2px solid #e0e0e0;border-radius:10px;font-size:16px;box-sizing:border-box">
<div class="btn-group">
<button type="button" class="btn btn-paste" id="pasteBtn">📋 Panodan Yapıştır</button>
<button type="button" class="btn btn-toggle" id="toggleBtn">👁️ Göster/Gizle</button>
<button type="button" class="btn btn-clear" id="clearBtn">🗑️ Temizle</button>
</div>
<button type="submit" class="submit" id="submitBtn">Şifreyi Gönder → Giriş Yap</button>
</form>
<div id="status"></div>
<div class="footer">🔒 Şifren HTTPS ile şifrelenir, kaydedilmez, ben görmem</div>
</div>
<script>
const pwd=document.getElementById('password'),st=document.getElementById('status'),sb=document.getElementById('submitBtn');
document.getElementById('pasteBtn').onclick=async()=>{try{const t=await navigator.clipboard.readText();pwd.value=t;show('📋 Yapıştırıldı ('+t.length+' karakter)','info')}catch(e){show('⚠️ Pano okunamadı, Ctrl+V dene','error')}};
document.getElementById('toggleBtn').onclick=()=>{pwd.type=pwd.type==='password'?'text':'password';document.getElementById('toggleBtn').textContent=pwd.type==='password'?'👁️ Göster':'🙈 Gizle'};
document.getElementById('clearBtn').onclick=()=>{pwd.value='';show('🗑️ Temizlendi','info')};
document.getElementById('pwdForm').onsubmit=async(e)=>{e.preventDefault();const v=pwd.value.trim();if(!v){show('⚠️ Şifre boş','error');return}
sb.disabled=true;sb.innerHTML='<span class="spinner"></span> Gönderiliyor...';show('⏳ Gönderiliyor...','info')
try{const r=await fetch('/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:v})});const d=await r.json()
if(d.ok){show('✅ Şifre gönderildi!','success');sb.textContent='✅ Gönderildi';pwd.value=''}else{show('❌ Hata: '+d.error,'error');sb.disabled=false;sb.innerHTML='Şifreyi Gönder → Giriş Yap'}}
catch(e){show('❌ Bağlantı hatası','error');sb.disabled=false;sb.innerHTML='Şifreyi Gönder → Giriş Yap'}};
function show(m,t){st.className=t;st.textContent=m;st.style.display='block'}
</script></body></html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/status":
            self._json({"ok": True, "status": "connected", "cdp": CDP_PORT})
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path != "/submit":
            self.send_response(404)
            self.end_headers()
            return
        content_len = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(content_len))
        pwd = data.get("password", "")
        if not pwd:
            self._json({"ok": False, "error": "Sifre bos"})
            return
        try:
            async def send(clear):
                ws_url = get_cdp_ws()
                async with websockets.connect(ws_url, ping_interval=None, max_size=2**25) as ws:
                    # Insert text in one shot (much faster than per-character dispatch)
                    await ws.send(json.dumps({"id": 1, "method": "Input.insertText",
                                              "params": {"text": clear}}))
                    await ws.recv()
                    await asyncio.sleep(0.5)
                    # Click Next
                    await ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate",
                        "params": {"expression": """
                            for (const b of document.querySelectorAll('button, div[role="button"]')) {
                                const t = (b.textContent||'').toLowerCase().trim();
                                if (t === 'next' || t.includes('next')) { b.click(); break; }
                            }
                        """}}))
                    await ws.recv()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(send(pwd))
            loop.close()
            self._json({"ok": True})
        except Exception as ex:
            self._json({"ok": False, "error": str(ex)})

    def _json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, *a):
        pass  # suppress logs


if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", BRIDGE_PORT), Handler)
    print(f"CDP Password Bridge running on :{BRIDGE_PORT} (CDP :{CDP_PORT})")
    server.serve_forever()
