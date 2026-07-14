# Deepgram Streaming Model Compatibility (WebSocket)

## Working Configurations (Tested 2026-06-16)

| Model | Language | WebSocket? | Notes |
|-------|----------|-----------|-------|
| `nova-2` | `language=tr` | ✅ Works | Proven Turkish accuracy. Current fallback. |
| `nova-2` | (auto) | ✅ Works | Auto-detect works, slightly less accurate for Turkish |
| `nova-3` | (auto) | ✅ Works | Better accuracy than nova-2, Turkish auto-detected |
| `nova-3` | `language=tr` | ❌ HTTP 405 | Explicit language rejected on WS streaming |
| `whisper-large` | any | ❌ HTTP 405 | NOT available on WebSocket streaming endpoint |
| `whisper-medium` | any | ❌ HTTP 405 | Same — whisper models are REST-only |

## Discovery Method (2026-06-16)

1. `nova-2` + `language=tr` → working for days ✅
2. User reports Turkish accuracy issues → try `whisper-large` → HTTP 405 ❌
3. Docs show `whisper-large` exists but only on REST `/v1/listen` endpoint, not WebSocket
4. Docs show `nova-3` supports Turkish → try `nova-3` + `language=tr` → HTTP 405 ❌
5. Remove `language=tr` → `nova-3` connects successfully ✅
6. Nova-3 auto-detects Turkish correctly

## Root Cause

- **Whisper models**: Deepgram Whisper (whisper-large, whisper-medium, whisper-small) is available ONLY on the REST pre-recorded endpoint (`POST /v1/listen`). The WebSocket streaming endpoint does NOT support whisper models.
- **Nova-3 + language=tr**: Nova-3's multilingual mode uses `language=multi`. Explicit single-language codes may conflict with the model's internal language routing, causing HTTP 405 on WebSocket handshake.

## Recommendation

For Turkish voice agents:
1. **Primary**: `model=nova-3` WITHOUT language parameter (auto-detect) — best accuracy
2. **Fallback**: `model=nova-2&language=tr` — proven reliable, slightly lower accuracy
3. **Never**: `whisper-*` on WebSocket, `nova-3&language=tr` on WebSocket
