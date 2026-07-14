# Cron Job Model Optimizasyonu (4 Haz 2026)

## Keşif: GPT-5.4-mini Türkçe APA Özetlemede Mükemmel

Test edildi: APA "Youth Mental Health Summit" makalesi, GPT-5.4-mini (Pollinations, port 19999), max_tokens=500.

Sonuç: Ana fikir 2-3 cümle, özet ~150 kelime, kavramlar açıklamalı, Türkçe kusursuz, 3.3s latency, 388 token.

**Eski (DeepSeek V4 Pro):** $12/ay, 94K input token, yavaş
**Yeni (GPT-5.4-mini):** ~$0/ay, 150 token prompt, 3.3s

## Maliyet Karşılaştırması (APA Cron, günde 3 çalışma)

| Model | Provider | Günlük | Aylık |
|-------|----------|--------|-------|
| DeepSeek V4 Pro | deepseek | ~$0.41 | ~$12.30 |
| **GPT-5.4-mini** | **pollinations** | **~$0.001** | **~$0.03** |
| Zen mimo-v2.5-free | opencode.ai/zen | $0 | $0 (rate-limit'li) |

## Zen API Rate-Limit Deneyimi

Zen API (opencode.ai/zen/v1) 6 ücretsiz model sunar:
- `mimo-v2.5-free` (Analist için kullanılıyor)
- `deepseek-v4-flash-free`
- `qwen3.6-plus-free`
- `minimax-m3-free`
- `nemotron-3-super-free`
- `nemotron-3-ultra-free`

**Pitfall:** Oracle Cloud IP'si direkt erişemez → WARP SOCKS5 (127.0.0.1:1080) zorunlu.
**Rate-limit:** Günlük kota var, aşılınca `FreeUsageLimitError`. Günde 3 cron çağrısı için yeterli olabilir ama test edilmedi (test sırasında limit aşıldı).

## Önerilen Konfigürasyon

### APA/Gmail Cron Job'ları
```yaml
model: gpt-5.4-mini
provider: pollinations
```
Orkestrasyon için yeterli. Asıl iş EKİP curl sistemi üzerinden:
- 🔬 Analist: mimo-v2.5-free (Zen, WARP)
- ✍️ Yazar: GPT-5.4-mini (Pollinations, direkt)

### IG Takip Kontrol
no_agent=true script, sadece curl → Instagram API. Gerçek maliyet $0.
Session tracking'te görünen maliyet artefakt'tır.

## Toplam Tasarruf

Eski: ~$51/ay (DeepSeek V4 Pro tüm cron job'larda)
Yeni: ~$5/ay (sadece IG script session tracking artefakt'ları)
Net tasarruf: ~$46/ay (%90)
