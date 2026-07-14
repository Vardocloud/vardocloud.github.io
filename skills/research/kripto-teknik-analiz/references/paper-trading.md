# Paper Trading Sistemi Kullanım Kılavuzu

## Script
- Ana script: `~/.hermes/scripts/paper-trading.py`
- Cron: `8082276086de` (her saat başı, no_agent)
- Portföy: `~/.hermes/data/paper-trade/portfoy.json`
- Geçmiş: `~/.hermes/data/paper-trade/gecmis.json`

## Komutlar
```bash
# Normal tarama (cron için)
python3 ~/.hermes/scripts/paper-trading.py

# Portföy sorgulama
python3 ~/.hermes/scripts/paper-trading.py --status

# Portföy sıfırlama
python3 ~/.hermes/scripts/paper-trading.py --reset
```

## Sinyal Üretim Süreci
1. **CoinGecko API** → 20 coin'in anlık fiyatı + 24s değişim
2. **yfinance** → Son 30 günlük veri: EMA5/10/20, RSI(7), trend, direnç/destek
3. **Sinyal üretimi:**
   - Direnç kırılımı (> son 20g yüksek) → LONG 🚀
   - Trend yukarı + RSI < 70 → LONG 📈
   - 24s değişim > %5 → LONG/SHORT ⚡
   - Ucuz coin (< $0.10) + momentum → LONG 💎

## Konfigürasyon
| Parametre | Değer |
|-----------|-------|
| Başlangıç sermayesi | $500 |
| Kaldıraç | x5 |
| Komisyon | %0.1 (giriş + çıkış) |
| Max eşzamanlı pozisyon | 3 |
| Stop-loss | %3 (giriş fiyatından) |
| Take-profit | %6 (giriş fiyatından) |
| Likitasyon | Kaldıraç × 0.9 oranında |

## Takip Listesi
BTC, ETH, XRP, SOL, DOGE, ADA, LINK, DOT, AVAX, LTC, BCH, NEAR, APT, ARB, OP, INJ, TIA, ATOM, UNI, MATIC

## Önemli
- Bu sistem **yapay zeka modeli kullanmaz** — no_agent=True, sadece Python script'i
- Token harcamaz, API bedavadır (CoinGecko public)
- Sinyaller Bitcoin Arısı (@BitcoinArisi) yöntemlerine dayanır
- Gerçek paraya geçmeden önce en az 30 gün pozitif getiri gerekir

---

## 🧪 1. Hafta Test Sonuçları (6 Temmuz 2026)

**5 günde $500 → $23 (%-95.4)**

| Metrik | Değer |
|--------|-------|
| Süre | 5 gün (1-6 Temmuz) |
| Net K/Z | -$477 (%-95.4) |
| Toplam işlem | 185 (günde ~37) |
| Win Rate | %53.5 (99W/83L) |

### Sebep: Aşırı İşlem Sıklığı

Saat başı cron (`0 * * * *`) = günde 24 sinyal fırsatı. Her saat 20 coin taranınca günde 37 işlem açıldı. x5 kaldıraçla 185 işlemde komisyonlar + likitasyonlar birikti.

### Alınacak Dersler

1. **Kaldıraçlı işlemde günlük işlem sayısını sınırla** (max 3-5)
2. **Circuit breaker ekle** — günlük kayıp limiti veya max işlem sayısı aşılınca trading dursun
3. **Win rate tek başına anlamsız** — K/Z oranı (kazanç/kayıp) daha önemli
4. **ATR bazlı stop-loss** — sabit %3 volatil coinlerde çok dar
5. **Saat başı cron yerine günde 4-6 kere** (4h aralık) yeterli
