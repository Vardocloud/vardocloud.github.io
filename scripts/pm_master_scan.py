#!/usr/bin/env python3
"""
Polymarket Master Scan — Tüm Pattern'leri Tek Script'te Çalıştırır
====================================================================
Pattern 1: News Signal (RSS + market karşılaştırması)
Pattern 2: Mispricing (uç fiyat tespiti) 
Pattern 3: Whale/Copy Trading İzleme
Pattern 4: Bregman Arbitraj (YES+NO < 0.98)
Pattern 5: BTC Takip Simülasyonu

Çıktı: ~/.hermes/data/master_scan_{timestamp}.json
       ~/.hermes/data/latest_scan.json (symlink/güncel)
"""

import json
import os
import sys
import subprocess
import urllib.request
import urllib.error
import datetime
import ssl
import time
import random

DATA_DIR = os.path.expanduser("~/.hermes/data")
PM_DATA_DIR = os.path.expanduser("~/.local/share/pm-trader")
os.makedirs(DATA_DIR, exist_ok=True)

ssl_ctx = ssl.create_default_context()

# Rate limit yönetimi
RATE_LIMIT_HITS = 0
MAX_RETRIES = 5

def fetch_json(url, timeout=15, retries=MAX_RETRIES):
    """Fetch JSON from URL with rate limit handling and exponential backoff"""
    global RATE_LIMIT_HITS
    last_error = None
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as r:
                # Başarılı — rate limit hit'ini sıfırla
                if attempt > 0:
                    RATE_LIMIT_HITS = max(0, RATE_LIMIT_HITS - 1)
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            status = e.code
            if status == 429:
                RATE_LIMIT_HITS += 1
                wait = min(2 ** attempt + random.uniform(0, 1), 60)
                print(f"  ⚠️  429 Rate Limit (attempt {attempt+1}/{retries}), waiting {wait:.0f}s...")
                time.sleep(wait)
                last_error = f"429_rate_limit_attempt_{attempt+1}"
            elif status == 503:
                wait = min(2 ** attempt + random.uniform(0, 1), 30)
                print(f"  ⚠️  503 Service Unavailable (attempt {attempt+1}/{retries}), waiting {wait:.0f}s...")
                time.sleep(wait)
                last_error = f"503_service_unavailable_attempt_{attempt+1}"
            else:
                return {"error": f"HTTP_{status}", "url": url}
        except urllib.error.URLError as e:
            if "timed out" in str(e).lower():
                wait = 2 ** attempt
                print(f"  ⚠️  Timeout (attempt {attempt+1}/{retries}), waiting {wait}s...")
                time.sleep(wait)
                last_error = f"timeout_attempt_{attempt+1}"
            else:
                return {"error": str(e), "url": url}
        except Exception as e:
            return {"error": str(e), "url": url}
    
    return {"error": f"rate_limited_after_{retries}_retries", "url": url, "rate_limited": True}

def run_cmd(cmd, timeout=30):
    """Run shell command and return output"""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return {"ok": r.returncode == 0, "stdout": r.stdout.strip(), "stderr": r.stderr.strip(), "exit": r.returncode}
    except subprocess.TimeoutExpired:
        return {"ok": False, "stdout": "", "stderr": "TIMEOUT", "exit": -1}
    except Exception as e:
        return {"ok": False, "stdout": "", "stderr": str(e), "exit": -1}

def scan_gamma_api():
    """Gamma API'den tüm kategorileri tara — Pattern 2+3+4"""
    results = {"events": [], "markets": [], "errors": []}
    
    # Events endpoint (yüksek hacimli event'ler)
    events_url = "https://gamma-api.polymarket.com/events?closed=false&limit=40&order=volume_usd&asc=false"
    events = fetch_json(events_url)
    if "error" in events:
        results["errors"].append(f"Events API: {events['error']}")
        return results
    
    for e in events[:40]:
        title = e.get("title", "?")
        vol = float(e.get("volume", 0))
        tag = e.get("tag", "unknown")
        event_id = e.get("id", "?")
        
        markets = e.get("markets", [])
        event_markets = []
        for m in markets:
            if m.get("closed", True):
                continue  # kapalı marketleri atla
            q = m.get("question", "?")
            try:
                prices = json.loads(m.get("outcomePrices", "[0,0]"))
                yes_p = float(prices[0])
                no_p = float(prices[1]) if len(prices) > 1 else 0
            except:
                yes_p, no_p = 0, 0
            m_vol = float(m.get("volume", 0))
            liq = float(m.get("liquidity", 0))
            slug = m.get("slug", "")
            end_date = m.get("endDate", "")[:10]
            
            market_data = {
                "slug": slug,
                "question": q,
                "yes_price": round(yes_p, 4),
                "no_price": round(no_p, 4),
                "volume": m_vol,
                "liquidity": liq,
                "end_date": end_date,
                "total_yn": round(yes_p + no_p, 4),
            }
            
            # Pattern 4: Bregman Arbitraj
            if 0 < yes_p + no_p < 0.98 and m_vol > 1000:
                market_data["bregman_arbitrage"] = {
                    "type": "brengman",
                    "edge_pct": round((1.0 - (yes_p + no_p)) / (yes_p + no_p) * 100, 2),
                    "action": "BUY_BOTH",
                    "notional_max": min(200, liq * 0.1)
                }
            
            # Pattern 2: Mispricing candidates
            q_lower = q.lower()
            is_gta = "gta vi" in q_lower or "gta" in q_lower
            is_meme = any(w in q_lower for w in ["jesus", "rihanna", "playboi", "carti", "ufo", "alien", "bigfoot", "ghost"])
            
            if is_gta or (is_meme and m_vol < 500000):
                market_data["filter_reason"] = "GTA VI 50/50 floor" if is_gta else "low_volume_meme"
                market_data["skip_trade"] = True
            else:
                # Extreme fiyat kontrolü
                if 0 < yes_p <= 0.15 and m_vol > 100000:
                    market_data["mispricing"] = {"type": "yes_cheap", "direction": "BUY_YES", "confidence": "medium"}
                elif no_p <= 0.15 and yes_p >= 0.85 and m_vol > 100000:
                    market_data["mispricing"] = {"type": "no_cheap", "direction": "BUY_NO", "confidence": "medium"}
                elif yes_p <= 0.01 and m_vol > 50000:
                    market_data["mispricing"] = {"type": "yes_extreme", "direction": "INVESTIGATE", "confidence": "low"}
            
            event_markets.append(market_data)
        
        if event_markets:
            results["markets"].extend(event_markets)
    
    # Pattern 3: Whale/Copy Trading signals
    whale_signals = []
    for m in results["markets"]:
        if m.get("skip_trade"):
            continue
        if m["volume"] > 500000 and 0.20 <= m["yes_price"] <= 0.80:
            whale_signals.append({
                "slug": m["slug"],
                "question": m["question"],
                "type": "whale_watch",
                "reason": f"High volume (${m['volume']:,.0f}) + contested price ({m['yes_price']:.0%})",
                "action": "IZLE"
            })
        elif m["volume"] > 100000 and (m["yes_price"] < 0.15 or m["yes_price"] > 0.85):
            whale_signals.append({
                "slug": m["slug"],
                "question": m["question"],
                "type": "near_extreme",
                "reason": f"Volume ${m['volume']:,.0f} at extreme price {m['yes_price']:.0%}",
                "action": "ARASTIR"
            })
    
    results["whale_signals"] = whale_signals
    return results

def scan_btc():
    """Pattern 5: BTC Fiyat Takibi"""
    btc = fetch_json("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT")
    if "error" in btc:
        return {"error": btc["error"]}
    
    price = float(btc.get("lastPrice", 0))
    change = float(btc.get("priceChangePercent", 0))
    
    if abs(change) > 2:
        signal = "OLASILIK_VAR"
    elif abs(change) > 1:
        signal = "IZLE"
    else:
        signal = "BEKLE"
    
    return {
        "btc_price": price,
        "change_24h_pct": change,
        "signal": signal,
        "high_24h": float(btc.get("highPrice", 0)),
        "low_24h": float(btc.get("lowPrice", 0)),
        "volume_24h": float(btc.get("volume", 0)),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

def scan_news():
    """Pattern 1: RSS haber taraması (blogwatcher)"""
    bw = os.path.expanduser("~/bin/blogwatcher-cli")
    if not os.path.exists(bw):
        return {"error": "blogwatcher-cli not installed", "feeds": 0, "articles": []}
    
    # Feed'leri listele
    list_result = run_cmd(f"{bw} blogs", timeout=10)
    feeds = 0
    if list_result["ok"]:
        feeds = len([l for l in list_result["stdout"].split("\n") if l.strip()])
    
    # Son haberleri çek
    news_result = run_cmd(f"{bw} list --limit 30", timeout=30)
    articles = []
    if news_result["ok"]:
        for line in news_result["stdout"].split("\n"):
            if line.strip() and "\t" in line:
                parts = line.split("\t")
                articles.append({"source": parts[0] if len(parts) > 0 else "?", "title": parts[-1] if len(parts) > 1 else line.strip()})
    
    return {"feeds": feeds, "articles_count": len(articles), "articles": articles[:20], "feeds_list": list_result["stdout"][:1000]}

def scan_pm_trader():
    """pm-trader ile portföy ve market verisi çek"""
    portfolio = json.loads(run_cmd("pm-trader portfolio", timeout=10).get("stdout", "{}"))
    balance = json.loads(run_cmd("pm-trader balance", timeout=10).get("stdout", "{}"))
    stats = json.loads(run_cmd("pm-trader stats", timeout=10).get("stdout", "{}"))
    history = json.loads(run_cmd("pm-trader history --limit 20", timeout=10).get("stdout", "{}"))
    markets = json.loads(run_cmd("pm-trader markets list --limit 30 --sort volume", timeout=15).get("stdout", "{}"))
    
    return {
        "portfolio": portfolio.get("data", []),
        "balance": balance.get("data", {}),
        "stats": stats.get("data", {}),
        "history": history.get("data", [])[:10],
        "markets_from_trader": markets.get("data", [])[:5]
    }

def update_price_history(new_markets):
    """Fiyat geçmişini güncelle — trend analizi için"""
    history_file = os.path.join(DATA_DIR, "price_history.json")
    history = {}
    if os.path.exists(history_file):
        with open(history_file) as f:
            history = json.load(f)
    
    now = datetime.datetime.utcnow().isoformat()
    for m in new_markets:
        slug = m.get("slug", "")
        if not slug:
            continue
        if slug not in history:
            history[slug] = {"name": m.get("question", slug), "prices": []}
        history[slug]["prices"].append({
            "t": now,
            "y": m.get("yes_price", 0),
            "n": m.get("no_price", 0),
            "v": m.get("volume", 0)
        })
        # Son 500 kaydı tut
        history[slug]["prices"] = history[slug]["prices"][-500:]
    
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)
    
    # Trend analizi
    trends = {}
    for slug, data in history.items():
        prices = data["prices"]
        if len(prices) >= 2:
            first = prices[0]
            last = prices[-1]
            change = last["y"] - first["y"] if first["y"] > 0 else 0
            change_pct = (change / first["y"] * 100) if first["y"] > 0 else 0
            vol_change = ((last["v"] - first["v"]) / first["v"] * 100) if first["v"] > 0 else 0
            trends[slug] = {
                "name": data.get("name", slug),
                "price_change": round(change, 4),
                "price_change_pct": round(change_pct, 1),
                "volume_change_pct": round(vol_change, 1),
                "start_price": round(first["y"], 4),
                "current_price": round(last["y"], 4),
                "data_points": len(prices),
                "trend": "up" if change_pct > 5 else ("down" if change_pct < -5 else "stable")
            }
    
    return trends

# ===== MAIN =====
print("🔍 Polymarket Master Scan başlıyor...")
start = time.time()

results = {
    "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "human_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M %Z"),
    "patterns": {}
}

# Pattern 1: News
print("  📡 [1/5] News Signal (RSS)...", end=" ")
results["patterns"]["news_signal"] = scan_news()
news = results["patterns"]["news_signal"]
print(f"{news.get('feeds', 0)} feeds, {news.get('articles_count', 0)} articles")

# Pattern 2+3+4: Gamma API
print("  🌐 [2/5] Gamma API taraması...", end=" ")
gamma = scan_gamma_api()
results["patterns"]["market_scan"] = {
    "markets_scanned": len(gamma.get("markets", [])),
    "open_markets": [m for m in gamma.get("markets", []) if not m.get("skip_trade", False)],
    "filtered_gta_or_meme": [m for m in gamma.get("markets", []) if m.get("skip_trade", False)],
    "whale_signals": gamma.get("whale_signals", []),
    "errors": gamma.get("errors", [])
}
# Bregman ayrı listele
bregman = [m for m in gamma.get("markets", []) if "bregman_arbitrage" in m]
market_errors = gamma.get("errors", [])
print(f"{len(gamma.get('markets', []))} markets, {len(bregman)} bregman, {len(market_errors)} errors")

# Pattern 3: Whale (gamma içinde)
whales = gamma.get("whale_signals", [])
print(f"  🐋 [3/5] Whale signals: {len(whales)} found")

# Pattern 4: Bregman (gamma içinde)
print(f"  📐 [4/5] Bregman opportunities: {len(bregman)}")

# Pattern 5: BTC
print("  ₿  [5/5] BTC Tracker...", end=" ")
btc = scan_btc()
results["patterns"]["btc_tracker"] = btc
print(f"BTC ${btc.get('btc_price', 0):,.0f} ({btc.get('change_24h_pct', 0):+.2f}%) → {btc.get('signal', '?')}")

# pm-trader durumu
results["pm_trader"] = scan_pm_trader()

# Fiyat trend analizi — Fix #1
all_open_markets = gamma.get("markets", [])
results["trends"] = update_price_history(all_open_markets)

# Portföy yönetimi — Fix #3 (stop-loss/take-profit kontrolü)
portfolio = results.get("pm_trader", {}).get("portfolio", [])
risk_alerts = []
for p in portfolio:
    pnl = p.get("unrealized_pnl", 0)
    cost = p.get("total_cost", 0)
    pnl_pct = (pnl / cost * 100) if cost > 0 else 0
    slug = p.get("market_slug", "")
    
    # Stop-loss: -%50'nin altına düşerse uyarı
    if pnl_pct < -50:
        risk_alerts.append({
            "slug": slug,
            "market": p.get("market_question", ""),
            "type": "STOP_LOSS",
            "pnl_pct": round(pnl_pct, 1),
            "action": "DÜŞÜN: Zararına satmayı değerlendir"
        })
    # Take-profit: +%50'nin üstüne çıkarsa uyarı
    elif pnl_pct > 50:
        risk_alerts.append({
            "slug": slug,
            "market": p.get("market_question", ""),
            "type": "TAKE_PROFIT",
            "pnl_pct": round(pnl_pct, 1),
            "action": "DÜŞÜN: Kârı almayı değerlendir"
        })
results["risk_alerts"] = risk_alerts

# Local log — Fix #5
log_entry = {
    "ts": datetime.datetime.now().isoformat(),
    "status": "ok" if not results.get("rate_limit", {}).get("any_rate_limited") else "rate_limited",
    "markets_scanned": results.get("patterns", {}).get("market_scan", {}).get("markets_scanned", 0),
    "portfolio_count": len(portfolio),
    "pnl": results.get("pm_trader", {}).get("stats", {}).get("pnl", 0),
    "total_value": results.get("pm_trader", {}).get("balance", {}).get("total_value", 0),
    "btc_price": btc.get("btc_price", 0),
    "btc_signal": btc.get("signal", ""),
    "whale_count": len(gamma.get("whale_signals", [])),
    "new_matches": len(results.get("news_market_matches", [])),
    "risk_alerts": len(risk_alerts),
    "trades_count": len(results.get("pm_trader", {}).get("history", []))
}
log_file = os.path.join(DATA_DIR, "scan_log.jsonl")
with open(log_file, "a") as f:
    f.write(json.dumps(log_entry) + "\n")

# Haber-market eşleştirmesi — Fix #2
news_data = results["patterns"].get("news_signal", {})
articles = news_data.get("articles", [])
if articles:
    keyword_market_map = {
        "kraken": ["kraken-ipo", "kraken"],
        "bitcoin": ["bitcoin", "btc"],
        "openai": ["openai"],
        "trump": ["trump"],
        "ukraine": ["ukraine"],
        "nato": ["nato"],
        "election": ["election", "uk election"],
        "china": ["china", "taiwan", "chinese"],
        "russia": ["russia"],
        "crypto": ["bitcoin", "ethereum", "crypto"],
        "ipo": ["ipo", "strava"],
        "ai": ["openai"],
    }
    news_matches = []
    for article in articles[:30]:
        title = article.get("title", "").lower()
        source = article.get("source", "")
        matched_markets = []
        for keyword, market_keywords in keyword_market_map.items():
            if keyword in title:
                matched_markets.extend(market_keywords)
        if matched_markets:
            news_matches.append({
                "title": article.get("title", "")[:80],
                "source": source,
                "matched_markets": list(set(matched_markets))
            })
    results["news_market_matches"] = news_matches[:10]

# Rate limit durumu
results["rate_limit"] = {
    "hits_this_scan": RATE_LIMIT_HITS,
    "any_rate_limited": RATE_LIMIT_HITS > 0,
    "note": "Rate limit aşılırsa bir sonraki saat tekrar dener" if RATE_LIMIT_HITS > 0 else "Normal"
}

elapsed = time.time() - start
results["elapsed_seconds"] = round(elapsed, 1)
results["scan_id"] = datetime.datetime.now().strftime("scan_%Y%m%d_%H%M")

# Kaydet
output_path = os.path.join(DATA_DIR, f"{results['scan_id']}.json")
latest_path = os.path.join(DATA_DIR, "latest_scan.json")
with open(output_path, "w") as f:
    json.dump(results, f, indent=2, default=str)
# Symlink yerine kopyala (Windows uyumluluğu)
with open(latest_path, "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n✅ Scan tamam: {elapsed:.1f}s → {output_path}")
print(f"   Portföy: {results['pm_trader']['balance'].get('total_value', '?')}$")
print(f"   Açık pozisyon: {len(results['pm_trader']['portfolio'])}")
