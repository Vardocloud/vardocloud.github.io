# Paper Trading 1 Hafta Testi — 6 Temmuz 2026

**Başlangıç:** 1 Temmuz 2026
**Süre:** 5 gün (planlanan 7 günün 5. gününde portföy %95 eridi)
**Script:** `~/.hermes/scripts/paper-trading.py`
**Cron:** Her saat başı (`8082276086de`)

## Sonuç

| Metrik | Değer |
|--------|-------|
| Başlangıç sermayesi | $500 |
| Kalan bakiye | $23 |
| Net K/Z | **-$477 (%-95.4)** |
| Toplam işlem | 185 |
| Günlük işlem ortalaması | 37 |
| Win Rate | %53.5 (99W/83L) |
| Kaldıraç | x5 |
| Strateji | Breakout (EMA + direnç/destek) |

## Temel Bulgular

### 1. Frekans × Kaldıraç = Portföy Katliamı
Saat başı cron (`0 * * * *`) = günde 24 sinyal fırsatı. Script her saat başı 20 coin'i tarayıp sinyal üretti. 185 işlemde her bir işlem için %0.1 komisyon (giriş + çıkış) birikti.

**Formül:** 185 işlem × (%0.1 giriş + %0.1 çıkış) × x5 kaldıraç = komisyonlar sermayenin önemli kısmını tüketti.

### 2. Win Rate Yanıltıcıdır
%53.5 win rate kârlı gibi görünür ama:
- Kazanan işlemlerin ortalaması kaybedenlerden büyük değilse portföy erir
- Kaldıraçlı işlemde küçük kayıplar bile büyür
- 185 işlemde 83 kaybeden işlem = likitasyon + stop-loss kümülatif hasarı

### 3. Sistemde Circuit Breaker Yok
Risk yönetimi tablosunda "Maks günlük kayıp %3" yazmasına rağmen paper-trading.py bu limiti uygulamaz. Script sadece sinyal üretir, zarar durduramaz.

### 4. BTC Trend Filtresi Çalışmadı
Test döneminde BTC $63K seviyesinde dalgalıydı. Breakout stratejisi yatay/volatil piyasada çok sayıda yalancı sinyal üretti.

## Alınacak Dersler

1. **Kaldıraçlı işlemde frekansı sınırla:** Günde max 3-5 işlem. Saat başı tarama yap ama pozisyon açma kriterlerini sıkı tut.
2. **Win rate tek başına anlamsız:** Ortalama kazanç / ortalama kayıp oranı (K/Z) win rate'ten daha önemli. K/Z > 2 hedef.
3. **Circuit breaker ekle:** Günlük kayıp limitine ulaşınca trading durmalı.
4. **ATR stop-loss kullan:** Sabit %3 SL volatil coin'lerde çok dar.
5. **Paper trading'de 30 gün pozitif:** Gerçek işleme geçmeden önce en az 30 gün pozitif getiri şartı korunmalı.

## Bağlantılı Kronlar

| Cron ID | İşlev | Durum |
|---------|-------|-------|
| `8082276086de` | Paper Trading Kontrol (saat başı) | ✅ Devam ediyor |
| `9c1b114d1771` | 1 Hafta Sonu Raporu (8 Tem 12:00) | ⏳ Bekliyor |
