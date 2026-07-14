---
name: ai-game-companion
description: AI vision-based game companion — watch, track, and comment on games in real-time
triggers: [okusun, takip etsin, oyun izle, hikaye, scene sahne, dialog, konuşma, karakter]
owner: Edel
status: active
---

# AI Game Companion

Use when: Edel wants an AI to watch/track a game in real-time — story progression, dialog, scene changes, turn-by-turn events.

Trigger: "okusun", "takip etsin", "oyun izle", "hikaye", "scene sahne", "karakter konuşması"

## Architecture

```
Windows PC (Game)
    ↓ screenshot per turn/scene
    ↓ HTTP POST (requests)
    ↓
Hermes Server (Flask/FastAPI endpoint)
    ↓
Pollinations Qwen VL (vision analysis)
    ↓
Story log + Telegram reply (text/voice)
```

**Key constraints:**
- PC is external to server (not same LAN) — no direct streaming
- PC-side: `mss` or `PIL` for screenshot, `requests` for HTTP
- Server-side: simple Flask endpoint receives image, calls vision, logs
- Vision model: Pollinations Qwen VL Plus (user preference over gemini)

## Workflow

1. **Clarify the use case FIRST** — don't jump to tools
   - "Anlık yardım mı, hikaye takibi mi, yoksa sürekli etkileşim mi?"
   - Anlık = screenshot + send, no streaming needed
   - Hikaye takibi = per-turn or per-scene capture, not real-time

2. **MVP first** — 5-line Python on PC + Flask endpoint on server
   - Verify connectivity works before building pipeline
   - Use mss (fast, lightweight) over PIL

3. **Scene detection** — pixel diff OR timer-based
   - Turn-based games: timer (every 3-5 sec) or explicit trigger
   - Pixel diff: compare current frame to previous, trigger on threshold

4. **Build story log** — chronological record of all analyzed frames
   - Store in session or file, append each analysis
   - Purpose: track narrative progression across sessions

## Edel's Preferences
- Short, direct responses — no preamble
- Plan first, then execute
- Prefers Telegram for updates
- OK with emojis in messages

## Pitfalls
- **Don't recommend Parsec** for Epic games — Epic has no Remote Play feature
- **Don't assume same LAN** — PC and server are typically external to each other
- **Latency is real** — vision + analysis = ~10-30 sec. Set expectations: "okuyup yorumlar" is near-realtime, not eşzamanlı
- **Don't over-research before confirming use case** — user will correct anyway
- **Verify recommendations before stating them as facts** — Edel called out Parsec certainty

## Tech Stack
- PC: Python 3 + mss + requests
- Server: Flask endpoint (or existing Hermes webhook)
- Vision: Pollinations Qwen VL Plus via `/v1/chat/completions` with vision input
- Delivery: Telegram text/voice

---

**Reference:** `references/pollinations-vision.md` for API details