# Kaldıraçlı İşlem Simülasyonu Referansı

**Oluşturma:** 1 Temmuz 2026
**Script:** `~/.hermes/scripts/kaldirac-simulator.py`
**Veri:** `~/.hermes/data/kaldirac-simulasyonu/`

---

## Mimari

KaldiracMotoru sınıfı üzerine kurulu:

- **Sermaye yönetimi:** Başlangıç sermayesi + komisyon kesintisi + kar/zarar
- **Kaldıraç çarpanı:** x1 - x100 arası, pozisyon büyüklüğü = sermaye × kaldıraç
- **Likitasyon hesaplama:** `fiyat × (1 - 1/kaldıraç × 0.9)` (long için)
- **Stop-loss / Take-profit:** Manuel seviye belirleme, otomatik tetikleme
- **Long/Short desteği:** Her iki yönde pozisyon açma
- **Funding rate:** Periyodik fonlama ücreti simülasyonu

---

## Stratejiler

### 1. Breakout (EMA Crossover + Direnç/Destek)
- EMA20/50 kesişiminde sinyal üret
- RSI filtresi (long <70, short >30)
- Pivot noktaları ile direnç/destek kırılımı
- %3 stop-loss / %6 take-profit

### 2. RSI Mean Reversion
- RSI < 30 → LONG (aşırı satım)
- RSI > 70 → SHORT (aşırı alım)
- RSI 40-60 nötr zone → pozisyon kapat

---

## Backtest Sonuçları (XRP-USD, 6 ay)

### Breakout Stratejisi
| Kaldıraç | Net K/Z | Getiri | Win Rate | Max DD | K/Z Oranı |
|----------|---------|--------|----------|--------|-----------|
| x1 | +$37 | +%7.5 | %50 | %3.4 | 3.35 |
| x3 | +$101 | +%20.1 | %50 | %10.1 | 3.12 |
| **x5** | **+$149** | **+%29.8** | **%50** | **%16.8** | **2.89** |
| x10 | +$204 | +%40.8 | %50 | %33.5 | 2.30 |
| x20 | +$33 | +%6.5 | %50 | %67.1 | 1.14 |

### RSI Mean Reversion (x10)
- **Sıfırlandı** 💀 — aşırı işlem sıklığı likitasyon yedirdi
- 11 işlem, %36 win rate, %100 drawdown

---

## Önemli Kurallar

1. **x5 optimal:** Riske göre en iyi getiri/risk oranı
2. **x10 max:** Üstü likitasyon riskini katlıyor
3. **K/Z oranı > 2** hedef: Kazandığında kaybettiğinin 2 katı
4. **Saatlik işlem:** Gün içi birden fazla işlem likitasyon riskini artırır
5. **Simülasyon önce, gerçek sonra:** Backtest'te kanıtlanmamış strateji asla canlıya geçmez
