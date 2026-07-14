# Android Client Fallback + Local Whisper Benchmark

**Date:** 12 Temmuz 2026
**Video:** "Zenginler Sıfırdan Başlasaydı Yapay Zekayı Böyle Kullanırdı" — Fatih Çoban
**Video ID:** 6aketTaBWzs
**Duration:** 31:34 (1894s)
**Platform:** WSL (x86_64), Oracle Cloud IP (104.28.x.x)

## Problem Chain

1. Auto-captions: PO token blocked (yt-dlp wrote 412-byte headers-only VTT)
2. yt-dlp `--list-formats` (default): only HLS formats 91-96 (video+audio, m3u8)
3. yt-dlp `--list-formats` (ios client): required GVS PO token → blocked
4. `youtube-transcript-api`: PO token → "no element found"
5. Browser `ytInitialPlayerResponse.captions`: timedtext URL found but returns empty (200 OK, 0 body)
6. Pollinations Whisper: HTTP 402 PAYMENT_REQUIRED (balance 0.0003, cost 0.0020)

## Android Client Solution

```bash
# Key command:
yt-dlp --extractor-args "youtube:player_client=android" -f 18 \
  --extract-audio --audio-format mp3 \
  "https://youtu.be/6aketTaBWzs" \
  -o "/tmp/yt_audio_%(id)s.%(ext)s"
```

| Metric | Value |
|--------|-------|
| Format discovered | 18 (360p MP4, combined) |
| File size | 129.69 MiB |
| Download time | 35 seconds |
| Avg speed | 3.69 MiB/s |
| Audio format | MP3 ~19.4 MB |
| Notes | Progressive HTTP (not HLS), no WARP needed |

**Why format 18 is faster:** It's a progressive download (single HTTP GET), not HLS segment streaming. Cloud IP throttle applies to individual connections but a single progressive download outperforms 344 sequential HLS fragment fetches (each with TCP handshake overhead).

## Local Whisper Performance

**Hardware:** x86_64 (unknown cores, likely 4 vCPU limit)
**Model:** faster-whisper small (cpu, int8)

| Segment | Duration | WAV Size | Processing Time | Real-time Factor |
|---------|----------|----------|-----------------|------------------|
| 000 (10:00) | 600s | 19.2 MB | ~30s | ~20x |
| 001 (10:00) | 600s | 19.2 MB merged | ~40s merged | ~15x |
| 002 (10:00) | 600s | 19.2 MB | ~40s merged | ~15x |
| 003 (1:34) | 94s | 3.0 MB | ~10s | ~9x |
| **Total** | **31:34** | **60.6 MB** | **~3 min** | **~10x** |

**Takeaway:** x86_64 faster-whisper small handles 31min video in ~3 minutes total processing time (including model load overhead). This is faster than the old ARM64 benchmark (1.1x realtime) by a factor of ~10.
