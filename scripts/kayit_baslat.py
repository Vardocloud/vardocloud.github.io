#!/usr/bin/env python3
"""ffmpeg ile APA kaydı başlat"""
import subprocess, os, time

ffmpeg_cmd = [
    '/usr/bin/ffmpeg', '-y',
    '-f', 'pulse', '-i', 'zoom_rec.monitor',
    '-c:a', 'libmp3lame', '-b:a', '128k',
    '-t', '01:15:00',
    '/home/ubuntu/recordings/10temmuz/apa_ebsa.mp3'
]

env = os.environ.copy()
env['LD_LIBRARY_PATH'] = '/tmp/pulseaudio_extract/usr/lib/x86_64-linux-gnu:/tmp/pulseaudio_extract/usr/lib/x86_64-linux-gnu/pulseaudio:/tmp/pulseaudio_extract/usr/lib/pulse-17.0+dfsg1/modules'
env['PULSE_SERVER'] = 'unix:/tmp/pulse-YiS0IhPtYxro/native'

proc = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True, env=env)
print(f'✅ ffmpeg başlatıldı (PID {proc.pid})')
