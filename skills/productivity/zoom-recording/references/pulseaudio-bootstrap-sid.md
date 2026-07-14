# PulseAudio Bootstrap from Debian Sid

When a container/VM has no `pulseaudio` binary (not in apt repo, no candidate), download from Debian Sid.

## Why Sid?

Debian Trixie (testing) and later releases dropped PulseAudio in favor of PipeWire. Sid (unstable) still has it.

## Quickstart

```bash
# Set once (extraction target)
EXTRACT=/tmp/pulseaudio_extract
mkdir -p "$EXTRACT"

# Download + extract pulseaudio + deps
cd /tmp
wget -q "http://ftp.debian.org/debian/pool/main/p/pulseaudio/pulseaudio_17.0+dfsg1-2.1+b1_amd64.deb" -O pulseaudio.deb
wget -q "http://ftp.debian.org/debian/pool/main/p/pulseaudio/pulseaudio-utils_17.0+dfsg1-2.1+b1_amd64.deb" -O pulseaudio-utils.deb
wget -q "http://ftp.debian.org/debian/pool/main/libt/libtool/libltdl7_2.5.4-11_amd64.deb" -O libltdl7.deb
wget -q "http://ftp.debian.org/debian/pool/main/s/samba/libtdb1_1.4.15+samba4.24.3+dfsg-1_amd64.deb" -O libtdb1.deb
wget -q "http://ftp.debian.org/debian/pool/main/s/speexdsp/libspeexdsp1_1.2.1-4_amd64.deb" -O libspeexdsp.deb
wget -q "http://ftp.debian.org/debian/pool/main/o/orc/liborc-0.4-0t64_0.4.42-3_amd64.deb" -O liborc.deb

for deb in pulseaudio.deb pulseaudio-utils.deb libltdl7.deb libtdb1.deb libspeexdsp.deb liborc.deb; do
  dpkg-deb -x "$deb" "$EXTRACT/"
done
```

## D-Bus Requirement

PulseAudio 17 requires D-Bus system bus. Containers without systemd need manual startup:

```bash
# Start D-Bus system bus
mkdir -p /tmp/run-dbus
dbus-daemon --system --address=unix:path=/tmp/run-dbus/system_bus_socket \
  --nofork --nopidfile --nosyslog &
sleep 1

# Start D-Bus session bus
dbus-daemon --session --address=unix:path=/tmp/dbus-session --fork
```

## PulseAudio Startup

```bash
export LD_LIBRARY_PATH="$EXTRACT/usr/lib/x86_64-linux-gnu:$EXTRACT/usr/lib/x86_64-linux-gnu/pulseaudio"
export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/tmp/run-dbus/system_bus_socket
export DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/dbus-session

# Config file (~/.config/pulse/default.pa equivalent)
cat > /tmp/default.pa << 'PAEOF'
#!/usr/bin/pulseaudio -nF
load-module module-native-protocol-unix
load-module module-null-sink sink_name=zoom_rec
load-module module-always-sink
set-default-sink zoom_rec
PAEOF

# Start
"$EXTRACT/usr/bin/pulseaudio" -nF /tmp/default.pa \
  --daemonize=no --exit-idle-time=-1 \
  --dl-search-path="$EXTRACT/usr/lib/pulse-17.0+dfsg1/modules" \
  --disallow-exit
```

## Verification

```bash
export LD_LIBRARY_PATH="$EXTRACT/usr/lib/x86_64-linux-gnu:$EXTRACT/usr/lib/x86_64-linux-gnu/pulseaudio"
"$EXTRACT/usr/bin/pactl" info
"$EXTRACT/usr/bin/pactl" list sinks short
# Should show "zoom_rec" null sink
```

## Known Quirks

- `--dl-search-path` is **required** — `PA_DL_SEARCH_PATH` env var is NOT read by pulseaudio 17
- **LD_LIBRARY_PATH MUST include the modules dir** (`.../pulse-17.0+dfsg1/modules`) — without it, `module-native-protocol-unix.so` fails with `libprotocol-native.so: cannot open shared object file`
- First attempt may fail with "Daemon already running" — `pkill -9 -f pulseaudio` and retry
- The "Couldn't canonicalize binary path" warning is cosmetic, ignore it
- `--log-level=error` suppresses startup noise; use `-v` for debug

## PULSE_SERVER (Connecting Clients)

After startup, `pactl` and `ffmpeg` need `PULSE_SERVER` to find the native socket.

```bash
# Find the socket (runtime path changes per session)
PULSE_SOCK=$(find /tmp -name "native" -type s 2>/dev/null | head -1)

# Use it for pactl and ffmpeg
export PULSE_SERVER="unix:$PULSE_SOCK"
"$EXTRACT/usr/bin/pactl" info
ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k kayit.mp3
```

## Version Pinning

Package versions listed above are from 2026-04/05. If they 404, find current versions at:
- https://packages.debian.org/sid/amd64/pulseaudio/download
- https://packages.debian.org/sid/amd64/pulseaudio-utils/download
- https://packages.debian.org/sid/amd64/libltdl7/download
- https://packages.debian.org/sid/amd64/libtdb1/download
- https://packages.debian.org/sid/amd64/libspeexdsp1/download
- https://packages.debian.org/sid/amd64/liborc-0.4-0t64/download

The file path pattern is always `pool/main/<prefix>/<package>/<full-deb-name>`.
