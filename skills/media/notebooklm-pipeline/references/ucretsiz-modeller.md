# Ücretsiz/Ajans Model Konfigürasyonu (4 Haz 2026)

## APA Pipeline — Önerilen Konfigürasyon

### Cron Job Modeli
| Parametre | Değer | Neden? |
|-----------|-------|--------|
| Model | gpt-5.4-mini | Türkçe kalitesi en iyi, ücretsiz |
| Provider | pollinations | Port 19999 üzerinden |

### Analist (Makale Tarama)
| Parametre | Değer | Neden? |
|-----------|-------|--------|
| Birincil | mimo-v2.5-free (Zen) | API keysiz, 0 reasoning, iyi Türkçe |
| Yedek | nemotron-3-super-free (Zen) | NVIDIA, 0 reasoning |
| Fallback | GPT-5.4-mini (Pollinations) | GLM boş dönerse |
| Endpoint | `https://opencode.ai/zen/v1` | WARP üzerinden, ALL_PROXY gerektirmez |
| ⚠️ WARP | Oracle Cloud'da ZORUNLU | Zen direkt 403 döner |

### Yazar (Türkçe Özet)
| Parametre | Değer | Neden? |
|-----------|-------|--------|
| Model | gpt-5.4-mini | En doğal Türkçe, 388 token yeterli |
| Provider | Pollinations | Port 19999, ~3.3s |
| max_tokens | 1500 | 800 yetersiz, 1500 daha uzun/bağlamsal |

## GPT-5.4-mini APA Test Sonucu (4 Haz 2026)

Test edildi: "Youth Mental Health Summit" makalesi Türkçe özet

| Kriter | Sonuç |
|--------|-------|
| Ana Fikir | 2-3 cümle, argümanlı ✅ |
| Özet | ~150 kelime, akıcı ✅ |
| Kavramlar | Her biri açıklamalı 1-2 cümle ✅ |
| Türkçe | Kusursuz ✅ |
| Hız | 3.3 saniye |
| Token | 388 output / 150 input |

**Karşılaştırma:** Eski sistem (DeepSeek V4 Pro + Yazar GPT-5.4-mini iki aşamalı) çok daha pahalı ve aynı kalitedeydi. Doğrudan GPT-5.4-mini hem daha hızlı hem ücretsiz.

## Zen API Kullanım Notları

### Oracle Cloud Erişimi
- Direkt erişim: ❌ 403 Forbidden
- WARP SOCKS5 üzerinden: ✅ Çalışıyor
- Rate-limit: `FreeUsageLimitError` alınırsa 5-10 dk bekle
- Günde 3-5 çağrı için genelde yeterli

### En İyi Ücretsiz Modeller (WARP üzerinden)
| Model | İçerik | Türkçe | Not |
|-------|--------|--------|-----|
| mimo-v2.5-free | ✅ | ⭐⭐⭐ | Analist birincil |
| nemotron-3-super-free | ✅ | ⭐⭐⭐ | Yedek |
| minimax-m3-free | ✅ | ⭐⭐ | `<think>` raw döküyor |
| deepseek-v4-flash-free | ❌ | — | Reasoning boğuyor |
| big-pickle | ❌ | — | Aynı sorun |
| qwen3.6-plus-free | HATA | — | Ücretli oldu |

## Maliyet Karşılaştırması

| Konfigürasyon | Aylık Maliyet | Model |
|---------------|---------------|-------|
| Eski (APA + Gmail) | ~$24 | DeepSeek V4 Pro |
| Yeni (APA + Gmail) | ~$0 | GPT-5.4-mini (Pollinations) |
| Tasarruf | $24/ay | — |
