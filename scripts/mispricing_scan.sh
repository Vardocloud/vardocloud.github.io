#!/bin/bash
# Polymarket Mispricing Scan — fixed version
# Scans "before GTA VI" race markets for obvious mispricings
# Outputs JSON with signals

OUTPUT_FILE="/tmp/pm_mispricing_signals.json"

# Search for "before GTA" markets and extract mispriced NO signals
pm-trader markets search "before gta vi" --limit 30 2>/dev/null | python3 -c "
import json, sys

data = json.load(sys.stdin)
markets = data.get('data', [])
signals = []
scanned = 0

for m in markets:
    q = m.get('question', '')
    slug = m.get('slug', '')
    yes_p = m['outcome_prices'][0]
    no_p = m['outcome_prices'][1]
    liq = m.get('liquidity', 0)
    vol = m.get('volume', 0)

    # Only GTA race markets with 50/50 safety net
    if 'before gta' not in q.lower():
        continue

    scanned += 1

    # Check for obvious mispricing: NO priced way below 50/50 floor but event is ~0% likely
    # 50/50 floor is $0.50 — real signals have NO < $0.52 (below the floor)
    unlikely_keywords = ['return', 'jesus', 'album', 'hit \$1m', 'president', 'invades']
    is_unlikely = any(kw in q.lower() for kw in unlikely_keywords)

    if is_unlikely and no_p < 0.52 and liq >= 10000:
        signals.append({
            'slug': slug,
            'question': q,
            'no_price': no_p,
            'yes_price': yes_p,
            'liquidity': liq,
            'volume': vol,
            'edge_pct': round((1.0 - no_p) * 100, 1),
            'direction': 'NO',
            'reason': f'Event extremely unlikely before Jul 31, NO at {no_p}'
        })

output = {
    'scanned': scanned,
    'signals_count': len(signals),
    'signals': signals,
    'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
}

print(json.dumps(output, indent=2))
" > "$OUTPUT_FILE" 2>&1

echo "✅ Scan complete: $(jq -r '.scanned' $OUTPUT_FILE) markets scanned, $(jq -r '.signals_count' $OUTPUT_FILE) signals found"
