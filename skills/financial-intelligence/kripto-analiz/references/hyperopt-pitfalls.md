# Hyperopt Bilinen Hatalar ve Çözümleri

_Session: 10-11 Temmuz 2026 — SwingRSIDivergence stratejisi hyperopt'u_

## Sorun 1: optuna modülü eksik

**Hata:** `No module named 'optuna'`
**Sebep:** Freqtrade hyperopt için optuna kütüphanesine ihtiyaç duyar. `pip install freqtrade[hyperopt]` ile kurulum yapılmadıysa veya sadece `pip install -e .` yapıldıysa optuna gelmez.
**Çözüm:** `pip install optuna`

## Sorun 2: trailing_stop BooleanParameter/DecimalParameter hatası

**Hata:**
```
TypeError: float() argument must be a string or a real number, not 'DecimalParameter'
```
**Sebep:** Freqtrade config validation'ı trailing_stop_positive ve trailing_stop_positive_offset değerlerini `float()` ile kontrol eder. Stratejide bu değerler `BooleanParameter` veya `DecimalParameter` objesi olarak tanımlanırsa validation patlar.
**Çözüm:** trailing_stop, trailing_stop_positive, trailing_stop_positive_offset değerleri **sabit** olmalıdır (ör. `trailing_stop = True`, `trailing_stop_positive = 0.01`). Hyperopt'ta optimize edilemezler.

## Sorun 3: `--spaces all` protection hatası

**Hata:**
```
The 'protection' space is included into the hyperoptimization but no parameter for this space was found...
```
**Sebep:** `--spaces all` protection space'ini de dahil eder ama stratejide protection parametresi yoksa hata verir.
**Çözüm:** `--spaces all` yerine `--spaces buy sell roi stoploss` kullan.

## Sorun 4: Background process çıktısı yakalanamıyor

**Belirti:** Hyperot tamamlandı (exit code 0) ama çıktı boş.
**Sebep:** Background process output'u doğrudan Hermes'e dönmeyebilir.
**Çözüm:** Çıktıyı dosyaya yönlendir: 
```bash
freqtrade hyperopt -c config.json ... > /tmp/hyperopt_result.txt 2>&1
```
Sonra `cat /tmp/hyperopt_result.txt` ile oku.

## Sorun 5: Hyperopt "No params for buy found"

**Belirti:** Hyperopt çalışıyor ama buy parameterlerini optimize etmiyor.
**Sebep:** Stratedeki IntParameter'lar `space='buy'` ile işaretlenmiş olmalı. Ayrıca `--spaces` parametresinde buy space'i belirtilmemiş olabilir.
**Çözüm:** Stratejideki tüm IntParameter tanımlarında `space='buy'` veya `space='sell'` olduğunu kontrol et. Komutta `--spaces buy sell roi stoploss` kullan.

## Sorun 6: Freqtrade config validation — tüm required alanlar dolu olmalı

Freqtrade config.json'da enabled=false olan özelliklerin bile tüm alanları doldurulmalıdır:
- **telegram:** token, chat_id, notification_settings (hepsi dolu olmalı)
- **api_server:** listen_ip_address, listen_port, username, password, jwt_secret_key (en az 32 karakter)
- **exchange:** key, secret, ccxt_config, sandbox (hepsi dolu olmalı)

En temiz çözüm: Freqtrade'in kendi `config.json.example` dosyasını al, sadece değiştirmek istediğin alanları güncelle.

## SwingRSIDivergence — Kanıtlanmış En İyi Parametreler

_10 ay backtest, %100 win rate, %8.48 kâr_

```python
buy_params = {
    "divergence_window": 7,
    "ema_long_period": 79,
    "ema_short_period": 37,
    "rsi_oversold": 35,
    "rsi_period": 17,
}

sell_params = {
    "rsi_overbought": 78,
}

minimal_roi = {
    "0": 0.724,
    "487": 0.118,
    "1133": 0.066,
    "3884": 0
}

stoploss = -0.132
```
