# VNC-Based Credential Extraction (Fallback)

When server-side Playwright/browser automation fails (bot detection, IP block, wrong login endpoint),
and the user has a VNC session open, use xdotool + scrot to interact with the user's browser directly.

## Trigger
- Server-side login returns "wrong password" but user confirms password is correct
- User opens VNC and navigates to the login page themselves
- User says "VNC aç bakayım" or similar

## VNC Service Setup (One-Time, Already Running)

```bash
# TigerVNC on :1, port 5901
vncserver :1 -geometry 1280x800 -depth 24 -localhost no

# noVNC: single-port HTML + WebSocket proxy
websockify --web /usr/share/novnc 6080 localhost:5901 &

# UFW — allow Tailscale only
sudo ufw allow from 100.64.0.0/10 to any port 6080
```

User connects via: `http://100.82.131.32:6080/vnc.html` (password: upwork123)

## Core xdotool Commands

```bash
# Take screenshot
DISPLAY=:1 scrot /tmp/vnc_screen.png

# List all windows
DISPLAY=:1 wmctrl -l

# Find specific window by title
DISPLAY=:1 xdotool search --name "Brave"     # returns window ID

# Activate/focus a window
DISPLAY=:1 xdotool windowactivate 0x03000004

# Get window geometry (for relative coordinates)
DISPLAY=:1 xdotool getwindowgeometry 0x03000004
# → Position: 10,37  Geometry: 1050x753

# Click at screen coordinates
DISPLAY=:1 xdotool mousemove 700 340 click 1

# Click at window-relative coordinates (avoids resize issues)
DISPLAY=:1 xdotool mousemove --window 0x03000004 660 403 click 1

# Type text
DISPLAY=:1 xdotool type "password_here"

# Press keyboard keys
DISPLAY=:1 xdotool key Escape     # dismiss popups
DISPLAY=:1 xdotool key Tab         # navigate
DISPLAY=:1 xdotool key Return      # submit
```

## Workflow Pattern

1. **User opens VNC** → they navigate to login page, open Bitwarden, position cursor
2. **Take screenshot** → `DISPLAY=:1 scrot /tmp/vnc.png`
3. **Analyze with vision** → use `vision_analyze(image_url="/tmp/vnc.png", question="...")` to locate form fields, buttons, icons
4. **Get exact coordinates** → ask vision model for specific pixel positions
5. **Click/interact** via xdotool (prefer window-relative coordinates)
6. **Verify with another screenshot** → loop until success
7. **Save credential** via `mcp_local_secure_secure_save`

## Coordinate Estimation Tips

- **Window-relative is more reliable** than screen-absolute (survives window moves)
- Get window geometry first: `xdotool getwindowgeometry <WINDOW_ID>`
- Convert: `window_rel_x = screen_x - window_position_x`
- Vision models give approximate coordinates; expect 2-4 attempts to hit small targets
- **Page resizing helps**: ask user to make the window smaller so elements are closer together
- When clicking icons in a table row, aim for the icon's center, not the text

## Common Pitfalls

- **Vision model reads code examples as real keys**: when a page has both masked keys AND code snippets, the vision model may hallucinate by reading the example code as the real key. Ask explicitly "Kod örneğindeki değil, gerçek API key'i oku."
- **`mcp_local_secure_secure_vision` timeout (120s)**: the local vision tool can timeout on complex screenshots. For non-credential screenshots (API keys, page layout, icon positions), prefer `vision_analyze` — it's faster and the data isn't sensitive enough to require local processing. Reserve `mcp_local_secure_secure_vision` for password/card-number screenshots only.
- **`import` (ImageMagick) may not be installed**: on minimal servers, `import` command may be missing. Use `scrot` instead — it's lighter and works on bare X11. `xwd` is also available but produces XWD format that needs conversion.
- **Popup windows block clicks**: always `DISPLAY=:1 xdotool key Escape` first to dismiss browser "Save password?" or other modals
- **GNOME keyring popup**: appears as "Choose password for new keyring" — dismiss with Escape, it's unrelated to Bitwarden
- **Wrong window in foreground**: `wmctrl -l` to list, `xdotool windowactivate` to switch, then screenshot to confirm
- **`scrot` needs DISPLAY set**: always prefix with `DISPLAY=:1`
- **Click accuracy drops on large windows**: if clicks repeatedly miss the target, ask the user to resize the browser window smaller. Compact layouts make coordinate estimation more forgiving. The user can say "sayfa boyutunu küçülttüm" and the next click will likely hit.

## Security Note

The credential passes through the vision_analyze tool (qwen-vision on Pollinations) when reading screenshots.
For maximum security, prefer the local-secure vision tool (`mcp_local_secure_secure_vision`) for screenshots containing passwords.
For API keys (lower sensitivity), vision_analyze is acceptable since the key never enters primary model context directly — only the vision model's text analysis does.
