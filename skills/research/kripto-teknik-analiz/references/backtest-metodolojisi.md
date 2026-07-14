# Backtest & Strateji Doğrulama Metodolojisi

## 3 Katmanlı Pipeline

```
Backtest (geçmiş veri) → Paper Trading (canlı sanal) → Gerçek İşlem
```

### 🔴 Kural: Her aşama bir öncekini doğrulamalıdır
- Backtest'te kanıtlanmamış strateji paper trading'e geçmez
- Paper trading'de 30+ gün pozitif K/Z yoksa strateji değiştirilir
- Gerçek işleme geçiş ANCak paper trading başarılı olduktan sonra yapılır

## Backtest Çalıştırma

```bash
# Tek coin backtest
python3 ~/.hermes/scripts/paper-trading.py --backtest 2026-01-01 --coin SOL --sermaye 500

# Strateji karşılaştırma (kaldirac-simulator ile)
python3 ~/.hermes/scripts/kaldirac-simulator.py --coin BTC-USD --karsilastir

# Toplu test
python3 ~/.hermes/scripts/kaldirac-simulator.py --hedef-coinler XRP,SOL,ADA,DOGE --baslangic 500 --kaldırac 5 --gun 180
```

## BTC Trend Filtresi (Kritik Geliştirme)

Altcoin sinyalleri üretilirken BTC'nin genel trend yönü kontrol edilir:

| BTC Trendi | LONG İzni | SHORT İzni |
|------------|-----------|------------|
| 📈 YUKARI | ✅ Evet | ❌ Kısıtla |
| 📉 AŞAĞI | ❌ Kısıtla | ✅ Evet |
| ⚪ YATAY | ✅ Evet | ✅ Evet |

**Neden?** Bitcoin Arısı'nın dediği gibi: *"BTC hareketine dikkat edilmeli"*.
BTC düşüş trendindeyken altcoin LONG sinyalleri çoğunlukla stop-loss yedirir (1 Tem 2026 SOL backtest'inde görüldü: $500 → $0).

**Uygulama:** Her sinyal üretiminden önce BTC-USD'nin 30 günlük EMA5/10/20 crossover'ı kontrol edilir.

## ATR Bazlı Dinamik Stop-Loss

Sabit %3 stop-loss çok dardır — volatil coinlerde sürekli stop yedirir.

| Coin | Günlük Volatilite | Sabit %3 SL | ATR Bazlı SL (1.5×ATR) |
|------|------------------|-------------|----------------------|
| BTC | ~%2-3 | ✅ Uygun | ✅ Uygun |
| SOL | ~%4-8 | ❌ Çok dar | ✅ %6-12 |
| DOGE | ~%5-10 | ❌ Çok dar | ✅ %7-15 |

**Formül:** 
- SL = ATR(14) × 1.5 (minimum %2)
- TP = SL × 2.5 (Risk:Ödül = 1:2.5)
- ATR = Average True Range (son 14 gün)

## Backtest'ten Alınan Dersler (1 Temmuz 2026)

### Çalışan Stratejiler
- **Breakout (EMA + Direnç/Destek):** BTC, LINK, DOGE, ADA'da 6 ayda %30-88 getiri (x5 kaldıraç)
- **En iyi kaldıraç:** x5 (x10'da drawdown 2 katına çıkıyor)
- **K/Z Oranı:** ~2.5-2.9 (kazandığında kaybettiğinin ~2.5 katı)

### Çalışmayan Yaklaşımlar
- **Günlük kazanç stratejisi:** 15 coin'de sadece 3'ü kârlı (%23). Küçük bütçede komisyonlar net kârı sıfırlıyor.
- **RSI Mean Reversion + x10 kaldıraç:** Sürekli likitasyon yediriyor.
- **Sabit %3 SL + yüksek volatilite:** Volatil coin'lerde sürekli stop-loss.
- **Gün sonu kapatma:** Trend devam ederken pozisyonu erken kapatıp kazancı sınırlıyor.
