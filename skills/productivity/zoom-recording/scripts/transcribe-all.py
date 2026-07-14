#!/usr/bin/env python3
"""Batch transcribe Zoom recordings via Pollinations whisper-1 proxy.
Usage: python3 scripts/transcribe-all.py [--m1] [--m2]
Splits large MP3s into chunks, sends each to proxy, writes combined markdown.
"""
import subprocess, json, os, time, argparse

PROXY = "http://localhost:19999/v1/audio/transcriptions"
CHUNKS_DIR = "/home/ubuntu/recordings/chunks"
OUT_DIR = "/home/ubuntu/recordings"

def transcribe_chunk(filepath):
    result = subprocess.run(['curl', '-s', '-X', 'POST', PROXY,
        '-F', f'file=@{filepath}', '-F', 'model=whisper-1', '-F', 'language=tr'],
        capture_output=True, text=True, timeout=180)
    try: return json.loads(result.stdout).get('text', '')
    except: return f"[ERROR: {result.stdout[:200]}]"

def transcribe_meeting(name, chunks):
    text = f"=== {name.upper()} ===\n\n"
    for i in range(1, chunks+1):
        fp = os.path.join(CHUNKS_DIR, name, f"{name}_chunk{i:02d}.mp3")
        if not os.path.exists(fp): continue
        print(f"  {i}/{chunks}: {os.path.basename(fp)}...", end=" ", flush=True)
        text += f"\n--- Part {i} ---\n{transcribe_chunk(fp)}\n"
        print("OK"); time.sleep(2)
    of = os.path.join(OUT_DIR, f"transkript_{name}.md")
    with open(of,"w") as f: f.write(text)
    print(f"  → {of} ({len(text)}c)")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('meetings', nargs='*', default=['m2','m1'],
                    choices=['m1','m2','both'])
    args = ap.parse_args()
    ms = ['m1','m2'] if 'both' in args.meetings else args.meetings
    if 'm1' in ms: transcribe_meeting("m1", 12)
    if 'm2' in ms: transcribe_meeting("m2", 3)
