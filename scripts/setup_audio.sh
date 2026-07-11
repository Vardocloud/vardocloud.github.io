#!/bin/bash
# setup_audio.sh — D-Bus + PulseAudio + null-sink bootstrap
# Runs as: terminal(background=true, command="bash ~/.hermes/scripts/setup_audio.sh")

PA_BASE=/tmp/pulseaudio_extract
MODULES_DIR=$PA_BASE/usr/lib/pulse-17.0+dfsg1/modules

export LD_LIBRARY_PATH=$PA_BASE/usr/lib/x86_64-linux-gnu:$PA_BASE/usr/lib/x86_64-linux-gnu/pulseaudio:$MODULES_DIR

# 1. Eski runtime'ları temizle
rm -rf /tmp/pulse-* 2>/dev/null
rm -rf /tmp/pulse-state /tmp/pulse-runtime 2>/dev/null
mkdir -p /tmp/pulse-state /tmp/pulse-runtime /tmp/dbus-session2

# 2. D-Bus session bus (--fork ile)
rm -f /tmp/dbus-session2/socket
dbus-daemon --session --address=unix:path=/tmp/dbus-session2/socket --fork
sleep 1

if [ -S /tmp/dbus-session2/socket ]; then
    echo "D-Bus: OK"
else
    echo "D-Bus: FAILED"
    exit 1
fi

export DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/dbus-session2/socket

# 3. default.pa (gerekli modüller)
cat > /tmp/default2.pa << 'PAEOF'
#!/usr/bin/pulseaudio -nF
load-module module-native-protocol-unix
load-module module-null-sink sink_name=zoom_rec
load-module module-always-sink
set-default-sink zoom_rec
PAEOF

# 4. PulseAudio başlat
$PA_BASE/usr/bin/pulseaudio -nF /tmp/default2.pa \
    --daemonize=no --exit-idle-time=-1 \
    --dl-search-path=$MODULES_DIR \
    --disallow-exit --log-level=error &
PA_PID=$!
sleep 3

if kill -0 $PA_PID 2>/dev/null; then
    echo "PulseAudio: OK (PID $PA_PID)"
    # Socket yolunu yaz
    PULSE_SOCK=$(find /tmp -name "native" -type s 2>/dev/null | head -1)
    echo "Socket: $PULSE_SOCK"
    # Sink kontrol
    PULSE_SERVER="unix:$PULSE_SOCK" $PA_BASE/usr/bin/pactl list sinks short 2>/dev/null
else
    echo "PulseAudio: FAILED"
    exit 1
fi

# Sonsuza kadar bekle (arka planda tut)
echo "Setup complete. Waiting..."
wait $PA_PID
