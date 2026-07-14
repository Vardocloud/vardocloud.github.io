# Zoom Anti-Bot Detection (13 Haz 2026)

## Summary
Zoom's web client uses Google reCAPTCHA Enterprise that blocks all headless/automated Chrome instances from joining meetings. This applies to BOTH the browser tool Chrome and any custom Chrome instances.

## Error
"Automated bots aren't allowed to join this meeting."

## What Was Tried
1. Browser tool (port 9222, NotebookLM Chrome, full GPU, Windows UA) → Blocked
2. Multiple overlay/dialog dismissals → Blocked at Join
3. Native value setter for React inputs → Join validation passes, reCAPTCHA blocks

## Why It Fails
- Zoom checks `navigator.webdriver` flag
- Automated mouse/keyboard events detected
- Missing user gesture history
- reCAPTCHA Enterprise v3 score threshold exceeded

## What Would Work (but not built yet)
- Zoom Meeting SDK — legitimate app-based join
- Server-to-Server OAuth app + Meeting SDK Component
- Bot joins via Zoom's own SDK, not through browser automation

## ⚠️ Registration vs. Joining
This file covers **joining** a meeting (anti-bot blocked). For **webinar registration** (form filling, no anti-bot), see `references/zoom-webinar-registration.md`. Registration forms use React comboboxes but are automatable — the anti-bot only triggers when actually joining the meeting.
