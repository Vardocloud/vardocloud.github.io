# TTS Pricing Comparison (June 2026)

Edel'in sesli asistanı Vanitas için ücretsiz/ücretli TTS seçenekleri.

## Fiyat Karşılaştırması

| Servis | Fiyat/1K karakter | 5$ ile | Türkçe | Kalite |
|--------|------------------|--------|--------|--------|
| **Edge TTS** (tr-TR-EmelNeural) | 🆓 Ücretsiz | Sınırsız | ✅ Native | ⭐⭐⭐ (Edel: "robotik") |
| **Piper TTS** (dfki-medium) | 🆓 Ücretsiz | Sınırsız | ✅ tr_TR | ⭐⭐ (Edel: "kötü beğenmedim") |
| **ElevenLabs API** (pay-as-you-go) | $0.05/1K | ~100K karakter (~13 gün) | ✅ Native | ⭐⭐⭐⭐⭐ |
| **Fish Audio S2** | $0.015/1K | ~333K karakter (~1.5 ay) | ✅ 80+ dil | ⭐⭐⭐⭐ |
| **MiniMax Speech 2.8 Turbo** | $0.03/1K | ~166K karakter (~1 ay) | ✅ Native | ⭐⭐⭐⭐⭐ |
| **MiniMax Speech 2.8 HD** | $0.05/1K | ~100K karakter (~13 gün) | ✅ Native | ⭐⭐⭐⭐⭐ |
| **Pollinations ElevenLabs** (proxy) | ~6.4 pollen/call | 0.156 pollen kaldı ❌ | ✅ Native | ⭐⭐⭐⭐⭐ |

## Edel'in Tercihleri (2026-06-24)

- Edge TTS'i beğenmedi: "fazla robotik"
- Piper dfki'yi beğenmedi: "kötü beğenmedim"
- Ücretli opsiyonlara açık: "5$ ne kadar götürür?"
- MiniMax Speech 2.8 merak ediyor, API key Bitwarden'da ama bakiye yetersiz

## Ücretsiz Bulut Alternatifleri

| Servis | Türkçe | Limit | Kalite |
|--------|--------|-------|--------|
| **Edge TTS** (Microsoft) | tr-TR-EmelNeural, tr-TR-AhmetNeural | Sınırsız | ⭐⭐⭐ |
| **gTTS** | tr | Sınırsız | ⭐⭐ (robotik) |
| **Gemini API TTS** | Bilinmiyor | Free tier | ⭐⭐⭐⭐ |
| **Web Speech API** (tarayıcı) | tr-TR | Sınırsız, ücretsiz | ⭐⭐⭐ (tarayıcıya bağlı) |

## Açık Kaynak / Local Modeller

| Model | Türkçe | GPU | Boyut | Kalite | Lisans |
|-------|--------|-----|-------|--------|--------|
| **Piper dfki-medium** | ✅ tr_TR | CPU (ONNX) | 61MB | ⭐⭐ | CC BY-NC-SA 4.0 |
| **Meta MMS-TTS** (mms-tts-tur) | ✅ Turkish checkpoint | CPU (Transformers) | 277MB | ⭐⭐⭐⭐ | CC BY-NC 4.0 |
| **Coqui XTTS-v2** | ✅ 16 dil, voice cloning | GPU önerilir | 1.9GB | ⭐⭐⭐⭐⭐ | Coqui Public License |
| **Chatterbox-Turbo** | ✅ Turkish (community) | GPU (RTX 3060+) | ~2GB | ⭐⭐⭐⭐⭐ | MIT |

## MiniMax Speech 2.8 API

### Endpoint
`POST https://api.minimax.io/v1/t2a_v2`
Alternatif: `https://api-uw.minimax.io/v1/t2a_v2` (düşük gecikme)

### Authentication
`Authorization: Bearer <MINIMAX_API_KEY>`
Key Bitwarden'da: `MINIMAX_API_KEY` (secret ID: d50db310)

### Models
- `speech-2.8-turbo` — hızlı, düşük maliyet (~$30/1M)
- `speech-2.8-hd` — yüksek kalite (~$50/1M)
- `speech-02-hd`, `speech-02-turbo` — eski modeller

### Turkish Voice IDs
| ID | Ad | Cinsiyet |
|----|----|----------|
| `Turkish_CalmWoman` | Calm Woman | Kadın |
| `Turkish_Trustworthyman` | Trustworthy man | Erkek |

Sadece 2 Türkçe ses var. Source: `platform.minimax.io/docs/faq/system-voice-id`

### Request Body
```json
{
  "model": "speech-2.8-turbo",
  "text": "Türkçe metin",
  "voice_setting": {
    "voice_id": "Turkish_CalmWoman",
    "speed": 1,
    "vol": 1,
    "pitch": 0
  },
  "audio_setting": {
    "sample_rate": 32000,
    "bitrate": 128000,
    "format": "mp3",
    "channel": 1
  },
  "language_boost": "Turkish",
  "stream": false
}
```

### Pitfalls
- `language_boost: "Turkish"` veya `"auto"` kullanılabilir
- voice_id yoksa hata: `2054 voice id not exist`
- Bakiye yetersiz: `1008 insufficient balance`
- Response hex encoded audio: `data.audio` → `bytes.fromhex()` ile decode et
- Max 10.000 karakter/request
- Pause kontrolü: `<1.5>` (1.5 saniye bekleme)
- Interjection tags: `(laughs)`, `(sighs)`, `(coughs)` vb. (sadece speech-2.8 modellerinde)

## Fish Audio S2

### API
- Fiyat: $15/1M karakter (80+ dil)
- Ses klonlama: 10-30 saniye referans ses
- Türkçe ses örnekleri: fish.audio'da "Türkçe Erkek Ses" (1.499+ kullanıcı), "Turkish Deep Voice"
- Örnek metin: "Bir kurşun insan vücuduna girdiğinde..."
- Kadın sesi: Fish Audio'da Türkçe kadın sesi bulunamadı (2026-06-24 itibarıyla)

## Tavsiye (Edel İçin)

1. **Hemen:** Edge TTS (ücretsiz, çalışıyor) — en iyi ücretsiz seçenek
2. **Bütçeli:** MiniMax Speech 2.8'e $5 yükle (~1 ay) — Türkçe Calm Woman kadın sesi
3. **Uzun vadede:** ElevenLabs API ($5 = 13 gün, en kaliteli)
