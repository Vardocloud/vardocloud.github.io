#!/usr/bin/env python3

import json
import time
import os
from datetime import datetime
import requests

# Configuration
OUTPUT_FILE = "/home/ubuntu/.hermes/data/latest_btc_tracker.json"
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/24hr"
POLYMARKET_API_URL = "https://polymarket.com/api/markets"

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

print("🚀 Starting Dexter's Lab BTC Tracker Simulation")

# Get BTC price from Binance
print("📊 Fetching BTC price from Binance...")
try:
    btc_response = requests.get(BINANCE_API_URL, params={"symbol": "BTCUSDT"})
    if btc_response.status_code != 200:
        print(f"❌ Failed to fetch BTC data: {btc_response.status_code}")
        exit(1)
    
    btc_data = btc_response.json()
    btc_price = float(btc_data['lastPrice'])
    price_change_24h = float(btc_data['priceChangePercent'])
    
    print(f"✅ Retrieved BTC data:")
    print(f"   - Current Price: ${btc_price:,.2f}")
    print(f"   - 24h Change: {price_change_24h:+.2f}%")
    
except Exception as e:
    print(f"❌ Error fetching Binance BTC data: {e}")
    exit(1)

# Search for Bitcoin-related markets on Polymarket
print("🔍 Searching for Bitcoin markets on Polymarket...")
try:
    # Use search query for bitcoin markets
    # Note: Polymarket API might require additional parameters or have different endpoint structure
    # We'll try multiple approaches
    markets_result = {
        'markets': [],
        'search_query': 'bitcoin',
        'total_found': 0
    }
    
    # Try different search approaches
    search_attempts = [
        {"query": "bitcoin", "category": "cryptocurrency"},
        {"query": "BTC", "category": "cryptocurrency"},
        {"query": "bitcoin price", "category": "cryptocurrency"}
    ]
    
    for attempt in search_attempts:
        try:
            params = {"query": attempt["query"]}
            response = requests.get(POLYMARKET_API_URL, params=params)
            if response.status_code == 200:
                markets_data = response.json()
                if markets_data and isinstance(markets_data, list):
                    markets_result['markets'] = markets_data
                    markets_result['total_found'] = len(markets_data)
                    markets_result['search_method'] = f"query: {attempt['query']}"
                    print(f"✅ Found {len(markets_data)} Bitcoin-related markets")
                    break
                elif markets_data and isinstance(markets_data, dict) and 'markets' in markets_data:
                    markets_result['markets'] = markets_data['markets']
                    markets_result['total_found'] = len(markets_data['markets'])
                    markets_result['search_method'] = f"query: {attempt['query']}"
                    print(f"✅ Found {len(markets_data['markets'])} Bitcoin-related markets")
                    break
        except Exception as e:
            print(f"⚠️ Attempt {attempt['query']} failed: {e}")
            continue
    
    if markets_result['total_found'] == 0:
        markets_result['markets'] = []
        markets_result['note'] = "No markets found or API structure not matched"
        print("⚠️ No Bitcoin markets found via Polymarket API")
    
except Exception as e:
    print(f"❌ Error searching Polymarket: {e}")
    markets_result = {
        'markets': [],
        'search_query': 'bitcoin',
        'total_found': 0,
        'error': str(e)
    }

# Determine simulation signal based on 24h price change
signal = 'BEKLE'  # Default
if price_change_24h > 2:
    signal = 'OLASILIK VAR'
elif price_change_24h > 1:
    signal = 'IZLE'
else:
    signal = 'BEKLE'

# Prepare output data
output_data = {
    'timestamp': datetime.now().isoformat(),
    'script_type': "Dexter's Lab BTC Simulation",
    'btc_data': {
        'symbol': 'BTCUSDT',
        'current_price': btc_price,
        'price_change_24h_percent': price_change_24h,
        'source': 'Binance API'
    },
    'polymarket_analysis': markets_result,
    'simulation_signal': {
        'signal': signal,
        'price_change_threshold': price_change_24h,
        '24h_performance': price_change_24h,
        'recommendation': f"Price changed {price_change_24h:+.2f}% in last 24 hours - Signal: {signal}"
    }
}

# Save to file
with open(OUTPUT_FILE, 'w') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"✅ Data saved to {OUTPUT_FILE}")
print(f"📊 Simulation Summary:")
print(f"   - BTC 24h Change: {price_change_24h:+.2f}%")
print(f"   - Polymarket Markets Found: {markets_result['total_found']}")
print(f"   - Simulation Signal: {signal}")
print(f"🚀 Script completed successfully!")

