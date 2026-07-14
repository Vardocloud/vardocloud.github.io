# NVIDIA NIM Free Tier — Model Durumu (14 Tem 2026)

## Katalog (121 model)

```bash
curl -s https://integrate.api.nvidia.com/v1/models
```

## 3 Katmanlı Rate Limit Sistemi

| Limit Türü | Değer | Hata Kodu | Geçici mi? |
|---|---|---|---|
| RPM (per account) | ~40 request/dk | `429 Too Many Requests` | ✅ 1dk bekle |
| Worker queue (per model) | 32-48 kuyruk | **`503 ResourceExhausted`** | ✅ Retry ile düzelir |
| Inference credits | 1.000 (5.000 talep) | `402 Payment Required` | ❌ Kredi gerek |

**Worker Local Total Request Limit (48/48):** Modelin worker instance'ı dolu. Retry et — worker işledikçe kuyruk boşalır. GitHub'da doğrulanmış: transient, not permanent.

## DeepSeek Modelleri

| Model | Katalog | Free Tier | Completion Test | Sonuç |
|---|---|---|---|---|
| `deepseek-ai/deepseek-v4-flash` | ✅ Var | ✅ Free tier | ❌ 503 ResourceExhausted (48/48) | Worker dolu — farklı zaman dene |
| `deepseek-ai/deepseek-v4-pro` | ✅ Var | ⚠️ Muhtemelen ücretli | ❌ Test edilmedi | |

## Test Edilip Çalışan Modeller

| Model ID | Çıktı Dili | HTTP | Not |
|---|---|---|---|
| `meta/llama-3.3-70b-instruct` | EN/TR | ✅ 200 | Config'de `nvidia-llama-3.3-70b` alias'ı ile mevcut |
| `minimaxai/minimax-m3` | EN (TR input) | ✅ 200 | Decomposition JSON çıktısı başarılı |
| `z-ai/glm-5.2` | EN | ✅ 200 | Çalışıyor, hızlı |
| `mistralai/mistral-nemotron` | - | ❌ 500 | Internal server error |
| `deepseek-ai/deepseek-v4-flash` | - | ❌ 503 (48/48) | Worker queue full |

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

**Değerlendirme:** DeepSeek V4 Flash decomposition için daha uygun — MIT lisansı, 13B aktif, lokal proxy'den hızlı, güçlü reasoning. NVIDIA'da free tier'da worker queue limitine takıldı (48/48). Retry edilebilir.

## Önemli Notlar

- `deepseek-ai/deepseek-v4-flash` → **503 ResourceExhausted**: "Worker local total request limit reached (48/48)". Worker dolu, retry et. Kalıcı değil.
- Decomposer text-only'dir → multimodal model avantaj sağlamaz.
- Türkçe kalitesi: DeepSeek > MiniMax M3 > llama-3.3-70b > nemotron-70b
- Kritik bir task'ı NVIDIA free tier'a atamadan ÖNCE limitleri test et. Free tier güvenilir değil.
