# CDP Password Bridge

Python HTTP server that provides a web form for password entry and types the password into Chrome via Chrome DevTools Protocol (CDP). The password is never saved to disk, never logged, and only exists in RAM during processing.

**Use case:** When VNC stack (x11vnc, websockify, noVNC) is unavailable after container restart, but Chrome with CDP is running on the login page.

## When to Use

- Container restarted, VNC stack died (no Xvfb, no x11vnc, no websockify)
- Chrome is running headless on CDP port but Google's passkey page is blocking
- Non-headless Chrome on Xvfb is running with CDP (to avoid "Couldn't sign you in")
- User doesn't want to share password in chat (correct!)

## Architecture

```
User browser → HTTPS (Serveo tunnel) → Python HTTP server (port 7777)
  → POST /submit with password → CDP WebSocket → Chrome → Google login page
  → Input.insertText(password) + Runtime.evaluate(click Next)
```

## Prerequisites

- Python 3.10+ with `websockets` module
- Chrome running with `--remote-debugging-port=36241 --remote-allow-origins=*`
- For non-headless Chrome: Xvfb display (see headless-browser-auth SKILL.md)
- SSH tunnel service (Serveo or localhost.run)

## Full Code

Save the following as `cdp_vnc.py` and make it executable:

```python
#!/usr/bin/env python3
import json, threading, asyncio, re, urllib.request, websockets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

CDP_PORT = 36241  # Change to match your Chrome's port

def get_cdp_ws_url(port=CDP_PORT):
    try:
        resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5)
        tabs = json.loads(resp.read())
        if tabs:
            return tabs[0]['webSocketDebuggerUrl']
    except Exception as e:
        print(f"CDP error: {e}")
    return None

async def send_password(password):
    ws_url = get_cdp_ws_url()
    if not ws_url:
        return "❌ CDP bağlantısı kurulamadı"
    
    async with websockets.connect(ws_url, ping_interval=None) as ws:
        # Bring page to front
        await ws.send(json.dumps({"id": 1, "method": "Page.bringToFront"}))
        await ws.recv()
        await asyncio.sleep(1)
        
        # Type password using Input.insertText (works in controlled inputs)
        await ws.send(json.dumps({
            "id": 2, "method": "Input.insertText",
            "params": {"text": password}
        }))
        await ws.recv()
        
        # Find and click "Next" button
        await ws.send(json.dumps({
            "id": 3, "method": "Runtime.evaluate",
            "params": {
                "expression": """
                (() => {
                    const selectors = [
                        '#identifierNext', '#passwordNext',
                        'button[type="submit"]',
                        'div[role="button"]:has(span:contains("Next"))',
                        'div[role="button"]:has(span:contains("İleri"))'
                    ];
                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el) { el.click(); return 'clicked'; }
                    }
                    // Fallback: find by text
                    const all = document.querySelectorAll('button, div[role="button"], input[type="submit"]');
                    for (const el of all) {
                        const text = (el.textContent || el.value || '').toLowerCase();
                        if (text.includes('next') || text.includes('ileri') || text.includes('devam')) {
                            el.click(); return 'clicked: ' + text;
                        }
                    }
                    return 'no button found';
                })()
                """,
                "awaitPromise": True
            }
        }))
        result = await ws.recv()
        data = json.loads(result)
        click_result = data.get('result', {}).get('result', {}).get('value', 'unknown')
        return f"✅ Şifre gönderildi. Buton: {click_result}"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            html = '''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Google Giriş</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f2f5;display:flex;justify-content:center;align-items:center;min-height:100vh}
.card{background:white;border-radius:12px;padding:40px;box-shadow:0 2px 16px rgba(0,0,0,0.1);width:400px;max-width:90vw}
h1{font-size:22px;margin-bottom:8px;color:#202124}
p{color:#5f6368;font-size:14px;margin-bottom:24px}
.email-display{background:#f8f9fa;border:1px solid #dadce0;border-radius:8px;padding:12px 16px;margin-bottom:20px;font-size:14px;color:#202124}
label{display:block;font-size:14px;font-weight:500;margin-bottom:6px;color:#202124}
.pwd-wrap{position:relative}
input[type="password"],input[type="text"]{width:100%;padding:12px 16px;font-size:16px;border:1px solid #dadce0;border-radius:8px;outline:none;transition:border-color 0.2s}
input:focus{border-color:#1a73e8}
.btn-row{display:flex;gap:8px;margin-top:8px}
.btn-row button{flex:1;padding:10px;background:#f8f9fa;border:1px solid #dadce0;border-radius:8px;cursor:pointer;font-size:14px}
.btn-row button:hover{background:#e8eaed}
.submit{width:100%;padding:12px;margin-top:20px;background:#1a73e8;color:white;border:none;border-radius:8px;font-size:16px;font-weight:500;cursor:pointer;transition:background 0.2s}
.submit:hover{background:#1557b0;}.submit:disabled{background:#ccc;cursor:not-allowed}
.status{margin-top:16px;padding:12px;border-radius:8px;font-size:14px;display:none}
.success{background:#e6f4ea;color:#137333;display:block}
.error{background:#fce8e6;color:#c5221f;display:block}
.secure{display:inline-flex;align-items:center;gap:6px;background:#e8f0fe;color:#1967d2;padding:4px 12px;border-radius:16px;font-size:12px;margin-bottom:20px}
.note{font-size:12px;color:#5f6368;margin-top:16px;text-align:center}
</style></head><body>
<div class="card">
<div class="secure">🔒 Şifren sana özel — Vanitas göremez</div>
<h1>Google Hesabına Giriş</h1>
<p>Chrome'da açık olan Google hesabına şifreni gönder</p>
<div class="email-display">📧 isimgorulsunn@gmail.com</div>
<form id="frm">
<label for="pwd">Google şifren</label>
<div class="pwd-wrap">
<input type="password" id="pwd" placeholder="Şifreni yapıştır veya yaz" autocomplete="off" required>
</div>
<div class="btn-row">
<button type="button" id="pasteBtn">📋 Yapıştır</button>
<button type="button" id="toggleBtn">👁️ Göster</button>
<button type="button" id="clearBtn">🗑️ Temizle</button>
</div>
<button type="submit" class="submit" id="submitBtn">Şifreyi Gönder → Giriş Yap</button>
</form>
<div id="status" class="status"></div>
<div class="note">Şifren HTTPS üzerinden gelir, RAM'de işlenir, asla kaydedilmez</div>
</div>
<script>
const inp=document.getElementById('pwd'),st=document.getElementById('status');
document.getElementById('toggleBtn').onclick=()=>{
  const p=inp.type==='password';
  inp.type=p?'text':'password';
  document.getElementById('toggleBtn').textContent=p?'🙈 Gizle':'👁️ Göster';
};
document.getElementById('pasteBtn').onclick=async()=>{
  try{
    const t=await navigator.clipboard.readText();
    inp.value=t;document.getElementById('pasteBtn').textContent='✅ Yapıştırıldı!';
    setTimeout(()=>document.getElementById('pasteBtn').textContent='📋 Yapıştır',2000);
  }catch(e){
    document.getElementById('pasteBtn').textContent='❌ İzin gerekli';
    setTimeout(()=>document.getElementById('pasteBtn').textContent='📋 Yapıştır',2000);
    inp.focus();
  }
};
document.getElementById('clearBtn').onclick=()=>{inp.value='';inp.focus()};
document.getElementById('frm').onsubmit=async(e)=>{
  e.preventDefault();const pwd=inp.value;const btn=document.getElementById('submitBtn');
  if(!pwd)return;btn.disabled=true;btn.textContent='Gönderiliyor...';st.style.display='none';
  try{
    const r=await fetch('/submit',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'pwd='+encodeURIComponent(pwd)});
    const t=await r.text();st.textContent=t;st.className='status '+(r.ok?'success':'error');st.style.display='block';
    inp.value='';
  }catch(e){st.textContent='Hata: '+e.message;st.className='status error';st.style.display='block'}
  btn.disabled=false;btn.textContent='Şifreyi Gönder → Giriş Yap';
};
</script></body></html>'''
            self.wfile.write(html.encode('utf-8'))
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            ws_url = get_cdp_ws_url()
            self.wfile.write(f"CDP: {'connected' if ws_url else 'disconnected'}".encode())
        else:
            self.send_response(404); self.end_headers()
    
    def do_POST(self):
        if self.path == '/submit':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            params = parse_qs(body.decode('utf-8'))
            password = params.get('pwd', [''])[0]
            if not password:
                self.send_response(400); self.end_headers()
                self.wfile.write(b'Sifre bos')
                return
            result = asyncio.run(send_password(password))
            password = ""  # Zero out
            self.send_response(200); self.end_headers()
            self.wfile.write(result.encode('utf-8'))

if __name__ == '__main__':
    ws_url = get_cdp_ws_url()
    print(f"CDP: {ws_url}")
    print(f"Server: http://0.0.0.0:7777")
    HTTPServer(('0.0.0.0', 7777), Handler).serve_forever()
```

## Setup & Run

```bash
# 1. Start the server
python3 /tmp/cdp_vnc.py &
# or use terminal(background=true)

# 2. Expose via tunnel (Serveo)
# Use Python subprocess for reliable URL capture:
python3 -c "
import subprocess, time
proc = subprocess.Popen(['ssh', '-o', 'StrictHostKeyChecking=no', '-R', '80:localhost:7777', 'serveo.net'],
    stdout=open('/tmp/bridge_tunnel.txt','w'), stderr=subprocess.STDOUT)
time.sleep(8)
print(open('/tmp/bridge_tunnel.txt').read())
"
# → URL: https://XXXX-XXX-XXX-XXX.serveousercontent.com

# 3. Give URL to user
```

## Limitations

- **Password is in RAM** during the `send_password` function call. It is zeroed after (set to empty string). Python's GC will free it eventually.
- **Works on any Chrome page** — not just login. Can type into any input field.
- **No CORS needed** — the password POST goes from user's browser to Python server (not directly to CDP).
- **WebSocket connection is per-request** — opens, types, closes. No persistent connection.
- **Does not handle 2FA/passkey** — use only for the password field. If Google shows passkey, click "Try another way" first.

## Troubleshooting

- **"CDP bağlantısı kurulamadı":** Chrome not running or wrong port. Check `ps aux | grep remote-debugging-port`, update CDP_PORT.
- **Google "Couldn't sign you in":** Chrome is headless. Restart Chrome on Xvfb without `--headless` (see headless-browser-auth SKILL.md).
- **"Input.insertText" doesn't work:** Try `Input.dispatchKeyEvent` with raw character codes instead. Some pages intercept Input.insertText.
- **Tunnel URL empty:** Use Python subprocess instead of Hermes background processes for SSH tunnels. Hermes doesn't capture SSH stdout reliably.
