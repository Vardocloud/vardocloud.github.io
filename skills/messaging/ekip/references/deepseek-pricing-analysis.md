# DeepSeek API Maliyet Analizi — 5 Haz 2026

Gercek kullanim verilerine dayali maliyet karsilastirmasi.

## Pricing (resmi)

| Model | Input (cache miss) | Input (cache hit) | Output | Context |
|:--|--:|--:|--:|:--|
| deepseek-v4-pro | $0.435/M | $0.003625/M | $0.87/M | 1M |
| deepseek-v4-flash | $0.14/M | $0.0028/M | $0.28/M | 1M |

Fark: Flash, Pro'dan **3.1x daha ucuz** (input) ve **3.1x daha ucuz** (output).

## Gercek Kullanim (son 24 saat, cron haric)

- 47 Telegram oturumu
- Input: 4,144,262 token
- Output: 481,857 token
- Reasoning: 0 (thinking kapali)

### Pro ile maliyet
```
Input:  4.14M × $0.435 = $1.80
Output: 0.48M × $0.87  = $0.42
                         ─────
Gunluk:                  $2.22
Aylik:                   $67
```

### Flash ile maliyet
```
Input:  4.14M × $0.14  = $0.58
Output: 0.48M × $0.28  = $0.13
                         ─────
Gunluk:                  $0.71
Aylik:                   $21
Tasarruf:                %68
```

## Bakiye Dogrulamasi

```
3 Haziran: $5.00 yuklendi
5 Haziran: $0.53 kaldi
2 gunde:   $4.47 harcandi
Gunluk:    $2.24 (hesaplanan $2.22 ile uyumlu)
$5 = 2 gun (Pro), $5 = 7 gun (Flash)
```

## Oneri

Varsayilan model Flash olmali. Pro sadece manuel geciste.
Router proxy ile sohbet/arastirma Zen Free'ye ($0) kaydirilirsa aylik $4'e duser.
