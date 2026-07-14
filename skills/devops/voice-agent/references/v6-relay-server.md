# Working v6 Voice Agent Relay Server

Minimal relay server using Deepgram's Voice Agent API with Mistral as custom LLM.

**Date:** 2026-06-14
**Status:** Working — tested with 3 consecutive exchanges on first session
**File:** `/home/ubuntu/voice-agent-venv/voice_agent_server.py` (v6)

## Key Configuration Points

1. **Deepgram Agent endpoint:** `wss://agent.deepgram.com/v1/agent/converse`
2. **LLM provider type MUST be `"open_ai"`** (not `"custom"` or `"mistral"`). Deepgram uses this internally to construct OpenAI-format requests.
3. **LLM endpoint:** `https://api.mistral.ai/v1/chat/completions` (Mistral's API is OpenAI-compatible)
4. **`temperature` is a top-level think field**, not inside `provider` — putting it inside provider caused "Error parsing client message"
5. **Browser sends raw PCM** (16-bit linear, 24000 Hz, mono, little-endian) as binary WebSocket frames
6. **Deepgram sends audio back** as binary frames (WAV container) — just forward to browser

## Server Structure

```python
# ── Settings payload ──
settings = {
    "type": "Settings",
    "audio": {
        "input": {"encoding": "linear16", "sample_rate": 24000},
        "output": {"encoding": "linear16", "sample_rate": 24000, "container": "wav"}
    },
    "agent": {
        "listen": {"provider": {"type": "deepgram", "model": "nova-3", "language": "en"}},
        "think": {
            "provider": {"type": "open_ai", "model": "mistral-small"},
            "endpoint": {
                "url": "https://api.mistral.ai/v1/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {mistral_key}",
                    "Content-Type": "application/json"
                }
            },
            "temperature": 0.8,
            "prompt": "You are Vanitas, Edel's personal AI assistant. Be warm, friendly, and VERY concise. 2-3 sentences max..."
        },
        "speak": {"provider": {"type": "deepgram", "model": "aura-2-athena-en"}}
    }
}

# ── WebSocket handler ──
async with ws_lib.connect(
    "wss://agent.deepgram.com/v1/agent/converse",
    additional_headers={"Authorization": f"Token {dg_key}"}
) as dg_ws:
    await dg_ws.send(json.dumps(settings))
    welcome = await dg_ws.recv()  # Must consume welcome before relay starts
    
    # Task 1: Browser PCM → Deepgram (binary forward)
    # Task 2: Deepgram events → Browser (parse & forward)
    # asyncio.wait with FIRST_COMPLETED
```

## Agent Events Handled

| Event Type | Meaning | Action |
|-----------|---------|--------|
| `ConversationText` | User or assistant text | Forward to browser UI |
| `AgentThinking` | LLM processing | Show "Thinking..." status |
| `AgentSpeaking` | TTS generating | Show "Speaking..." status |
| `AgentAudioDone` | TTS audio complete | Show "Listening..." status |
| `UserStartedSpeaking` | User began talking | Show "Listening..." status |
| `SettingsApplied` | Config accepted | Log only |
| `Error` | Agent error | Log + forward to browser |

## Required Environment Variables

- `DEEPGRAM_API_KEY` — from Deepgram console
- `MISTRAL_API_KEY` — from Mistral console (must have chat completions access)

## Browser Client Requirements

- `getUserMedia({audio: {echoCancellation: true, sampleRate: 24000, channelCount: 1}})`
- WebSocket binary mode: `ws.binaryType = 'arraybuffer'`
- `ScriptProcessorNode` with 4096 buffer → `Int16Array` → `ws.send(pcm.buffer)`
- **CRITICAL:** ScriptProcessorNode MUST have an output connection. Use silent GainNode (gain=0 → destination) to satisfy Chrome without echo.
- WAV header construction for received audio: 44-byte header + raw PCM

## What NOT To Do

- Do NOT put `max_tokens` inside the provider object — causes "Error parsing client message"
- Do NOT connect ScriptProcessorNode directly to `ctx.destination` — creates echo loop
- Do NOT skip consuming the Welcome message before starting the relay loop
- Do NOT use `interim_results=false` on the STT URL (for manual pipeline) — this is for the Agent API, which handles turn detection internally
- Do NOT use Pollinations as the LLM endpoint — the Agent think system had parsing issues; Mistral worked cleanly
