# Deepgram Voice Agent API Testing Without Audio

## Why Direct Testing
Iterating on Deepgram settings via the browser test page is slow: you need a phone, microphone, HTTPS tunnel, and manual speech each time. Direct WebSocket testing with Python lets you test settings, prompts, and TTS providers in seconds.

## Key Endpoint
```
wss://api.eu.deepgram.com/v1/agent/converse
```
Header: `Authorization: Token <DEEPGRAM_API_KEY>`

## Testing Think Configs (Schema Validation)
The most common failure is Deepgram rejecting settings with `UNPARSABLE_CLIENT_MESSAGE`. Test different `think` configs to find what the schema accepts:

```python
async def test_think_config(think_config):
    settings = {
        "type": "Settings",
        "audio": {...},
        "agent": {
            "listen": {"provider": {"type": "deepgram", "model": "nova-3", "language": "tr"}},
            "think": think_config,
            "speak": {"provider": {"type": "deepgram", "model": "aura-2-athena-en"}},
        },
    }
    # Connect, send settings, check for SettingsApplied vs Error
```

### Test Results (2026-06-15)
| Config | Result |
|--------|--------|
| `open_ai` + model + NO endpoint | ✅ SettingsApplied |
| `open_ai` + NO model + endpoint | ❌ UNPARSABLE |
| `open_ai` + model + endpoint | ❌ UNPARSABLE |
| `groq` + NO model + endpoint | ❌ UNPARSABLE |
| `groq` + model + endpoint | ✅ SettingsApplied |
| `groq` + model + NO endpoint | ❌ UNPARSABLE |

**Conclusion:** `groq` provider REQUIRES both `model` AND `endpoint`. `open_ai` provider REQUIRES `model` and REJECTS `endpoint`.

## Testing LLM Chain (InjectUserMessage)
Once settings are accepted, test the full LLM chain without real audio:

```python
# After SettingsApplied...
inject = {"type": "InjectUserMessage", "content": "Merhaba Vanitas, nasilsin?"}
await ws.send(json.dumps(inject))

# Read ConversationText from assistant
# Count audio chunks to verify TTS
```

This verifies:
- Deepgram → endpoint → proxy → Hermes → Vanitas → response
- TTS audio generation (byte count)
- Response content (personality check)

## Testing TTS Quality
To test TTS without listening, verify:
1. SettingsApplied received (provider accepted)
2. Audio chunks arrive (non-zero byte count)
3. No `FAILED_TO_SPEAKE` error
4. No empty Warnings before error

## DEEPGRAM_API_KEY Access
```bash
# From voice-agent-venv .env
grep DEEPGRAM_API_KEY /home/ubuntu/voice-agent-venv/.env | cut -d= -f2
```
Or set as environment variable in the Python test script.
