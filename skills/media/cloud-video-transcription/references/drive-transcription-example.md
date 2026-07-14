# Session Example: Three Seminar Videos (2026-06-25)

## Context
Edel had 3 seminar videos in a Google Drive folder named "seminer  videolar" and asked for transcription of all three.

## Videos Transcribed

| # | Name | Size | WAV Size | Transcript | Duration (transcribe) |
|---|------|------|----------|------------|----------------------|
| 1 | Treating BPD & Substance Use Disorders | 4.0 GB MP4 | 102 MB | 58,965 chars | 265s (CPU, base model) |
| 2 | Can Regulation Keep Pace with AI in Mental Healthcare | 1.7 GB MP4 | 44 MB | 25,254 chars | 140s |
| 3 | zihinselsaglikapp.mp4 | 5.6 GB MP4 | 142 MB | 63,753 chars | 231s |

## Key Lessons from This Session

### 1. Language Detection Bug
`zihinselsaglikapp.mp4` was English content but `language="tr"` was forced based on filename assumption. Result: Turkish-like gibberish in first transcript. Fixed by re-running with `language="en"`.

**Lesson:** Let auto-detection run first, or check filename + content clues more carefully. When in doubt, omit `language=` parameter.

### 2. Background Process Output
Python background processes need `flush=True` on every `print()` call. Without it, the `process(action='poll')` shows empty output even when the script is running fine.

### 3. Download + Transcribe Parallelism
Most efficient pattern: download all videos to WAV first (they stream through ffmpeg), then transcribe them. The WAV extraction is I/O-bound (network + ffmpeg), while transcription is CPU-bound (whisper). Running both in parallel on CPU-only systems degrades performance.

### 4. Timings on CPU-only
On a system with no GPU (faster-whisper "base" model, int8):
- 44 MB WAV → 140s (AI Mental Healthcare)
- 102 MB WAV → 265s (BPD)
- 142 MB WAV → 231s (zihinselsaglikapp)
- General ratio: ~1.6-2.6 seconds per MB of WAV

## Folder Structure Found
Drive folder "seminer  videolar" (ID: 1F7ZpsofYCkyTSm2lrc-fdb8h81a9oz9G) contained exactly 3 MP4 files. No subfolders.

## Transcript Format
All transcripts saved as `*_transcript.txt` with timestamps on each line:
```
[0.00 - 10.10] text here
[10.10 - 14.00] more text
```
