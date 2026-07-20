---
name: drive-media-transcription
description: "Transcribe Google Drive video/audio files: stream via Drive API, extract audio with ffmpeg, transcribe with faster-whisper."
version: 1.0.0
---

# Drive Media Transcription

Stream Google Drive videos through ffmpeg for audio extraction, then
transcribe with faster-whisper. No intermediate video file on disk.

## Prerequisites

- Google Workspace OAuth setup (token at `~/.hermes/google_token.json`)
- `ffmpeg` in PATH
- `faster-whisper` Python package

## References

- `references/pipeline-detail.md` — exact code listings, sizes, pitfalls

## ⚠️ KRİTİK: Whisper Dil Seçimi

**Her transkripsiyondan ÖNCE içeriğin dilini belirle. Yanlış dilde transkripsiyon çıktıyı kullanılamaz hale getirir.**

**Kural tablosu:**
| İçerik Dili | `language=` parametresi |
|-------------|------------------------|
| 🇹🇷 Türkçe | `language=tr` |
| 🇬🇧 İngilizce | `language=en` |
| 🤔 Emin değilsen | Dosya adına bak veya 10 saniye dinle |

**Bilinen hata (20 Tem 2026):** `language=tr` ile İngilizce içerik transkript edilince anlamsız fonetik dönüşüm olur.

---

## Step 1: Find the folder and files

First, locate the folder:

```bash
GAPI="python ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py"
$GAPI drive search "FOLDER_NAME_KEYWORD" --max 10
```

Note the folder ID from the `webViewLink` (last path segment).

Then list files inside it via direct Drive API v3 (the CLI wrapper cannot
query by `parents`):

```python
import importlib.util
spec = importlib.util.spec_from_file_location('google_api', 'google_api.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
service = mod.build_service('drive', 'v3')

results = service.files().list(
    q="'FOLDER_ID' in parents and trashed=false",
    fields='files(id, name, mimeType, size)'
).execute()
```

## Step 2: Stream to audio

Use `service.files().get_media(fileId=...)` piped directly to ffmpeg:

```python
from googleapiclient.http import MediaIoBaseDownload

request = service.files().get_media(fileId=FILE_ID)
ffmpeg = subprocess.Popen([
    'ffmpeg', '-i', 'pipe:0', '-vn',
    '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le',
    '-f', 'wav', 'output.wav'
], stdin=subprocess.PIPE, stderr=subprocess.PIPE)

downloader = MediaIoBaseDownload(ffmpeg.stdin, request)
done = False
while not done:
    status, done = downloader.next_chunk()
    if hasattr(status, 'progress'):
        print(f"  Progress: {int(status.progress() * 100)}%", flush=True)

ffmpeg.stdin.close()
ffmpeg.wait()
```

Key ffmpeg flags: `-vn` (drop video), `-ar 16000` (whisper sample rate),
`-ac 1` (mono), `-c:a pcm_s16le` (uncompressed 16-bit PCM).

## Step 3: Transcribe

```python
from faster_whisper import WhisperModel
model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe("input.wav", language="en", beam_size=5)
for seg in segments:
    print(f"[{seg.start:.2f} - {seg.end:.2f}] {seg.text}")
```

## ⚠️ Pitfalls

- **Stdout buffering in background processes:** Python `print()` buffers
  when run via Hermes `terminal(background=True)`. Always add `flush=True`
  to every print call, or the process will appear to produce no output.
- **`drive search` + `parents`:** The `google_api.py` CLI uses `fullText
  contains` which cannot filter by parent folder. Always use direct API
  calls for folder-scoped listing.
- **Large video timeouts:** A 4–6 GB MP4 streams for 5–10 minutes. Use
  `terminal(background=True, timeout=600)` or split into steps.
- **CPU-only whisper is slow:** The `base` model runs ~2× realtime on CPU.
  For large files, batch downloads first, then transcribe sequentially.
- **File name whitespace:** Google Drive allows double spaces in folder
  names (`"seminer  videolar"`). Search queries handle this but inspect
  results carefully.

## Output

Transcription files are plain text with timestamp markers:
```
[0.00 - 10.10] First line of transcript
[10.10 - 14.00] Second line
```
