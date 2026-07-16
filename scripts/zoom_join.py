#!/usr/bin/env python3
"""
zoom_join.py — Parametrik Zoom join script'i
Kullanım: python3 zoom_join.py --meeting 81347534550 --pwd 1234 --name Sudenaz

Chrome 9333 çalışır durumda olmalı. PulseAudio + ffmpeg ayrıca başlatılır.
"""
import json, urllib.request, time, argparse, sys
from websocket import create_connection
from pathlib import Path

def find_zoom_tab(port=9333):
    tabs = json.loads(urllib.request.urlopen(f'http://localhost:{port}/json').read())
    for t in tabs:
        url = t.get('url', '')
        if 'app.zoom.us/wc/' in url or '/j/' in url:
            return t
    for t in tabs:
        if 'zoom.us' in t.get('url', ''):
            return t
    return None

def cdp_eval(ws, expression, user_gesture=False, timeout=15):
    msg_id = int(time.time() * 1000) % 100000
    ws.send(json.dumps({
        'id': msg_id, 'method': 'Runtime.evaluate',
        'params': {'expression': expression, 'returnByValue': True, 'userGesture': user_gesture}
    }))
    deadline = time.time() + timeout
    while time.time() < deadline:
        ws.settimeout(2)
        try:
            resp = json.loads(ws.recv())
            if resp.get('id') == msg_id:
                if 'error' in resp: return f"ERR: {resp['error']}"
                return resp.get('result', {}).get('result', {}).get('value')
        except: continue
    return 'TIMEOUT'

def check_join_success(ws):
    """Returns (bool, details)"""
    r = cdp_eval(ws, """
    (function(){
        var iframe = document.getElementById('webclient');
        if(!iframe) return JSON.stringify({error:'no webclient'});
        try{
            var idoc = iframe.contentDocument || iframe.contentWindow.document;
            var txt = idoc.body.innerText || '';
            var btns = [];
            idoc.querySelectorAll('button').forEach(function(b){
                var t = b.textContent.trim().substring(0,20);
                if(t) btns.push(t);
            });
            return JSON.stringify({
                bodyStart: txt.substring(0,200),
                buttons: btns,
                hasUnmute: txt.includes('Unmute'),
                hasLeave: txt.includes('Leave'),
                isWaiting: txt.includes('Waiting for the host'),
                bodyLen: txt.length
            });
        }catch(e){return JSON.stringify({error:e.message});}
    })()
    """)
    if not r: return False, 'no response'
    try:
        d = json.loads(r)
        if d.get('isWaiting'): return False, 'bekleme odasında'
        if d.get('hasUnmute') or d.get('hasLeave'): return True, f"içeride: {d.get('bodyStart','')[:60]}"
        return False, f"bilinmiyor: bodyLen={d.get('bodyLen',0)}"
    except: return False, r[:100]

def join_zoom(meeting_id, passcode, display_name, zoom_url=None):
    port = 9333
    
    # 1. Open tab
    url = zoom_url or f"https://app.zoom.us/wc/join/{meeting_id}"
    print(f"[1/8] Opening Zoom tab...")
    req = urllib.request.Request(f"http://localhost:{port}/json/new?{url}", method="PUT")
    resp = urllib.request.urlopen(req, timeout=10)
    new_tab = json.loads(resp.read().decode())
    print(f"       Tab: {new_tab.get('id','?')[:20]}")
    time.sleep(5)
    
    # 2. Find tab & connect
    print(f"[2/8] Connecting CDP...")
    tab = find_zoom_tab(port)
    if not tab: return False, "Zoom tab bulunamadı"
    ws = create_connection(tab['webSocketDebuggerUrl'], timeout=15)
    print(f"       Title: {tab.get('title','?')[:50]}")
    
    # 3. Click "Join from Browser" if on landing page
    print(f"[3/8] Looking for 'Join from Browser'...")
    r = cdp_eval(ws, """
    (function(){
        var targets = document.querySelectorAll('a, button');
        for(var i=0;i<targets.length;i++){
            var t = targets[i].textContent.toLowerCase();
            if(t.includes('join from browser')){
                targets[i].click(); return 'clicked: '+targets[i].textContent.trim().substring(0,20);
            }
        }
        return 'not found';
    })()""", user_gesture=True)
    print(f"       {r}")
    
    time.sleep(6)
    
    # 4. Reconnect (tab may have changed)
    tab = find_zoom_tab(port)
    if tab:
        ws = create_connection(tab['webSocketDebuggerUrl'], timeout=15)
    
    # 5. Check for iframe (PWA pattern)
    print(f"[4/8] Checking for iframe...")
    r = cdp_eval(ws, """
    (function(){
        var iframe = document.getElementById('webclient');
        if(!iframe) return JSON.stringify({iframe:false});
        try{
            var idoc = iframe.contentDocument || iframe.contentWindow.document;
            var inputs = [];
            idoc.querySelectorAll('input').forEach(function(inp){
                if(inp.offsetParent!==null) inputs.push({id:inp.id,type:inp.type});
            });
            return JSON.stringify({iframe:true, inputs:inputs, bodyLen:idoc.body.innerText.length});
        }catch(e){return JSON.stringify({iframe:true, error:e.message});}
    })()""")
    if r:
        d = json.loads(r)
        if d.get('iframe'):
            print(f"       PWA iframe bulundu, bodyLen: {d.get('bodyLen',0)}")
    
    # 6. Fill form (in main doc or iframe)
    print(f"[5/8] Filling form (name={display_name})...")
    escaped_name = display_name.replace("'", "\\'")
    r = cdp_eval(ws, f"""
    (function(){{
        var results = [];
        var fillInput = function(inp, val){{
            var ns = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
            ns.call(inp, val);
            inp.dispatchEvent(new Event('input', {{bubbles:true}}));
            inp.dispatchEvent(new Event('change', {{bubbles:true}}));
        }};
        
        var tryDoc = function(doc, prefix){{
            ['input-for-name', 'input-for-pwd'].forEach(function(id){{
                var inp = doc.getElementById(id);
                if(inp){{ fillInput(inp, id==='input-for-name' ? '{escaped_name}' : '{passcode}'); results.push(prefix+id+' ok'); }}
            }});
            var btns = doc.querySelectorAll('button');
            for(var i=0;i<btns.length;i++){{
                var t = btns[i].textContent.trim().toLowerCase();
                if(t==='join' || t.startsWith('join ')){{ btns[i].click(); results.push(prefix+'join clicked'); break; }}
            }}
        }};
        
        tryDoc(document, 'main.');
        var iframe = document.getElementById('webclient');
        if(iframe){{
            try{{ tryDoc(iframe.contentDocument || iframe.contentWindow.document, 'iframe.'); }}
            catch(e){{ results.push('iframe error: '+e.message); }}
        }}
        return JSON.stringify(results);
    }})()
    """, user_gesture=True)
    print(f"       {r}")
    
    time.sleep(6)
    
    # 7. Second join click
    print(f"[6/8] Second join click...")
    r = cdp_eval(ws, """
    (function(){
        var tryClick = function(doc){
            var btns = doc.querySelectorAll('button');
            for(var i=0;i<btns.length;i++){
                var t = btns[i].textContent.trim().toLowerCase();
                if((t==='join' || t.startsWith('join ')) && btns[i].offsetParent!==null){
                    btns[i].click(); return 'clicked main';
                }
            }
            return null;
        };
        var r = tryClick(document);
        if(r) return r;
        var iframe = document.getElementById('webclient');
        if(iframe){
            try{
                var idoc = iframe.contentDocument || iframe.contentWindow.document;
                return tryClick(idoc) || 'no btn in iframe';
            }catch(e){return 'iframe err';}
        }
        return 'no join btn';
    })()""", user_gesture=True)
    print(f"       {r}")
    
    time.sleep(5)
    
    # 8. Final check
    print(f"[7/8] Final status check...")
    success, detail = check_join_success(ws)
    print(f"       {'✅ JOIN OK' if success else '❌ JOIN FAILED'}: {detail}")
    
    ws.close()
    return success, detail

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Zoom toplantısına katıl')
    parser.add_argument('--meeting', required=True, help='Meeting ID')
    parser.add_argument('--pwd', default='', help='Passcode')
    parser.add_argument('--name', default='Sudenaz', help='Görünen isim')
    parser.add_argument('--url', default=None, help='Zoom URL (opsiyonel)')
    args = parser.parse_args()
    
    ok, detail = join_zoom(args.meeting, args.pwd, args.name, args.url)
    sys.exit(0 if ok else 1)
