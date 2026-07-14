# Freqtrade Kurulum ve Kullanım Referansı

## Kurulum

```bash
git clone --depth 1 https://github.com/freqtrade/freqtrade.git
cd freqtrade
pip install -e .
# NOT: Container'da python3-venv yoksa ./setup.sh çalışmaz, direkt pip install -e . kullan
```

## Hyperopt İçin Ek Bağımlılık

```bash
pip install optuna
# Hyperopt öncesi bu adım unutulursa "No module named 'optuna'" hatası alınır
```

## Config

Config dosyası `user_data/config.json`. Örnek config'den uyarla, tüm required alanları doldur:
- `exchange.name`, `exchange.pair_whitelist`, `exchange.pair_blacklist`
- `telegram.enabled: false`, `api_server.enabled: false`
- Telegram false olsa bile `token: ""` ve `chat_id: ""` eklenmeli (validation geçer)
- `api_server` false olsa bile `listen_ip_address`, `listen_port`, `username`, `password`, `jwt_secret_key` (min 32 karakter) eklenmeli

## Veri İndirme

```bash
freqtrade download-data -c user_data/config.json --exchange binance \
  --pairs BTC/USDT ETH/USDT SOL/USDT AVAX/USDT \
  --timeframes 4h --days 400 --datadir user_data/data
```

## Backtest

```bash
freqtrade backtesting -c user_data/config.json \
  --strategy StratejiAdi --timeframe 4h \
  --timerange 20250901-
```

## Hyperopt (Parametre Optimizasyonu)

```bash
# Background'da çalıştır (2+ saat):
nohup freqtrade hyperopt -c user_data/config.json \
  --strategy StratejiAdi --timeframe 4h \
  --timerange 20250901- \
  --hyperopt-loss SharpeHyperOptLoss \
  --epochs 200 --spaces all \
  > /tmp/hyperopt_result.txt 2>&1 &

# Çıktıyı takip et:
tail -f /tmp/hyperopt_result.txt

# NOT: Background process output'u doğrudan yakalanmayabilir. 
# Mutlaka dosyaya yönlendir (> dosya 2>&1).
```

## Background Process Yönetimi

Hermes'te `terminal(background=true, notify_on_complete=true)` kullan:
- notify_on_complete: bittiğinde bildirim alırsın
- Çıktıyı `> dosya 2>&1` ile dosyaya yönlendir (process log'u kaçırabilir)
- Bittiğinde: `process(action='log', session_id='...')` veya dosyayı oku

## Strateji Dosyası Yapısı

`user_data/strategies/` dizinine yazılır:
- `IStrategy` sınıfından türet
- `populate_indicators()` — indikatörleri hesapla
- `populate_entry_trend()` — al sinyallerini tanımla
- `populate_exit_trend()` — sat sinyallerini tanımla
- Parametreler: `IntParameter`, `DecimalParameter`, `BooleanParameter` ile hyperopt'a aç
- `space='buy'`, `space='sell'`, `space='stoploss'`, `space='roi'` etiketleri

## Sık Hatalar

| Hata | Çözüm |
|------|-------|
| "No module named 'optuna'" | `pip install optuna` |
| "jwt_secret_key is too short" | En az 32 karakter yap |
| "'token' is a required property" | Telegram enabled=false olsa bile token+chat_id ekle |
| "'listen_ip_address' is a required property" | api_server false olsa bile required alanları ekle |
