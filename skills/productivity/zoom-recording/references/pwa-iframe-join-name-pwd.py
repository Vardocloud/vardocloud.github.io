#!/usr/bin/env python3
"""
PWA Iframe Join Pattern — İsim + Passcode (Kanıtlanmış, 15 Tem 2026)

Bu script bir Zoom toplantısına PWA iframe üzerinden join yapar:
  1. Landing page (zoom.us/j/ID?pwd=...) yeni tab'da açılır
  2. "Join from browser" butonu tıklanır (SPA navigasyon)
  3. Tab yeniden bulunur (SPA navigation tab ID DEĞİŞTİREBİLİR)
  4. #webclient iframe'i içinde input-for-name + input-for-pwd doldurulur
  5. Join butonu tıklanır
  6. Bekleme odası/waiting room doğrulanır

Kullanım:
  python3 pwa-iframe-join-name-pwd.py
  
Değişkenler:
  PORT, MEETING_ID, PASSCODE, DISPLAY_NAME, ZOOM_URL
"""

import json, time, urllib.request
from websocket import create_connection

PORT = 9333
MEETING_ID = "81347534550"
PASSCODE = "1234"
DISPLAY_NAME = "Sudenaz"
ZOOM_URL = f"https://us06web.zoom.us/j/{MEETING_ID}?pwd=tICpWSrdE7ZljJbkUovrJoLDwHwl6A.1"

def cdp_send(ws, method, params=None, timeout=15):
    if params is None: params = {}
    msg_id = int(time.time() * 1000) % 100000
    cmd = json.dumps({"id": msg_id, "method": method, "params": params})
    ws.send(cmd)
    deadline = time.time() + timeout
    while time.time() < deadline:
        ws.settimeout(2)
        try:
            resp = json.loads(ws.recv())
            if resp.get("id") == msg_id:
                if "error" in resp:
                    print(f"  CDP Error: {resp['error']}")
                    return None
                return resp.get("result")
        except:
            continue
    print(f"  Timeout waiting for {method}")
    return None

def find_zoom_tab():
    """Find the Zoom tab from all open tabs (SPA may have changed it)"""
    req = urllib.request.urlopen(f"http://localhost:{PORT}/json", timeout=10)
    all_tabs = json.loads(req.read().decode())
    for t in all_tabs:
        url = t.get("url","")
        title = t.get("title","")
        if "app.zoom.us/wc/" in url and "zoom" in title.lower():
            return t
    for t in all_tabs:
        url = t.get("url","")
        title = t.get("title","")
        if "zoom" in url.lower() or "zoom" in title.lower() or "join" in title.lower():
            return t
    return all_tabs[-1] if all_tabs else None

# Step 1: Open landing page (PUT method — Chrome /json/new requires PUT)
print("1. Opening Zoom page...")
req = urllib.request.Request(f"http://localhost:{PORT}/json/new?{ZOOM_URL}", method="PUT")
resp = urllib.request.urlopen(req, timeout=10)
new_tab = json.loads(resp.read().decode())
print(f"   Tab: {new_tab.get('id','?')[:20]}")
time.sleep(6)

# Step 2: Click "Join from browser"
tab = find_zoom_tab()
print(f"2. Tab: {tab.get('title','?')[:50]}")
ws = create_connection(tab["webSocketDebuggerUrl"], timeout=20)

r = cdp_send(ws, "Runtime.evaluate", {
    "expression": """
    (function(){
        var btns = document.querySelectorAll('button');
        for(var i=0;i<btns.length;i++){
            if(btns[i].textContent.toLowerCase().includes('join from browser')){
                btns[i].click(); return 'clicked btn ' + i;
            }
        }
        var links = document.querySelectorAll('a');
        for(var i=0;i<links.length;i++){
            if(links[i].textContent.toLowerCase().includes('join from browser')){
                links[i].click(); return 'clicked link ' + i;
            }
        }
        return 'not found';
    })()
    """,
    "returnByValue": True, "userGesture": True
})
print(f"3. Join from browser: {r.get('result',{}).get('value','') if r else 'no resp'}")
ws.close()

# Step 3: Wait for SPA navigation, then RE-FIND tab
time.sleep(8)
tab = find_zoom_tab()
print(f"4. After-nav tab: {tab.get('title','?')[:50]} | {tab.get('url','?')[:70]}")
ws = create_connection(tab["webSocketDebuggerUrl"], timeout=20)

# Step 4: Fill form inside PWA iframe
print("5. Filling iframe form...")
r = cdp_send(ws, "Runtime.evaluate", {
    "expression": f"""
    (function(){{
        var iframe = document.getElementById('webclient');
        if(!iframe) return JSON.stringify({{error:'no iframe'}});
        try {{
            var idoc = iframe.contentDocument || iframe.contentWindow.document;
            var info = [];
            
            // Fill name
            var ni = idoc.getElementById('input-for-name');
            if(ni) {{
                var ns = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
                ns.call(ni, '{DISPLAY_NAME}');
                ni.dispatchEvent(new Event('input', {{bubbles:true}}));
                ni.dispatchEvent(new Event('change', {{bubbles:true}}));
                info.push('name=ok');
            }}
            
            // Fill passcode
            var pi = idoc.getElementById('input-for-pwd');
            if(pi) {{
                var ns = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
                ns.call(pi, '{PASSCODE}');
                pi.dispatchEvent(new Event('input', {{bubbles:true}}));
                pi.dispatchEvent(new Event('change', {{bubbles:true}}));
                info.push('pwd=ok');
            }}
            
            // Click Join in iframe
            var btns = idoc.querySelectorAll('button');
            for(var i=0;i<btns.length;i++){{
                if(btns[i].textContent.trim().toLowerCase() === 'join') {{
                    btns[i].click();
                    info.push('join=clicked');
                    break;
                }}
            }}
            
            return JSON.stringify({{status: 'ok', info: info}});
        }} catch(e) {{
            return JSON.stringify({{error: e.message}});
        }}
    }})()
    """,
    "returnByValue": True, "userGesture": True
})
if r:
    print(f"   Result: {r.get('result',{}).get('value','')}")

time.sleep(6)

# Step 5: Verify meeting state
print("6. Verifying meeting state...")
r = cdp_send(ws, "Runtime.evaluate", {
    "expression": """
    (function(){
        var iframe = document.getElementById('webclient');
        if(!iframe) return 'no iframe';
        try {
            var idoc = iframe.contentDocument || iframe.contentWindow.document;
            var body = idoc.body.innerText;
            return JSON.stringify({
                title: idoc.title,
                hasWaiting: body.includes('Waiting for the host'),
                hasUnmuted: body.includes('You are unmuted'),
                hasHostSignIn: body.includes('Host Sign in'),
                bodyStart: body.substring(0,200)
            });
        } catch(e) { return 'error: ' + e.message; }
    })()
    """,
    "returnByValue": True
})
if r:
    val = r.get("result",{}).get("value","")
    print(f"   Meeting state: {val}")

ws.close()
print("\n=== Done ===")
