# Groq Whisper Rate Limit — 7200 sn/saat

## Limit Detayı

Groq `whisper-large-v3` API'si **On-Demand tier**'da saatlik ses limiti uygular:

| Parametre | Değer |
|-----------|-------|
| Limit türü | ASPH (Audio Seconds Per Hour) |
| Limit | **7200 saniye** |
| Pencere | Rolling 1 saat |
| Her chunk | 1200 saniye (20 dk) |
| Max chunk/saat | 6 chunk |
| Tier | On-Demand |

## Hata Mesajı

```
Rate limit reached for model `whisper-large-v3` in organization
`org_01jmzghpf1e9vvg42vgqgc4e0p` service tier `on_demand` on
seconds of audio per hour (ASPH): Limit 7200, Used 6619,
Requested 1200. Please try again in 5m9.5s.
```

## Recovery Stratejisi

1. **Hatayı oku:** `Try again in Xm.Xs` süresini not et
2. **Gerekiyorsa bekle:** O süre kadar bekle
3. **Devam et:** Kalan chunk'ları transkript et
4. **Planlama:** 5+ chunk'lık işlerde ya saat başını bekle ya da 6 chunk/saat ile sınırla

## 20 Tem 2026 Vakası

| İşlem | Chunk | Süre | Kalan Limit |
|-------|-------|------|-------------|
| APA EBSA (önceden) | 3 chunk | 3600 sn | 3600 sn |
| APA EBSA (tekrar en) | 3 chunk | 3600 sn | 0 sn (estimated) |
| APA Mentoring chunk_000 | 1 chunk | 1200 sn | ~581 sn |
| APA Mentoring chunk_001 (red) | - | - | Limit aşıldı, 5dk bekle |

Not: Kesin kullanım API yanıtındaki `Used X` değerinden okunur.
