---
name: kripto-analiz
description: "Kripto para piyasası analiz sistemi — backtest, teknik analiz, no-agent strateji testi ve portföy takibi"
version: 1.0.0
metadata:
  hermes:
    tags: [kripto, bitcoin, altcoin, backtest, trading, strateji]
    category: financial-intelligence
---

# Kripto Analiz Sistemi

## Amaç
Kripto piyasasında backtest odaklı, kanıtlanmış stratejileri test edip geliştirmek. Kaldıraçsız, disiplinli bir sistem kurmak.

> ⚠️ **KRİTİK: Stratejileri sıfırdan icat etme.** Reddit, YouTube, quantifiedstrategies.com, CoinQuant gibi kaynaklardan kanıtlanmış stratejileri al, kendi verinle test et. Edel'in talimatı: "İnternette araştırma yapıp işe yaradığını bildiğimiz bir sistemi test etmek daha iyi."

> ⚠️ **KRİTİK #2: Sonuçları Edel'e direkt raporla, ayrı bir bildirim kanalı kurma.** Edel'in uyarısı: "Sinyalleri telegrama düşürme bana sonuç getir zaten bir sürü cron çıktısı okuyorum." Backtest/hyperopt sonuçlarını cron'a bağlayıp Telegram kanalına yönlendirme. Edel doğrudan sohbet içinde sonucu görmek ister.

## Teknik Altyapı — Freqtrade
Freqtrade (GitHub ~34k ⭐) ana backtest aracıdır. Kurulum ve kullanım:
- `git clone --depth 1 https://github.com/freqtrade/freqtrade.git`
- `pip install -e .` (veya container'da sanal ortam sorunu varsa direkt pip)
- Config: `user_data/config.json` (örnek config'den uyarla, tüm required alanları doldur)
- Veri indir: `freqtrade download-data -c user_data/config.json --exchange binance --pairs BTC/USDT ... --timeframes 4h --days 400`
- Backtest: `freqtrade backtesting -c user_data/config.json --strategy StratejiAdi --timeframe 4h --timerange 20250901-`
- **Hyperopt (otomatik parametre optimizasyonu):** `freqtrade hyperopt -c user_data/config.json --strategy StratejiAdi --timeframe 4h --timerange 20250901- --hyperopt-loss SharpeHyperOptLoss --epochs 200 --spaces all`
  - NOT: Hyperopt için **optuna** kütüphanesi gerekir (`pip install optuna`)
  - **Bilinen hyperopt hataları ve çözümleri:** `references/hyperopt-pitfalls.md`
  - 200 epoch ~2 saat sürer, background'da çalıştır
  - Çıktıyı dosyaya yönlendir (`> /tmp/hyperopt_result.txt 2>&1`) — background process output'u yakalanmayabilir
- Stratejiler: `user_data/strategies/` dizinine yazılır, `IStrategy` sınıfından türetilir
- Parametreler: IntParameter/DecimalParameter/BooleanParameter ile hyperopt'a aç

## 🪙 Takip Edilen Coin'ler
- **BTC** — ana akım, düşük volatilite, piyasa lideri
- **ETH** — en büyük altcoin, akıllı kontrat platformu
- **SOL** — yüksek performanslı blockchain, farklı pattern
- **AVAX** — daha küçük cap, alternatif test
- **XRP** — Edel'in uzun vadeli elde tuttuğu coin (trading için değil)

## 🔬 Analiz Katmanları

### 1. Piyasa Katmanı (Günlük)
- **BTC Dominance:** Bitcoin'in toplam piyasadaki payı
- **Fear & Greed Index:** Piyasa duyarlılığı (korku/açgözlülük)
- **Toplam Piyasa Değeri:** Kripto piyasasının toplam büyüklüğü
- **24s İşlem Hacmi:** Likidite göstergesi
- **Kaynaklar:** CoinMarketCap, CoinGecko, Alternative.me

### 2. Teknik Katman (Strateji için)
Kullanılan indikatörler ve parametreleri:
- **MA (Moving Average):** 50, 100, 200 günlük
- **RSI (Relative Strength Index):** 14 günlük, aşırı alım/satım bölgeleri
- **ADX (Average Directional Index):** 14 günlük, trend gücü ölçümü
- **MACD:** Momentum ve trend dönüşleri
- **Volume Profile:** Hacim analizi

### 3. Backtest Katmanı (No-Agent)
Backtest sistemi özellikleri:
- **Veri:** Binance API'den geçmiş mum verisi çekilir
- **Zaman Aralığı:** Günlük mumlar (1h, 4h opsiyonel)
- **Dönem:** En az 2 yıl geriye dönük
- **İşlem Maliyeti:** %0.1 komisyon dahil edilir
- **Değerlendirme:** Buy & Hold ile karşılaştırma
- **Metrikler:** Win rate, risk/ödül oranı, max drawdown, Sharpe ratio

### 4. No-Agent Sistemi
- **Çalışma Şekli:** Shell script + Python, LLM kullanmaz
- **Zamanlama:** Sinyal üretildiğinde manuel tetikleme (crona bağlama — Edel ayrı bir bildirim kanalı istemiyor)
- **Sinyal Üretimi:** Belirlenen strateji kurallarına göre mekanik sinyal
- **Loglama:** Tüm sinyaller ve işlemler kaydedilir

## 🎯 Strateji Geliştirme Döngüsü

1. **Araştırma:** Kanıtlanmış stratejileri tara (Reddit, YouTube, akademik)
2. **Kur:** Seçilen stratejiyi backtest sistemine entegre et
3. **Test:** 2+ yıl veriyle geriye dönük test et
4. **Değerlendir:** Buy & Hold'u geçiyor mu? Risk/ödül oranı nedir?
   - ⚠️ %60 win rate kâr garantisi değildir. Kazanan işlemler az kazandırıp kaybedenler çok götürüyorsa strateji başarısızdır. Risk/ödül oranı win rate'ten önemlidir.
5. **Optimize (Hyperopt):** Freqtrade hyperopt ile parametreleri dene (200 epoch, ~2 saat)
   - Sharpe, Sortino, Calmar oranlarını maksimize etmeye çalış
   - Stratejide IntParameter/DecimalParameter ile hangi değişkenlerin optimize edileceğini işaretle
   - `spaces=all` ile buy, sell, roi, stoploss, trailing hepsini optimize et
6. **Doğrula:** Optimize edilmiş parametrelerle backtest'i tekrar çalıştır
7. **Onay:** Edel onaylarsa bir sonraki aşamaya geç

## 📖 Kaynak Kütüphanesi

### Strateji Kaynakları
- Reddit r/algotrading — topluluk backtest sonuçları
- QuantifiedStrategies.com — backtest verileri
- TradingStrategyTesting (YouTube) — strateji testleri
- Davidd Tech (YouTube) — kripto stratejileri

### Veri Kaynakları
- Binance API — geçmiş mum verisi
- CoinMarketCap — piyasa verileri
- CoinGecko — alternatif veri kaynağı
- TradingView — grafik ve topluluk analizleri

## Uyarılar
- Kaldıraç kullanılmaz (önceki testte x5'in zararı görüldü: $500 → $19)
- Backtest geçmişi garanti etmez, sadece referanstır
- Hiçbir strateji %100 kâr garantisi vermez
- Düşük bütçeyle (10.000 TL altı) işlem maliyetleri oransal olarak yüksektir
- Ani piyasa hareketlerinde (black swan) stratejiler çalışmayabilir
- %60+ win rate tek başına anlamlı değildir — risk/ödül oranı her zaman win rate'ten önce gelir

## 📊 Rapor Formatı

Backtest sonucu:
```
🧪 [Strateji Adı] — Backtest Raporu
📅 Dönem: [başlangıç] → [bitiş]
💰 Başlangıç: $X | Bitiş: $Y | Getiri: %Z
📊 B&H Karşılaştırması: %Z'ye karşı %BH
🎯 Win Rate: %X
📉 Max Drawdown: %X
⚖️ Risk/Ödül: 1:X
```

Günlük durum:
```
🪙 Kripto Günlük
BTC: $X (24s %...)
ETH: $X (24s %...)
Fear & Greed: ...
Sinyal: YOK/BEKLE/AL/SAT
```
