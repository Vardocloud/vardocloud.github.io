# NVIDIA NIM Free Tier — Model Durumu (14 Tem 2026)

## Katalog (121 model)

```bash
curl -s https://integrate.api.nvidia.com/v1/models
```

## DeepSeek Modelleri

| Model | Katalog | Free Tier | Completion Test |
|-------|---------|-----------|----------------|
| `deepseek-ai/deepseek-v4-flash` | ✅ Var | ✅ Free tier'da | ❌ Test edilmedi (önceki 503) |
| `deepseek-ai/deepseek-v4-pro` | ✅ Var | ❌ Muhtemelen ücretli | ❌ Test edilmedi |

## Test Edilip Çalışan Modeller

| Model ID | Çıktı Dili | Süre | Not |
|----------|-----------|------|-----|
| `meta/llama-3.3-70b-instruct` | EN/TR | Hızlı | Config'de `nvidia-llama-3.3-70b` alias'ı ile mevcut |
| `minimaxai/minimax-m3` | EN (Türkçe input'ta) | Normal | Decomposition JSON çıktısı başarılı |
| `mistralai/mistral-nemotron` | - | Timeout | Çok yavaş, cron için uygun değil |

## Decomposition Test (14 Tem 2026)

İki model aynı prompt ile test edildi: "BIST analizini güncelle" (Türkçe input) → İngilizce decomposition.

**DeepSeek V4 Flash (opencode-go proxy, 127.0.0.1:19998):**
- 5 task çıkardı ✅
- İngilizce output ✅
- Veri çek → 3 paralel analiz (supp/res, MACD, RSI) → rapor
- Çok hızlı (lokal proxy, gecikme yok)

**MiniMax M3 (NVIDIA API, integrate.api.nvidia.com/v1):**
- 5 task çıkardı ✅
- İngilizce output ✅
- MACD+RSI'yi tek task'ta birleştirmiş
- NVIDIA API üzerinden çalışıyor (network gecikmesi var)

**Değerlendirme:** DeepSeek V4 Flash decomposition için daha uygun — MIT lisansı, 13B aktif, lokal proxy'den hızlı, güçlü reasoning. NVIDIA'da free tier'da completion test edilmeli.

## Önemli Notlar

- `deepseek-ai/deepseek-v4-flash` daha önce "503 ResourceExhausted" dönmüştü — free tier kotası dolduğu için. Farklı zamanda tekrar test et.
- Decomposer text-only'dir → multimodal model avantaj sağlamaz.
- Türkçe kalitesi: DeepSeek > MiniMax M3 > llama-3.3-70b > nemotron-70b
