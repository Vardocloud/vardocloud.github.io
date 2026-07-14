# Soniox WebSocket STT Integration — 17 June 2026

## Endpoint & Auth
- **URL:** `wss://stt-rt.soniox.com/transcribe-websocket` (verified in SDK v2.6.0 `client.py:35`)
- **Auth:** API key sent as first JSON message (NOT as HTTP header)
- **SDK reference:** `soniox==2.6.0`, `RealtimeSTTConfig.build_payload(key)`

## Config Message (First WebSocket Message)
```json
{
  "api_key": "REDACTED",
  "model": "stt-rt-v5",
  "audio_format": "pcm_s16le",
  "sample_rate": 16000,
  "num_channels": 1,
  "language_hints": ["tr"],
  "enable_endpoint_detection": true,
  "max_endpoint_delay_ms": 1000
}
```

## Audio Streaming (After Config)
- Raw PCM s16le bytes, 16kHz, mono
- Each chunk: 8192 bytes (4096 samples × 2 bytes) from ScriptProcessorNode
- No container/header — raw samples only

## Response Format
```json
{
  "tokens": [
    {"text": "Mer", "is_final": false},
    {"text": "hab", "is_final": true},
    {"text": "a", "is_final": true}
  ],
  "final_audio_proc_ms": 1200,
  "total_audio_proc_ms": 1500,
  "finished": false
}
```

### Critical: Per-Token `is_final`
- Each TOKEN has `is_final` flag — NOT at message level
- `is_final: false` → provisional, may change/disappear
- `is_final: true` → confirmed, never repeated
- Mixed messages: some tokens final, some non-final in same response
- `finished: true` → session ending (final message)

### Special Tokens
- Space tokens: `{"text": " ", "is_final": true}` — separate words
- `TOKEN_TEXT_FIN = "<fin>"` — end of utterance marker
- `TOKEN_TEXT_END = "<end>"` — stream end marker

## Control Messages (Client → Server)
- `{"type": "finalize"}` — force pending tokens to final
- `{"type": "keepalive"}` — prevent timeout during silence
- `""` (empty string) — signal end-of-audio, close stream

## Error Handling
- `error_code` and `error_message` fields in response
- Session timeout: requires keepalive messages during pauses
- SDK implements background keepalive thread for paused sessions

## Token Concatenation for Turkish
Turkish subword tokenization produces partial words:
- "Merhaba" arrives as `["Mer", "hab", "a"]`
- Join with `"".join()` — NO spaces between tokens
- Space tokens (literal `" "`) handle word boundaries

## Accumulator Pattern (Deduplication)
```python
final_buffer = ""
for msg in soniox_messages:
    final_tokens = [t for t in msg.tokens if t.is_final]
    new_text = "".join(t.text for t in final_tokens)
    if new_text and not final_buffer.endswith(new_text):
        final_buffer += new_text
    current_transcript = final_buffer.strip()
```

Final tokens are CUMULATIVE — each message includes previously finalized tokens plus new ones. The `endswith` check prevents duplicate text.
