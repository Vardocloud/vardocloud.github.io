# Kaldıraçlı İşlem Simülatörü Kullanım Kılavuzu

**Script:** `~/.hermes/scripts/kaldirac-simulator.py`

## Kullanım

### Tek Coin Backtest
```bash
# Varsayılan: BTC, $500, x10, breakout, 180 gün
python3 ~/.hermes/scripts/kaldirac-simulator.py

# XRP, düşük kaldıraç
python3 ~/.hermes/scripts/kaldirac-simulator.py --coin XRP --baslangic 500 --kaldırac 5 --strateji breakout --gun 180

# Coin listesini görüntüle
python3 ~/.hermes/scripts/kaldirac-simulator.py --coin list
```

### Strateji Karşılaştırma
```bash
# Tüm stratejileri + kaldıraç seviyelerini karşılaştır
python3 ~/.hermes/scripts/kaldirac-simulator.py --coin XRP --karsilastir
```

### Toplu Test (Birden çok coin)
```bash
# Belirli coin'lerde test
python3 ~/.hermes/scripts/kaldirac-simulator.py --hedef-coinler XRP,SOL,ETH,BTC,DOGE --baslangic 500 --kaldırac 5 --gun 180

# Coin listesinden ilk 10 coin'de test
python3 ~/.hermes/scripts/kaldirac-simulator.py --top-test 10 --baslangic 500 --kaldırac 5
```

### Geçmiş Raporlar
```bash
python3 ~/.hermes/scripts/kaldirac-simulator.py --rapor
```

## Stratejiler

| Strateji | Açıklama | Kullanım |
|----------|----------|----------|
| **breakout** | EMA crossover + direnç/destek kırılımı (Bitcoin Arısı tarzı) | `--strateji breakout` |
| **rsi** | RSI aşırı alım/satım bölgelerinde ters işlem | `--strateji rsi` |

## Parametreler

| Parametre | Varsayılan | Açıklama |
|-----------|-----------|----------|
| `--coin` | BTC-USD | Coin sembolü veya "list" |
| `--baslangic` | 1000 | Başlangıç sermayesi ($) |
| `--kaldırac` | 10 | Kaldıraç çarpanı (1-100) |
| `--strateji` | breakout | breakout veya rsi |
| `--gun` | 180 | Test edilecek gün sayısı |
| `--hedef-coinler` | — | Virgülle ayrılmış coin listesi |

## Backtest Sonuçları (1 Temmuz 2026)

### XRP Breakout — Kaldıraç Karşılaştırması (6 Ay)
| Kaldıraç | Net K/Z | Getiri | DD | Win Rate |
|:--------:|:-------:|:------:|:--:|:--------:|
| x1 | +$37 | +%7.5 | %3.4 | %50 |
| x3 | +$101 | +%20.1 | %10.1 | %50 |
| **x5** | **+$149** | **+%29.8** | **%16.8** | **%50** |
| x10 | +$204 | +%40.8 | %33.5 | %50 |
| x20 | +$33 | +%6.5 | %67.1 | %50 |

### Breakout — 8 Coin (x5, 6 Ay)
| Coin | Net K/Z | Getiri | WR |
|:----:|:-------:|:------:|:--:|
| BTC | **+$441** | **+%88** | %100 |
| LINK | +$184 | +%37 | %100 |
| DOGE | +$176 | +%35 | %100 |
| ADA | +$160 | +%32 | %100 |
| XRP | +$149 | +%30 | %50 |

### Optimum Parametreler
- **En iyi kaldıraç:** x5 (riske göre en iyi getiri)
- **K/Z oranı:** 2.3-2.9 (kazandığında kaybettiğinden 2.5x fazla)
- **Max kaldıraç:** x10 (üstü likitasyon riskini çok artırır)
- **RSI stratejisi x10'da sıfırlandı** — kaldıraçlı işlemlerde kullanılmamalı
