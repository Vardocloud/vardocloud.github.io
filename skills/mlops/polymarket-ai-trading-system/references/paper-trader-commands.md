# polymarket-paper-trader CLI Referansı

## Hesap Yönetimi
- `pm-trader init --balance N` — N $ sanal bakiye ile hesap oluştur
- `pm-trader balance` — Nakit, pozisyon değeri, toplam P&L
- `pm-trader reset --confirm` — Tüm veriyi sil
- `pm-trader accounts list` — Hesapları listele
- `pm-trader accounts create NAME` — A/B test için yeni hesap oluştur

## Market Keşfi
- `pm-trader markets list --limit N --sort volume|liquidity` — Aktif marketleri listele
- `pm-trader markets search QUERY` — Full-text market arama
- `pm-trader markets get SLUG` — Market detayı (question, outcomes, prices, volume, liquidity)
- `pm-trader price SLUG` — YES/NO midpoints ve spread
- `pm-trader book SLUG --depth N` — Order book snapshot
- `pm-trader watch SLUG [SLUG...] --outcome yes|no` — Canlı fiyat takibi

## İşlem (Market Order)
- `pm-trader buy SLUG OUTCOME AMOUNT --type fok|fak` — Market alış
- `pm-trader sell SLUG OUTCOME SHARES --type fok|fak` — Market satış
  - `fok` = fill-or-kill (tamamı dolarsa, yoksa iptal)
  - `fak` = immediate-or-cancel (kısmi dolabilir)

## Limit Emir
- `pm-trader orders place SLUG OUTCOME SIDE AMOUNT PRICE` — Limit emir ver
- `pm-trader orders list` — Bekleyen limit emirler
- `pm-trader orders cancel ID` — Limit emir iptal
- `pm-trader orders check` — Fiyat eşleşmiş emirleri doldur

## Portföy & Geçmiş
- `pm-trader portfolio` — Açık pozisyonlar (canlı fiyatlarla)
- `pm-trader history --limit N` — İşlem geçmişi
- `pm-trader stats` — Win rate, ROI, profit, max drawdown
- `pm-trader leaderboard` — Yerel hesap sıralaması
- `pm-trader pk ACCOUNT_A ACCOUNT_B` — İki hesabı karşılaştır

## Veri Dışa Aktar
- `pm-trader export trades --format csv|json` — İşlem geçmişi export
- `pm-trader export positions --format csv|json` — Pozisyon export

## Backtest & Benchmark
- `pm-trader benchmark run MODULE.FUNC` — Strateji çalıştır
- `pm-trader benchmark compare ACCT1 ACCT2` — Hesap performans karşılaştır
- `pm-trader benchmark pk STRAT_A STRAT_B` — Strateji karşılaştır

## MCP Server
- `pm-trader mcp` — MCP server başlat (stdio transport)

## Global Flags
- `--data-dir PATH` — Veri dizinini belirle
- `--account NAME` — Hesap seç

## Örnek Kullanım Akışı (İlk Adım)
```
pm-trader init --balance 10000
pm-trader markets search "bitcoin"
pm-trader markets get will-bitcoin-hit-100k  # detayları gör
pm-trader buy will-bitcoin-hit-100k yes 100  # $100 YES al
pm-trader portfolio                          # pozisyonu gör
pm-trader stats                               # metrikleri gör
```
