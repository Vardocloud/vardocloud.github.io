# Docker Container Bootstrap — Python subprocess.Popen Yöntemi

## Ne Zaman Kullanılır

`scripts/start_pulseaudio.sh` ve shell `background=true` yöntemi çalışmadığında.
Özellikle:
- `cap_drop=ALL` olan Docker container'larında (D-Bus system bus başlatılamaz)
- `terminal(background=true)` ile Chrome hemen çıktığında
- PulseAudio 17 D-Bus session bus'a ihtiyaç duyduğunda

## Kök Neden

1. **D-Bus `--fork` çalışmaz**: Container'da dbus-daemon `--fork` modunda child oluşturamaz.
2. **D-Bus `--nofork` + `background=true` çalışmaz**: `exec` ile başlatılan process background'ta hemen ölür.
3. **Chrome `exec` + `background=true` çalışmaz**: Chrome fork+exec ile process tree oluşturur, parent exit code 0 döner, child'lar zombie olur.
4. **Shell `&` foreground'da yasak**: Hermes foreground komutta `&` kullanımını engeller.

## Çalışan Yöntem: Python subprocess + start_new_session

`execute_code` kullan. `start_new_session=True` ile başlatılan subprocess'ler Python bitse bile
yaşamaya devam eder (yeni bir process group/session oluşur, parent'dan bağımsız olur).

### Adım 1: D-Bus Session Bus

```python
import subprocess, os, time

os.makedirs("/tmp/dbus-live", exist_ok=True)
dbus_proc = subprocess.Popen(
    ["dbus-daemon", "--session",
     "--address=unix:path=/tmp/dbus-live/socket",
     "--nofork", "--print-address"],
    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    text=True, bufsize=0,
    start_new_session=True  # KRİTİK: parent bitse bile yaşa!
)
time.sleep(1)
addr = dbus_proc.stdout.readline().strip()
os.environ['DBUS_SESSION_BUS_ADDRESS'] = 'unix:path=/tmp/dbus-live/socket'
```

### Adım 2: PulseAudio (doğru LD_LIBRARY_PATH ile)

```python
PA_BASE = "/tmp/pulseaudio_extract"
MODULES_DIR = f"{PA_BASE}/usr/lib/pulse-17.0+dfsg1/modules"

env = os.environ.copy()
env['LD_LIBRARY_PATH'] = (
    f"{PA_BASE}/usr/lib/x86_64-linux-gnu:"
    f"{PA_BASE}/usr/lib/x86_64-linux-gnu/pulseaudio:"
    f"{MODULES_DIR}"  # ← libprotocol-native.so İÇİN ZORUNLU
)
env['DBUS_SESSION_BUS_ADDRESS'] = 'unix:path=/tmp/dbus-live/socket'

# default.pa
with open("/tmp/default_live.pa", "w") as f:
    f.write("""#!/usr/bin/pulseaudio -nF
load-module module-native-protocol-unix
load-module module-null-sink sink_name=zoom_rec
load-module module-always-sink
set-default-sink zoom_rec
""")

pa_proc = subprocess.Popen(
    [f"{PA_BASE}/usr/bin/pulseaudio",
     "-nF", "/tmp/default_live.pa",
     "--daemonize=no", "--exit-idle-time=-1",
     "--dl-search-path", MODULES_DIR,
     "--disallow-exit", "--log-level=error"],
    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    text=True, bufsize=0,
    start_new_session=True,
    env=env
)
time.sleep(3)
```

### Adım 3: Chrome (PulseAudio + D-Bus env ile)

```python
env['DISPLAY'] = ':99'
env['PULSE_SINK'] = 'zoom_rec'
# PULSE_SERVER: native socket'i bul
import glob
socks = glob.glob("/tmp/**/native", recursive=True)
if socks:
    env['PULSE_SERVER'] = f'unix:{socks[0]}'

chrome_proc = subprocess.Popen(
    ['/usr/bin/chromium',
     '--no-sandbox', '--remote-debugging-port=9333',
     '--remote-allow-origins=*',
     '--user-data-dir=/tmp/zoom_profile',
     '--no-first-run', '--no-default-browser-check',
     '--disable-features=TranslateUI', '--ozone-platform=x11',
     '--window-size=1280,720',
     '--use-fake-device-for-media-stream',
     '--use-fake-ui-for-media-stream',
     '--disable-dev-shm-usage',
     'about:blank'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    start_new_session=True,
    env=env
)
```

### Doğrulama

```python
import urllib.request, json

# Chrome port kontrol
resp = urllib.request.urlopen('http://localhost:9333/json/version', timeout=5)
d = json.loads(resp.read().decode())
print(f"Chrome: {d.get('Browser')}")

# PulseAudio sink kontrol
pactl = subprocess.run(
    [f"{PA_BASE}/usr/bin/pactl", "list", "sinks", "short"],
    capture_output=True, text=True,
    env=env
)
print(f"Sinks: {pactl.stdout}")
```

## ffmpeg Kaydı — `delegate_task` ile (10 Tem 2026) ⭐

`terminal(background=true)` ile ffmpeg Docker container'ında çalışmaz — ffmpeg ya hiç başlamaz
ya da exit 254 alır. `nohup` + `&` da foreground'da yasaktır. **Çözüm: `delegate_task`.**

Subagent kendi terminal session'ına sahiptir ve ffmpeg'i foreground'da çalıştırabilir:

```python
delegate_task(
    goal="ffmpeg ile kayıt başlat",
    context=f"""
PULSE_SERVER=unix:{SOCKET_PATH}
LD_LIBRARY_PATH={PA_BASE}/usr/lib/x86_64-linux-gnu:{PA_BASE}/usr/lib/x86_64-linux-gnu/pulseaudio:{PA_BASE}/usr/lib/pulse-17.0+dfsg1/modules

ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k -t 01:15:00 /path/to/output.mp3

Önce eski ffmpeg'leri öldür: pkill -f ffmpeg
Sonra ffmpeg'i bekle (foreground'da timeout ile).
""",
    toolsets=["terminal"]
)
```

**Önemli:** Subagent task'i tamamlayınca döner. ffmpeg çıktıktan sonra döner.
Bu yüzden süreyi (`-t`) doğru ayarla. `notify_on_complete` yok — subagent
çıktıktan sonra kontrol et.

## İkinci Chrome (Port 9334) — Paralel Kayıt

İkinci Chrome'u Docker'da başlatmak da aynı Python yöntemiyle yapılır.
Farklı profil + farklı port + farklı PULSE_SINK kullan:

```python
env2 = env.copy()
env2['PULSE_SINK'] = 'zoom_rec_2'
env2.pop('PULSE_SERVER', None)  # yeniden bul

chrome2 = subprocess.Popen(
    ['/usr/bin/chromium',
     '--no-sandbox', '--remote-debugging-port=9334',
     '--remote-allow-origins=*',
     '--user-data-dir=/tmp/zoom_profile2',
     # aynı flag'ler...
     'about:blank'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    start_new_session=True,
    env=env2
)
```

⚠️ **Bilinen sorun:** `terminal(background=true)` ile ikinci Chrome bazen
process tree zombie olur (Chromium 149, Debian Trixie). Bu durumda
`delegate_task` ile başlat veya `execute_code` + `start_new_session=True` dene.
`execute_code` bloklanırsa `delegate_task` fallback olarak kullan.

## YouTube Live Kaydı — yt-dlp

YouTube canlı yayınları için ayrıca Chrome'a gerek yok — `yt-dlp` kullan:

```bash
# yt-dlp ~/.local/bin'de (PATH'te değilse python3 -m yt_dlp)
python3 -m yt_dlp -f bestaudio -o "/path/to/yt_seminer.%(ext)s" "LIVE_URL"

# Canlı yayın başlamamışsa "This live event will begin in N minutes" döner.
# Başlayınca indirme otomatik başlar.
```

## Önemli Uyarılar

1. **`start_new_session=True`** olmazsa Python bitince tüm subprocess'ler ölür.
2. **LD_LIBRARY_PATH** modül dizinini içermezse `module-native-protocol-unix.so` yüklenemez.
3. **D-Bus session bus** PulseAudio 17 için **system bus değil, session bus** gerekir.
4. **`dbus-daemon --fork` çalışmaz** — her zaman `--nofork` + `start_new_session=True` kullan.
5. **Chrome `exec` + `background=true` ile başlatılamaz** — Python subprocess şart.
6. **Chrome `DBUS_SESSION_BUS_ADDRESS`** görmezse D-Bus hataları basal da çalışır.
   Ama ileride sorun çıkarmaması için environment'a ekle.
7. **ffmpeg `background=true` ile Docker'da çalışmaz** — `delegate_task` kullan.
