# faster-whisper STT — Test & Performance Notes

## Installation
System-level pip3 (not Hermes venv): `pip3 install faster-whisper`

## Performance (Oracle ARM64 CPU, 2026-05-26)
| Metric | Value |
|--------|-------|
| Model | small (int8, CPU) |
| Model load | ~19s |
| Transcription speed | ~3x realtime |
| Language confidence (Turkish) | 1.00 |
| RAM | ~1GB |

## Testing Checklist
1. DO NOT test with TTS → STT loop. Synthetic audio is too clean — always passes, false confidence.
2. Valid tests:
   - **YouTube**: Download audio from a real video, transcribe, compare
   - **Voice message**: Edel sends real voice message → STT transcribes
3. Turkish transcription quality is excellent — punctuation added naturally, minor word expansions (e.g., "harikaydı" → "harika idi") are normal.

## Model Cache
First run downloads from HuggingFace (~500MB).
Cache: `~/.cache/huggingface/hub/models--Systran--faster-whisper-small/`

## OpenWebUI
Docker env: `WHISPER_MODEL=small`, `WHISPER_MODEL_DIR=/app/backend/data/cache/whisper/models`
