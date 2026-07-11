#!/usr/bin/env python3
"""Chrome 2 (port 9334) başlat — YouTube için"""
import subprocess, os, time, glob

env = os.environ.copy()
env['DISPLAY'] = ':99'
env['PULSE_SINK'] = 'zoom_rec_2'
env['DBUS_SESSION_BUS_ADDRESS'] = 'unix:path=/tmp/dbus-live/socket'
socks = glob.glob('/tmp/**/native', recursive=True)
if socks:
    env['PULSE_SERVER'] = f'unix:{socks[0]}'

profile = '/tmp/zoom_profile2'
os.makedirs(f'{profile}/Default', exist_ok=True)

proc = subprocess.Popen(
    ['/usr/bin/chromium',
     '--no-sandbox', '--remote-debugging-port=9334',
     '--remote-allow-origins=*', '--user-data-dir='+profile,
     '--no-first-run', '--no-default-browser-check',
     '--disable-features=TranslateUI', '--ozone-platform=x11',
     '--window-size=1280,720', '--use-fake-device-for-media-stream',
     '--use-fake-ui-for-media-stream', '--disable-dev-shm-usage',
     'about:blank'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    start_new_session=True, env=env)

time.sleep(5)
import urllib.request
try:
    resp = urllib.request.urlopen('http://localhost:9334/json/version', timeout=5)
    import json
    d = json.loads(resp.read().decode())
    print(f'✅ Chrome 2 port 9334: {d.get("Browser","?")}')
except Exception as e:
    print(f'❌ Chrome 2 failed: {e}')

# Canlı tut (process'i bekle — hiç bitmez)
proc.wait()
