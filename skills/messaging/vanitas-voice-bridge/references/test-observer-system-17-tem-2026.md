# Vanitas Voice Test Observer System — 17 Temmuz 2026

## Architecture

```
Her WebSocket Session
  │
  ├─ session_recorder.py (ALWAYS ON — no toggle)
  │   ├── /tmp/vanitas-test-logs/<session_id>/
  │   │   ├── mic.wav           # Kullanıcı sesi (16kHz mono PCM→WAV)
  │   │   ├── tts.wav           # Vanitas cevabı (24kHz mono PCM→WAV)
  │   │   ├── transcript.txt    # Zaman damgalı konuşma dökümü
  │   │   └── session.json      # Yapılandırılmış metadat
  │
  └─ voice_test_analyzer.py (manual / cron)
      ├── --hours 24     → son 24 saat raporu
      ├── --all          → tüm kayıtlar
      ├── --session <id> → tek session derin analiz
      └── --watch        → sürekli izleme modu
```

## session.json Fields

```json
{
  "session_id": "uuid",
  "status": "success|partial|degraded|failed|silent|in_progress",
  "duration_seconds": 12.5,
  "user_audio_seconds": 3.2,
  "tts_audio_seconds": 1.8,
  "connection_quality": "excellent|good|fair|poor|no_response|disconnected",
  "vad_events": {"speech_starts": 2, "speech_ends": 1},
  "llm_metrics": {"first_token_ms": 320, "total_ms": 1450},
  "stt_metrics": {"transcription_count": 3, "endpoint_count": 1},
  "errors": [{"time_offset": 5.2, "message": "STT timeout"}],
  "transcript_sentences": [
    {"time_offset": 0.5, "speaker": "user", "text": "Merhaba Vanitas"},
    {"time_offset": 2.1, "speaker": "vanitas", "text": "Merhaba Edel, nasilsin?"}
  ]
}
```

## Status Meanings

| Status | Anlamı | Kriter |
|--------|--------|--------|
| success | ✅ Sorunsuz | LLM total_ms var, hata yok |
| partial | 🟡 Kısmen | STT var ama LLM yok / TTS yok |
| degraded | 🟠 Sorunlu | Hata var ama kritik degil |
| failed | 🔴 Basarisiz | Kritik hata (timeout, STT crash) |
| silent | ⚫ Sessiz | Hic transkripsiyon alinamadi |
| in_progress | 🔄 Devam ediyor | Henuz kapanmamis |

## Anomaly Detection (Automatic)

| Anomali | Dedektor | Cozum |
|---------|----------|-------|
| Ses yok | status=silent + VAD var | AudioWorklet/getUserMedia sorunu |
| VAD loop | speech_starts>1 ve speech_ends=0 | Echo loop (GainNode eksik) |
| STT var LLM yok | transcription_count>0 ve total_ms=null | LLM timeout / API hatasi |
| LLM var TTS yok | total_ms var tts_audio < 1s | TTS baglanti sorunu |
| LLM >5sn | total_ms > 5000 | Model yavas / tool_choice auto |

## Commands

```bash
cd ~/vanitas-web/soniox-server
python3 voice_test_analyzer.py              # son 24 saat
python3 voice_test_analyzer.py --all        # tum kayitlar
python3 voice_test_analyzer.py --session <id>  # tek session
python3 voice_test_analyzer.py --watch      # surekli izleme
```
