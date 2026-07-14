# Turkish STT Provider Landscape (June 2026)

## Research from voice agent v10.7 development session

### Providers Evaluated

| Provider | STT Streaming | Turkish WER | Free Tier | Credit Card | Notes |
|----------|--------------|-------------|-----------|-------------|-------|
| **Deepgram** nova-3+multi | ✅ WebSocket | Unknown (poor in tests) | $200 credit | ❌ No | Model must be `nova-3&language=multi&endpointing=100`. `whisper-large` returns 405. `language=tr` not valid for nova-3. |
| **ElevenLabs Scribe** | ✅ Realtime API | **3.8% FLEURS** | Pay-as-you-go | ✅ Yes | Best tested Turkish accuracy. $0.39/hr realtime. Pollinations does NOT proxy Scribe STT. |
| **Soniox** | ✅ WebSocket | "Native-speaker" | ❌ None (removed Oct 2025) | ❌ Email only | ~$0.12/hr STT. Open-source voice bot demo. Barge-in via Silero VAD. Signup: console.soniox.com/signup — email only, no card. |
| **Azure Speech** | ✅ WebSocket | Good | 5 hrs/month | ✅ Yes | Free tier generous for testing. Complex setup. |
| **Google Cloud STT** | ✅ gRPC | Good | 60 min/month | ✅ Yes | gRPC streaming complex. |
| **Groq Whisper** | ❌ REST only | ~12% WER (turbo) | Free tier | — | Fast LPU but NO streaming. Not viable for real-time voice. |
| **Vosk** small-tr-0.3 | ✅ WebSocket | **TBD (unpublished)** | Free (local) | ❌ No | 35MB model, ~300MB RAM. GitHub issue #1503: "small model not enough." Big model "contact us by email" — sketchy. |
| **faster-whisper** (local) | ❌ No native streaming | 7.5% WER (large-v3) | Free (local) | ❌ No | ARM64: tiny=0.7x RT ✅, base=1.1x RT ⚠️, small=30s+ ❌. whisper.cpp may be faster. |
| **AssemblyAI** Universal-3 | ✅ WebSocket | ❌ **Turkish NOT supported** | Paid | ✅ | Only 6 languages (EN, ES, DE, FR, PT, IT). |

### Soniox Detailed Pricing (Verified June 2026)

Token-based billing:
- Input audio tokens: $2.00/1M tokens (~$0.06/hr)
- Output text tokens: $4.00/1M tokens (~$0.06/hr)
- **Total STT real-time: ~$0.12/hr** ✅ (matches Soniox's own "~$0.12/hour")
- TTS real-time: ~$0.70/hr

Monthly estimate (30min/day conversation, ~15min actual speech):
- STT: 7.5 hrs × $0.12 = **$0.90/month**
- TTS: $0 (use Bella via Pollinations, free)

**Signup flow:** console.soniox.com/signup → email → verification email → set password → login → API Keys

**No free credits** as of October 2025 blog post.

### ElevenLabs Scribe Detail

- Real-time API: `speech-to-text/v-1-speech-to-text-realtime`
- Turkish WER: 3.8% on FLEURS (vs Deepgram Nova-2: 9.9%, Whisper Large v3: 7.5%)
- Pricing: $0.39/hr realtime, $0.22/hr batch
- Free tier: "Free / Pay as you go" — exact minutes unclear
- NOT available through Pollinations proxy (only TTS is)

### Key Decisions from This Session

1. **Soniox selected as primary alternative** to Deepgram for Turkish voice agent
2. **Deepgram $200 credit** kept as fallback (English mode)
3. **Groq for LLM** (not STT) — `groq-llama-4-scout` via Hermes custom_provider
4. **Bella TTS** stays (free via Pollinations) — no need for paid TTS
5. **Vosk rejected** due to unpublished accuracy + "contact us for big model" sketchiness

### Architecture Decision Matrix

```
Scenario: User speaks Turkish → needs Turkish STT streaming

Option A (Free): Deepgram $200 credit + English mode
  └─ User speaks English → STT English → LLM understands → replies Turkish

Option B (Paid, ~$1/mo): Soniox STT only
  └─ User speaks Turkish → Soniox STT → Groq LLM → Bella TTS

Option C (Paid, ~$6/mo): ElevenLabs Scribe
  └─ Best Turkish accuracy but more expensive

Option D (Free, local): faster-whisper tiny + VAD
  └─ Already works on ARM64 but accuracy loss with tiny model
```
