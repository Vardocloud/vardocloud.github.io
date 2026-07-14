# Soniox WebSocket API v2 — Token Format & Integration Details

## API Endpoint
```
wss://stt-rt.soniox.com/transcribe-websocket
```
Source: Soniox Python SDK v2.6.0 `client.py` line 35: `_DEFAULT_WEBSOCKET_BASE_URL`

## Connection Flow

1. Connect WebSocket to the endpoint above
2. Send config as FIRST JSON message (not as headers or query params)
3. Send raw PCM audio bytes for subsequent messages
4. Receive JSON events in response

## Config Format (First Message)

```json
{
  "api_key": "SONIOX_API_KEY",
  "model": "stt-rt-v5",
  "audio_format": "pcm_s16le",
  "sample_rate": 16000,
  "num_channels": 1,
  "language_hints": ["tr"],
  "enable_endpoint_detection": true,
  "max_endpoint_delay_ms": 1000
}
```

All config fields from SDK's `RealtimeSTTConfig` (soniox/types/realtime.py):
- `api_key`: Required. Sent as JSON field, not header.
- `model`: "stt-rt-v5" (real-time v5 model)
- `audio_format`: "auto" for containers, "pcm_s16le" for raw PCM
- `sample_rate`: Required for raw formats
- `num_channels`: Required for raw formats
- `language_hints`: ISO language codes array
- `language_hints_strict`: bool, strongly bias toward hints
- `enable_endpoint_detection`: bool
- `max_endpoint_delay_ms`: 500-3000ms, default 2000ms
- `endpoint_sensitivity`: -1.0 to 1.0, default 0.0 (v5 model only)
- `enable_speaker_diarization`: bool
- `enable_language_identification`: bool
- `context`: Additional context for accuracy
- `translation`: Translation config
- `client_reference_id`: 256-char max tracking ID

Build payload: `config.model_copy(update={"api_key": key}).model_dump(exclude_none=True)`

## Response Format — RealtimeEvent

```python
class RealtimeEvent(BaseModel):
    tokens: list[Token] = []
    final_audio_proc_ms: int | None = None
    total_audio_proc_ms: int | None = None
    finished: bool = False
    error_code: int | None = None
    error_message: str | None = None
```

## Token Format

```python
class Token(BaseModel):
    text: str                    # "Mer", "haba", " ", "nasılsın"
    start_ms: int | None = None  # Relative to audio start
    end_ms: int | None = None
    confidence: float | None = None  # 0.0 to 1.0
    is_final: bool | None = None     # ⭐ PER-TOKEN, not per-message!
    speaker: str | None = None       # If diarization enabled
    language: str | None = None      # If language ID enabled
    translation_status: str | None = None
    source_language: str | None = None
```

## CRITICAL: is_final is PER-TOKEN

This was the #1 bug in our implementation. The Soniox v2 API places `is_final` on each Token
object, NOT as a top-level `"final"` field on the message. Checking `msg.get("final", False)`
at the message level will ALWAYS return False.

### Token Evolution Pattern

Non-final tokens can appear, change, disappear, or be replaced. Final tokens are sent once
and never repeated. However, final tokens can appear CUMULATIVELY in subsequent messages.

Example evolution of "How are you doing?":
```
Message 1: [{"text": "How", "is_final": false}, {"text": "'re", "is_final": false}]
Message 2: [{"text": "How", "is_final": false}, {"text": " ", "is_final": false}, {"text": "are", "is_final": false}]
Message 3: [{"text": "How", "is_final": true}, {"text": " ", "is_final": true}, {"text": "are", "is_final": false}]
Message 4: [{"text": "are", "is_final": true}, {"text": " ", "is_final": true}, {"text": "you", "is_final": true}]
...
```

### Correct Handling (Python)

```python
final_buffer = ""  # Cumulative final transcript

async for raw in soniox_ws:
    msg = json.loads(raw)
    tokens = msg.get("tokens", [])
    if not tokens:
        continue
    
    final_tokens = [t for t in tokens if t.get("is_final")]
    nonfinal_tokens = [t for t in tokens if not t.get("is_final")]
    
    # Show interim instantly (non-final = guess)
    if nonfinal_tokens:
        interim = "".join(t["text"] for t in nonfinal_tokens).strip()
        if interim:
            await safe_send({"type": "interim", "text": interim})
    
    # Build cumulative final transcript — deduplicate
    if final_tokens:
        new_text = "".join(t["text"] for t in final_tokens)
        if new_text and not final_buffer.endswith(new_text):
            final_buffer += new_text
        
        transcript = final_buffer.strip()
        if transcript:
            await safe_send({"type": "transcript", "text": transcript})
```

### Key Rules

1. **Never use `" ".join()`** — Soniox uses subword tokenization. Turkish words like "Merhaba"
   come as ["Mer", "hab", "a"]. `" ".join()` produces "Mer hab a". Use `"".join()`.
   
2. **Deduplicate with prefix check** — Final tokens are cumulative. Second message containing
   final tokens will include previously finalized tokens. Use `endswith()` or track
   last-processed index.

3. **Flush timing for Turkish** — `delayed_flush(2.5)` seconds. The 0.8 second default is
   too short for Turkish conversational pacing — the LLM starts responding before the user
   finishes their sentence.

4. **Spacing tokens** — Soniox includes " " (space) tokens between words. When using `"".join()`,
   these naturally form proper spacing.

## Control Messages

```json
{"type": "finalize"}   // Force all pending tokens to final status
{"type": "keepalive"}  // Prevent timeout during long silences
{"type": "CloseStream"} // Graceful close (or send empty string "")
```

## Connection Keepalive

For sessions with long periods of silence, implement keepalive to prevent timeout.
The SDK sends `{"type": "keepalive"}` every `KEEP_ALIVE_INTERVAL_SEC` seconds
(default from SDK constants).

## Key Differences from Deepgram

| Feature | Deepgram | Soniox v2 |
|---------|----------|-----------|
| Auth | Header: `Authorization: Token <key>` | JSON body: `"api_key"` |
| Config | URL query params | First JSON message |
| is_final | `is_final: false` on message | `is_final` on EACH token |
| Speech end | `speech_final: true` | Endpoint detection + `finished: true` |
| Language | `language=multi` in URL | `language_hints` in config |
| Interim | `is_final: false` tokens | Non-final tokens (`is_final: false`) |
