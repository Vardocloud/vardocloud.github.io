# NVIDIA NIM Free Tier — Research Notes (14 Tem 2026)

## Kaynaklar
- build.nvidia.com — 140 model, 76'si "Free Endpoint"
- API: https://integrate.api.nvidia.com/v1 (OpenAI-compatible)
- Free tier: no credit card, 40 RPM, 1K inference credits

## 3 Ayrı Limit Katmanı

| Limit | Değer | HTTP | Geçici? |
|-------|-------|------|---------|
| RPM (account) | ~40/dk | 429 | 1dk bekle |
| Worker queue (model) | 32-48 | 503 ResourceExhausted | Evet, retry |
| Inference credits | 1K-5K | 402 | Hayır, kredi gerek |

## Test Edilmiş Modeller

### GLM 5.2 (z-ai/glm-5.2) — EN STABİL
- 20/20 burst: %100 başarı
- Ortalama süre: ~2.0s (0.8s-7.8s)
- Worker/rpm limiti: tetiklenmedi
- **Tavsiye:** NVIDIA free tier'da kullanılacak en güvenilir model

### MiniMax M3 (minimaxai/minimax-m3)
- 4/5 başarılı (%80)
- Arada "500 Internal Server Error" düşürüyor
- Ortalama süre: 2.3-9.8s (yavaş)
- Worker limiti: tetiklenmedi

### DeepSeek V4 Flash (deepseek-ai/deepseek-v4-flash)
- ❌ 503 ResourceExhausted: Worker local total request limit reached (48/48)
- Bu geçici bir overload, kalıcı limit değil
- GitHub'da doğrulanmış: transient error, retry ile düzelir
- Popüler model olduğu için worker sürekli dolu

### Llama 3.3 70B (meta/llama-3.3-70b-instruct)
- Test: ✅ Çalışıyor, hızlı
- Tavsiye: GLM 5.2'den sonra ikinci tercih

### Mistral Nemotron (mistralai/mistral-nemotron)
- ❌ HTTP 500 Internal Server Error (kalıcı)

## Önemli Notlar

1. **Worker limiti kalıcı değil** — retry et, kuyruk boşalınca düzelir
2. **Model bazlı limitler** — DeepSeek V4 Flash overload iken GLM 5.2 rahat çalışıyor
3. **40 RPM günlük karşılığı** — 57.600 request/gün teorik max. Bizim kullanımımızda ~100 request/gün = limitin %0.2'si
4. **Aylık abonelik YOK** — NVIDIA NIM'de ChatGPT Plus benzeri bir ürün bulunmaz. Sadece free tier veya $4,500/GPU/yıl AI Enterprise (self-host).
