# Voice Agent v3 Template — Quick Start

Real working code at: `/home/ubuntu/voice-agent-venv/voice_agent_v3.py`
Backup: `/home/ubuntu/voice-agent-venv/voice_agent_v2.py.bak`

## Architecture (3-hop pipeline)
```
Browser WS (:8765) → [Deepgram STT WS] → [Hermes Proxy :8767] → [Pollinations TTS HTTP] → Browser
```

## Key Endpoints
- Deepgram STT WS: `wss://api.deepgram.com/v1/listen?encoding=linear16&sample_rate=24000&language=tr&model=nova-3&interim_results=true&utterance_end_ms=700`
- Hermes Proxy: `http://127.0.0.1:8767/v1/chat/completions`
- Pollinations TTS: `https://gen.pollinations.ai/v1/audio/speech`

## Required Env Vars
- `DEEPGRAM_API_KEY` — for STT
- `POLLINATIONS_API_KEY` — for TTS (ElevenLabs Bella)

## TTS Config (ElevenLabs Bella, Turkish)
```json
{"model": "elevenlabs", "input": "text", "voice": "bella", "response_format": "pcm", "speed": 1.0}
```
Fallback: `{"model": "openai-audio", "voice": "nova", "response_format": "pcm"}`

## Browser PCM Streaming (JavaScript)
```javascript
const audioCtx = new AudioContext({sampleRate: 24000});
const source = audioCtx.createMediaStreamSource(stream);
const processor = audioCtx.createScriptProcessor(4096, 1, 1);
processor.onaudioprocess = (e) => {
  const pcm = e.inputBuffer.getChannelData(0);
  const int16 = new Int16Array(pcm.length);
  for (let i = 0; i < pcm.length; i++) int16[i] = pcm[i] * 32767;
  ws.send(int16.buffer);
};
source.connect(processor);
// NOTE: Do NOT connect processor to destination (echo)
```

## Process Management
```bash
# Restart after code changes (CRITICAL — running process keeps old code)
pkill -f voice_agent_v3.py; sleep 1
cd /home/ubuntu/voice-agent-venv && ./bin/python voice_agent_v3.py 2>&1 | tee /tmp/voice_agent_v3.log &

# Health check
curl -s http://localhost:8765/health
```

## Conversation Context
Proxy maintains per-session conversation list (last 10 exchanges) for continuity.
Cross-session memory relies on Hermes USER.md/MEMORY.md injection.

See `references/custom-voice-pipeline-v3.md` for full documentation including:
- Complete architecture diagram
- v2 vs v3 comparison
- Deepgram Aura-2 Turkish limitation
- Pollinations TTS model list
- Cartesia free tier pricing
- Troubleshooting table
