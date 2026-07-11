#!/usr/bin/env python3
"""Transcribe all Zoom recording chunks via Pollinations whisper-1"""
import subprocess, json, os, time

PROXY = "http://localhost:19999/v1/audio/transcriptions"
CHUNKS_DIR = "/home/ubuntu/recordings/chunks"

def transcribe_chunk(filepath):
    """Send a single chunk to whisper API and return text"""
    with open(filepath, 'rb') as f:
        result = subprocess.run(
            ['curl', '-s', '-X', 'POST', PROXY,
             '-F', f'file=@{filepath}',
             '-F', 'model=whisper-1',
             '-F', 'language=tr'],
            capture_output=True, text=True, timeout=180
        )
    try:
        data = json.loads(result.stdout)
        return data.get('text', '')
    except:
        # Try to find JSON in the output (curl -v sometimes adds noise)
        import re
        m = re.search(r'\{.*"text":.*\}', result.stdout, re.DOTALL)
        if m:
            try:
                return json.loads(m.group()).get('text', '')
            except:
                pass
        return f"[TRANSCRIPTION_ERROR: {result.stdout[:200]}]"

def transcribe_all(name_prefix, file_pattern, total_chunks):
    """Transcribe all chunks in sequence"""
    text = f"=== {name_prefix} Transkripti ===\n\n"
    
    for i in range(1, total_chunks + 1):
        fname = f"{name_prefix}_chunk{i:02d}.mp3"
        fpath = os.path.join(CHUNKS_DIR, name_prefix, fname)
        
        if not os.path.exists(fpath):
            print(f"  Atlaniyor: {fname} (yok)")
            continue
        
        print(f"  {i}/{total_chunks}: {fname} ({os.path.getsize(fpath)//1024//1024}MB)...")
        result = transcribe_chunk(fpath)
        text += f"\n--- Bölüm {i} ---\n{result}\n"
        
        # Rate limiting: be nice to the API
        if i < total_chunks:
            time.sleep(2)
    
    return text

def main():
    print("=== TRANSCRIPTION START ===\n")
    
    # Meeting 2 first (smaller)
    print("Meeting 2 (APA Webinar):")
    m2_text = transcribe_all("m2", "m2_chunk*.mp3", 3)
    with open("/home/ubuntu/recordings/transkript_meeting2.md", "w") as f:
        f.write(m2_text)
    print(f"  Yazildi: transkript_meeting2.md ({len(m2_text)} chars)")
    
    # Meeting 1 (bigger)
    print("\nMeeting 1 (KOMPLEKS TRAVMA):")
    m1_text = transcribe_all("m1", "m1_chunk*.mp3", 12)
    with open("/home/ubuntu/recordings/transkript_meeting1.md", "w") as f:
        f.write(m1_text)
    print(f"  Yazildi: transkript_meeting1.md ({len(m1_text)} chars)")
    
    print("\n=== TRANSCRIPTION COMPLETE ===")

if __name__ == '__main__':
    main()
