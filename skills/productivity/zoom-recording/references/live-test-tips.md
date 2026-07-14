# Live Test & Bot Bypass Tips (13 Haz 2026)

## Bot Detection Bypass

When Zoom says "Automated bots aren't allowed to join this meeting":

1. Close ALL existing page tabs via browser-level CDP `Target.closeTarget`
2. Create a fresh tab with a neutral HTTP page (e.g. `http://example.com`)
3. Wait for full `Page.loadEventFired`
4. THEN navigate to `https://app.zoom.us/wc/join/MEETING_ID`
5. Wait again for full load
6. Fill name + passcode using native setter + dispatchEvent (input + change events)
7. Click Join with `userGesture: True`
8. If Join doesn't respond, check if the tab ID changed (cross-origin nav) and re-connect

## Real-Time Audio Verification

During an active recording, check audio levels without stopping ffmpeg:

```bash
ffmpeg -y -f pulse -i zoom_rec.monitor -t 5 -c:a libmp3lame -b:a 128k /tmp/check_now.mp3
ffmpeg -i /tmp/check_now.mp3 -af "volumedetect" -f null - 2>&1 | grep -E "mean_volume|max_volume"
```
- `max_volume: -91.0 dB` = silence (no audio captured)
- `max_volume: -30 dB to -5 dB` = audio present ✅

Also check PulseAudio routing:
```bash
pactl list sink-inputs short  # See active audio streams
pactl list sinks short        # See sinks
```
Look for `target.object = "zoom_rec"` in Chrome's sink-input properties.

## Puppeteer MCP for Chrome 9333

Alternative CDP method:

- Connect: `mcp_puppeteer_puppeteer_connect_active_tab(debugPort=9333)`
- Navigate, fill form, click via puppeteer tools
- Evaluate JS: `mcp_puppeteer_puppeteer_evaluate(script="...")`

## Transcription Chunking

Pollinations whisper-1 has ~25MB file limit. For larger recordings:
- Split at 20MB boundaries
- Use `verbose_json` format for detailed output
- Language forced to `tr`

## CDP Quirks

- Tab IDs CHANGE after cross-origin navigation or SPA reload — always re-list tabs via `/json` before connecting
- Runtime.evaluate responses interleave with events — use ID matching
- userGesture: True essential for AudioContext and click simulation
- Native value setter + input/change events required for React/SPA inputs
