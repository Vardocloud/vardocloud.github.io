---
name: cloud-video-transcription
description: "Transcribe videos from cloud storage (Google Drive, etc.) — download/stream, audio extraction with ffmpeg, transcription with faster-whisper. Covers Drive API streaming, language detection pitfalls, and parallel processing patterns."
version: 1.0.0
tags: [transcription, video, audio, whisper, ffmpeg, google-drive]
---

# Cloud Video Transcription

Stream videos from cloud storage, extract audio with ffmpeg, and transcribe with faster-whisper — without downloading the full video file to disk.

## When to Use

- User asks to "transcript videos from Google Drive" or similar cloud storage
- Voice-over/seminar/lecture videos that need text transcription
- Any cloud-hosted video that doesn't have built-in captions

## Workflow

### 1. List Videos in Cloud Storage

For Google Drive, use the Python API directly (the CLI wrapper has limited query support):

```python
import importlib.util
spec = importlib.util.spec_from_file_location('google_api', 'google_api.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
service = mod.build_service('drive', 'v3')

results = service.files().list(
    q="'FOLDER_ID' in parents and trashed=false",
    pageSize=20,
    fields='files(id, name, mimeType, modifiedTime, webViewLink, size)'
).execute()
```

### 2. Stream + Audio Extraction (No Full Download)

Pipe the video stream directly through ffmpeg to extract audio:

```python
from googleapiclient.http import MediaIoBaseDownload
import subprocess

request = service.files().get_media(fileId=FILE_ID)
ffmpeg_cmd = [
    'ffmpeg', '-i', 'pipe:0', '-vn',
    '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le',
    '-f', 'wav', 'output.wav'
]
ffmpeg = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
downloader = MediaIoBaseDownload(ffmpeg.stdin, request)
done = False
while not done:
    status, done = downloader.next_chunk()
    # status.progress() gives 0.0 to 1.0
ffmpeg.stdin.close()
ffmpeg.wait()
```

### 3. Transcribe with faster-whisper

```python
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe("audio.wav", beam_size=5)

for seg in segments:
    print(f"[{seg.start:.2f} - {seg.end:.2f}] {seg.text}")
```

## Critical: Language Detection

**This is the #1 pitfall.** Forcing the wrong language produces hallucinated gibberish.

- If a video is English and you force `language="tr"`, Whisper outputs Turkish-sounding nonsense
- If a video is Turkish and you force `language="en"`, Whisper outputs English-sounding nonsense
- **Best practice:** Omit `language=` parameter for auto-detection, OR inspect the filename for language clues (English title → `language="en"`, Turkish title → `language="tr"`)
- Auto-detection adds ~5% overhead but avoids hallucination

## Parallel Processing

For multiple videos, run download and transcription in parallel using `terminal(background=True, notify_on_complete=True)`:

1. Start downloading video 1 (background)
2. While it downloads, transcribe any already-downloaded videos
3. Chain: download all first, then transcribe in parallel

Monitor with `process(action='poll')` or `process(action='log')`.

Note: background Python scripts need `flush=True` on print() calls for real-time output capture. Without it, output buffers until the script finishes.

## Storage & Cleanup

- Input video: stays in cloud (never downloaded fully)
- Intermediate WAV: ~3-5% of video size (e.g., 4 GB MP4 → ~100 MB WAV for 16kHz mono)
- WAV files should be cleaned up after transcription: `rm /path/to/*.wav`
- Target: transcripts saved as `.txt` files with timestamps `[start - end] text`

## References

- `references/drive-transcription-example.md` — Full session example with three seminars from 2026-06-25

## Troubleshooting

| Problem | Fix |
|---------|-----|
| ffmpeg stdin pipe blocks on large files | Redirect ffmpeg stderr to DEVNULL or consume it |
| Permission error on Drive API | Ensure `https://www.googleapis.com/auth/drive.readonly` scope is in OAuth token |
| Whisper model download slow | Set `HF_TOKEN` environment variable for faster downloads |
| Background process has no output | Add `flush=True` to print() calls; use `-u` Python flag |
