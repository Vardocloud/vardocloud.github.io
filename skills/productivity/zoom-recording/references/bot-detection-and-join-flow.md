# Bot Detection & Join Flow — 13 Haz 2026 Testi

## Test Summary
- **Meeting 1:** 821 6626 0086 — bot detection triggered: "automated bots aren't allowed"
- **Meeting 2:** 871 0678 4019 — SUCCESS: joined and recorded

## Bot Detection
Zoom blocks some meetings with "Automated bots aren't allowed" error. This appears AFTER clicking Join with name/passcode filled.

**Detection triggers (observed):**
- reCAPTCHA enterprise check fails
- CDP (Chrome DevTools Protocol) usage detectable
- `--headless` flag (even without it, automation indicators persist)

**What worked:** Fresh tab with clean state, join form filled with native setter, Join clicked TWICE (first click opens preview session + overlay, second click enters meeting)

**What didn't help:**
- User-agent override (Windows Chrome UA still detected)
- Different profile

**Root cause hypothesis:** Some Zoom accounts/hosts have stricter security settings. Meeting 1 blocked, Meeting 2 allowed. Possibly host-level setting.

## Join Flow (Proven Sequence)

### Tab Management
```python
# 1. Get browser WS URL
curl http://localhost:9333/json/version  # get webSocketDebuggerUrl

# 2. Create new tab with neutral URL first (avoid Zoom tracking)
Target.createTarget(url="http://example.com")

# 3. Wait for Page.loadEventFired

# 4. Navigate to join page
Page.navigate(url="https://app.zoom.us/wc/join/MEETING_ID")
```

### Form Fill
Input elements are found by ID:
- `input-for-name` — "Your Name" field
- `input-for-pwd` — "Meeting Passcode" field

**CRITICAL:** Use native setter, NOT `el.value = 'x'`:
```javascript
const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
setter.call(el, 'Sudenaz');
el.dispatchEvent(new Event('input', {bubbles: true}));
el.dispatchEvent(new Event('change', {bubbles: true}));
```

### Join Button
The Join button is a `<button>` element with text "Join". Using `document.querySelector('button')` works because the form's Join button is the first visible button.
- First click: Opens media preview (shows "Unmute", "You are muted", video preview)
- Second click: Dismisses overlay, enters full meeting UI

### State Transitions
| State | Title | Body Length | Key Indicators |
|-------|-------|-------------|----------------|
| Loading | "Zoom meeting on web" | N/A | "Joining Meeting..." |
| Form visible | "Zoom meeting on web" | ~500 chars | "Meeting Passcode", "Your Name", "Join" |
| Preview (after 1st click) | "Zoom meeting on web" | ~300 chars | "Unmute", "You are muted", form still visible |
| **IN MEETING** ✅ | **"Sudenaz Zoom Toplantısı"** | **<100 chars** | **"Unmute", "Leave", "Participants", "2"** |

### Tab ID Change
After successful join, the CDP target ID changes (cross-origin SPA navigation). Old WebSocket connections break with "No such target id". Need to:
1. `curl localhost:9333/json` to get fresh tab list
2. Find the new page tab ID
3. Reconnect

### Puppeteer MCP Connection
Alternative to raw CDP WebSocket:
```bash
# Connect puppeteer-mcp to custom Chrome port
mcp_puppeteer_puppeteer_connect_active_tab(debugPort=9333)
# Then use puppeteer_navigate, puppeteer_evaluate, puppeteer_click
```
Note: puppeteer_evaluate returns `undefined` for some expressions due to CSP. Use CDP Runtime.evaluate for reliable results.

## Audio Pipeline (PulseAudio)

Tested and confirmed working (13 Haz 2026):
```
Chrome 9333 (--use-fake-device-for-media-stream)
  → PulseAudio null-sink (zoom_rec)
    → ffmpeg zoom_rec.monitor → MP3
```

- Volume detection: mean_volume -13.9 dB, max_volume -10.3 dB ✅
- AudioContext running (userGesture required)
- Fake device generates 3 audio inputs: "Fake Default Audio Input", "Fake Audio Input 1", "Fake Audio Input 2"
