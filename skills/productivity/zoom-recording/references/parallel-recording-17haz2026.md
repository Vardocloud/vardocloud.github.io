# Parallel Zoom Recording — 17 Haz 2026

First successful dual-meeting recording on ARM64 Oracle Cloud.

## Meeting Details

| | Meeting 1 | Meeting 2 |
|---|---|---|
| **Topic** | KOMPLEKS TRAVMA EGITIM - DOC DR TANER OZNUR | Clinical Work With Men (APA Webinar) |
| **Time** | 19:30–21:30 | 21:00–22:00 |
| **Overlap** | 21:00–21:30 (30 min parallel) | |
| **Name** | Berkcan Ulucan | Berkcan Ulucan |
| **Type** | Regular Zoom meeting | Zoom Webinar (apa-org.zoom.us/w/) |

## Architecture

```
Meeting 1:  Chrome :9333 → PULSE_SINK=zoom_rec   → ffmpeg → zoom_meeting1.mp3
Meeting 2:  Chrome :9334 → PULSE_SINK=zoom_rec_2 → ffmpeg → zoom_meeting2.mp3
```

## Key Learnings

### 1. Separate Chrome instances are MANDATORY
Single Chrome with two Zoom tabs would mix audio into one PULSE_SINK. Each meeting needs:
- Separate Chrome process (different `--remote-debugging-port`)
- Separate `--user-data-dir` (profile collision prevention)
- Separate `PULSE_SINK` env var
- Separate ffmpeg process recording from the corresponding `.monitor`

### 2. Chrome ARM64 Zygote Crash Pattern
Both Chrome instances crashed around the 30-minute mark with:
```
WebRTC SSRC which doesn't exist errors → zygote NOTREACHED → exit code 0
```

Recovery: restart Chrome (`background=true`), verify with `curl /json/version`, rejoin meeting.
ffmpeg does NOT need restart — it keeps recording to the same file (gap filled with silence).

Impact: ~45 seconds of silence in the recording per crash. Other port's Chrome unaffected.

### 3. `/json/new` Requires PUT Method
```
urllib.request.Request(url, method='PUT')  # CORRECT
urllib.request.urlopen(url)                # WRONG → HTTP 405
```

### 4. Cron-Timed Join Pattern
Setup 15-30 min before meeting, join via one-shot cron at meeting time.
Each meeting gets its own cron job with a self-contained Python script.

### 5. Test Join Leaves Stale Tab State
After test join → Leave, the tab's form inputs won't render on next navigation.
Solution: open a fresh tab via `/json/new` for each join attempt.
Do NOT use `/json/close/` — can crash Chrome entirely.

### 6. Post-Crash Rejoin Proves Recovery Works
Meeting 1 Chrome crashed at ~20:15. Restarted, rejoined within 45 seconds.
Title confirmed: "KOMPLEKS TRAVMA EGITIM - DOC DR TANER OZNUR"
Recording continued with minimal gap.

## Privacy Measures
- All recordings: `chmod 600` (owner-only read)
- No cloud upload — entirely local PulseAudio → ffmpeg → disk pipeline
- Display name is pseudonym (Berkcan Ulucan), not real name
- Transcript only on explicit request

## Disk Usage
- 128kbps MP3 ≈ 1 MB/min
- Meeting 1 (2h): ~120 MB
- Meeting 2 (1h): ~60 MB
- Total: ~180 MB on 8.6 GB free space (2%)
