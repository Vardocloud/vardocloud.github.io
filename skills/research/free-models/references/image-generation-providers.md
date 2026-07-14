# Image Generation Provider Durumu (14 Tem 2026)

Pollinations terk edildikten sonra boşluğu doldurmak için test edilen sağlayıcılar.

## Test Edilen Sağlayıcılar

| Sağlayıcı | Durum | HTTP | Sebep |
|-----------|-------|------|-------|
| **HuggingFace Inference API** | ❌ | DNS | `api-inference.huggingface.co` adresine Docker/WSL'den erişim yok (Name or service not known). Key BWS'de: `hf_pul...Kxni` |
| **OpenRouter (Gemini/GPT image)** | ❌ | 401 | API key geçersiz/süresi dolmuş. BWS'de: `37ca1b49...` |
| **Pexels (stok foto)** | ❌ | 403 | API key süresi dolmuş. BWS'de: `KOKr85t9muWH...` |
| **Fireworks AI** | ❌ | 412 | Key sorunu. BWS'de: FIREWORKS_AI_API_KEY |
| **Mistral AI** | ❌ | — | API format hatası |
| **NVIDIA NIM** | ❌ | — | Image generation modeli yok, sadece LLM |

## Çalışan Provider'lar (LLM için)

| Sağlayıcı | Durum | Kullanım |
|-----------|-------|----------|
| **NVIDIA** | ✅ | LinkedIn sabah cron (minimax-m3) |
| **LiteRouter** | ✅ | deepseek-v3.2:free |
| **opencode-zen** | ❌ Bozuk | content boş döner |
| **Groq** | ✅ | Whisper transkripsiyon, vision |

## Önerilen Çözümler

### Segmind (ÖNERİLEN — 100 image/gün ücretsiz)
- Kayıt: https://www.segmind.com/
- Free tier: 100 image/gün, Flux, SDXL, SSD-1B
- API: REST + OpenAI-compatible
- Pipeline: prompt → Segmind API → /tmp/gorsel.jpg → linkedin_api.py create_post(image_path=...)

### OpenRouter Kredi Yükleme
- Gemini 3.1 Flash Lite Image: $0.00000025/prompt (çok ucuz)
- GPT-5 Image Mini: $0.0000025/prompt
- Minimum $5 yükleme, aylarca yeter

### Unsplash (API key gerekmez)
- Hazır stok foto, RSS feed
- URL: https://source.unsplash.com/1200x628/?psychology,calm
- Dezavantaj: özgün değil, aynı görsel başkalarında da var
