#!/usr/bin/env python3
"""
CDP WebSocket ile Zoom join — Puppeteer MCP CSP engeline takılmaz.
16 Haz 2026'da test edildi, başarıyla çalıştı.

Kullanım: Bu dosya doğrudan çalıştırılmaz. skill içindeki join flow'un
Python/websocket implementasyonudur. Chrome --remote-debugging-port=9333 
çalışır durumda olmalı.

Gereksinim: pip install websocket-client
"""

import json, urllib.request, time
from websocket import create_connection


def get_zoom_tab(port=9333):
    """Zoom sekmesini bul, WebSocket URL'ini dön"""
    tabs = json.loads(
        urllib.request.urlopen(f'http://localhost:{port}/json').read()
    )
    for t in tabs:
        url = t.get('url', '')
        if 'app.zoom.us' in url:
            return t
    # Fallback: landing page
    for t in tabs:
        url = t.get('url', '')
        if 'zoom.us' in url:
            return t
    return None


def cdp_evaluate(ws, expression, return_by_value=True, user_gesture=False):
    """Runtime.evaluate gönder, sonucu dön"""
    ws.send(json.dumps({
        'id': int(time.time() * 1000) % 100000,
        'method': 'Runtime.evaluate',
        'params': {
            'expression': expression,
            'returnByValue': return_by_value,
            'userGesture': user_gesture,
        }
    }))
    resp = json.loads(ws.recv())
    return resp.get('result', {}).get('result', {}).get('value')


# === KULLANIM ÖRNEĞİ ===

# 1. Tab'ı bul
tab = get_zoom_tab(9333)
ws = create_connection(tab['webSocketDebuggerUrl'], timeout=10)

# 2. Formu doldur (native setter + dispatchEvent — React için ZORUNLU)
FILL_NAME = '''
(function() {
    var inp = document.getElementById("input-for-name");
    if (!inp) return "no input-for-name";
    var ns = Object.getOwnPropertyDescriptor(
        HTMLInputElement.prototype, "value").set;
    ns.call(inp, "Sudenaz");
    inp.dispatchEvent(new Event("input", {bubbles: true}));
    inp.dispatchEvent(new Event("change", {bubbles: true}));
    return "filled: " + inp.value;
})()
'''

FILL_PWD = '''
(function() {
    var inp = document.getElementById("input-for-pwd");
    if (!inp) return "no input-for-pwd";
    var ns = Object.getOwnPropertyDescriptor(
        HTMLInputElement.prototype, "value").set;
    ns.call(inp, "PASSWORD_HERE");
    inp.dispatchEvent(new Event("input", {bubbles: true}));
    inp.dispatchEvent(new Event("change", {bubbles: true}));
    return "pwd filled";
})()
'''

# 3. Join butonuna tıkla (userGesture=True — autoplay için ŞART)
CLICK_JOIN = '''
(function() {
    var btns = document.querySelectorAll("button");
    for (var i = 0; i < btns.length; i++) {
        var t = btns[i].textContent.toLowerCase();
        if (t.includes("join")) {
            btns[i].click();
            return "clicked: " + btns[i].textContent.trim();
        }
    }
    return "no join button";
})()
'''

# 4. Toplantı durumunu kontrol et
CHECK_STATE = '''
(function() {
    return JSON.stringify({
        title: document.title,
        hasUnmute: document.body.innerText.includes("Unmute"),
        hasLeave: document.body.innerText.includes("Leave"),
        btnCount: document.querySelectorAll("button").length,
        bodyLen: document.body.innerText.length,
    });
})()
'''

# Join flow
result = cdp_evaluate(ws, FILL_NAME)
print(f"Name: {result}")

result = cdp_evaluate(ws, FILL_PWD)
print(f"Pwd: {result}")

result = cdp_evaluate(ws, CLICK_JOIN, user_gesture=True)
print(f"Join1: {result}")

time.sleep(8)  # SPA geçişini bekle

# Tab ID değişmiş olabilir — yeniden bul
tab = get_zoom_tab(9333)
if tab:
    ws = create_connection(tab['webSocketDebuggerUrl'], timeout=10)

result = cdp_evaluate(ws, CLICK_JOIN, user_gesture=True)
print(f"Join2: {result}")

time.sleep(3)

state = cdp_evaluate(ws, CHECK_STATE)
print(f"State: {state}")

ws.close()
