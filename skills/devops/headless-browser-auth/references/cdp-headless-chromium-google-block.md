# CDP Headless Chromium — Google "Couldn't Sign You In" Block

**Date confirmed:** 21 Jul 2026 (Chromium 149.0.7827.155 on Debian 13 Docker)

## What We Tried

### Setup
```bash
/usr/bin/chromium \
  --user-data-dir=/home/ubuntu/.hermes/chrome-profile \
  --remote-debugging-port=9222 \
  --no-first-run \
  --no-default-browser-check \
  --no-sandbox \
  --headless=new \
  --disable-gpu \
  --disable-dev-shm-usage \
  --disable-blink-features=AutomationControlled \
  --disable-features=TranslateUI,BlinkGenPropertyTrees \
  --window-size=1920,1080 \
  --disable-background-networking \
  --disable-sync \
  --disable-default-apps \
  --disable-extensions \
  --disable-component-update
```

### Result
- CDP connected successfully (port 9222)
- Navigation to Google sign-in works
- Typing email + clicking Next → **immediate rejection**
- Google shows: "Couldn't sign you in — This browser or app may not be secure"
- This happens BEFORE password entry — Google detects headless mode at the email stage

## What Didn't Work
- `--disable-blink-features=AutomationControlled` — no effect on Google's detection
- `--disable-features=TranslateUI,BlinkGenPropertyTrees` — no effect
- Switching flow (Gmail sign-in vs Gemini sign-in) — same rejection
- The `apt` package `chromium` on Debian is stock Chromium without anti-detection patches

## What DOES Work (from earlier sessions)
- **Xvfb + non-headless Chrome** — Google detects a real display; doesn't block
- **Camofox** (Firefox fork) — Google's detection targets Chromium specifically
- **VNC manual login** — human completes auth in real browser

## Recommendation
For automated Google auth on headless Docker: use Camofox (managed_persistence) for short-lived supervised sessions, or Xvfb+Chrome for longer unattended runs. Never use `--headless=new` for Google sign-in — it's a guaranteed dead end.
