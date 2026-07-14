# Master Scan Output Schema (Polymarket)

`pm_master_scan.py` çıktısı `~/.hermes/data/scan_YYYYMMDD_HHMM.json` formatında kaydedilir. Bu dosya `polymarket-ai-trading-system` skill'inin Pattern 1-5 taramalarının birleşik çıktısıdır.

## Dosya Adı
- **Gerçek format:** `scan_20260701_1800.json` (timestamp'li)
- ~~`latest_scan.json`~~ — bu isimde dosya yok, skill'deki eski referans. En son scan'i bulmak için: `ls -t ~/.hermes/data/scan_*.json | head -1`
- **Dizin:** `/home/ubuntu/.hermes/data/`

## Üst Seviye Alanlar

| Alan | Tip | İçerik |
|------|-----|--------|
| `patterns` | object | 4 alt pattern: news_signal, market_scan, copy_trading_evaluator, btc_tracker |
| `pm_trader` | object | Paper trader portföy, bakiye, istatistik, geçmiş |
| `trends` | object | Market bazlı fiyat değişimleri (slug → trend datası) |
| `risk_alerts` | array | Stop-loss ve take-profit uyarıları |
| `rate_limit` | object | API rate limit durumu |
| `elapsed_seconds` | number | Scan süresi |
| `scan_id` | string | Scan kimliği |

## patterns Detayı

### patterns.news_signal
```json
{
  "feeds": 56,
  "articles_count": 0,
  "articles": [],
  "feeds_list": "Tracked blogs (14):..."
}
```
- `articles_count = 0` = feed'ler taranmamış/stale. `blogwatcher-cli scan` gerekir.
- Bu durumda `rss-feed-maintenance` skill'ini kullan.

### patterns.market_scan
```json
{
  "markets_scanned": 512,
  "open_markets": [
    {
      "slug": "kraken-ipo-by-december-31-2026-513",
      "question": "Kraken IPO by December 31, 2026?",
      "yes_price": 0.245,
      "no_price": 0.755,
      "volume": 544248.72,
      "liquidity": 4171.20,
      "end_date": "2027-01-01",
      "total_yn": 1.0,
      "mispricing": {  // varsa
        "type": "yes_cheap",
        "direction": "BUY_YES",
        "confidence": "medium"
      }
    }
  ]
}
```

### patterns.copy_trading_evaluator
```json
{
  "whale_signals": [
    {
      "slug": "...",
      "question": "...",
      "type": "whale_watch|near_extreme",
      "reason": "High volume ($X) + contested/extreme price",
      "action": "IZLE|ARASTIR"
    }
  ],
  "errors": []
}
```

### patterns.btc_tracker
```json
{
  "btc_price": 59548.0,
  "change_24h_pct": 1.824,
  "signal": "IZLE|BEKLE|OLASILIK_VAR",
  "high_24h": 60092.0,
  "low_24h": 57800.19,
  "volume_24h": 22928.74
}
```

## pm_trader Detayı

### pm_trader.portfolio (her pozisyon)
```json
{
  "market_slug": "...",
  "market_question": "...",
  "outcome": "yes|no|over|under",
  "shares": 83.37,
  "avg_entry_price": 0.4614,
  "total_cost": 38.47,
  "live_price": 0.245,
  "current_value": 20.43,
  "unrealized_pnl": -18.04,
  "percent_pnl": -46.9
}
```

### pm_trader.balance
```json
{
  "cash": 9941.9,
  "starting_balance": 10000.0,
  "positions_value": 31.40,
  "total_value": 9973.30,
  "pnl": -26.70
}
```

### pm_trader.stats
```json
{
  "roi_pct": -0.267,
  "total_trades": 4,
  "buy_count": 3,
  "sell_count": 1,
  "win_rate": 0.0,
  "sharpe_ratio": 0.0,
  "max_drawdown": 0.0058,
  "total_fees": 0.0,
  "avg_trade_size": 17.95
}
```

## trends Detayı

Her market slug için, 120 data point üzerinden trend analizi:
```json
{
  "name": "Market sorusu",
  "price_change": -0.05,
  "price_change_pct": -16.9,
  "volume_change_pct": 0.5,
  "start_price": 0.295,
  "current_price": 0.245,
  "data_points": 120,
  "trend": "up|down|stable"
}
```

## risk_alerts Detayı
```json
[
  {
    "slug": "atp-blockx-zverev-...",
    "market": "Blockx vs. Zverev: Match O/U 36.5",
    "type": "STOP_LOSS|TAKE_PROFIT",
    "pnl_pct": -100.0,
    "action": "DÜŞÜN: Zararına satmayı değerlendir"
  }
]
```
