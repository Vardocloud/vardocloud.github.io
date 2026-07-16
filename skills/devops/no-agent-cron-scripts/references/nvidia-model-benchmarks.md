# NVIDIA Model Benchmark (16 Tem 2026, rev. 3)

Endpoint: `https://integrate.api.nvidia.com/v1`
API: OpenAI-compatible (chat.completions)
API key env: `NVIDIA_API_KEY`

## Web Sitesi Doğrulaması (build.nvidia.com, 16 Tem 2026)

NVIDIA'nın model kataloğunda `Free Endpoint` etiketi taşıyan **73 model** bulunuyor (toplam 138 model). Ancak listede olması = API'den yanıt alınabilmesi anlamına gelmez.

| Model | Site'de Free | API'de Var | Çalışıyor | Sürpriz |
|-------|:-----------:|:----------:|:---------:|---------|
| `z-ai/glm-5.2` | ✅ (8M indirme) | ✅ | ❌ Timeout | ⚠️ Listedeki en büyük sürpriz |
| `minimaxai/minimax-m3` | ✅ | ✅ | ✅ (13sn) | |
| `mistralai/mistral-small-4-119b-2603` | ✅ | ✅ | ✅ (0.9sn) | |
| `deepseek-ai/deepseek-v4-flash` | ✅ | ✅ | ✅ (1.1sn) | |
| `meta/llama-3.3-70b-instruct` | ✅ | ✅ | ❌ Timeout | timeout |
| `nvidia/nemotron-3-ultra-550b-a55b` | ✅ | ✅ | ❓ test edilmedi | |

GLM-5.2 özel durumu: build.nvidia.com'da "Free Endpoint" etiketiyle listelenmiş, Z.ai tarafından yayınlanmış, 8M indirme. API model listesinde `z-ai/glm-5.2` olarak mevcut. Ancak API çağrısı 100sn+ timeout yiyor. Muhtemelen Z.ai'nin kendi endpoint'inden NVIDIA'ya geçişte altyapı sorunu var.

## Test Sonuçları — Küçük Prompt (max_tokens=5, "1+1?")

| Model | Süre | Cron (120sn) | Not |
|-------|------|:---:|------|
| `nvidia/nemotron-mini-4b-instruct` | 0.9s | ✅ | En hızlı, minik işler |
| `meta/llama-3.2-3b-instruct` | 1.1s | ✅ | Hızlı, küçük işler |
| `mistralai/mistral-small-4-119b-2603` | **0.9s** | ✅ | ⭐ En güvenilir |
| `deepseek-ai/deepseek-v4-flash` | 1.1s | ✅ | Orijinal sentez modeli |
| `minimaxai/minimax-m3` | **13s** | ✅ | Yavaş ama Edel onaylı |
| ~~`meta/llama-3.3-70b-instruct`~~ | 47s timeout | ❌ | **ÇALIŞMIYOR** (timeout) |
| ~~`z-ai/glm-5.2`~~ | 47s timeout | ❌ | **ÇALIŞMIYOR** (timeout — sitede Free Endpoint yazsa da) |
| `mistralai/ministral-14b-instruct-2512` | 138s timeout | ❌ | Çok yavaş |

## Günlük Sentez Full Context Testi

Script: `gunluk_sentez.py` — ~13 haber dosyası + 7 gün öğrenme geçmişi + şema

| Model | Süre | Çıktı | Durum |
|-------|------|-------|:-----:|
| `mistralai/mistral-small-4-119b-2603` | ~30-60sn | 10,719 karakter sentez | ✅ Çalışıyor |
| `deepseek-ai/deepseek-v4-flash` | ~82sn | 2,989 karakter (test) | ✅ Çalışıyor |
| `minimaxai/minimax-m3` | >139sn (zaman aşımı) | - | ❌ Full context'te timeout |
| `meta/llama-3.3-70b-instruct` | ~40-80sn | 2,050 karakter sentez | ⚠️ Çalışır ama Türkçesi zayıf |

Not: MiniMax M3 küçük prompt'ta 13sn'de yanıt verse de **full context'te 120sn cron limitini aşar** — günlük sentez için uygun değil. Ancak ekonomi bültenleri gibi daha dar context'li işlerde kullanılabilir.

## Ekonomi Bültenleri İçin Model Kararları (16 Tem 2026)

Edel'in seçimi:
- `nvidia-free-m3` (`minimaxai/minimax-m3`) — **Ekonomi Sabah + Akşam** ✅ (yavaş ama önemli değil, cron'da çalışır)
- `nvidia-free-mistral-small` (`mistralai/mistral-small-4-119b-2603`) — **Günlük Sentez** (Edel test etmedi ama hızlı ve güvenilir)
- `nvidia-free-deepseek-flash` (`deepseek-ai/deepseek-v4-flash`) — alternatif, orijinal sentez modeli

**NVIDIA'da çalışmayan modeller (agent job için):**
- ~~`z-ai/glm-5.2`~~ — timeout, GLM 5.2 opencode-go üzerinden kullanılır
- ~~`meta/llama-3.3-70b-instruct`~~ — timeout, Türkçesi zayıf

## Provider Model Whitelist — Agent Job vs no_agent Script

NVIDIA provider `discover_models: false` ile yapılandırılmıştır.

- **no_agent script (direkt OpenAI API çağrısı):** ✅ Herhangi bir model çalışır (provider listesini bypass eder)
- **Agent job (Hermes provider routing):** ❌ Sadece `models:` listesindekiler çalışır. Listedekilerin hepsi de fiilen çalışmaz (GLM 5.2, Llama 3.3 timeout).

**Agent job'da bir model kullanmadan önce MUTLAKA şunları kontrol et:**
1. `config.yaml` → `custom_providers` → NVIDIA → `models:` listesinde var mı?
2. Küçük prompt'la 15sn timeout'lu test et (GLM-5.2 listede olmasına rağmen timeout yiyor)
3. Cron job'un schedule'ına göre süre uygun mu? (ekonomi sabah/akşam için M3'ün 139sn'si sorun değil)

## Dersler

1. **Modelin "Free Endpoint" etiketi taşıması yetmez** — her modeli API'den fiilen test etmek şart
2. **Mistral Small 4 (119B)** en güvenilir NVIDIA modeli — hem hızlı hem kaliteli
3. **MiniMax M3** yavaş ama çalışır — Edel onaylı ekonomi modeli
4. **Llama 3.3 70B ve GLM 5.2 NVIDIA'da timeout** — kullanma, açık değiller
5. **GLM 5.2** opencode-go üzerinden (`glm-5.2`) çalışır — voice agent ve Türkçe işler için
6. **Agent job model seçerken:** listede olması yetmez, API testi şart
