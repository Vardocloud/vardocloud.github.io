# STT Model Karşılaştırması (Türkçe)

Vanitas Voice Agent için test edilen STT modelleri.

## Özet

| Model | Nerede | TR Kalitesi | Gecikme | Ücret | Tavsiye |
|-------|--------|-------------|---------|-------|---------|
| faster-whisper small | Lokal CPU | ✅ İyi | ~1-2sn | Ücretsiz | **Kullan** |
| Pollinations Whisper | Pollinations API | ❌ Kötü | ~2-3sn | Polen | Kullanma |
| universal-3-pro | Pollinations API | ? | ? | ? | 401 auth |
| Deepgram nova-3 | Deepgram API | ✅ İyi | ~200ms | API kotası | Timeout sorunu |
| Deepgram Aura-2 | Deepgram Agent | N/A (TTS) | - | - | TR desteklemez |

## faster-whisper small (AKTİF)

- Model: Systran/faster-whisper-small
- CPU'da int8 quantize, ~1.5GB RAM
- İlk yükleme 9sn, sonraki çağrılar ~1-2sn
- `language="tr"` ile iyi sonuç
- beam_size=5 yeterli

## Pollinations Whisper (PITFALL)

- 2026-06-16 test: "Merhaba ben Edel nasılsın" → "Merhaba, ben Edel. Nasılsın?" (tek kelimede iyi)
- **Uzun cümlelerde**: "Edel" → "altyazı M.K." gibi uydurma yapıyor
- Neden: Muhtemelen whisper-small veya daha küçük model, Türkçe fine-tuning yok
- Sonuç: Sesli görüşme için güvenilmez

## universal-3-pro

- Pollinations /v1/models listesinde var
- `/v1/audio/transcriptions` endpoint'inde model adı geçerli
- Ama HTTP 401 dönüyor: "Authentication required"
- Pollinations API key ile erişilemiyor — muhtemelen ek ücret/onay gerekiyor
- Araştırılacak: AssemblyAI kendi API key'i ile mi çalışıyor?
