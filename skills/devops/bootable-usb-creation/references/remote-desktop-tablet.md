# Remote Desktop: Android Tablet → PC

## Top Pick: Parsec

**Why:** 60 FPS, native keyboard passthrough, trackpad mode for touch screens.

### Setup
1. Install Parsec on Windows host: https://parsec.app
2. Install Parsec on Android tablet (Play Store)
3. Create free account, sign in on both devices
4. Connect — the host PC appears in the Android app

### Touch Optimization (Critical)
Settings → Client → Touch Mode: **Trackpad Mode**

This makes the tablet screen act like a giant trackpad. Your finger moves the cursor (not directly tapping). Combined with a physical keyboard, this is the best tablet→PC remote desktop experience.

- Two-finger tap = right click
- Two-finger drag = scroll
- Pinch = zoom

### Alternatives
- **Sunshine + Moonlight:** Even lower latency, open source. Moonlight on Android, Sunshine on Windows. Slightly more complex setup.
- **Microsoft RDP:** Windows 11 Pro only. Good keyboard support, slower over internet.

### Not Recommended
- **TeamViewer:** May flag personal use as commercial and block
- **AnyDesk:** Touch support inferior to Parsec
- **Chrome Remote Desktop:** Poor touch mapping (exactly what prompted this search)
