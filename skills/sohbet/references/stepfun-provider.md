# StepFun Provider — LiteRouter (20 Haz 2026 Güncel)

## Aktif Provider: LiteRouter ✔️

- **Base URL:** `https://api.literouter.com/v1`
- **Script:** `~/.hermes/scripts/stepfun_evaluator.py`
- **Model:** `deepseek-v3.2:free`
- **API Key:** Bitwarden secret ID `673ec835-9f80-4200-8e55-b46f00ecc30d` → `/tmp/.or_key`
- **ALL_PROXY=""** zorunlu

### Neden LiteRouter?
| Sorun | Routeway | LiteRouter |
|-------|----------|------------|
| deepseek 502 | Her seferde | Çalışıyor |
| Free model sayısı | 2 çalışan / 19 toplam | 19, tamamı erişilebilir |
| Rate limit (free) | 5 RPM / 200 RPD | Unlimited (1 req/5sn soft) |
| JSON output | step-3.5-flash'ta regex gerekiyordu | deepseek-v3.2'de resmi destek |
| Content boş sorunu | step-3.5-flash reasoning (hep boş) | deepseek-v3.2 non-thinking (dolu) |

### deepseek-v3.2:free Detayları
- DeepSeek V3.2, DeepSeek ailesi — Türkçede en başarılı modellerden
- Non-thinking mod → content her zaman dolu
- JSON `response_format` resmi olarak destekleniyor
- GPT-5 seviyesinde benchmark
- "Thinking in Tool-Use" ile reasoning + JSON birlikte çalışabiliyor

### Önemli Kod Değişiklikleri
1. **Base URL:** `https://api.routeway.ai/v1` → `https://api.literouter.com/v1`
2. **Model:** `step-3.5-flash:free` → `deepseek-v3.2:free`
3. **Reasoning regex extraction kaldırıldı:** Content dolu geldiği için direkt JSON parse yeter
4. **Markdown code block temizleme eklendi:** Bazen ````json` içinde gelebiliyor
5. **max_tokens:** 8000 → 4000 (non-thinking modelde 4000 yeterli)

### Olası Fallback Modeller
| Model | Ne Zaman? |
|-------|-----------|
| `grok-4.1-fast-reasoning:free` | deepseek 502/504 verirse (reasoning kapatılabilir) |
| `mistral-small-24b-instruct-2501:free` | Grok da çalışmazsa |
| `gemma-3-27b-it:free` | Son çare (140+ dil, Türkçe muhtemelen iyi) |

---

## Geçmiş Provider'lar (Tarihçe)

### Routeway (19-20 Haziran 2026)
Çalışan free model: sadece `step-3.5-flash:free` (reasoning, content boş). 
Sebep: deepseek-v4-flash:free ve diğer 13 model 502 Bad Gateway (Cloudflare upstream bağlantı sorunu, free tier düşük öncelik).
Kullanılamaz hale gelince LiteRouter'a geçildi.

### OpenRouter (31 Mayıs - 8 Haziran 2026)
StepFun modelleri ücretsizken kullanılıyordu. 8 Haziran'da her yerde ücretli oldu.
`openai/gpt-oss-120b:free` alternatifi denendi ama o da Routeway'de 502 verdi.
API key bakiyesi tükendiği için Routeway'e geçilmişti.

### Zenmux (8 Haziran 2026 - kısa süreli)
`sk-ai-v1-...` key ile PAYG. StepFun modelleri ücretli, bakiye gerekli.
Hızla Routeway'e geçildi.
