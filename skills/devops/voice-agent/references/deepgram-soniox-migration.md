# Deepgram → Soniox Migration (Code-Level)

Step-by-step diff for replacing Deepgram with Soniox in voice agent codebase.

## Variable Renames

- `DEEPGRAM_API_KEY` → `SONIOX_API_KEY` (read from `~/.hermes/soniox_api_key.txt`)
- `dg_ws` → `soniox_ws`
- `dg_task` → `soniox_task`
- `process_deepgram()` → `process_soniox()`
- `connect_deepgram()` → `connect_soniox()`

## Connect Function

**Old (Deepgram):** Auth via header. Config in URL query params.  
**New (Soniox):** Auth in JSON body. Config sent as first WebSocket message after connect.

```python
# Soniox — JSON config after connect, auth in body
soniox_ws = await ws_lib.connect(
    "wss://stt-rt.soniox.com/transcribe-websocket"
)
config = {
    "api_key": SONIOX_API_KEY,
    "model": "stt-rt-v5",
    "audio_format": "pcm_s16le",
    "sample_rate": 16000,
    "num_channels": 1,
    "language_hints": ["tr"],
    "enable_endpoint_detection": True,
    "max_endpoint_delay_ms": 1000
}
await soniox_ws.send(json.dumps(config))
```

## Process Function

**Old (Deepgram):** Nested `channel.alternatives[0].transcript`, `speech_final` flag.  
**New (Soniox):** Flat `tokens[]` array, `final` flag.

```python
# Soniox — flat tokens array
async for raw in soniox_ws:
    msg = json.loads(raw)
    tokens = msg.get("tokens", [])
    is_final = msg.get("final", False)
    if tokens:
        transcript = " ".join(t.get("text", "") for t in tokens).strip()
```

## Response Handling

**Deepgram:** `msg["type"] == "Results"` → `msg["channel"]["alternatives"][0]["transcript"]`  
**Soniox:** `msg.get("tokens", [])` → `" ".join(t["text"] for t in tokens)`

No intermediate type check needed — tokens appear in every response.

## Speech End Detection

**Deepgram:** `speech_final: true` flag → flush utterances.  
**Soniox:** Endpoint detection configured via `enable_endpoint_detection` + `max_endpoint_delay_ms`. Final tokens arrive with `"final": true`. No explicit speech_final handling needed.

## Stream Close

**Deepgram:** `{"type": "CloseStream"}` JSON message.  
**Soniox:** Empty binary frame `b''`.

## Audio Format

Both use identical format: PCM 16-bit signed little-endian, 16kHz, mono. No format conversion needed when switching providers.

## Verified Working (June 2026)

- ✅ Soniox WebSocket connects successfully
- ✅ Config accepted, no auth errors
- ✅ Audio forwarding works (PCM 16kHz, 16-bit, mono)
- ❌ Balance required — zero balance = `organization_balance_exhausted` (HTTP 402)
- ⚠️ Turkish transcription quality not yet verified (pending balance deposit)

## Reference Files

- Soniox API details: `sensitive-data-pipeline/references/soniox-api-integration.md`
- STT provider comparison: `voice-agent/references/stt-providers.md`
