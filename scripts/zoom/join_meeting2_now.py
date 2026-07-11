#!/usr/bin/env python3
"""APA Webinar Join"""
import json, urllib.request, urllib.parse, time, sys
from websocket import create_connection

PORT=9334
URL="https://apa-org.zoom.us/w/94249463797?tk=qPUwbLU8hl1ryGiz5dLZSUN4BLoPvWYmmDUwCqzidQE.DQkAAAAV8bSv9RZvMEM4cUN6LVEwNjBlb3MyS3lGNDV3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA&uuid=WN_XTPBWAw5Rcu18lqjRfUKvQ"
NAME="Berkcan Ulucan"

def log(m): print(f'[{time.strftime("%H:%M:%S")}] {m}')

# Navigate
log("Navigating...")
req = urllib.request.Request(f'http://localhost:{PORT}/json/new?{urllib.parse.quote(URL, safe="")}', method='PUT')
urllib.request.urlopen(req)
time.sleep(8)

tabs = json.loads(urllib.request.urlopen(f'http://localhost:{PORT}/json').read())
tab = next((t for t in tabs if 'zoom.us' in t.get('url','') and 'service-worker' not in t.get('url','')), None)
if not tab: log("NO TAB"); sys.exit(1)
log(f'Tab1: {tab["title"][:50]}')

ws = create_connection(tab['webSocketDebuggerUrl'], timeout=15)

# Click "Join from browser"
ws.send(json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':'(()=>{const a=document.querySelectorAll("a");for(const l of a){const t=l.textContent.trim();if(t.includes("Join from browser")||t.includes("Tarayıcıdan")){l.click();return t}}return"NOTFOUND"})()','returnByValue':True,'userGesture':True}}))
print(f'Click: {json.loads(ws.recv()).get("result",{}).get("result",{}).get("value","?")}')
ws.close()
time.sleep(8)

# Tab2
tabs = json.loads(urllib.request.urlopen(f'http://localhost:{PORT}/json').read())
tab = next((t for t in tabs if 'zoom.us' in t.get('url','') and 'service-worker' not in t.get('url','')), None)
if not tab: log("NO TAB2"); sys.exit(1)
log(f'Tab2: {tab["title"][:50]}')
ws = create_connection(tab['webSocketDebuggerUrl'], timeout=15)

# Check form
ws.send(json.dumps({'id':2,'method':'Runtime.evaluate','params':{'expression':'!!document.getElementById("input-for-name")','returnByValue':True}}))
has_form = json.loads(ws.recv()).get("result",{}).get("result",{}).get("value",False)
log(f'Has form: {has_form}')

if has_form:
    # Fill name
    ws.send(json.dumps({'id':3,'method':'Runtime.evaluate','params':{'expression':f'(()=>{{const i=document.getElementById("input-for-name");const n=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,"value").set;n.call(i,"{NAME}");i.dispatchEvent(new Event("input",{{bubbles:true}}));i.dispatchEvent(new Event("change",{{bubbles:true}}));return i.value}})()','returnByValue':True}}))
    print(f'Name: {json.loads(ws.recv()).get("result",{}).get("result",{}).get("value","?")}')
    
    # Join1
    ws.send(json.dumps({'id':4,'method':'Runtime.evaluate','params':{'expression':'(()=>{const b=document.querySelectorAll("button");for(let i=0;i<b.length;i++){if(b[i].textContent.toLowerCase().includes("join")){b[i].click();return b[i].textContent.trim()}}return"NO"})()','returnByValue':True,'userGesture':True}}))
    print(f'Join1: {json.loads(ws.recv()).get("result",{}).get("result",{}).get("value","?")}')
    ws.close()
    time.sleep(8)
    
    # Tab3
    tabs = json.loads(urllib.request.urlopen(f'http://localhost:{PORT}/json').read())
    tab = next((t for t in tabs if 'zoom.us' in t.get('url','') and 'service-worker' not in t.get('url','')), None)
    if tab:
        ws = create_connection(tab['webSocketDebuggerUrl'], timeout=15)
        ws.send(json.dumps({'id':5,'method':'Runtime.evaluate','params':{'expression':'(()=>{const b=document.querySelectorAll("button");for(let i=0;i<b.length;i++){if(b[i].textContent.toLowerCase().includes("join")){b[i].click();return b[i].textContent.trim()}}return"NO"})()','returnByValue':True,'userGesture':True}}))
        print(f'Join2: {json.loads(ws.recv()).get("result",{}).get("result",{}).get("value","?")}')
        time.sleep(4)
        
        ws.send(json.dumps({'id':6,'method':'Runtime.evaluate','params':{'expression':'(()=>{return JSON.stringify({title:document.title,leave:document.body.innerText.includes("Leave"),url:window.location.href})})()','returnByValue':True}}))
        state = json.loads(ws.recv()).get("result",{}).get("result",{}).get("value","?")
        print(f'State: {state}')
        if '"leave":true' in str(state): print('✅ WEBINARDA!')
        else: print('⚠️')
        ws.close()
    else:
        log("Tab3 yok")
else:
    # Show what's on the page  
    ws.send(json.dumps({'id':7,'method':'Runtime.evaluate','params':{'expression':'document.title + " | " + document.body.innerText.substring(0,300)','returnByValue':True}}))
    print(f'Sayfa: {json.loads(ws.recv()).get("result",{}).get("result",{}).get("value","?")}')
    ws.close()
