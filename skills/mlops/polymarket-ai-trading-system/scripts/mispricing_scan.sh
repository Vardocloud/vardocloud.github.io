#!/bin/bash
# Polymarket Mispricing Scan — pm-trader CLI tabanlı
# 
# ⚠️ GÜNCELLEME (25 Haz 2026): 
# GTA VI "before" comparison marketlerinde 50/50 fallback clause nedeniyle edge yoktur.
# GTA VI Fall 2026 için onaylı — 31 Temmuz'dan önce çıkma ihtimali ~%0.
# 50/50'de her iki outcome $0.50 alır → NO fiyatı ~50¢'de efficient fiyatlanır.
# 
# Bu script mispricing fırsatlarını tarar. GTA VI marketleri ARTIK filtrelenir.
# Gerçek mispricing için: sport, finance, crypto kategorileri daha verimlidir.
#
# Çıktı: ~/.hermes/data/latest_mispricing.json

OUTPUT_FILE="$HOME/.hermes/data/latest_mispricing.json"
mkdir -p "$(dirname "$OUTPUT_FILE")"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Tarama stratejisi: farklı kategorilerde yüksek hacimli marketler
# GTA VI "before" marketleri 50/50 floor nedeniyle edgesiz — filtrelenir.

# Gamma API'den canlı marketleri çek (pm-trader search yerine — daha geniş kapsam)
curl -s 'https://gamma-api.polymarket.com/events?closed=false&limit=30&order=volume_usd&asc=false' 2>/dev/null | python3 -c "
import json, sys, os, subprocess

data = json.load(sys.stdin)
signals = []
scanned = 0
filtered_gta = 0
errors = []

for e in data:
    for m in e.get('markets', []):
        if m.get('closed', True):
            continue
        q = m.get('question', '').lower()
        slug = m.get('slug', '')
        try:
            prices = json.loads(m.get('outcomePrices', '[0,0]'))
            yes_p = float(prices[0])
            no_p = float(prices[1]) if len(prices) > 1 else 0
        except:
            continue
        liq = float(m.get('liquidity', 0))
        vol = float(m.get('volume', 0))

        # GTA VI filtresi
        if 'gta vi' in q or 'gta' in q:
            filtered_gta += 1
            continue

        scanned += 1

        # Likidite filtresi
        if liq < 5000 and vol < 50000:
            continue

        # Meme filtresi
        meme_keywords = ['jesus', 'rihanna', 'playboi', 'carti', 'alien', 'ufo', 'bigfoot']
        is_meme = any(kw in q for kw in meme_keywords)
        if is_meme and vol < 500000:
            continue

        # Bregman arbitraj kontrolü (Pattern 4)
        total = yes_p + no_p
        bregman = None
        if 0 < total < 0.98 and vol > 1000:
            bregman = {'edge_pct': round((1.0-total)/total*100, 2), 'action': 'BUY_BOTH'}

        signals.append({
            'slug': slug,
            'question': m.get('question'),
            'yes_price': round(yes_p, 4),
            'no_price': round(no_p, 4),
            'liquidity': liq,
            'volume': vol,
            'end_date': m.get('end_date', '')[:10],
            'total_yn': round(total, 4),
            'bregman': bregman,
            'analyze': True
        })

output = {
    'scanned': scanned,
    'filtered_gta_50_50': filtered_gta,
    'candidates': len(signals),
    'signals': signals,
    'bregman_count': len([s for s in signals if s['bregman']]),
    'timestamp': '$TS',
    'note': 'Mispricing scan via Gamma API. GTA VI filtered. Bregman arbitraj check included.'
}

with open('$OUTPUT_FILE', 'w') as f:
    json.dump(output, f, indent=2)
print(f'Scanned: {scanned}, Candidates: {len(signals)}, Bregman: {output[\"bregman_count\"]}')
" 2>&1

CANDIDATES=$(python3 -c "import json; d=json.load(open('$OUTPUT_FILE')); print(d.get('candidates', 0))" 2>/dev/null)
echo "✅ Scan complete: $CANDIDATES candidates found (GTA VI markets filtered out)"
