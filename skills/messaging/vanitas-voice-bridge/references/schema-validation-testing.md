# Deepgram Schema Validation — Testing Think Configs

**Source:** Conversation 2026-06-15 — debugging `UNPARSABLE_CLIENT_MESSAGE`

## Quick Schema Test Pattern

When debugging Deepgram Settings parse errors, test `think` configs directly against the WebSocket API:

```python
import asyncio, json, os, websockets

async def test_think(think_config, description="test"):
    """Returns True if SettingsApplied, False if Error"""
    DG_KEY = "your-deepgram-api-key"
    url = "wss://api.eu.deepgram.com/v1/agent/converse"
    
    settings = {
        "type": "Settings",
        "audio": {
            "input": {"encoding": "linear16", "sample_rate": 24000},
            "output": {"encoding": "linear16", "sample_rate": 24000},
        },
        "agent": {
            "listen": {"provider": {"type": "deepgram", "model": "nova-3", "language": "tr"}},
            "think": think_config,
            "speak": {"provider": {"type": "deepgram", "model": "aura-2-athena-en"}},
            "greeting": "Test",
        },
    }
    
    async with websockets.connect(
        url, extra_headers={"Authorization": f"Token {DG_KEY}"}, close_timeout=5
    ) as ws:
        await ws.send(json.dumps(settings))
        async for raw in ws:
            if isinstance(raw, bytes): continue
            data = json.loads(raw)
            if data["type"] == "SettingsApplied":
                print(f"  ✅ {description}: PASS")
                return True
            if data["type"] == "Error":
                print(f"  ❌ {description}: {data.get('description', data)}")
                return False
    return False

# Usage:
asyncio.run(test_think(
    {"provider": {"type": "groq", "model": "llama-3.3-70b-versatile"}},
    "BYO groq + endpoint"
))
```

## Schema Discovery via .md Endpoint

Deepgram docs expose clean markdown schemas at `https://developers.deepgram.com/reference/voice-agent/voice-agent.md`:

```bash
# Find ThinkSettingsV1 schema
curl -s 'https://developers.deepgram.com/reference/voice-agent/voice-agent.md' | grep -A 30 'ThinkSettingsV1:'

# Find provider-specific schemas
curl -s '...' | grep -A 20 'OpenAiThinkProvider:'
curl -s '...' | grep -A 20 'GroqThinkProvider:'

# Find endpoint schema
curl -s '...' | grep -A 15 'ThinkSettingsV1Endpoint:'
```

## Schema Findings (2026-06-15)

| Field | In Schema? | Notes |
|-------|-----------|-------|
| `think.provider` | ✅ REQUIRED | Must have `type` + `model` |
| `think.provider.type` | ✅ REQUIRED | One of: open_ai, groq, google, anthropic, nvidia, aws_bedrock |
| `think.provider.model` | ✅ REQUIRED | For ALL provider types, even BYO |
| `think.provider.temperature` | ✅ Optional | Valid field |
| `think.endpoint` | ✅ Optional | Has `url` (string) + `headers` (object of strings) |
| `think.prompt` | ✅ Optional | String field |
| `think.context_length` | ✅ Optional | Only configurable with custom endpoint |
| `think.functions` | ✅ Optional | Array of function definitions |
| `think.timeout` | ❌ NOT IN SCHEMA | Adding causes parse error |
| `agent.language` | ⚠️ Deprecated | Use `listen.provider.language` instead |
| `agent.think` (array) | ✅ Valid | `oneOf`: single object OR array (fallback chain) |
