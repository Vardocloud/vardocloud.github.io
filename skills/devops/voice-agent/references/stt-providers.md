# STT Provider Comparison

Real-time streaming STT providers evaluated for Turkish voice agent on ARM64 (Oracle Cloud, 5.8GB RAM).

## Comparison Matrix (June 2026)

| Provider | Model | Turkish | Latency | Cost/mo* | Setup | Verdict |
|---|---|---|---|---|---|---|
| **Soniox** | stt-rt-v5 | ✅ Native | 100-200ms | ~$0.90 | Cloud WS | 🏆 Best |
| Deepgram | nova-3 multi | ❌ Garbage | 100-200ms | Free tier | Cloud WS | Unusable |
| Deepgram | nova-2 whisper | ❌ Poor | 100-200ms | Free tier | Cloud WS | Unusable |
| faster-whisper | large-v3 | ✅ Good | 2000-5000ms | Free | Local | Too slow |
| Whisper-Small TR | fine-tuned | ✅ Good | 500-2000ms | Free | Local | Too slow |
| Wav2Vec2-XLS-R | 300M | ✅ Good | 1000-3000ms | Free | Local | Too slow |
| Azure STT | latest | ✅ Good | 100-200ms | ~$1.00 | Cloud REST | Card required |
| Google STT | chirp | ✅ Good | 100-200ms | ~$1.50 | Cloud REST | Card required |

*Estimated for 30 min/day usage.

## Key Findings

1. **Local STT on ARM64 is NOT viable for realtime.** All local models (Whisper, Wav2Vec2) exceed 500ms latency on 5.8GB ARM64. CPU-only inference is the bottleneck.
2. **Deepgram Turkish is broken.** `nova-3` with `language=multi` produces gibberish for Turkish. `nova-2` with `language=tr` also poor. Deepgram is effectively English-only for quality.
3. **Soniox is the only viable option.** Native Turkish support, $0.12/hr, no free tier.
4. **Soniox balance required.** Zero balance = HTTP 402. Minimum deposit: none. Stripe payment with "$5 back" promo.

## Selection Criteria

For Turkish voice agent on this server:
- ✅ Must be cloud (ARM64 too slow for local)
- ✅ Must support Turkish natively
- ✅ Must be streaming WebSocket (REST batch unacceptable)
- ✅ Cost < $2/month

**Only Soniox meets all criteria.**
