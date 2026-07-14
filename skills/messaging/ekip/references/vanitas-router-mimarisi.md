# Vanitas Router Proxy Mimarisi — 5 Haz 2026

Vanitas'in kendi API cagrilarini gorev tipine gore farkli model/provider'lara yonlendiren akilli proxy.

## Motivasyon

- DeepSeek V4 Pro: Gunluk $2.22, aylik ~$67 (4.1M input + 0.48M output)
- DeepSeek V4 Flash: Gunluk $0.71, aylik ~$21 (%68 tasarruf)
- OpenCode Zen Free: $0 (7 ucretsiz model)
- Hedef: Sohbet+arastirmayi Zen Free'ye, kod/debug'u Flash'a, agir isleri Pro'ya → aylik ~$4-9

## Mimari

```
HERMES  →  ROUTER PROXY (:9999)  →  OpenCode Zen (free)
                                  →  DeepSeek API (paid)
```

Hermes tarafinda `custom_providers` ile tek provider olarak tanimlanir.
Router proxy OpenAI-compatible `/v1/chat/completions` endpoint'i sunar.

## Model Secim Mantigi

```python
TASK_PATTERNS = {
    "sohbet":    r"\b(naber|selam|nasilsin|iyi misin|tesekkur|tamam|olur|hayir)\b",
    "arastirma": r"\b(arastir|bul|ogren|nedir|kim|nerede|ne zaman|kac)\b",
    "kodlama":   r"\b(kod|yaz|fonksiyon|script|python|js|html|css|api|endpoint)\b",
    "debug":     r"\b(debug|hata|fix|duzelt|calismiyor|bozuk|sorun|bug)\b",
}

MODEL_MAP = {
    "sohbet":    "deepseek-v4-flash-free",   # Zen, $0
    "arastirma": "deepseek-v4-flash-free",   # Zen, $0
    "kodlama":   "deepseek-v4-flash",        # Zen/DeepSeek, $0.14
    "debug":     "deepseek-v4-flash",        # Zen/DeepSeek, $0.14
}
FALLBACK = "deepseek-v4-pro"  # DeepSeek, $0.435 — sadece gerektiginde
```

## Maliyet Projeksiyonu

Bugunku kullanim baz alinarak (4.1M input + 0.48M output/gun):

| Senaryo | Gunluk | Aylik | $5 suresi |
|:--|--:|--:|--:|
| DeepSeek V4 Pro (su an) | $2.22 | $67 | 2 gun |
| DeepSeek V4 Flash | $0.71 | $21 | 7 gun |
| Router (Zen Free + Flash) | $0.13 | $4 | **38 gun** |

Gercek DeepSeek bakiyesi: 3 Haz $5 → 5 Haz $0.53 (2 gunde $4.47 = gunluk $2.24).

## Model Kesfi (cron, 6 saatte bir)

Zen `/v1/models` endpoint'i WARP uzerinden sorgulanir, `-free` suffix'li modeller taranir.
Yeni free modeller otomatik kesfedilir, kalkanlar duser.

## Onemli Notlar

- **WARP zorunlu:** Oracle Cloud IP'si Zen tarafindan block'laniyor
- **Rate-limit:** Zen free modellerde `FreeUsageLimitError` alinirsa Flash'a fallback
- **6 saatlik tarama:** Model listesi dinamik, yeni modeller eklenebilir/kalkabilir
- **Thinking mode:** Router'da kapali (maliyet x3 yapar). Manuel model degisimi ile Pro+thinking
- **Henuz implemente edilmedi** — mimari tasarim asamasinda (5 Haz 2026)

## Hermes Provider Mimarisi Notlari

- `custom_providers`: OpenAI uyumlu dis API tanimlama — router buraya baglanir
- `fallback_providers`: Sadece hata durumunda tetiklenir, gorev bazli routing YAPAMAZ
- `model_aliases`: `/model hizli` gibi kisayollar — manuel gecis icin
- Plugin sistemi ("Fast Path"): OpenAI-compatible provider'lar icin `plugins/model-providers/`
- Auxiliary tasks (vision, compression, vb.) kendi bagimsiz provider/model zincirine sahip
