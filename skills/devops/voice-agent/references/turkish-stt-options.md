# Turkish Speech-to-Text Options (Streaming) — 17 Haz 2026

Comprehensive research on streaming STT options with Turkish support for real-time voice agents.

## Verdict: Deepgram Turkish Is Weak

- **nova-2 + language=tr**: Poor accuracy. Transcriptions like "Sesim ismini net etiket geliyor ya baba" instead of "Sesim nasıl, net geliyor mu baba?"
- **nova-3 + language=tr**: HTTP 405 on WebSocket (rejected). `language` param on nova-3 requires `multi`, not `tr`.
- **nova-3 + language=multi**: Connects, but Turkish accuracy still poor in practice.

## Streaming STT Options Compared

| Service | Streaming | Turkish Accuracy | Free Tier | Credit Card | Notes |
|---------|-----------|-----------------|-----------|-------------|-------|
| Deepgram nova-3+multi | WebSocket ✅ | ⚠️ Poor | $200 credit, no card | No | Already tried, Turkish weak |
| ElevenLabs Scribe v2 | REST realtime | 🏆 3.8% WER | Limited | Yes | Best Turkish accuracy, $0.39/hr |
| Soniox | WebSocket ✅ | ✅ Native-speaker | None (removed Oct 2025) | No (email only) | $0.12/hr STT, ~$0.90/mo for 30min/day |
| Azure Speech | WebSocket ✅ | ✅ Good | 5 hr/month free | Yes | Complex setup |
| Google Cloud STT | gRPC | ✅ Good | 60 min/month free | Yes | Complex setup |
| Whisper (local) | ❌ No streaming | ✅ 7.5% WER | Free forever | No | ARM64 too slow for large model |
| Whisper.cpp (local) | Possible | ✅ Good | Free forever | No | C++ optimized, may work on ARM64 |
| Groq Whisper | ❌ REST only | ✅ Good | Free tier | No | LPU-fast but no streaming |
| Vosk small-tr-0.3 | WebSocket ✅ | ❓ TBD | Free forever | No | 35MB model, accuracy unknown, big model "contact us" |

## Soniox Pricing (Verified 17 Haz 2026)

**Token-based pricing, verified against Soniox's own estimate of ~$0.12/hour:**

```
Input audio tokens:  $2.00 / 1M tokens  (1 hr audio ≈ 30,000 tokens → $0.06/hr)
Output text tokens:  $4.00 / 1M tokens  (1 hr speech ≈ 15,000 tokens → $0.06/hr)
TOTAL STT/hour:      $0.12 ✓ MATCHES
TTS:                 $0.70/hr (can skip, use Bella free)
```

**Monthly cost (30 min/day conversation, ~15 min actual speech):**
- STT only: 7.5 hrs × $0.12 = **$0.90/month**
- TTS via Bella: $0
- **Total: ~$0.90/month**

**Signup:** console.soniox.com/signup — email only, no credit card.

## ElevenLabs Scribe (Best Accuracy)

- Turkish WER: 3.8% on FLEURS benchmark
- Deepgram nova-2 comparison: 9.9% WER
- Scribe v2 Realtime: $0.39/hr, ~150ms latency
- But: pay-as-you-go only, free tier very limited

## Key Lesson: Streaming Is Mandatory

REST-based STT (Groq Whisper, ElevenLabs batch) cannot provide real-time display of interim results. For a natural voice conversation, WebSocket streaming with interim results is required. This was verified through multiple test sessions (16-17 Haz 2026).

## Deepgram $200 Free Credits

- console.deepgram.com/signup — no credit card needed
- "Get $200 in credit absolutely free. That can fuel a voice agent for at least 50 hours."
- But: credits don't fix Turkish accuracy problem
- Useful only if user is willing to speak English
