#!/bin/bash
# APA kaydı — zoom_rec.monitor
PA_BASE=/tmp/pulseaudio_extract
export LD_LIBRARY_PATH=$PA_BASE/usr/lib/x86_64-linux-gnu:$PA_BASE/usr/lib/x86_64-linux-gnu/pulseaudio:$PA_BASE/usr/lib/pulse-17.0+dfsg1/modules
export PULSE_SERVER="unix:/tmp/pulse-YiS0IhPtYxro/native"
mkdir -p /home/ubuntu/recordings/10temmuz
nohup ffmpeg -y -f pulse -i zoom_rec.monitor -c:a libmp3lame -b:a 128k -t 01:15:00 /home/ubuntu/recordings/10temmuz/apa_ebsa.mp3 > /tmp/ffmpeg_apa_out.log 2>&1 &
FFPID=$!
echo "ffmpeg PID: $FFPID"
# ffmpeg'in bitmesini bekle (arka planda)
wait $FFPID
