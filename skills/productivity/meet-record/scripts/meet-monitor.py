#!/usr/bin/env python3
"""meet-monitor: Keep Google Meet session alive and monitor ffmpeg recording."""
import json, time, os, subprocess, sys

CDP_URL = "http://localhost:9222"
RECORDING_FILE = "/tmp/meet_kaydi.mp3"
MEET_KEYWORD = sys.argv[1] if len(sys.argv) > 1 else "meet.google.com"

def log(msg): print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def check_meeting():
    try:
        import urllib.request
        tabs = json.loads(urllib.request.urlopen(f"{CDP_URL}/json").read())
        for t in tabs:
            if MEET_KEYWORD in t.get("url", ""):
                return True
        return False
    except: return False

def check_recording():
    try: return os.path.getsize(RECORDING_FILE)
    except: return -1

log(f"Monitor started — watching '{MEET_KEYWORD}'")
start_sz = check_recording()
log(f"Initial size: {start_sz} bytes")

for cycle in range(720):
    time.sleep(30)
    in_meeting = check_meeting()
    rec_sz = check_recording()
    log(f"[{cycle*30}s] meeting={in_meeting} rec={rec_sz} grow={rec_sz-start_sz}")
    ff = subprocess.run(["pgrep", "-f", "ffmpeg.*zoom_rec.monitor"],
                       capture_output=True, timeout=5)
    if ff.returncode != 0:
        log("ffmpeg down, restarting...")
        subprocess.Popen(["ffmpeg","-y","-f","pulse","-i","zoom_rec.monitor",
                         "-c:a","libmp3lame","-b:a","128k",RECORDING_FILE],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
log("Monitor finished")
