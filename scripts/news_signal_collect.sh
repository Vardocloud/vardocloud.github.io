#!/bin/bash
# news_signal_collect.sh - Polymarket News Signal Scanner
# Pattern 1: RSS haberleri tara + market verisi çek
#
# Güncelleme 27 Haz 2026:
# - blogwatcher-cli komutları: scan (refresh değil), articles (list değil)
# - Gamma API events + markets endpoint'leri kullanılır
# - deploy_task ile alt görev çalıştırma (skill'deki 2-aşamalı yapı)
#
# Çıktı: ~/.hermes/data/news_scan_$(date +%Y%m%d).json

DATA_DIR="$HOME/.hermes/data"
mkdir -p "$DATA_DIR"

BW="$HOME/bin/blogwatcher-cli"
TS=$(date +%Y%m%d_%H%M)

echo "📡 [Pattern 1] News Signal Scan başlıyor..."

# Adım 1: RSS haberlerini tara
echo "  → RSS feed'ler taranıyor..."
$BW scan 2>/dev/null

# Adım 2: Son makaleleri çek
ARTICLES=$($BW articles 2>/dev/null | head -100)

# Adım 3: Polymarket market verisi çek
echo "  → Polymarket market verisi çekiliyor..."
pm-trader markets list --limit 30 --sort volume 2>/dev/null > "$DATA_DIR/pm_markets_$TS.json"
pm-trader portfolio 2>/dev/null > "$DATA_DIR/pm_portfolio_$TS.json"

# Adım 4: Gamma API'den canlı marketler
curl -s 'https://gamma-api.polymarket.com/events?closed=false&limit=10&order=volume_usd&asc=false' 2>/dev/null > "$DATA_DIR/gamma_events_$TS.json"

echo "✅ News Scan tamam: $TS"
echo "   Market verisi: $DATA_DIR/pm_markets_$TS.json"
echo "   Portföy: $DATA_DIR/pm_portfolio_$TS.json"
echo ""
echo "📋 Özet:"
echo "  $(pm-trader portfolio 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); p=d.get(\"data\",[]); print(f\"Pozisyon: {len(p)}, Nakit: ${d.get(\"ok\",{})}\")' 2>/dev/null || echo 'Portföy okunamadı')"
