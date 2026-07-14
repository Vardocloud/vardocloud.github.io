# Soniox TTS Supported Voices

**Source:** https://soniox.com/docs/tts/concepts/voices (retrieved 10 Tem 2026)
**Model:** tts-rt-v1 (all 28 voices)
**Feature:** Any voice works with all 60+ supported languages — pick one voice for all languages.

## Voice List (28 voices)

| Voice | Gender | Style | Good For |
|-------|--------|-------|----------|
| **Maya** | Female | Steady, clear, warm, measured | ✅ AI assistant, conversation |
| Daniel | Male | Rich, polished, reassuring | |
| Noah | Male | Lively, crisp, youthful | |
| **Nina** | Female | Bright, expressive, friendly | ✅ Warm assistant |
| **Emma** | Female | Smooth, relaxed, warm | ✅ Natural conversation |
| Jack | Male | Friendly, clear, upbeat | |
| Adrian | Male | Deep, focused, authoritative | |
| **Claire** | Female | Polished, articulate, bright | ✅ Professional |
| **Grace** | Female | Gentle, soothing, calm | ✅ Soft conversation |
| Owen | Male | Grounded, steady, natural | |
| Mina | Female | Soft, thoughtful, sincere | |
| Kenji | Male | Calm, precise, trustworthy | |
| Rafael | Male | Spanish accent, composed | |
| Mateo | Male | Spanish accent, warm | |
| Lucia | Female | Spanish accent, composed | |
| Sofia | Female | Spanish accent, bright | |
| Oliver | Male | British accent, refined | |
| Arthur | Male | British accent, deep | |
| Isla | Female | British accent, lively | |
| Victoria | Female | British accent, elegant | |
| Cooper | Male | Australian accent, bold | |
| Mason | Male | Australian accent, relaxed | |
| Ruby | Female | Australian accent, confident | |
| Elise | Female | Australian accent, warm | |
| Arjun | Male | Indian accent, deep | |
| Rohan | Male | Indian accent, lively | |
| [Others] | | | |

## Current Default

**Maya** is the active voice for Vanitas full-duplex (10 Tem 2026). Warm, clear, natural — good for Turkish conversation.

## Common Mistakes

- **`Alina`** → NOT a valid Soniox TTS voice. Returns `400 Invalid voice 'Alina' for model 'tts-rt-v1'`.
- **`tr-TR-EmelNeural`** → Microsoft Edge TTS voice code. NOT a Soniox voice.
- The error manifests only when TTS actually runs (VAD detects speech → LLM responds → TTS tries to speak). Session start and STT work fine.
