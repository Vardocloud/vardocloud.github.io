# STT/TTS Pricing Comparison (2026)

**Last verified:** June 16, 2026
**Source:** Awesome Agents pricing comparisons, OpenRouter model pages, provider docs
**Use case:** Voice agent cost optimization for Vanitas voice bridge

## Speech-to-Text (STT) — Per-Minute Pricing

| Provider | Model | Per-Min | Per 1,000 Min | Streaming | Turkish |
|----------|-------|---------|---------------|-----------|---------|
| **Groq** | Whisper-Large-V3-Turbo | **~$0.0006** | ~$0.60 | ❌ Batch | ✅ |
| **Together AI** | Whisper-Large-V3 | ~$0.001 | ~$1.00 | ❌ Batch | ✅ |
| **Fireworks AI** | Whisper-Large-V3 | ~$0.001 | ~$1.00 | ❌ Batch | ✅ |
| **OpenAI** | gpt-4o-mini-transcribe | **$0.003** | $3.00 | ✅ Streaming | ✅ |
| **Deepgram** | Nova-3 (batch) | $0.0036 | $3.60 | ❌ Batch | ✅ |
| **ElevenLabs** | Scribe | $0.004 | $4.00 | ❌ Batch | ✅ |
| **Deepgram** | Nova-3 (streaming) | $0.0056 | $5.60 | ✅ Streaming | ✅ |
| **OpenAI** | Whisper-1 / gpt-4o-transcribe | $0.006 | $6.00 | ❌ Batch | ✅ |
| **Google** | Chirp 2 | $0.0048 | $4.80 | ✅ Streaming | ✅ |
| **Azure** | Speech Standard | $0.016 | $16.00 | ✅ Streaming | ✅ |
| **AWS** | Transcribe Standard | $0.024 | $24.00 | ✅ Streaming | ✅ |

### STT Key Takeaways
- **Cheapest overall:** Groq Whisper at $0.0006/min (but batch-only, no streaming)
- **Best streaming value:** OpenAI gpt-4o-mini-transcribe at $0.003/min
- **Current (v10):** Deepgram Nova-2 streaming at $0.0056/min
- **Türkçe için:** Deepgram Nova-3, OpenAI Whisper, Groq all support Turkish well

## Text-to-Speech (TTS) — Per-Character Pricing

| Provider | Model / Tier | Per 1M Chars | Per Hour | Streaming | Voice Cloning | Turkish |
|----------|-------------|-------------|----------|-----------|---------------|---------|
| **Amazon Polly** | Standard | **$4.00** | ~$17.65 | ✅ | ❌ | ✅ Sınırlı |
| **Google Cloud** | Standard | **$4.00** | ~$17.65 | ❌ | ❌ | ✅ |
| **Azure** | Neural Standard | **$14.11** | ~$16.00/hr | ✅ | ❌ | ✅ 500+ ses |
| **OpenAI** | tts-1 | **$15.00** | ~$66.18 | ✅ | ❌ | ✅ 57 dil |
| **OpenAI** | gpt-4o-mini-tts | **$15.00** | ~$66.18 | ✅ | ❌ | ✅ |
| **Deepgram** | Aura | $15.00 | ~$66.18 | ✅ | ❌ | ❌ English only |
| **Play.ht** | Pro | $22.00 | ~$97.00 | ✅ | ✅ Instant | ✅ 142 dil |
| **Google Cloud** | WaveNet / Neural2 | $16.00 | ~$70.59 | ❌ | ❌ | ✅ |
| **Cartesia** | Sonic (PAYG) | $50.00 | ~$220.59 | ✅ | ✅ | ✅ 15+ dil |
| **ElevenLabs** | Turbo v2.5 | $66.00 | ~$291.00 | ✅ | ✅ Instant | ✅ 32 dil |
| **Amazon Polly** | Generative | $30.00 | ~$132.35 | ❌ | ❌ | ❌ English |
| **Amazon Polly** | Long-form | $100.00 | ~$441.18 | ❌ | ❌ | ❌ English |
| **Azure** | Neural HD | $91.75 | ~$103.90/hr | ✅ | ❌ | ❌ English |
| **Resemble.ai** | PAYG | ~$21.60/hr | ~$21.60 | ✅ | ✅ | ✅ 10+ dil |

\* Per-hour conversion assumes ~150 wpm, ~5 chars/word → ~2.27 hrs per 1M chars.

### TTS Key Takeaways
- **Cheapest with streaming:** OpenAI tts-1 at $15/1M chars ($66/hr)
- **Cheapest overall:** Amazon Polly Standard at $4/1M chars (but no streaming, limited Turkish)
- **Best value for Turkish:** Azure Neural Standard at $14.11/1M chars (500+ voices, 140+ langs)
- **Current (v10):** ElevenLabs Bella at $66/1M chars — premium quality, premium price
- **Up to 4x savings:** Switching ElevenLabs → OpenAI tts-1 saves ~4x on TTS costs

## OpenRouter Audio Models (Token-Based)

### STT on OpenRouter
| Model | Input Tokens | Output Tokens | Audio? |
|-------|-------------|--------------|--------|
| GPT-4o Mini Transcribe | $1.25/M | $5/M | ✅ Audio |
| GPT-4o Transcribe | $2.50/M | $10/M | ✅ Audio |
| Voxtral Mini Transcribe | $3,000/M | $0/M | ✅ Audio |
| Qwen3 ASR Flash | $35/M | $0/M | ✅ Audio (11 langs) |
| Chirp 3 | $16,000/M | $0/M | ✅ Audio |
| Parakeet TDT 0.6B | $1,500/M | $0/M | ✅ Audio |

### TTS on OpenRouter
| Model | Input Tokens | Output Tokens | Turkish |
|-------|-------------|--------------|---------|
| Kokoro 82M | $0.62/M | $0/M | ❌ (8 langs, no TR) |
| Gemini 3.1 Flash TTS | $1/M | $20/M | ✅ 70+ langs |
| Grok Voice TTS 1.0 | $15/M | $0/M | ✅ 20+ langs |
| Voxtral Mini TTS | $16/M | $0/M | ✅ Multilingual |
| MAI-Voice-2 | $22/M | $0/M | ✅ 10+ langs |
| Orpheus 3B | $7/M | $0/M | ❌ English only |

**Verdict:** OpenRouter audio models are token-based, making direct $/min comparison difficult. For high-volume voice, dedicated STT/TTS APIs (Deepgram, OpenAI, Groq) are more economical than OpenRouter's token-based pricing.

## Current Voice Bridge Cost Estimate

Assumes ~30 min/day voice interaction (conservative for voice agent):

| Component | Current | Monthly Cost |
|-----------|---------|-------------|
| **STT** (Deepgram Nova-2, $0.0056/min × 30dk × 30gün) | $5.04 | ~$5/mo |
| **TTS** (ElevenLabs Bella, ~66M chars @ $66/1M, ~4500 char/gün × 30) | $8.91 | ~$9/mo |
| **Total** | | **~$14/mo** |

### If Optimized (Cheapest Streaming Options)
| Component | Alternative | Monthly Cost |
|-----------|------------|-------------|
| **STT** | OpenAI gpt-4o-mini-transcribe ($0.003/min) → $2.70/mo | **-$2.34/mo** |
| **TTS** | OpenAI tts-1 ($15/1M chars) → $2.03/mo | **-$6.88/mo** |
| **Total Optimized** | | **~$4.73/mo** |

Note: Optimizing TTS from ElevenLabs to OpenAI tts-1 means losing voice cloning and premium quality. Only worth it if cost > quality priority.

## Soniox Pricing (Added 20 Haz 2026)

Soniox uses token-based pricing (not per-minute). Conversion to $/min is approximate.

| Service | Pricing Model | Cost | Notes |
|---------|--------------|------|-------|
| **STT** (async) | $1.50/1M input tokens | ~$0.10/hr | Batch pre-recorded |
| **STT** (real-time) | $2.00/1M input tokens | ~$0.13/hr | Streaming WebSocket |
| **TTS** (real-time) | $4.00/1M input + $21.50/1M output tokens | ~$0.70/hr | Token-based, competitive |

**Key points:**
- STT is highly competitive ($0.10-0.13/hr vs Deepgram $0.0056/min = $0.34/hr)
- Real-time STT supports Turkish well via `language_hints: ["tr"]`
- MCP server available for Cursor/Claude Code docs integration
- Currently used as primary STT in vanitas-voice-bridge v10.10

**Source:** soniox.com/pricing (20 Haz 2026)

## Sources
- https://awesomeagents.ai/pricing/transcription-api-pricing/ (Apr 19, 2026)
- https://awesomeagents.ai/pricing/voice-tts-pricing/ (Apr 19, 2026)
- https://openrouter.ai/collections/speech-to-text-models (Jun 2026)
- https://openrouter.ai/collections/text-to-speech-models (Jun 2026)
