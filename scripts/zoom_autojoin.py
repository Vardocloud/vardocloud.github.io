#!/usr/bin/env python3
"""
zoom_autojoin.py — Otomatik Zoom Join + Fail-Safe Bildirim
Kullanım: python3 zoom_autojoin.py <title> <meeting_url> <passcode> <display_name> [port]

Not: Join'den 10 DAKIKA ÖNCE çalıştırılmalı (aksilik durumunda zaman kalsın).

Örnek: python3 zoom_autojoin.py "Cocuk Cizim" "https://us06web.zoom.us/j/..." "864163" "Berkcan Ulucan" 9333

Başarılı -> stdout: OK
Başarısız -> stdout: FAIL|sebep (bu Edel'e gider)
"""
import sys, json, urllib.request, time, os

def log(msg):
    print(msg, file=sys.stderr)

def main():
    args = sys.argv[1:]
    if len(args) < 4:
        print("FAIL|Eksik argüman: title url passcode name [port]")
        return

    title = args[0]
    url = args[1]
    passcode = args[2]
    name = args[3]
    port = int(args[4]) if len(args) > 4 else 9333

    # 1. Chrome port kontrol
    try:
        resp = urllib.request.urlopen(f'http://localhost:{port}/json/version', timeout=5)
        browser = json.loads(resp.read().decode()).get('Browser', '?')
        log(f"✅ Chrome {port}: {browser}")
    except Exception as e:
        print(f"FAIL|Chrome port {port} ölü: {e}")
        return

    # 2. PulseAudio kontrol
    try:
        import subprocess
        r = subprocess.run(['/tmp/pulseaudio_extract/usr/bin/pactl', 'list', 'sinks', 'short'],
                         capture_output=True, text=True, timeout=5,
                         env={**os.environ, 'PULSE_SERVER': 'unix:/tmp/pulse-YiS0IhPtYxro/native',
                              'LD_LIBRARY_PATH': '/tmp/pulseaudio_extract/usr/lib/x86_64-linux-gnu:/tmp/pulseaudio_extract/usr/lib/x86_64-linux-gnu/pulseaudio:/tmp/pulseaudio_extract/usr/lib/pulse-17.0+dfsg1/modules'})
        if 'zoom_rec' not in r.stdout:
            print("FAIL|PulseAudio zoom_rec sink bulunamadı")
            return
        log("✅ PulseAudio OK")
    except Exception as e:
        print(f"FAIL|PulseAudio kontrol hatası: {e}")
        return

    # 3. Yeni tab aç
    try:
        import urllib.parse
        quoted_url = urllib.parse.quote(url, safe='')
        req = urllib.request.Request(f'http://localhost:{port}/json/new?{quoted_url}', method='PUT')
        resp = urllib.request.urlopen(req, timeout=10)
        tab_data = json.loads(resp.read().decode())
        tab_id = tab_data.get('id', '')
        log(f"✅ Tab açıldı: {tab_id}")
    except Exception as e:
        print(f"FAIL|Tab açılamadı: {e}")
        return

    # 4. WS ile join
    time.sleep(4)
    try:
        tabs = json.loads(urllib.request.urlopen(f'http://localhost:{port}/json', timeout=5).read().decode())
        ws_url = None
        for t in tabs:
            if url.split('?')[0] in t.get('url', ''):
                ws_url = t.get('webSocketDebuggerUrl', '')
                break
        if not ws_url:
            # url kısalmış olabilir, zoom içeren tab'ı bul
            for t in tabs:
                if 'zoom.us/j/' in t.get('url', '') or 'zoom.us/wc/' in t.get('url', ''):
                    ws_url = t.get('webSocketDebuggerUrl', '')
                    break
        
        if not ws_url:
            print("FAIL|Join tab'ı bulunamadı (WebSocket URL yok)")
            return

        import websocket
        ws = websocket.create_connection(ws_url, timeout=15)

        def cdp(method, params=None):
            msg = {"id": 1, "method": method, "params": params or {}}
            ws.send(json.dumps(msg))
            return json.loads(ws.recv())

        # "Join from Browser" tıkla
        r = cdp("Runtime.evaluate", {
            "expression": """
            (function(){
                var btns = document.querySelectorAll('button');
                for(var b of btns){
                    if(b.textContent.trim().toLowerCase().includes('join from browser')){
                        b.click(); return 'OK';
                    }
                }
                return 'NOT_FOUND';
            })()
            """, "returnByValue": True, "userGesture": True
        })
        res = r.get('result',{}).get('result',{}).get('value','')
        if res != 'OK':
            # Belki direkt iframe vardır
            log(f"Join from Browser butonu bulunamadı, direkt iframe deneniyor...")
        else:
            log("Join from Browser tıklandı")

        time.sleep(5)

        # İframe kontrol
        r = cdp("Runtime.evaluate", {
            "expression": """
            (function(){
                var ifr = document.getElementById('webclient');
                if(!ifr) return 'NO_IFRAME';
                try {
                    var idoc = ifr.contentDocument || ifr.contentWindow.document;
                    return idoc.body.innerText.slice(0,300);
                } catch(e){ return 'IFRAME_ERR:'+e.message; }
            })()
            """, "returnByValue": True
        })
        iframe_text = r.get('result',{}).get('result',{}).get('value','')
        log(f"İframe: {iframe_text[:100]}")

        if iframe_text == 'NO_IFRAME':
            # Normal meeting — belki direkt giriş
            r = cdp("Runtime.evaluate", {
                "expression": """
                (function(){
                    var inputs = document.querySelectorAll('input');
                    var btns = document.querySelectorAll('button');
                    var result = '';
                    for(var i of inputs) result += 'input:'+i.id+' ';
                    for(var b of btns) result += 'btn:'+b.textContent.trim().slice(0,20)+' ';
                    return result;
                })()
                """, "returnByValue": True
            })
            log(f"Sayfa elemanları: {r.get('result',{}).get('result',{}).get('value','')}")

        # Passcode varsa gir
        if passcode and 'input-for-pwd' in iframe_text:
            r = cdp("Runtime.evaluate", {
                "expression": f"""
                (function(){{
                    var ifr = document.getElementById('webclient');
                    var idoc = ifr.contentDocument || ifr.contentWindow.document;
                    var inp = idoc.getElementById('input-for-pwd');
                    if(!inp) return 'pwd_input_yok';
                    var s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
                    s.call(inp, '{passcode}');
                    inp.dispatchEvent(new Event('input', {{bubbles:true}}));
                    inp.dispatchEvent(new Event('change', {{bubbles:true}}));
                    return 'pwd_girildi';
                }})()
                """, "returnByValue": True, "userGesture": True
            })
            log(f"Passcode: {r.get('result',{}).get('result',{}).get('value','')}")
            time.sleep(1)

        # İsim varsa gir
        if name and ('Your Name' in iframe_text or 'input-for-name' in iframe_text):
            r = cdp("Runtime.evaluate", {
                "expression": f"""
                (function(){{
                    var ifr = document.getElementById('webclient');
                    var idoc = ifr.contentDocument || ifr.contentWindow.document;
                    var inputs = idoc.querySelectorAll('input');
                    var nameInput = null;
                    for(var inp of inputs){{
                        if(inp.placeholder && inp.placeholder.toLowerCase().includes('name')){{nameInput=inp;break;}}
                        if(inp.id=='input-for-name'){{nameInput=inp;break;}}
                    }}
                    if(!nameInput && inputs.length>0) nameInput=inputs[0];
                    if(!nameInput) return 'input_yok';
                    var s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
                    s.call(nameInput, '{name}');
                    nameInput.dispatchEvent(new Event('input', {{bubbles:true}}));
                    nameInput.dispatchEvent(new Event('change', {{bubbles:true}}));
                    return 'isim_girildi';
                }})()
                """, "returnByValue": True, "userGesture": True
            })
            log(f"İsim: {r.get('result',{}).get('result',{}).get('value','')}")
            time.sleep(1)

        # Join butonuna tıkla (2 kez)
        for i in range(2):
            r = cdp("Runtime.evaluate", {
                "expression": """
                (function(){
                    var ifr = document.getElementById('webclient');
                    if(!ifr) return 'iframe_yok';
                    try{
                        var idoc = ifr.contentDocument || ifr.contentWindow.document;
                        var btns = idoc.querySelectorAll('button');
                        for(var b of btns){
                            if(b.textContent.trim()==='Join'){ b.click(); return 'tiklandi'; }
                        }
                        return 'join_yok';
                    }catch(e){ return 'hata:'+e.message; }
                })()
                """, "returnByValue": True, "userGesture": True
            })
            res2 = r.get('result',{}).get('result',{}).get('value','')
            log(f"Join deneme {i+1}: {res2}")
            time.sleep(4)

        # Meeting'de mi kontrol
        r = cdp("Runtime.evaluate", {
            "expression": """
            (function(){
                var ifr = document.getElementById('webclient');
                if(!ifr) return 'NO_IFRAME';
                try{
                    var idoc = ifr.contentDocument || ifr.contentWindow.document;
                    var txt = idoc.body.innerText;
                    if(txt.includes('Leave')) return 'MEETING_ACTIVE';
                    if(txt.includes(' ended') || txt.includes('This meeting')) return 'MEETING_ENDED';
                    return txt.slice(0,100);
                }catch(e){ return 'CHECK_ERR:'+e.message; }
            })()
            """, "returnByValue": True
        })
        final = r.get('result',{}).get('result',{}).get('value','')
        log(f"Son durum: {final}")

        ws.close()

        if 'MEETING_ACTIVE' in final:
            print("OK")
        elif 'MEETING_ENDED' in final:
            print(f"FAIL|{title}: Toplantı bitmiş")
        else:
            print(f"FAIL|Join sonrası beklenmeyen durum: {final}")

    except Exception as e:
        print(f"FAIL|Join hatası: {e}")

if __name__ == '__main__':
    main()
