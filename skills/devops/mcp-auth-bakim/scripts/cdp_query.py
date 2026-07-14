#!/usr/bin/env python3
"""CDP NotebookLM Sorgu v4 — keepalive Chrome üzerinden doğrudan soru-cevap.

Kullanım: python3 cdp_query.py "Soru" [notebook_kısa_adı]
         python3 cdp_query.py "BDT nedir?" bdt
"""
import websocket, json, time, urllib.request, sys

NOTEBOOKS = {
    "bdt": ("a4fe729d-c561-4238-9bea-81bea8e3dcbc", 1),
    "apa": ("c44469fe-a69a-4a86-8dd8-756c2f365109", 0),
}
CDP_PORT = 18800

def ask(question, notebook="bdt"):
    nb_id, authuser = NOTEBOOKS.get(notebook, (notebook, 1))
    nb_url = f"https://notebooklm.google.com/notebook/{nb_id}?authuser={authuser}"

    req = urllib.request.Request(f'http://127.0.0.1:{CDP_PORT}/json/new', method='PUT')
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
                break
        except:
            break

    time.sleep(5)

    # Önceki cevapları kaydet
    prior = eval_js(ws, """
        (function(){
            var msgs = document.querySelectorAll('[class*=message]');
            var r = [];
            msgs.forEach(function(m){ var t = m.innerText?.substring(0,200)||''; if(t) r.push(t); });
            return JSON.stringify(r);
        })()
    """)
    try:
        prior = json.loads(prior) if prior else []
    except:
        prior = []

    # Soruyu yaz
    q = json.dumps(question)
    ta = eval_js(ws, f"""
        (function(){{
            var ta = document.querySelector('textarea');
            if(!ta) return 'TAYOK';
            ta.focus(); ta.value = {q};
            ta.dispatchEvent(new Event('input', {{bubbles:true}}));
            return 'OK';
        }})()
    """)

    if ta != 'OK':
        ws.close()
        body = eval_js(ws, 'document.body?.innerText?.substring(0,300)||""')
        if 'Erişim izni' in body:
            return {'error': 'Erişim izni yok — notebook başka hesaba ait'}
        return {'error': f'textarea bulunamadı: {ta}', 'body': body[:200]}

    time.sleep(1)

    # Enter
    for evt in ['keyDown', 'char', 'keyUp']:
        ws.send(json.dumps({'id': 99, 'method': 'Input.dispatchKeyEvent', 'params': {
            'type': evt, 'key': 'Enter', 'code': 'Enter', 'windowsVirtualKeyCode': 13,
            'text': '\r' if evt == 'char' else None
        }}))
        time.sleep(0.2)

    time.sleep(1)
    ws.settimeout(0.5)
    try:
        while True: ws.recv()
    except: pass

    # Cevap bekle
    stop_words = ['yükleniyor', 'thinking', 'creating', 'generating', 'bekleniyor']
    for i in range(35):
        time.sleep(4)
        current = eval_js(ws, """
        (function(){
            var msgs = document.querySelectorAll('[class*=message]');
            if(msgs.length === 0) return '[]';
            var r = [];
            msgs.forEach(function(m){ var t = m.innerText?.substring(0,400)||''; if(t) r.push(t); });
            return JSON.stringify(r);
        })()
        """)
        try:
            current = json.loads(current) if current else []
        except:
            current = []

        for msg in current:
            if msg not in prior and len(msg) > 20:
                clean = msg.strip().lower()
                if not any(w in clean for w in stop_words):
                    ws.close()
                    return {'response': msg}

    ws.close()
    return {'error': 'timeout — NotebookLM cevap vermedi'}

def eval_js(ws, expr, timeout=8):
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
    return ''

if __name__ == '__main__':
    q = sys.argv[1] if len(sys.argv) > 1 else "BDT nedir?"
    nb = sys.argv[2] if len(sys.argv) > 2 else "bdt"
    result = ask(q, nb)
    if 'response' in result:
        print(result['response'])
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
