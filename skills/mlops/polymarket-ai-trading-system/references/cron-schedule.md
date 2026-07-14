# Polymarket Cronjob Schedule

## Haftalık Program

| Gün | Saat UTC+3 | Strateji | Script | Model |
|---|---|---|---|---|
| Pazartesi | 10:00 | 📡 News Signal | news_signal_collect.sh | deepseek-v4-flash-free (opencode-zen) |
| Salı | 10:00 | 💰 Mispricing | mispricing_scan.sh | deepseek-v4-flash-free (opencode-zen) |
| Çarşamba | 10:00 | 📡 News Signal | news_signal_collect.sh | deepseek-v4-flash-free (opencode-zen) |
| Perşembe | 10:00 | 💰 Mispricing | mispricing_scan.sh | deepseek-v4-flash-free (opencode-zen) |
| Cuma | 10:00 | 📡 News Signal | news_signal_collect.sh | deepseek-v4-flash-free (opencode-zen) |

## Cronjob Programı (Güncel — 27 Haz 2026)

### Saat Başı Master Scan (HER SAAT)
```yaml
name: Polymarket Hourly Master Scan
schedule: "0 * * * *"  # Her saat başı
script: pm_master_scan.py
skills: [polymarket-ai-trading-system]
deliver: origin
not: Tüm pattern'leri (1-5) çalıştırır. LLM analizi cron agent'ında yapılır.
```

Bu cron job, Pattern 1-5'in tamamını her saat başı otomatik çalıştırır. Script veri toplar, agent analiz eder, sinyal varsa trade açar.

### Haftalık Özel Stratejiler (Yedek)
- **📡 News Signal** (ID: 44e9e732aa91): Pzt-Çar-Cuma 10:00 → Derin RSS analizi
- **💰 Mispricing** (ID: 6d44c24d9068): Salı-Perşembe 10:00 → Kategori bazlı tarama

### Rate Limit Yönetimi
- **429 Too Many Requests:** 5 kez dener, exponential backoff (1sn, 2sn, 4sn, 8sn, 16sn)
- **503 Service Unavailable:** Aynı backoff stratejisi
- **Timeout:** 2x backoff ile tekrar dener
- **Limit bitince:** Cron job'u 1 saat sonra otomatik tekrar dener (zaten saat başı)
- **İkinci LiteRouter:** Hazırlık yapıldı, API key Bitwarden'a eklenince provider aktif edilir

### Model Kararları (Güncel)

### News Signal (ID: 7968c2d276bb)
```yaml
name: Polymarket News Signal Scan
schedule: "0 10 * * 1,3,5"  # Pzt-Çar-Cuma
script: news_signal_collect.sh
model: deepseek-v4-flash-free
provider: opencode-zen
deliver: origin
data_file: /data/pm-trader/latest_scan.json
strategy_dir: /data/pm-trader/strategies/
```

### Mispricing (ID: e493e0f2a8d3)
```yaml
name: Polymarket Obvious Mispricing
schedule: "0 10 * * 2,4"  # Salı-Perşembe
script: mispricing_scan.sh
model: deepseek-v4-flash-free
provider: opencode-zen
deliver: origin
data_file: /data/pm-trader/latest_mispricing.json
note: >
  25 Haz 2026 düzeltmesi: GTA VI "before" marketleri 50/50 fallback clause
  nedeniyle efficient fiyatlanmıştır (edge: %0-4). Artık filtrelenir.
  Gerçek mispricing için sport/finance/crypto kategorileri taranır.
```

## Veri Dizini
```
Varsayılan: /data/pm-trader/  (ama Docker'da mount edilmemiş olabilir!)
Fallback:   ~/.local/share/pm-trader/  (pm-trader default data dir)

Docker'da /data/ yoksa:
  ├── latest_scan.json   ← pm-trader markets list > buraya
  ├── portfolio.json     ← pm-trader portfolio --format json
  └── pm-trader.db       ← default location (~/.local/share/pm-trader/)

/var/ mevcutsa:
  └── strategies/        ← collect_data.py vs. (opsiyonel)
```

## Model Kararları

| Provider | Model | Maliyet | Ne Zaman Kullanılır |
|---|---|---|---|
| opencode-zen | deepseek-v4-flash-free | Ücretsiz | **Ana model** — tüm cronjob'lar |
| opencode-zen | mimo-v2.5-free | Ücretsiz | Alternatif (deepseek down olursa) |
| Pollinations | deepseek | Ücretli | **KULLANMA** — rate limit 429, gereksiz maliyet |
| local Ollama | phi4-mini:3.8b | Yerel | **KULLANMA** — çok yavaş (60sn/market) |

## Önemli Hatırlatmalar

- Haftasonu çalışmaz: likidite düşer, spread açılır, sinyal-gürültü oranı kötü
- İki strateji aynı $10K paper hesabı kullanır — portföy yönetimi ortak
- Her scan sonucu otomatik olarak bu Telegram thread'ine düşer
- Detaylı inceleme gerekiyorsa `/data/pm-trader/logs/` altındaki JSON loglar okunur

## Scan Geçmişi

| Tarih | Tür | Sonuç |
|---|---|---|
| 2026-06-25 | 💰 Mispricing | Sıfır sinyal — GTA VI marketleri efficient fiyatlı (50/50 floor). Hiçbir trade açılmadı. |
| 2026-06-27 | 🚀 İlk Setup | $10K paper trade hesabı açıldı. Kraken IPO YES @ 46¢ ($50). 5 pattern uygulandı. 2 cronjob kuruldu. |

