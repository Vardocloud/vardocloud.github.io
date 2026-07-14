# Soniox API Integration (June 2026)

Provider: Soniox — multilingual speech-to-text platform. Turkish native-speaker accuracy claimed.

## Account Setup
- **Signup**: `app.soniox.com` → email + password → verify email
- **Login (console)**: `console.soniox.com/signin` — password-only (email entered on prior step)
- **Login (OAuth2 backend)**: `mobile-app-backend.soniox.com/accounts/login/` — Django OAuth2, has CSRF tokens, email+password form. This is DIFFERENT from the console signin — credentials that work on console may be silently rejected here due to bot detection or IP filtering.
- **Dashboard**: `console.soniox.com/org/<org-id>` — shows balance, projects, API endpoints

## Pricing (June 2026)
- STT: $0.12/hour
- Estimated monthly: ~$0.90 for 30 min/day usage
- Free credits: NONE — requires payment method even for testing
- Monthly limit default: $1,000.00
- **Error on zero balance**: `organization_balance_exhausted` (HTTP 402) — blocks all API calls

## API Endpoints

### REST
- STT REST: `https://api.soniox.com/v1`
- TTS REST: `https://tts-rt.soniox.com/tts`

### WebSocket (Streaming)
- STT WebSocket: `wss://stt-rt.soniox.com/transcribe-websocket`
- TTS WebSocket: `wss://tts-rt.soniox.com/tts-websocket`

## Authentication
- API key goes in JSON config message (NOT in headers)
- Config sent as first WebSocket message AFTER connect, BEFORE audio
- Format:
```json
{
  "api_key": "<SONIOX_API_KEY>",
  "model": "stt-rt-v5",
  "audio_format": "pcm_s16le",
  "sample_rate": 16000,
  "num_channels": 1,
  "language_hints": ["tr"],
  "enable_endpoint_detection": true,
  "max_endpoint_delay_ms": 1000
}
```
- `audio_format: "auto"` also works but raw PCM gives more control

## Turkish Support
✅ All 11 Soniox models support Turkish (60 languages total):
- `stt-rt-v5` (recommended for real-time)
- `stt-rt-v4`, `stt-rt-v3`
- `stt-async-v5`, `stt-async-v4`, `stt-async-v3`
- `stt-rt-preview`, `stt-rt-preview-v2`
- `stt-rt-v3-preview`
- `stt-async-preview-v1`

## Response Format (WebSocket)
```json
{
  "tokens": [
    {"text": "Merhaba", "start_ms": 600, "end_ms": 800},
    {"text": "dünya", "start_ms": 900, "end_ms": 1100}
  ],
  "final": true,
  "result_index": 0,
  "final_audio_proc_ms": 1200,
  "total_audio_proc_ms": 3500
}
```
- `tokens[]`: array of word tokens with timing
- `final`: true for complete utterances, false for interim
- Build transcript: `" ".join(t["text"] for t in tokens)`
- No `speech_final` equivalent (unlike Deepgram) — use `final` + `endpoint_detection` instead

## Error Format
```json
{
  "tokens": [],
  "error_code": 402,
  "error_type": "organization_balance_exhausted",
  "error_message": "Organization balance exhausted. Please either add funds manually or enable autopay.",
  "request_id": "..."
}
```

## Voice Agent Integration Pattern
Replacing Deepgram with Soniox in `voice_agent_v10_8.py`:
1. Connect WebSocket to `wss://stt-rt.soniox.com/transcribe-websocket`
2. Send JSON config (NOT auth header)
3. Stream audio as binary frames (PCM 16-bit LE, 16kHz, mono)
4. Parse responses: `tokens[]` → transcript, `final` → utterance boundary
5. Send empty binary frame to end stream gracefully
6. Soniox sends final response and closes connection

### Key differences from Deepgram:
| Feature | Deepgram | Soniox |
|---|---|---|
| Auth | Header: `Authorization: Token <key>` | JSON body: `"api_key": "<key>"` |
| Config | URL query params | JSON message after connect |
| Interim | `is_final: false` in Results | `final: false` |
| Speech end | `speech_final: true` | `final: true` + endpoint detection |
| Turkish accuracy | Poor (garbage output) | Claimed native-speaker (untested) |
| Cost | Free tier available | $0.12/hr, no free tier |
| Endpoint | `api.deepgram.com/v1/listen` | `stt-rt.soniox.com/transcribe-websocket` |

## Known Issues
- **Balance requirement**: even for testing, a payment method or prepaid balance is needed. Error 402 blocks all transcription attempts.
- **Login endpoint confusion**: `console.soniox.com/signin` vs `mobile-app-backend.soniox.com/accounts/login/` — same credentials, different behavior. Console login succeeded where OAuth2 backend silently rejected (likely bot detection on datacenter IP).
- **WebSocket config must arrive before audio**: if audio is sent before config is processed, connection may close silently.
