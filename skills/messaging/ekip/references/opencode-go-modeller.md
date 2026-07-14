# OpenCode Go Model Karşılaştırması (2 Haz 2026)

## Test Koşulları
- Prompt: "Top 3 AI safety concerns 2026? Short."
- max_tokens: 500 (kimi-k2.6 hariç, GLM-5.1 fixed test 2000)
- Proxy: OpenCode Go :19998, Pollinations :19999 (GPT-5.4-mini)
- Tarih: 2 Haziran 2026

## Sonuç Tablosu

| Model | Port | Reasoning | Content | Finish | Süre | Güvenilirlik |
|-------|------|-----------|---------|--------|------|-------------|
| **minimax-m2.7** | 19998 | 0 chars | 429 chars | stop | ~25s | ⭐⭐⭐ Analist birincil |
| **GPT-5.4-mini** | 19999 | 0 chars | 367 chars | stop | ~10s | ⭐⭐⭐ Yazar birincil |
| GLM-5.1 (fixed) | 19998 | 2883 chars | 258 chars | stop | ~40s | ⭐⭐ Yedek |
| kimi-k2.6 | 19998 | 0 chars | 2399 chars | length | ~25s | ⭐ Kullanma |
| qwen3.7-max | 19998 | — | HATA | — | — | ❌ Bozuk |
| GLM-5 (fixed) | 19998 | 1567 chars | 0 chars | length | ~30s | ❌ Kullanma |
| GLM-5.1 (eski) | 19998 | — | TIMEOUT | — | >120s | ❌ Fix gerek |

## GLM-5.1 Root Cause

OpenCode GitHub Issue [#16903](https://github.com/anomalyco/opencode/issues/16903):
- v1.1.46+'da `extractReasoningMiddleware` kaldırıldı (PR [#11270](https://github.com/anomalyco/opencode/pull/11270))
- `<think>` tag'leri context window'u kirletiyor → TUI bozuluyor, model takılı kalıyor
- **Workaround:** temperature=1.0 + timeout=300000

## Config Hatası

`compaction: "auto"` string değeri `opencode stats` komutunda:
```
Error: Configuration is invalid - Expected object | undefined, got "auto" compaction
```
**Fix:** `"compaction": {"mode": "auto"}`

## Önerilen EKİP Model Atamaları

| Ajan | Birincil Model | Yedek Model | Platform |
|------|---------------|-------------|----------|
| Analist | minimax-m2.7 | GLM-5.1 (fixed) | OpenCode Go :19998 |
| Yazar | GPT-5.4-mini | — | Pollinations :19999 |
| Kodcu | minimax-m2.7 | DeepSeek V4 Pro | OpenCode Go / Ana model |
| Yardımcı | gemma-4-26b | — | Pollinations :19999 |

## Pitfall Özeti

1. **OpenCode Go reasoning modelleri** (glm-5.1, deepseek-v4-*) max_tokens < 500'de content boş döner — reasoning tüm token'ları yer.
2. **minimax-m2.7 istisna** — OpenCode Go'da 0 reasoning, direkt content. En güvenilir.
3. **GLM-5.1 temperature fix** — temperature=1.0 stabilite sağlar ama hala ~3000 chars reasoning tüketir.
4. **Paralel fallback pattern** — Analist görevlerini hem minimax-m2.7 hem GPT-5.4-mini ile paralel başlat, ilk biteni kullan.
