# Deepgram Voice Agent — Settings Schema & Provider Options

> Tested June 2026 with Deepgram Voice Agent API v1
> WebSocket endpoint: `wss://agent.deepgram.com/v1/agent/converse`

## Full Settings JSON

```json
{
  "type": "Settings",
  "audio": {
    "input": {
      "encoding": "linear16",
      "sample_rate": 24000
    },
    "output": {
      "encoding": "linear16",
      "sample_rate": 24000,
      "container": "wav"
    }
  },
  "flags": {
    "history": true
  },
  "agent": {
    "listen": {
      "provider": {
        "type": "deepgram",
        "model": "nova-3"
      }
    },
    "think": {
      "provider": {
        "type": "open_ai",
        "model": "deepseek-chat"
      },
      "endpoint": {
        "url": "https://api.deepseek.com/v1/chat/completions",
        "headers": {
          "Authorization": "Bearer <TOKEN>",
          "Content-Type": "application/json"
        }
      },
      "prompt": "System prompt text here"
    },
    "speak": {
      "provider": {
        "type": "deepgram",
        "model": "aura-2-athena-en"
      }
    }
  }
}
```

## STT Providers (listen)

| Type | Model | Language Support | Notes |
|---|---|---|---|
| `deepgram` | `nova-3` | Multilingual (incl. Turkish) | Recommended, fast |
| `deepgram` | `nova-2` | Multilingual | Older generation |
| `deepgram` | `whisper` | Multilingual | Slower but accurate |

## LLM Providers (think)

| Type | Model | Notes |
|---|---|---|
| `open_ai` | `deepseek-chat` | BYO — DeepSeek API |
| `open_ai` | `gpt-4o` | BYO — OpenAI API |
| `anthropic` | `claude-*` | BYO — Anthropic API |
| `deepgram` | `nova-3` | Built-in, no BYO needed |

For BYO LLM, `endpoint.url` and `endpoint.headers` are required.
The `prompt` field sets the system message.

## TTS Providers (speak)

| Type | Model | Turkish | voice_id | Notes |
|---|---|---|---|---|
| `deepgram` | `aura-2-athena-en` | ❌ | N/A | Female, English |
| `deepgram` | `aura-2-thalia-en` | ❌ | N/A | Female, English |
| `deepgram` | `aura-2-zeus-en` | ❌ | N/A | Male, English |
| `eleven_labs` | `eleven_multilingual_v2` | ✅ | REQUIRED | Multilingual TTS |
| `eleven_labs` | `eleven_turbo_v2_5` | ✅ | REQUIRED | Faster, lower quality |

### ElevenLabs Voice ID

When using `eleven_labs` provider:
- `voice_id` is MANDATORY — without it, Deepgram returns `INVALID_SETTINGS`
- `language: "tr"` enables Turkish output
- Voice IDs come from ElevenLabs console or `GET /v1/voices` API
- If API returns 0 voices, no voices exist on the account — must create/clone one first

Example ElevenLabs speak settings:
```json
"speak": {
  "provider": {
    "type": "eleven_labs",
    "model_id": "eleven_multilingual_v2",
    "language": "tr",
    "voice_id": "<ELEVENLABS_VOICE_ID>"
  }
}
```

## Audio Encoding

Deepgram Voice Agent expects:
- **Input**: `linear16` PCM, 24000 Hz, mono
- **Output**: `linear16` PCM, 24000 Hz, mono, WAV container

Browser-side: `getUserMedia({ audio: { sampleRate: 24000, channelCount: 1 } })`
Convert Float32 → Int16 PCM before sending over WebSocket.

## Message Types (Server → Client)

| Type | Direction | Meaning |
|---|---|---|
| `Welcome` | DG → Client | Connection established |
| `SettingsApplied` | DG → Client | Settings accepted |
| `ConversationText` | DG → Client | Transcribed/response text |
| `UserStartedSpeaking` | DG → Client | User began speaking |
| `AgentThinking` | DG → Client | LLM processing |
| `AgentAudioDone` | DG → Client | TTS audio complete |
| `Error` | DG → Client | Error with code + description |

## Connection Headers

```
Authorization: Token <DEEPGRAM_API_KEY>
User-Agent: deepgram-sdk/7.3.1
X-Fern-Language: Python
X-Fern-SDK-Name: deepgram-sdk
X-Fern-SDK-Version: 7.3.1
```

The Fern headers are optional but recommended for SDK compatibility.
