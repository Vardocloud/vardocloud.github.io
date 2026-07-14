# Cartesia TTS Configuration for Vanitas Voice Bridge

## Status (2026-06-16): NOT WORKING — 401 Unauthorized

Cartesia returns HTTP 401 when used via Deepgram Voice Agent. Root cause: No Cartesia API key configured in the system. The environment variable is not set.

Deepgram's managed Cartesia integration may still require a Cartesia API key — either configured in Deepgram's dashboard or passed through the Voice Agent settings. This has not been verified.

**Until resolved, use Deepgram Aura-2 as fallback** (see main SKILL.md for working Aura-2 config).

## Why Cartesia (When It Works)

Deepgram's native TTS voices (Aura family) are English-only. All available voices have the `-en` suffix. When given Turkish text, Aura voices speak with a heavy English accent — "like a foreigner who just arrived in Turkey." "İyiyim, teşekkürler" is heard as "I am teşekkürler."

Cartesia Sonic 3.5 supports 42 languages natively, including Turkish. Any voice can speak any language — the model is fully multilingual.

## Cartesia Pricing (2026-06-16)

- **Free tier**: 20K credits/month ≈ 27 min Sonic-3.5 TTS, 1 agent slot
- **Pro**: $4-5/month, 100K credits ≈ 133 min
- Source: https://www.cartesia.ai/pricing

Free tier is sufficient for testing. Sign up at https://play.cartesia.ai/sign-up

## Working Configuration (When API Key Available)

```json
"speak": {
    "provider": {
        "type": "cartesia",
        "model_id": "sonic-3.5",
        "voice": {
            "mode": "id",
            "id": "db6b0ed5-d5d3-463d-ae85-518a07d3c2b4"
        }
    }
}
```

**Voice:** Skylar (`db6b0ed5...2b4`, en-US female). Tested working across multi-turn conversations when API key is valid. Katie (`f786b574...4c02`) is an alternative.

**Do NOT set `"language": "tr"`** — causes `FAILED_TO_SPEAKE` after 3 empty warnings. Cartesia auto-detects language from text content.

## Troubleshooting

### 401 Unauthorized
- Cartesia API key missing or expired
- Test: direct API call to Cartesia TTS endpoint with the key
- Resolution: obtain new key from https://play.cartesia.ai

### FAILED_TO_SPEAKE (after 3 empty Warnings)
- Most common cause: `"language": "tr"` set on Cartesia provider — remove it
- Also caused by: invalid voice ID, expired API key, or account quota exceeded
- Cartesia auto-detects language — explicit `language` is optional and risky

## Voice IDs (Cartesia Sonic 3.5 Compatible)

| Voice | Accent | Gender | ID |
|-------|--------|--------|----|
| Skylar | en-US | female | `db6b0ed5-d5d3-463d-ae85-518a07d3c2b4` |
| Katie | en-US | female | `f786b574-daa5-4673-aa0c-cbe3e8534c02` |
| Gemma | en-GB | female | `62ae83ad-4f6a-430b-af41-a9bede9286ca` |

Any of these work with Turkish — voice ID determines timbre only. Language is auto-detected from text.

Find more: https://play.cartesia.ai/voices

## ElevenLabs Attempt (Failed)

We tried ElevenLabs BYO TTS via Pollinations endpoint:
```json
"speak": {
    "provider": {"type": "eleven_labs", "model_id": "eleven_turbo_v2_5"},
    "endpoint": {"url": "https://gen.pollinations.ai/v1/audio/speech?...&voice=bella"}
}
```
Result: Deepgram rejected with `Voice ID must not be provided for ElevenLabs when using a custom URL.`
Pollinations endpoint format is incompatible with Deepgram's ElevenLabs BYO integration.

## Provider Schema Reference

From Deepgram API spec:
```yaml
CartesiaSpeakProvider:
  type: object
  properties:
    type: {enum: [cartesia]}
    model_id: {description: Cartesia model ID}
    voice:
      type: object
      properties:
        mode: {type: string}
        id: {type: string}
      required: [mode, id]
    language: {type: string}       # OPTIONAL — avoid setting!
    volume: {type: number, range: 0.5-2.0}
  required: [type, model_id, voice]
```
