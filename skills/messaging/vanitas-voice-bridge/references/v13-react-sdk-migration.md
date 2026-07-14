# v13 — Soniox React SDK Migration Plan

**Created:** 2026-07-01
**Supersedes:** v12-stage3-plan.md, references/v13-nextjs-ui.md (Web Speech TTS plan)

## Why React SDK Instead of v12 + Web Speech

Edel shared two news items (1 Temmuz 2026):
1. **Soniox `useRecording()` hook** — One hook for browser STT, `finalText`/`partialText` reactive state
2. **Soniox `useTts()` hook** — WebSocket TTS management, chunk streaming

Combined, these make v12 (soniox-js + WS text + Python server) and the old v13 plan (Web Speech API) obsolete.

## Architecture Comparison

### v11 (current): vanitas_ses.py
```
Phone → PCM binary WS → Server (vanitas_ses.py :8765)
  → Soniox Python SDK STT (300 lines)
  → Audio buffer + utterance detection (80 lines)
  → LLM proxy Groq/Hermes (150 lines, 3-retry, timeout chain)
  → Edge TTS + MP3 encoding (50 lines)
  → MP3 binary WS → Phone speaker
```
**Total: ~790 lines Python, all on server.**

### v13 (target): Next.js + Soniox React SDK
```
Phone → useRecording() → Soniox API (direct STT)
  → finalText → POST /api/chat → Groq streaming
  → response text → useTts() → Soniox TTS → Phone speaker
```
**Total: ~50 lines Next.js API routes. No server STT/TTS/WS.**

## Key Benefits

| Aspect | v11 | v13 |
|--------|-----|-----|
| Server code | 790 lines | ~50 lines |
| Audio on server | PCM buffer, silence timer | None |
| WebSocket | Binary + text | None |
| Deadlock risk | reply_lock, utterance_queue, timeout chain | None (React state) |
| STT location | Server | Browser (direct to Soniox) |
| TTS | Edge TTS (Python) | Soniox TTS (browser useTts) |
| UI | Inline HTML+JS | Next.js + Tailwind |
| Voiceprint | Server-side | Not needed |

## Open Questions

1. **Soniox TTS Turkish quality** — Needs testing. Edge TTS EmelNeural baseline.
2. **Soniox TTS pricing** — Edel has $2 balance. Need to estimate monthly cost.
3. **Barge-in support** — Does `useTts()` support interrupt? If not, need workaround.
4. **React SDK maturity** — New release, unknown edge cases.

## Migration Steps (when Edel approves)

1. `create-next-app vanitas-web` with TypeScript + Tailwind
2. Install: `npm install @soniox/client` (React SDK)
3. Create `/api/tmp-key` — temporary Soniox API key endpoint (300s)
4. Create `/api/chat` — Groq streaming proxy (llama-4-scout-17b)
5. Implement `useRecording()` in page component
6. Implement `useTts()` for TTS output
7. Add token middleware (security)
8. Test with cloudflared tunnel

## Edel's Instructions

- Soniox hesabında $2 bakiye var, arttırılabilir (ucuz)
- "test etmeye başlarız" — onay verdi
- Bug'lar için sub-agent'lar kullanılabilir
- Claude Code alternatifi düşünülüyor (Anthropic API key gerekli, henüz yok)
