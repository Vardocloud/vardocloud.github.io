# Soniox Speaker Diarization + Voice Fingerprint Integration Plan — 18 Tem 2026

## Goal
1. Detect who is speaking (Edel vs stranger) during voice sessions
2. Count and separate multiple speakers in real-time
3. Adapt Vanitas behavior based on speaker identity

## Part 1: Soniox Speaker Diarization (Built-in)

### API
Soniox STT supports speaker diarization natively — just add one config parameter:

```python
# In stt.py config message:
config["enable_speaker_diarization"] = True
```

### Output Format
Each token includes a `speaker` field:
```json
{"text": "merhaba", "speaker": "1", "is_final": true}
{"text": " selam", "speaker": "2", "is_final": true}
```

### Constraints
- **Max 15 speakers** per session
- **Endpoint detection conflict:** Docs say "endpoint detection or manual finalization forces early token finalization, which negatively impacts diarization accuracy." For voice agent with endpoint detection enabled, diarization may have **higher attribution errors** — speaker labels may temporarily switch and stabilize as more context is processed.
- **Language support:** All 60+ languages including Turkish
- **Model:** `stt-rt-v5` (current) supports diarization

### Implementation in stt.py
```python
# Add to config:
config["enable_speaker_diarization"] = True

# In _receive_task_handler, tokens now have "speaker" field:
for token in tokens:
    speaker = token.get("speaker", "1")  # default to speaker 1
    # Group tokens by speaker for diarization
```

### Integration with TranscriptionMessage
`TranscriptionMessage` needs a `speaker` field. Currently it only tracks `final_tokens` and `non_final_tokens`. Each token dict from Soniox includes `"speaker": "N"` when diarization is enabled.

## Part 2: Voice Fingerprint (MFCC — Existing Infrastructure)

### Existing Components
- **`voiceprint_service.py`** — FastAPI microservice, port 5050
- **`edel_voiceprint.npy`** — Edel's 20-dim MFCC voiceprint (already enrolled)
- **`voiceprint_enroll.py`** — enrollment tool with `--add` for incremental updates
- **MFCC pipeline:** pre-emphasis → FFT → mel filterbank (40 filters) → DCT → 20 coefficients
- **Threshold:** cosine similarity > 0.82 = Edel
- **Latency:** <5ms per utterance

### Approach: Hybrid Soniox Diarization + MFCC Verification

```
Browser mic → PCM 16kHz → Server
  ├→ Soniox STT (with diarization) → tokens with speaker IDs
  └→ Per-utterance PCM buffer → MFCC extraction → cosine similarity vs edel_voiceprint.npy
       → is_edel: True/False/None

Soniox speaker "1" ≈ Edel's voiceprint? → Cross-verify
Soniox speaker "2" ≠ Edel's voiceprint → "Tanımadık" (stranger)
```

### Why Both?
- **Soniox diarization** = "who spoke when" in real-time (fast, no enrollment needed)
- **MFCC voiceprint** = "is this Edel?" (precise, requires enrollment, cross-validates)
- Together: Soniox assigns speaker IDs fast → MFCC maps speaker ID to known identity

### Integration Steps
1. **Enable diarization in stt.py** — `enable_speaker_diarization: True`
2. **Tag TranscriptionMessage with speaker** — add `speaker` to message
3. **Buffer per-speaker PCM** — group audio by speaker ID in session.py
4. **On utterance flush** — send PCM to voiceprint service for MFCC verification
5. **Map speaker IDs to identities** — speaker_1 → Edel (if MFCC match), speaker_2 → "Tanımadık"
6. **Pass speaker identity to LLM** — prefix user message: `[Edel] merhaba` or `[Tanımadık] selam`
7. **Vanitas behavioral adaptation** — system prompt includes speaker identity context

### LLM Context Example
```python
# In llm.py _append_user_message:
if speaker_name == "Edel":
    content = text  # direct, no prefix needed (Edel is default)
elif speaker_name:
    content = f"[Konuşan: {speaker_name}] {text}"
```

### System Prompt Extension
```
Eğer konuşan kişi Edel değilse (örn. "[Tanımadık]" etiketi varsa):
- Daha mesafeli ve kibar ol
- Kişisel bilgi paylaşma
- Vanitas kimliğini açıklama, sadece "bir sesli asistan" de
- Sadece genel bilgi ver

Eğer konuşan Edel ise:
- Samimi, sıcak, kendin ol
- Tüm yeteneklerini kullan
```

## Part 3: Multi-Speaker Analysis

When Edel is with other people, Vanitas can:
1. **Track each speaker separately** — different conversation history per speaker
2. **Only respond to Edel** unless Edel introduces someone
3. **Analyze group dynamics** — who talks more, who asks questions
4. **Adapt tone** — formal with strangers, casual with Edel's friends

### Implementation Considerations
- **Barge-in:** When stranger speaks during Vanitas's TTS, should we still interrupt? Only for Edel?
- **Privacy:** Don't store stranger voiceprints. Diarization labels are session-local (no biometric data).
- **LLM context:** Limit conversation history per speaker to control token count.

## File Locations

| Component | Path | Status |
|-----------|------|--------|
| Voiceprint service | `~/voice-agent-venv/voiceprint_service.py` | Built (needs restart) |
| Enrollment tool | `~/voice-agent-venv/voiceprint_enroll.py` | Built |
| Edel's voiceprint | `~/voice-agent-venv/edel_voiceprint.npy` | Enrolled (may need refresh) |
| MFCC reference | `references/voice-fingerprint-mfcc.md` | Documented |
| Hybrid architecture | `references/voiceprint-hybrid-architecture.md` | Documented |
| Soniox diarization docs | https://soniox.com/docs/stt/concepts/speaker-diarization | Read |

## Recommended Implementation Order
1. Enable Soniox diarization (1 line) — get speaker IDs immediately
2. Add speaker field to TranscriptionMessage and session log
3. Start voiceprint service (port 5050) — verify it's running
4. Cross-validate: Soniox speaker_1 vs MFCC Edel match
5. Pass speaker identity to LLM context
6. Update system prompt for stranger behavior