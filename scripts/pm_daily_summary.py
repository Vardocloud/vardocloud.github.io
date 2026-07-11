#!/usr/bin/env python3
"""Polymarket Daily Summary — son 24 saatteki işlemleri özetler"""
import json, os, glob, datetime

DATA_DIR = os.path.expanduser("~/.hermes/data")
SCAN_DIR = os.path.expanduser("~/.local/share/pm-trader")

# Son 24 saatteki scan dosyalarını bul
now = datetime.datetime.now()
cutoff = now - datetime.timedelta(hours=24)
scans = sorted(glob.glob(os.path.join(DATA_DIR, "scan_2*.json")), reverse=True)

print(f"📡 **Daily Polymarket Summary** — {now.strftime('%Y-%m-%d %H:%M')}")
print()

# Son scan dosyasını oku
latest = None
recent_scans = []
for f in scans[:48]:  # son 48 scan (24 saat × 30dk)
    try:
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(f))
        if mtime > cutoff:
            with open(f) as fh:
                data = json.load(fh)
                recent_scans.append(data)
                if latest is None:
                    latest = data
    except:
        continue

if not latest:
    print("❌ Son 24 saatte scan bulunamadı")
    exit(0)

# Portföy bilgisi
pf = latest.get("pm_trader", {}).get("portfolio", [])
bal = latest.get("pm_trader", {}).get("balance", {})
stats = latest.get("pm_trader", {}).get("stats", {})
btc = latest.get("patterns", {}).get("btc_tracker", {})
whales = latest.get("patterns", {}).get("market_scan", {}).get("whale_signals", [])

print(f"├ Scans today: {len(recent_scans)}")
print(f"├ Portfolio: {len(pf)} positions")
print(f"├ Total value: ${bal.get('total_value', 0):,.2f}")
print(f"├ PnL: ${stats.get('pnl', 0):,.2f}")
print(f"├ BTC: ${btc.get('btc_price', 0):,.0f} ({btc.get('change_24h_pct', 0):+.2f}%)")
print(f"└ Whale signals: {len(whales)}")
print()

# Pozisyonlar
if pf:
    print("**Open Positions:**")
    total_pnl = 0
    for i, p in enumerate(pf, 1):
        pnl = p.get("unrealized_pnl", 0)
        total_pnl += pnl
        emoji = "🟢" if pnl > 0 else "🔴"
        print(f"{i}. {emoji} {p['market_question'][:50]}")
        print(f"   {p['outcome']} @ {p.get('live_price', 0)*100:.1f}¢ | Cost: ${p['total_cost']:.2f} | PnL: ${pnl:.2f}")
    print(f"\n**Total PnL:** ${total_pnl:.2f}")
else:
    print("**No open positions.**")
print()

# Son 24 saatteki trade'leri kontrol et
all_trades = []
for scan in recent_scans[:5]:  # ilk 5 scan'de trade var mı?
    hist = scan.get("pm_trader", {}).get("history", [])
    all_trades.extend(hist)

new_trades_today = [t for t in all_trades if t.get("side") == "buy"]
sells_today = [t for t in all_trades if t.get("side") == "sell"]

if new_trades_today:
    print(f"**New trades today:** {len(new_trades_today)}")
    for t in new_trades_today[:5]:
        print(f"  • BUY {t.get('market_question','?')[:45]} | ${t.get('amount_usd',0):.2f} @ {t.get('avg_price',0)*100:.1f}¢")

if sells_today:
    print(f"**Sells today:** {len(sells_today)}")

print()

# Whale sinyalleri
if whales:
    print(f"**Whale Watch:** {len(whales)} signals")
    for w in whales[:3]:
        print(f"  • {w['action']}: {w.get('question','?')[:45]}")

# BTC
if btc.get("signal"):
    print(f"\n**BTC Tracker:** {btc.get('signal')} — ${btc.get('btc_price',0):,.0f} ({btc.get('change_24h_pct',0):+.2f}%)")

# Insight
print(f"\n---")
print(f"*Next scan in ~30min | Daily report every 21:00*")
