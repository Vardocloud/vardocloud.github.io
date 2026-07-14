# Soniox Voice Bot Demo — Full-Duplex Reference

**Source:** https://github.com/soniox/soniox_examples/tree/master/apps/soniox-voice-bot-demo
**Local path:** `~/vanitas-web/soniox-server/`

## Architecture

```
User mic → WebSocket (PCM s16le 16kHz mono)
  → VADProcessor (Silero VAD) — detects speech start/end, emits barge-in
  → STTProcessor (Soniox stt-rt-v5) — streaming transcription
  → LLMProcessor (OpenAI/Groq) — streaming response + tool calls
  → TTSProcessor (Soniox tts-rt-v1) — streaming audio 24kHz
  → WebSocket → Browser speaker
```

**Key feature: Barge-in.** VAD detects user speech during TTS playback → sends `UserSpeechStartMessage` → cancels LLM generation → new transcription begins. Enables natural interruption.

## Server Setup

```bash
cd ~/vanitas-web/soniox-server
python3 -u main.py
# WebSocket on ws://127.0.0.1:8765
```

Dependencies: `silero-vad`, `torch`, `torchaudio`, `openai`, `websockets`, `python-dotenv`, `structlog`

## Frontend Connection

```
ws://127.0.0.1:8765/?language=tr&voice=Maya
```

Sends raw PCM s16le audio (16kHz, mono). Receives JSON messages for transcription, TTS audio, and metrics.

## Current Status (v16)

| Component | Status |
|-----------|--------|
| Python server | ✅ Kurulu, çalışıyor |
| Silero VAD | ✅ Cache'li, 1sn warmup |
| Groq LLM | ✅ Entegre (OPENAI_API_KEY + base_url) |
| Soniox TTS | ✅ Aktif (tts-rt-v1, voice=Maya) |
| Cloudflare tunnel | ✅ Quick tunnel aktif (port 3005 üzerinden) |
| Barge-in | ✅ VAD ile hazır |

## Pitfalls

- **Python 3.11 vs 3.13**: pyproject.toml `requires-python = ">=3.13"` → `>=3.11` olarak değiştirilmeli
- **VAD model download**: İlk çalıştırmada `torch.hub.load("snakers4/silero-vad", ...)` modeli indirir (~30sn), sonra cache'lenir
- **WEBSOCKET_HOST**: Varsayılan `localhost` IPv6'ya çözülebilir → `127.0.0.1` override edilmeli
- **Background process**: Python asyncio server Hermes background tool'da stabil kalamayabilir → `screen`, `tmux`, Node.js child_process, veya cron ile yönet
- **OpenAI key vs Groq**: `.env`'de `OPENAI_API_KEY` olarak saklanır (isim karışıklığı), gerçekte Groq key kullanılır. `base_url=https://api.groq.com/openai/v1`
