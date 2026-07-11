#!/usr/bin/env python3
"""YouTube transcript fetcher with fallback chain.
Usage: python3 yt_transcript.py VIDEO_ID [lang]
"""
import sys
import subprocess
import os

def try_transcript_api(video_id, langs):
    """Primary: youtube-transcript-api (direct timedtext API)."""
    from youtube_transcript_api import YouTubeTranscriptApi
    api = YouTubeTranscriptApi()
    errors = []
    # Try each language individually, then fallback to English
    for lang_list in [langs, ["en"], ["en", "tr"]]:
        try:
            transcript = api.fetch(video_id, lang_list)
            return " ".join([seg.text for seg in transcript])
        except Exception as e:
            errors.append(f"{lang_list}: {str(e)[:100]}")
    raise RuntimeError("; ".join(errors))

def try_yt_dlp(video_id, langs):
    """Fallback: yt-dlp --write-auto-subs."""
    import tempfile
    ytdlp = "/data/ubuntu/cache/pipx/cdb38dc80efe72d/bin/yt-dlp"
    if not os.path.exists(ytdlp):
        ytdlp = "yt-dlp"  # try PATH
    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            "yt-dlp", "--skip-download", "--write-auto-subs",
            "--sub-langs", ",".join(langs),
            "--output", os.path.join(tmpdir, "%(id)s"),
            f"https://youtube.com/watch?v={video_id}"
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            raise RuntimeError(f"yt-dlp failed: {r.stderr[:200]}")
        
        # Find the subtitle file
        for root, _, files in os.walk(tmpdir):
            for f in files:
                if f.endswith(".vtt") or f.endswith(".srt"):
                    path = os.path.join(root, f)
                    with open(path) as fh:
                        raw = fh.read()
                    # Simple VTT/SRT cleanup
                    lines = [l.strip() for l in raw.split("\n") if l.strip() 
                            and not l.strip().isdigit() 
                            and "-->" not in l]
                    return " ".join(lines[:200])
    raise RuntimeError("No subtitle file found")

def main():
    if len(sys.argv) < 2:
        print("Usage: yt_transcript.py VIDEO_ID [lang]")
        sys.exit(1)
    
    video_id = sys.argv[1]
    langs = sys.argv[2].split(",") if len(sys.argv) > 2 else ["tr", "en"]
    
    # Chain: API first, then yt-dlp fallback
    methods = [
        ("youtube-transcript-api", lambda: try_transcript_api(video_id, langs)),
        ("yt-dlp fallback", lambda: try_yt_dlp(video_id, langs)),
    ]
    
    for name, method in methods:
        try:
            text = method()
            if text and len(text) > 20:
                print(text[:8000])  # Limit to ~8K chars
                if name != "youtube-transcript-api":
                    print(f"\n[Used fallback: {name}]", file=sys.stderr)
                return
        except Exception as e:
            print(f"[{name} failed: {e}]", file=sys.stderr)
    
    print("ERROR: All methods failed to get transcript")
    sys.exit(1)

if __name__ == "__main__":
    main()
