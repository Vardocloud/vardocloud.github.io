# Meet-Bot Debugging Reference

## Common Crash: "Target page, context or browser has been closed"

**Location**: bot-meet.js:79 — `await page.waitForTimeout(5000)` after clicking join

**Root Causes**:
1. Meeting link expired (Google shows 400 Bad Request → page context dies)
2. Meeting hasn't started yet (Google redirects to "meeting doesn't exist")
3. Auth session expired (Google forces re-login)
4. Google security prompt (captcha/phone verification) appears and page navigates away

**Debug Sequence**:
```bash
# 1. Check if monitor is running
curl -s http://localhost:8766

# 2. Check auth status (must be ✅)
cd /home/ubuntu/meet-bot && node test-auth.js

# 3. Check screenshot if available
cat /home/ubuntu/meet-bot/auth-screenshots/current.png | base64 | head -c 100  # or use vision_analyze

# 4. Check auth log
cat /home/ubuntu/meet-bot/auth-screenshots/auth.log

# 5. Check if Playwright/Chromium processes are stale
ps aux | grep -E "chromium|playwright" | grep -v grep
```

## Test Meeting Creation

When creating a test meeting on Google Calendar:
- Must have actual Google Meet link (automatic for calendar events)
- Must be currently active or start within next few minutes
- After meeting ends, the link becomes invalid
- Recreating the event generates a new link

## Auth File Location
- `/home/ubuntu/meet-bot/auth-data/google-auth.json`
- Created by: `node setup-auth-v2.js` (uses Xvfb + web control panel at :8767)
- Test with: `node test-auth.js`

## Related Files
- `start-cdp.js` — runs Xvfb + Chromium for persistent browser context (port 9222)
- `bot-meet.js` — handles actual Meet joining and audio capture
- `bot.js` — main controller, spawns server + browser processes
- `server.js` — WebSocket + HTTP server for transcript streaming