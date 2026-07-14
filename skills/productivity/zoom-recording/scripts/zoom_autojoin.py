#!/usr/bin/env python3
"""
zoom_autojoin.py — Otomatik Zoom Join + Fail-Safe Bildirim
"""
import sys, json, urllib.request, time, os, subprocess, glob
def log(msg): print(msg, file=sys.stderr)
def main():
    args = sys.argv[1:]
    if len(args) < 4:
        print("FAIL|Eksik argüman: title url passcode name [port]")
        return
    title, url, passcode, name = args[0], args[1], args[2], args[3]
    port = int(args[4]) if len(args) > 4 else 9333
    try:
        resp = urllib.request.urlopen(f'http://localhost:{port}/json/version', timeout=5)
        json.loads(resp.read().decode())
    except Exception as e:
        print(f"FAIL|Chrome port {port} ölü: {e}")
        return
    try:
        pa_base = "/tmp/pulseaudio_extract"
        pa_env = {**os.environ, 'PULSE_SERVER': 'unix:/tmp/pulse-YiS0IhPtYxro/native',
                  'LD_LIBRARY_PATH': f'{pa_base}/usr/lib/x86_64-linux-gnu:{pa_base}/usr/lib/x86_64-linux-gnu/pulseaudio:{pa_base}/usr/lib/pulse-17.0+dfsg1/modules'}
        r = subprocess.run([f'{pa_base}/usr/bin/pactl', 'list', 'sinks', 'short'],
                         capture_output=True, text=True, timeout=5, env=pa_env)
        if 'zoom_rec' not in r.stdout:
            socks = glob.glob('/tmp/pulse-*/native')
            if not socks:
                print("FAIL|PulseAudio socket bulunamadı")
                return
    except Exception as e:
        print(f"FAIL|PulseAudio kontrol hatası: {e}")
        return
    try:
        import urllib.parse
        quoted = urllib.parse.quote(url, safe='')
        req = urllib.request.Request(f'http://localhost:{port}/json/new?{quoted}', method='PUT')
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"FAIL|Tab açılamadı: {e}")
        return
    time.sleep(4)
    try:
        tabs = json.loads(urllib.request.urlopen(f'http://localhost:{port}/json', timeout=5).read().decode())
        ws_url = None
        for t in tabs:
            tu = t.get('url','')
            if 'zoom.us/j/' in tu or 'zoom.us/wc/' in tu or 'zoom.us/w/' in tu:
                ws_url = t.get('webSocketDebuggerUrl','')
                break
        if not ws_url:
            print("FAIL|Zoom tab bulunamadı")
            return
        import websocket
        ws = websocket.create_connection(ws_url, timeout=15)
        def cdp(method, params=None):
            m = {"id":1,"method":method,"params":params or {}}
            ws.send(json.dumps(m))
            return json.loads(ws.recv())
        cdp("Runtime.evaluate", {"expression":"""
            (function(){
                var btns=document.querySelectorAll('button');
                for(var b of btns){if(b.textContent.trim().toLowerCase().includes('join from browser')){b.click();return 'OK';}}
                return 'NOT_FOUND';
            })()
        ""","returnByValue":True,"userGesture":True})
        time.sleep(5)
        r = cdp("Runtime.evaluate", {"expression":"""
            (function(){
                var ifr=document.getElementById('webclient');
                if(!ifr) return 'NO_IFRAME';
                try{var idoc=ifr.contentDocument||ifr.contentWindow.document;return idoc.body.innerText.slice(0,300);}
                catch(e){return 'IFRAME_ERR';}
            })()
        ""","returnByValue":True})
        ift = r['result']['result']['value']
        if passcode and 'input-for-pwd' in ift:
            cdp("Runtime.evaluate", {"expression":f"""
                (function(){{
                    var ifr=document.getElementById('webclient');
                    var idoc=ifr.contentDocument||ifr.contentWindow.document;
                    var inp=idoc.getElementById('input-for-pwd');if(!inp)return;
                    var s=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
                    s.call(inp,'{passcode}');inp.dispatchEvent(new Event('input',{{bubbles:true}}));inp.dispatchEvent(new Event('change',{{bubbles:true}}));
                }})()
            ""","returnByValue":True,"userGesture":True})
            time.sleep(1)
        if name and ('Your Name' in ift or 'input-for-name' in ift):
            cdp("Runtime.evaluate", {"expression":f"""
                (function(){{
                    var ifr=document.getElementById('webclient');
                    var idoc=ifr.contentDocument||ifr.contentWindow.document;
                    var inputs=idoc.querySelectorAll('input');
                    var ni=inputs[0];
                    for(var i of inputs){{if(i.placeholder&&i.placeholder.toLowerCase().includes('name')){{ni=i;break;}}if(i.id=='input-for-name'){{ni=i;break;}}}}
                    if(!ni)return;
                    var s=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
                    s.call(ni,'{name}');ni.dispatchEvent(new Event('input',{{bubbles:true}}));ni.dispatchEvent(new Event('change',{{bubbles:true}}));
                }})()
            ""","returnByValue":True,"userGesture":True})
            time.sleep(1)
        for i in range(2):
            cdp("Runtime.evaluate", {"expression":"""
                (function(){
                    var ifr=document.getElementById('webclient');
                    if(!ifr)return;try{
                        var idoc=ifr.contentDocument||ifr.contentWindow.document;
                        var btns=idoc.querySelectorAll('button');
                        for(var b of btns){if(b.textContent.trim()==='Join'){b.click();return;}}
                    }catch(e){}
                })()
            ""","returnByValue":True,"userGesture":True})
            time.sleep(4)
        r = cdp("Runtime.evaluate", {"expression":"""
            (function(){
                var ifr=document.getElementById('webclient');
                if(!ifr)return 'NO_IFRAME';try{
                    var idoc=ifr.contentDocument||ifr.contentWindow.document;
                    var txt=idoc.body.innerText;
                    if(txt.includes('Leave'))return 'MEETING_ACTIVE';
                    if(txt.includes('ended')||txt.includes('This meeting'))return 'MEETING_ENDED';
                    return txt.slice(0,100);
                }catch(e){return 'ERR';}
            })()
        ""","returnByValue":True})
        final = r['result']['result']['value']
        ws.close()
        if 'MEETING_ACTIVE' in final: print("OK")
        elif 'MEETING_ENDED' in final: print(f"FAIL|{title}: Toplantı bitmiş")
        else: print(f"FAIL|{final[:80]}")
    except Exception as e:
        print(f"FAIL|Join hatası: {e}")
if __name__ == '__main__': main()
