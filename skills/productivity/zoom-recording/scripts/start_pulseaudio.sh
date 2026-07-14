#!/bin/bash
# start_pulseaudio.sh
# PulseAudio + D-Bus bootstrap for Zoom/Google Meet recording
# Prerequisites: pulseaudio extracted to /tmp/pulseaudio_extract/ 
#   (see references/pulseaudio-bootstrap-sid.md)

PA_BASE=/tmp/pulseaudio_extract

export LD_LIBRARY_PATH=$PA_BASE/usr/lib/x86_64-linux-gnu:$PA_BASE/usr/lib/x86_64-linux-gnu/pulseaudio:$PA_BASE/usr/lib/pulse-17.0+dfsg1/modules:$PA_BASE/usr/lib/pulse-17.0+dfsg1/modules
export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/tmp/run-dbus/system_bus_socket
export DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/dbus-session

# Start D-Bus system bus if not running
if [ ! -S /tmp/run-dbus/system_bus_socket ]; then
    mkdir -p /tmp/run-dbus
    dbus-daemon --system --address=unix:path=/tmp/run-dbus/system_bus_socket --nofork --nopidfile --nosyslog &
    sleep 1
fi

# Start PulseAudio if not running
if ! $PA_BASE/usr/bin/pactl info &>/dev/null; then
    $PA_BASE/usr/bin/pulseaudio -nF /tmp/default.pa \
        --daemonize=no --exit-idle-time=-1 \
        --dl-search-path=$PA_BASE/usr/lib/pulse-17.0+dfsg1/modules \
        --disallow-exit &
    sleep 2
fi

# Export PULSE_SERVER for subsequent tools
PULSE_SOCK=$(find /tmp -name "native" -type s 2>/dev/null | head -1)
if [ -n "$PULSE_SOCK" ]; then
    echo "PULSE_SERVER=unix:$PULSE_SOCK"
    echo "Run: export PULSE_SERVER=unix:$PULSE_SOCK"
fi

echo "PulseAudio: $($PA_BASE/usr/bin/pactl info 2>/dev/null | grep 'Server Name')"
echo "Sink: $($PA_BASE/usr/bin/pactl list sinks short 2>/dev/null | grep zoom_rec)"
