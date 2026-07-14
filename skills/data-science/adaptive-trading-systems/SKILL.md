---
name: adaptive-trading-systems
description: "Adaptive trading prediction — çoklu zaman dilimi + indikatör + kendini optimize eden ağırlık sistemi"
version: 1.0.0
metadata:
  hermes:
    tags: [trading, prediction, adaptive, btc, technical-analysis]
    category: data-science
---

# Adaptive Trading Prediction Systems

Çoklu tahminci + ağırlık optimizasyonu + sürekli öğrenme tabanlı BTC fiyat tahmin sistemleri.

## Mimari Prensipler

### Çoklu Tahminci (Ensemble)
- Tek bir indikatöre güvenme — birden fazla sinyal üret
- Her sinyal kendi uzmanlık alanında değerlendirilir
- Ağırlıklı oylama ile final karar

### Çoklu Zaman Dilimi
- 1dk, 5dk, 15dk, 1s — her TF farklı bilgi verir
- Kısa TF (1dk): ani hareketler
- Orta TF (5dk, 15dk): ana trend
- Uzun TF (1s): genel yön
- Her TF'nin ağırlığı farklı: 5dk ve 15dk > 1dk ve 1s

### Kendini Optimize Eden Ağırlıklar
- Her tahmin 5dk sonra değerlendirilir (doğru/yanlış)
- Doğru tahmincinin ağırlığı artar: `w *= (1 + (acc - 0.5))`
- Yanlış tahmincinin ağırlığı azalır: `w *= (1 - (0.5 - acc) * 0.5)`
- Ağırlık sınırları: [0.1, 5.0] — hiçbir sinyal tamamen yok olmaz

### Simülasyon Önce
- Gerçek para ile başlamadan ÖNCE simülasyon
- En az 2-3 hafta simülasyon verisi topla
- %55+ doğruluk oranı → gerçek paraya geçebilirsin

## Teknik İndikatörler

### RSI (Relative Strength Index)
- Aşırı alım (>70) → DOWN sinyali
- Aşırı satım (<30) → UP sinyali
- Periyot: 14
- Güç: `(rsi - 70) / 30` veya `(30 - rsi) / 30`

### MACD (Moving Average Convergence Divergence)
- Histogram > 0 → UP
- Histogram < 0 → DOWN
- Parametreler: fast=12, slow=26, signal=9

### Bollinger Bands
- Alt banda yakın (<%10) → UP (geri dönüş)
- Üst banda yakın (>%90) → DOWN (geri dönüş)
- Band position: `(price - lower) / (upper - lower)`

### Momentum (Çoklu TF)
- Son 5 mumun yönü ve büyüklüğü
- TF'ye göre ağırlık: 1s en yüksek, 1dk en düşük
- Eşik: %0.1+ hareket

### Volatilite (ATR + Daralma)
- Son 5 mum range'i < ATR * 0.5 → daralma
- Daralma sonrası patlama → son mum yönü
- Güven: %60 (düşük, çünkü patlama yönü belirsiz)

### VWAP (Volume Weighted Average Price)
- VWAP'tan uzak (%0.3+) → geri dönüş
- Aşağıdaysa → UP, yukarıdaysa → DOWN

### Stochastic
- K > 80 → aşırı alım → DOWN
- K < 20 → aşırı satım → UP
- Periyot: 14

## Dosya Yapısı

```
/data/pm-trader/strategies/
├── adaptive_btc_predictor.py   # Ana simülasyon motoru
├── dexters_lab_sim.py          # BTC latency arbitrage (pasif, hazır)
├── copy_trade_evaluator.py     # Whale izleme (değerlendirme modu)
├── collect_data.py             # News Signal data collector (v2.1)
├── mispricing.py               # Obvious mispricing scanner
└── news_signal.py              # Haber analizi

/data/pm-trader/
├── adaptive_btc_v2.json        # Son tahmin çıktısı
├── adaptive_btc_history_v2.json # Ağırlıklar + istatistikler
├── adaptive_btc_pending_v2.json # Bekleyen tahminler
└── dexters_lab_*.json          # Dexter's Lab çıktıları
```

## Çalıştırma

```bash
# Snapshot (tek seferlik)
python3 /data/pm-trader/strategies/adaptive_btc_predictor.py

# Continuous (döngü, her 30s)
python3 /data/pm-trader/strategies/adaptive_btc_predictor.py --continuous
```

## Pitfall'lar

### Dexter's Lab UP_DOWN Marketleri Yok
Polymarket'te 5dk/15dk BTC Up/Down marketleri şu an mevcut değil.
`dexters_lab_sim.py` altyapısı hazır — marketler geri gelirse otomatik çalışır.
Şimdilik kendi tahmin motorumuz (`adaptive_btc_predictor.py`) kullanılıyor.

### Binance API Rate Limit
Binance public API rate limit'e dikkat. `--continuous` modda 30s aralık güvenli.
10s veya daha kısa yapma.

### Simülasyon vs Gerçek
Simülasyon sonucu %60+ bile olsa, gerçek piyasada:
- Slippage vardır
- Spread vardır
- Emir gecikmesi vardır
- Gerçek doğruluk simülasyondan %10-15 düşük olur

### Ağırlık Sıfırlama
Sistem piyasa rejimi değiştiğinde (trend → range, range → trend)
eski ağırlıklar geçersiz kalır. Aylık sıfırlama düşünülebilir.

## Gelecek Geliştirmeler

- WebSocket ile gerçek zamanlı veri (REST yerine)
- Order book analizi (derinlik, spread)
- Funding rate (Polymarket'te)
- On-chain veriler (whale hareketleri)
- Gerçek cüzdan entegrasyonu (Polygon + USDC)

## Referanslar

- `references/adaptive-trading-architecture.md` — Mimari detaylar, indikatör formülleri
- `references/btc-market-types.md` — Polymarket BTC market tipleri ve durumları
