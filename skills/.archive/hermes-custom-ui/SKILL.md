---
name: hermes-custom-ui
description: "Build mobile-friendly custom chat UIs connected to Hermes API via Python proxy"
version: 1.0.0
metadata:
  hermes:
    tags: [chat, ui, mobile, proxy, cors, frontend]
    category: messaging
---

# Hermes Custom Chat UI

Build a custom mobile-friendly chat interface that connects to Hermes API. Covers the proxy pattern that eliminates CORS issues, deployment steps, and known pitfalls.

## When to Use

- User wants a custom-branded chat UI (beyond Telegram / Open WebUI)
- Mobile-first design with character/artwork + chat layout
- Need same-origin API access to avoid CORS preflight problems
- Deploying on the same server as Hermes gateway

## Architecture

```
Browser (mobile) → Proxy :8880 → Hermes API :8642
                      ↑
            Serves static files
            Proxies chat requests internally
```

Single port, no CORS. Proxy handles auth server-side.

## Step 1: Expose Hermes API

Hermes API server listens on its configured host/port. By default it binds to loopback only. To accept external connections, set the host env var and restart.

Verify binding after restart — it should show the wildcard address, not loopback. If the process survives a graceful restart, force-kill it.

Open the firewall for the API port.

## Step 2: Create Python Proxy

Single Python server that serves static files AND proxies chat requests internally. This eliminates browser CORS issues entirely.

Template: `templates/proxy-server.py`

Design:
- Extends `http.server.SimpleHTTPRequestHandler`
- GET → static files from web directory
- POST `/api/chat` → forwards to Hermes API internally
- OPTIONS → returns permissive CORS headers
- Auth handled server-side (API key never reaches browser)

## Step 3: Create Mobile-First HTML UI

Layout pattern:
- Upper section (~42vh): character image, subtle float animation, sparkle effects
- Lower section: chat messages (scrollable) + text input + send button
- Dark purple theme, rounded bubbles, typing indicator
- Vanilla JS, no framework — lightweight

Template: `templates/mobile-chat-ui.html`

Chat JS fetches to `/api/chat` (same origin), no auth header needed. Conversation history tracked in-memory array.

## Step 4: Deploy

1. Create app directory, copy image + proxy script + HTML
2. Open firewall for proxy port
3. Start proxy in background
4. Access via Tailscale IP if not using public IP

## Mobile Keyboard Fix

When the input field is focused on mobile, the keyboard pushes the viewport up and the input can end up below the visible area. Fix with two techniques:

1. **`scrollIntoView` on focus** — after a 300ms delay (keyboard animation), scroll the input into view
2. **`visualViewport` resize listener** — dynamically adjust the messages container height when the keyboard changes the viewport

```js
inputEl.addEventListener('focus', () => {
    setTimeout(() => {
        inputEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 300);
});

if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', () => {
        const vh = window.visualViewport.height;
        messagesEl.style.maxHeight = (vh - headerH - inputH) + 'px';
    });
}
```

## Pitfalls

- **Graceful restart may not pick up env changes** — the gateway process can survive SIGTERM. `systemctl --user restart` may silently keep the old PID. Check binding with `ss -tlnp`. If PID unchanged and still on loopback, use `kill -9 <PID>` then `systemctl --user start hermes-gateway`. Wait 4 seconds before checking.
- **systemctl restart timeout** — the restart command can hang (10s+ timeout). It's normal. Check `ss -tlnp` after to confirm the new process bound correctly.
- **CORS preflight returns 403** — Hermes API server does not set CORS headers. DO NOT try to add them. Use the same-origin proxy pattern (Step 2) instead.
- **Tailscale dependency** — if not exposing via public IP, user's device must have Tailscale connected and online.
- **API auth** — if the API server requires a key, the proxy injects it server-side. The browser never sees it.

## Templates

- `templates/proxy-server.py` — Python proxy that serves static files + proxies /api/chat
- `templates/mobile-chat-ui.html` — Mobile-first chat UI with character image, dark theme, animations
