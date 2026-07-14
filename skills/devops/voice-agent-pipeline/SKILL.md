---
name: voice-agent-pipeline
description: "Build and debug Vanitas voice agent WebSocket pipeline — VAD → STT → Hermes (Vanitas) → TTS. Covers architecture options, PCM handling, VAD, and troubleshooting."
---

# Voice Agent Pipeline (DEPRECATED — see vanitas-voice-bridge)

> **⚠️ This skill is outdated.** Current production architecture is v10 (Deepgram Nova-2 STT + MediaRecorder + ElevenLabs Bella TTS).  
> **Authoritative skill:** `vanitas-voice-bridge` — covers ALL current architecture, pitfalls, startup, TTS comparison, and version history.  
> Load `skill_view(name='vanitas-voice-bridge')` for the real thing. This skill preserved for historical PCM/VAD code reference only.

## Current Status (2026-06-16)

| Version | STT | Status |
|---------|-----|--------|
| **v10** | Deepgram Nova-2 REST + MediaRecorder | ✅ **PRODUCTION** |
| v9 | faster-whisper-tiny + VAD + PCM | ❌ ARM64 too slow, 4 browser bugs |
| v6-v8 | Chrome Web Speech API | ❌ Poor Turkish, clicking sounds, echo loops |
| v5 | Pollinations Whisper | ❌ Returns 500 errors — unreliable |
| v2 | Deepgram Voice Agent (managed) | 🔄 Fallback (TTS had English accent) |

**All current architecture, detailed pitfalls, Debugging, startup commands, and TTS comparison → load `vanitas-voice-bridge` skill.**

### Key findings moved to vanitas-voice-bridge:
- Pollinations Whisper → 500 internal errors (OVH upstream), NOT reliable for production
- Deepgram STT (Nova-2) is excellent for Turkish; Deepgram TTS (Aura-2) has English accent — they are separate products
- faster-whisper benchmarks on ARM64: tiny 0.7x real-time, base 1.1x, small 10x+ (unusable)
- FastAPI/Starlette WebSocket binary → `{"bytes": ...}` dict, not raw bytes — critical pitfall
- MediaRecorder webm first chunk is the EBML header — must be preserved across flushes
- webrtcvad 2.0.10 has broken `pkg_resources` import — hardcode version string
- ScriptProcessorNode needs output connection (GainNode(0) → destination) to fire

Port: **8765**. Dışa açma: Cloudflared tunnel (WARP proxy üzerinden). Tüm servisler loopback.

## STT Options (Historical — see vanitas-voice-bridge for current)

> **Current recommendation:** Deepgram Nova-2 REST (v10). Pollinations Whisper returns 500 errors.  
> Load `vanitas-voice-bridge` for full comparison including Deepgram, faster-whisper benchmarks, and Web Speech API pitfalls.

## TTS Options (Historical — see vanitas-voice-bridge for current)

> **Current:** ElevenLabs Bella via Pollinations proxy. Deepgram Aura-2 has English accent on Turkish.  
> Cartesia requires separate API key (not in system). See `vanitas-voice-bridge` for full TTS provider truth table.

## PCM Format Handling (Reference Only)

> **v10 uses MediaRecorder (webm/opus) — no PCM needed.** This section preserved for v9 historical reference.  
> See `vanitas-voice-bridge` → "MediaRecorder vs ScriptProcessor" for why MediaRecorder won.

## Troubleshooting (Quick Reference)

> **Full troubleshooting matrix → `vanitas-voice-bridge` pitfalls section.** Key additions since this skill was last updated:
> - FastAPI WebSocket binary: `raw.get("bytes")` extracts from dict
> - MediaRecorder webm: save first chunk as header, prepend to every flush
> - webrtcvad: hardcode `__version__ = "2.0.10"` for setuptools compat
> - ScriptProcessorNode: connect to GainNode(0) → destination or it won't fire
> - faster-whisper: `tiny` only on ARM64, `small` times out

## Files

> **Current:** `voice_agent_v10.py` — production. All versions in `/home/ubuntu/voice-agent-venv/`.  
> See `vanitas-voice-bridge` for version table (v2 through v10) and which is which.
