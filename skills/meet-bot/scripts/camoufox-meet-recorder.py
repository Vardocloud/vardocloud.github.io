#!/usr/bin/env python3
"""Google Meet audio recorder using Camoufox + ffmpeg.
Usage: python3 camoufox-meet-recorder.py MEET_URL [GUEST_NAME] [DURATION_SEC]

DURATION_SEC: recording duration in seconds (default: 3600 = 1 hour)
              pass 0 for infinite recording (Ctrl+C to stop)

Requires: pip install camoufox
PulseAudio null sink must exist: pactl load-module module-null-sink sink_name=zoom_recording

CRITICAL: The PULSE_SINK env var MUST be set for audio to flow from Firefox to ffmpeg.
CRITICAL: Recording file size growing does NOT mean you're in the meeting.
          Verify with ffmpeg silencedetect after recording.
"""
import subprocess, time, os, sys
from camoufox import Camoufox

MEET_URL = sys.argv[1] if len(sys.argv) > 1 else "https://meet.google.com/..."
GUEST_NAME = sys.argv[2] if len(sys.argv) > 2 else "Sudenaz"
DURATION = int(sys.argv[3]) if len(sys.argv) > 3 else 3600  # default 1 hour
OUTPUT_FILE = f"/tmp/meet_recording_{int(time.time())}.mp3"
LOBBY_TIMEOUT = 120  # seconds to wait for host admission

FIREFOX_PREFS = {
    "permissions.default.microphone": 1,
    "permissions.default.camera": 1,
    "media.navigator.permission.disabled": True,
    "media.navigator.streams.fake": True,
}

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def main():
    with Camoufox(headless=True, firefox_user_prefs=FIREFOX_PREFS,
                  env={"PULSE_SINK": "zoom_recording"}) as browser:
        page = browser.new_page()
        page.on("pageerror", lambda err: log(f"JS Error (survived): {err}"))

        log(f"Navigating to {MEET_URL}...")
        page.goto(MEET_URL, wait_until="domcontentloaded", timeout=30000)

        # MUST wait for "Getting ready..." spinner to finish
        for i in range(30):
            txt = page.evaluate("document.body.innerText")
            if "Ask to join" in txt:
                log(f"Join UI ready after {i}s")
                break
            time.sleep(1)
        time.sleep(3)

        # Fill name via JS (React input setter)
        page.evaluate("""(name) => {
            const inp = document.querySelector('input[type="text"]');
            if (inp) {
                const ns = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value').set;
                ns.call(inp, name);
                inp.dispatchEvent(new Event('input', {bubbles: true}));
                inp.dispatchEvent(new Event('change', {bubbles: true}));
            }
        }""", GUEST_NAME)
        log(f"Entered name: {GUEST_NAME}")

        # Click "Ask to join" via JS — survives Playwright crash
        clicked = page.evaluate("""() => {
            const b = [...document.querySelectorAll('button')].find(
                b => (b.textContent||'').toLowerCase().includes('ask'));
            if (b) { b.click(); return 'clicked'; }
            return 'not found';
        }""")
        log(f"Click result: {clicked}")

        # Wait for admission
        log("Waiting for host to admit...")
        for i in range(LOBBY_TIMEOUT // 5):
            time.sleep(5)
            try:
                has_leave = page.evaluate(
                    'document.querySelector("[aria-label*=\\"Leave\\" i]") !== null')
                has_captions = page.evaluate(
                    'document.querySelector("[role=\\"region\\"][aria-label*=\\"aption\\" i]") !== null')
                log(f"[{i*5}s] Leave={has_leave} Captions={has_captions}")
                if has_leave or has_captions:
                    log("IN THE MEETING!")
                    break
            except Exception:
                log(f"[{i*5}s] Page disconnected (expected after crash)")

        # Start recording
        log("Starting ffmpeg recording...")
        ffmpeg_proc = subprocess.Popen(
            ["ffmpeg", "-y", "-f", "pulse", "-i", "zoom_recording.monitor",
             "-c:a", "libmp3lame", "-b:a", "128k", OUTPUT_FILE],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        log(f"Recording to {OUTPUT_FILE} (PID {ffmpeg_proc.pid})")

        # Record for DURATION seconds (or forever if DURATION == 0)
        if DURATION == 0:
            log("Infinite recording mode — press Ctrl+C to stop")
            try:
                while True:
                    time.sleep(30)
                    sz = os.path.getsize(OUTPUT_FILE) if os.path.exists(OUTPUT_FILE) else 0
                    log(f"rec_size={sz} (running)")
                    if ffmpeg_proc.poll() is not None:
                        log("ffmpeg died, restarting...")
                        ffmpeg_proc = subprocess.Popen(
                            ["ffmpeg", "-y", "-f", "pulse", "-i", "zoom_recording.monitor",
                             "-c:a", "libmp3lame", "-b:a", "128k", OUTPUT_FILE],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except KeyboardInterrupt:
                log("Stopped by user")
        else:
            iterations = max(1, DURATION // 10)
            for _ in range(iterations):
                time.sleep(10)
                sz = os.path.getsize(OUTPUT_FILE) if os.path.exists(OUTPUT_FILE) else 0
                log(f"rec_size={sz}")
                if ffmpeg_proc.poll() is not None:
                    ffmpeg_proc = subprocess.Popen(
                        ["ffmpeg", "-y", "-f", "pulse", "-i", "zoom_recording.monitor",
                         "-c:a", "libmp3lame", "-b:a", "128k", OUTPUT_FILE],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    log(f"Restarted ffmpeg: {ffmpeg_proc.pid}")

        if ffmpeg_proc and ffmpeg_proc.poll() is None:
            ffmpeg_proc.terminate()
            ffmpeg_proc.wait()

    log(f"Recording saved to {OUTPUT_FILE}")
    sz = os.path.getsize(OUTPUT_FILE) if os.path.exists(OUTPUT_FILE) else 0
    log(f"Size: {sz} bytes")
    if sz > 0:
        log("NOTE: File size > 0 does NOT mean audio has content.")
        log("Verify with: ffmpeg -i {} -af silencedetect -f null - 2>&1 | grep silence_end".format(OUTPUT_FILE))

if __name__ == "__main__":
    main()
