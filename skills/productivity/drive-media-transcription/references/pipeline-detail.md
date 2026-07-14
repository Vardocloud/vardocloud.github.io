# Session Detail: 3 Seminar Videos Transcribed

## Source
Google Drive folder: `"seminer  videolar"` (double space in name)
Folder ID: `1F7ZpsofYCkyTSm2lrc-fdb8h81a9oz9G`
3 MP4 videos, total ~11.3 GB

## Videos Processed

| # | Name | Size | WAV size | Transcript |
|---|------|------|----------|------------|
| 1 | Treating BPD & Substance Use Disorders | 4.0 GB | 102 MB | ~? chars |
| 2 | Can Regulation Keep Pace with AI in Mental Healthcare | 1.7 GB | 44 MB | 25,254 chars |
| 3 | zihinselsaglikapp.mp4 | 5.6 GB | — | — |

## Pipeline Used

1. **Locate folder** via `drive search "seminer"` — found folder with double-space name
2. **List contents** via direct Drive v3 API: `service.files().list(q="'FOLDER_ID' in parents")`
3. **Stream + convert** each video: `get_media()` piped to ffmpeg → 16kHz mono WAV
4. **Transcribe** with `faster-whisper` base model, CPU, `int8`, English, beam_size=5

## Timing

- Video 2 (1.7 GB → 44 MB WAV): stream+convert ~4 min, transcribe ~2.3 min
- Total pipeline workable with background processes

## Key Discovery

The `google_api.py` `drive search` CLI does NOT support `parents` queries.
It wraps `fullText contains` internally. For folder-scoped listing, you must
import `build_service` from `google_api.py` and call the Drive v3 API directly.

## Whisper Notes

- Model: `base` (runs ~2× realtime on CPU)
- No GPU available — all CPU inference
- 25,254 chars transcript produced from a ~30 min seminar
- Output format: `[start.end - end.end] text` with timestamps
