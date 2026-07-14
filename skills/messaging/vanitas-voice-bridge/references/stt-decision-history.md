# STT Karar Geçmişi — Vanitas Voice Agent

## Pipeline Gecikmesi (5 Tem 2026)

| Adım | Servis | Süre | Not |
|------|--------|------|-----|
| VAD | Browser AnalyserNode | 1000ms | Sessizlik bekleme (ayarlanabilir) |
| STT | Groq Whisper `whisper-large-v3` | ~400ms | Ses uzunluğuna göre değişir |
| LLM | Groq `llama-3.3-70b` | ~250ms | Streaming |
| TTS | Edge TTS `EmelNeural` | ~1300ms | En büyük darboğaz |
| **Toplam** | | **~2950ms** | |

## STT Seçenekleri

### 1. Groq Whisper `whisper-large-v3` (CURRENT ✅)
- **Latency**: ~400ms (2sn ses için)
- **Maliyet**: $0 (Groq ücretsiz tier)
- **API Key**: Aynı GROQ_API_KEY ile çalışır
- **Model**: whisper-large-v3 veya whisper-large-v3-turbo
- **Endpoint**: POST /v1/audio/transcriptions (multipart/form-data)
- **Dil**: language=tr parametresi ile Türkçe
- **Not**: Deepgram'dan ~2.7x daha hızlı, ek API key gerektirmez

### 2. Deepgram Nova-2 (❌ REDDEDİLDİ — 5 Tem 2026)
- **Latency**: ~1100ms
- **Sorun**: v10'da format uyuşmazlığı nedeniyle terk edilmişti
- **Edel'in tepkisi**: "Biz deepgramdan çıkmıştık şimdi niye döndük"
- **Ders**: Eski versiyon kararlarını kontrol etmeden servis değiştirme

### 3. Soniox stt-rt-v5 (🎯 HEDEF)
- **Latency**: ~100-200ms (WebSocket, gerçek zamanlı)
- **Maliyet**: ~$0.12/saat (~$1.80/ay)
- **Durum**: API key bulunamadı (BWS/BW/.env'de yok)
- **Avantaj**: VAD beklemesi kalkar, anında transkripsiyon
- **SDK Seçenekleri**: 
  - `@soniox/react` (useRecording hook) — v13 hedefi
  - `@soniox/client` (JS SDK, browser-side) — v12 yazıldı/test edilmedi
- **Entegrasyon**: Browser → SonioxClient → Soniox API → text WS → Server

## TTS Seçenekleri

### 1. Edge TTS `tr-TR-EmelNeural` (CURRENT ✅)
- **Latency**: ~1300ms
- **Maliyet**: $0
- **Not**: CLI başlatma + dosya yazma overhead'i var

### 2. ElevenLabs Bella (🔶 KISMİ ÇALIŞIYOR)
- **Latency**: ~1080ms
- **Maliyet**: API key ücretli
- **Voice ID**: `pNInz6obpgDQGcFmaJgB`
- **Model**: `eleven_multilingual_v2`
- **Key Durumu**: BWS'de ELEVENLABS_API_KEY altında 2 key var:
  - İlki 401 (süresi dolmuş)
  - İkincisi çalışıyor
  - Kullanırken `.strip().split('\n')[1]` ile ikinci alınmalı

## PITFALL: BWS Secret İçinde Çoklu Değer

BWS secret değeri yeni satırla ayrılmış birden çok değer içerebilir:
```
sk_birinci...\nsk_ikinci...
```
Bu durumda ilk değer eski/geçersiz, ikincisi güncel olabilir.
**Çözüm:** Değeri `\n` ile ayır, her birini dene veya kullanıcıya hangisi olduğunu sor.
