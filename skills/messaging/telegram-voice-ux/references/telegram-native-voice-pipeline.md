# Telegram Native Voice Pipeline (Built-in, Not Browser Voice Agent)

This documents the **built-in** Telegram voice processing pipeline — the flow when a user sends a voice message inside a Telegram chat and Hermes processes it through the gateway. This is SEPARATE from the browser-based voice agent (vanitas_ses.py / voice agent v10.x).

## Pipeline Overview

```
User sends voice message (.ogg Opus)
  → Telegram Bot API (getUpdates polling)
    → telegram.py:_handle_media_message()
      → msg.voice → cache_audio_from_bytes(.ogg) → event.media_urls
        → adapter.handle_message(event)
          → GatewayRunner → _enrich_message_with_transcription()
            → transcribe_audio() (faster-whisper local)
              → transcript prepended as "[The user sent a voice message~ Here's what they said: "..."]"
                → Agent processes the text
                  → Response generated
                    → Auto-TTS check (base.py:4165):
                      if _should_auto_tts_for_chat(chat_id)      ← voice_only mode
                      AND event.message_type == MessageType.VOICE
                      AND text_content exists
                      AND no media_files
                        → TTS via text_to_speech_tool → voice bubble
```

## Handler Registration

In `telegram.py` (line 1617-1620):
```python
self._app.add_handler(TelegramMessageHandler(
    filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.VOICE | filters.Document.ALL | filters.Sticker.ALL,
    self._handle_media_message
))
```

The `filters.VOICE` handler sends voice messages to `_handle_media_message`, which:
1. Downloads the .ogg file via Telegram API (`msg.voice.get_file()`)
2. Caches it via `cache_audio_from_bytes()` to audio cache directory
3. Sets `event.media_urls` and `event.media_types = ["audio/ogg"]`
4. Falls through to `await self.handle_message(event)` (line 5651)

## Voice Message → Text Transcription

In `run.py`, `_enrich_message_with_transcription()` (line 15731):
- Detects audio paths from `event.media_urls` where `event.message_type == MessageType.VOICE`
- Calls `transcribe_audio(path)` from `tools.transcription_tools.py`
- Provider selection: `_get_provider(stt_config)` 
  - Explicit config → honour user's choice
  - Auto-detect: local > groq > openai > mistral > xai > elevenlabs
- Local provider uses faster-whisper (supports .ogg directly, no conversion needed)
- Config: `stt.local.model: small` (valid name, NOT ARM64 so no timeout issues)
- Result prepended as structured text to the message the agent sees

## Auto-TTS (Voice Reply)

In `base.py` (line 4165), after agent response:
```python
if (self._should_auto_tts_for_chat(event.source.chat_id)
        and event.message_type == MessageType.VOICE
        and text_content
        and not media_files):
    # Generate TTS audio
    tts_result = text_to_speech_tool(text=speech_text)
    # Send voice bubble BEFORE text
```

`_should_auto_tts_for_chat(chat_id)` checks:
1. If `chat_id in _auto_tts_enabled_chats` → True (voice_only or all mode)
2. If `chat_id in _auto_tts_disabled_chats` → False (off mode)
3. Fallback: `voice.auto_tts` config default

## Voice Mode Persistence

`gateway_voice_mode.json` stores per-chat voice mode:
```json
{
  "telegram:6306976553": "voice_only"
}
```

Key format: `platform:chat_id`
- `telegram:6306976553` = DM with user 6306976553
- `telegram:-1003917030255` = group chat -1003917030255

**CRITICAL: Voice mode is per-chat, not per-user.** Setting `/voice on` in a DM only applies to that DM. To use voice in a group, run `/voice on` inside the group.

## Gateway State

Check gateway_voice_mode.json and gateway_state.json:
```bash
cat ~/.hermes/gateway_voice_mode.json  # Current voice modes
cat ~/.hermes/gateway_state.json       # Gateway connection state
```

Gateway state should show `"telegram": {"state": "connected"}`.

## Config (STT)

From `config.yaml`:
```yaml
stt:
  enabled: true
  provider: local
  local:
    model: small
    language: ''  # auto-detect
```

TTS:
```yaml
tts:
  provider: openai  # routes to elevenlabs via Pollinations proxy
  openai:
    model: elevenlabs
    voice: bella
    base_url: http://127.0.0.1:19999/v1
```

## STT Provider (transcription_tools.py)

- `_get_provider()` (line 740): Checks config, then auto-detects
- `_transcribe_local()` (line 1110): Uses faster-whisper, supports .ogg natively
- Language: config `stt.local.language` > env var > auto-detect (None)
- Model: `stt.local.model: small` → normalized to `small` (valid)
- On ARM64: `small` model times out (30s+), use `tiny` instead
- On x86_64/WSL: `small` works fine

## Debugging "Voice message not being sent"

1. **Check gateway connection**
   ```bash
   cat ~/.hermes/gateway_state.json | grep telegram
   ```
   Should show: `"telegram": {"state": "connected"}`

2. **Check voice mode config**
   ```bash
   cat ~/.hermes/gateway_voice_mode.json
   ```
   Verify the chat_id matches where the user is sending from.

3. **Check the chat_id mismatch**
   - DM chat_id (e.g., 6306976553) ≠ group chat_id (e.g., -1003917030255)
   - If voice mode is set for DM but conversation is in group, voice replies won't fire
   - Fix: `/voice on` inside the group

4. **Check STT works**
   ```bash
   python3 -c "from faster_whisper import WhisperModel; m = WhisperModel('small', device='cpu', compute_type='int8'); print('OK')"
   ```

5. **Check logs for voice processing**
   ```bash
   grep -i "cached.*voice\|transcrib\|stt\|voice_only" ~/.hermes/logs/gateway.log
   ```

6. **Check Telegram handler registration**
   The handler at `telegram.py:1617` uses `filters.VOICE` — verify it exists in the code.

7. **Check Telegram privacy mode**
   If the bot is in a group with other users and has privacy mode enabled, it won't receive voice messages that don't mention it. Fix: disable privacy mode via @BotFather → Bot Settings → Group Privacy → Disable.
