#!/usr/bin/env python3
"""CDP NotebookLM Sorgu — Final v5 (kanıtlanmış).
Kullanım: python3 cdp_notebooklm_query.py "soru" [notebook_id]
"""
import websocket, json, time, urllib.request, sys

NOTEBOOKS = {"bdt": "a4fe729d-c561-4238-9bea-81bea8e3dcbc"}

def ask(question, notebook_id="bdt"):
    nb_id = NOTEBOOKS.get(notebook_id, notebook_id)
    nb_url = f"https://notebooklm.google.com/notebook/{nb_id}?authuser=1"

    req = urllib.request.Request('http://127.0.0.1:18800/json/new', method='PUT')
    page = json.loads(urllib.request.urlopen(req).read())
    ws = websocket.create_connection(page['webSocketDebuggerUrl'], timeout=30)

    for m in ['Page.enable', 'Runtime.enable']:
        ws.send(json.dumps({'id': 0, 'method': m}))
    time.sleep(0.3)
    ws.settimeout(0.3)
    try:
        while True: ws.recv()
    except: pass

    ws.send(json.dumps({'id': 1, 'method': 'Page.navigate', 'params': {'url': nb_url}}))

    # loadEventFired bekle
    ws.settimeout(60)
    while True:
        try:
            d = json.loads(ws.recv())
            if d.get('method') == 'Page.loadEventFired':
                time.sleep(5)
                break
        except:
            ws.close()
            return None

    # Önceki mesaj sayısını al
    prior = eval_js(ws, 'document.querySelectorAll(".message-content").length')
    if prior is None:
        prior = 0

    # Soruyu gönder
    ws.send(json.dumps({'id': 10, 'method': 'Runtime.evaluate', 'params': {
        'expression': f"""
        (function(){{
            var ta = document.querySelector('textarea');
            if(!ta) return 'TAYOK';
            ta.focus();
        }})()
        """,
        'returnByValue': True}}))
    time.sleep(0.3)

    for ch in question:
        ws.send(json.dumps({'id': 99, 'method': 'Input.dispatchKeyEvent', 'params': {
            'type': 'keyDown' if ch != ' ' else 'rawKeyDown',
            'key': ch, 'text': ch,
            'windowsVirtualKeyCode': ord(ch.upper()) if ch.isalpha() else 32}}))
        time.sleep(0.03)

    # Enter
    for evt in ['rawKeyDown', 'char', 'keyUp']:
        ws.send(json.dumps({'id': 99, 'method': 'Input.dispatchKeyEvent', 'params': {
            'type': evt, 'key': 'Enter', 'code': 'Enter',
            'windowsVirtualKeyCode': 13, 'text': '\r'}}))
        time.sleep(0.1)

    time.sleep(1)
    ws.settimeout(0.5)
    try:
        while True: ws.recv()
    except: pass

    # Cevap bekle
    for i in range(40):
        time.sleep(4)
        current = eval_js(ws, """
        (function(){
            var msgs = document.querySelectorAll('.message-content');
            return JSON.stringify({
                count: msgs.length,
                last: msgs.length > 0 ? msgs[msgs.length-1].innerText?.substring(0,2000)||'' : ''
            });
        })()
        """)
        if current:
            info = json.loads(current)
            if info.get('count', 0) > prior:
                ws.close()
                return info.get('last', '')

    ws.close()
    return None

def eval_js(ws, expr, timeout=5):
    mid = int(time.time() * 1000000)
    ws.send(json.dumps({'id': mid, 'method': 'Runtime.evaluate',
                         'params': {'expression': expr, 'returnByValue': True}}))
    ws.settimeout(timeout)
    while True:
        try:
            d = json.loads(ws.recv())
            if d.get('id') == mid:
                return d.get('result', {}).get('result', {}).get('value', '')
        except:
            break
    return None

if __name__ == '__main__':
    q = sys.argv[1] if len(sys.argv) > 1 else "Merhaba"
    nb = sys.argv[2] if len(sys.argv) > 2 else "bdt"
    result = ask(q, nb)
    if result:
        print(result[:2000])
    else:
        print("❌ Cevap alınamadı")
