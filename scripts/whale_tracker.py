#!/usr/bin/env python3

import json
import time
import os
from datetime import datetime
import requests

# Configuration
OUTPUT_FILE = "/home/ubuntu/.hermes/data/latest_whale_tracker.json"
GAMMA_API_BASE = "https://gamma-api.wormhole.gg"

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

print("🚀 Starting Copy Trading Evaluator - Whale Tracker")

# Get top 20 events from all categories
print("📊 Fetching top 20 events from Gamma API...")
try:
    events_response = requests.get(f"{GAMMA_API_BASE}/events", params={"limit": 20, "offset": 0})
    if events_response.status_code != 200:
        print(f"❌ Failed to fetch events: {events_response.status_code}")
        exit(1)
    
    events_data = events_response.json()
    print(f"✅ Retrieved {len(events_data)} events from Gamma")
    
except Exception as e:
    print(f"❌ Error fetching Gamma events: {e}")
    exit(1)

# Process events and analyze markets
processed_events = []

for i, event in enumerate(events_data):
    print(f"📋 Processing event {i+1}/{len(events_data)}: {event.get('question', 'Unknown')[:50]}...")
    
    # Get markets for this event
    try:
        markets_response = requests.get(f"{GAMMA_API_BASE}/markets", params={
            "event_id": event.get('id'),
            "limit": 50,
            "offset": 0
        })
        
        if markets_response.status_code == 200:
            markets_data = markets_response.json()
            
            # Analyze each market for signals
            event_signals = []
            
            for market in markets_data:
                # Extract market data
                market_question = market.get('question', '')
                market_yes_price = float(market.get('yes_price', 0))
                market_no_price = float(market.get('no_price', 0))
                
                # Calculate volume from available data
                volume_usd = market.get('volume', 0)
                
                # Calculate weighted average price (approximate)
                if market_yes_price + market_no_price > 0:
                    weighted_price = (market_yes_price * 100) / (market_yes_price + market_no_price)
                else:
                    weighted_price = 50
                
                # Detect whale watch signal
                if volume_usd > 500000 and 20 <= weighted_price <= 80:  # $500K+ and price range 0.20-0.80
                    signal_type = 'whale_watch'
                    event_signals.append({
                        'market_question': market_question,
                        'signal_type': signal_type,
                        'volume_usd': volume_usd,
                        'price': weighted_price,
                        'yes_price': market_yes_price,
                        'no_price': market_no_price,
                        'analysis': f"Volume ${volume_usd:,.0f} + price {weighted_price:.2f}% (contested range)"
                    })
                
                # Detect near extreme signal
                elif volume_usd > 100000 and (weighted_price < 15 or weighted_price > 85):
                    signal_type = 'near_extreme'
                    event_signals.append({
                        'market_question': market_question,
                        'signal_type': signal_type,
                        'volume_usd': volume_usd,
                        'price': weighted_price,
                        'yes_price': market_yes_price,
                        'no_price': market_no_price,
                        'analysis': f"Volume ${volume_usd:,.0f} + extreme price {weighted_price:.2f}%"
                    })
            
            # Add event info if signals were found
            if event_signals:
                processed_events.append({
                    'event_id': event.get('id'),
                    'event_question': event.get('question'),
                    'event_end_timestamp': event.get('end_timestamp'),
                    'signals': event_signals,
                    'total_signals_found': len(event_signals)
                })
                
    except Exception as e:
        print(f"⚠️ Error processing markets for event {event.get('id', 'unknown')}: {e}")
        continue

# Prepare output data
output_data = {
    'timestamp': datetime.now().isoformat(),
    'script_type': 'Copy Trading Evaluator - Whale Tracker',
    'total_events_processed': len(events_data),
    'events_with_signals': len(processed_events),
    'total_signals_found': sum(len(event['signals']) for event in processed_events),
    'events': processed_events
}

# Save to file
with open(OUTPUT_FILE, 'w') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"✅ Data saved to {OUTPUT_FILE}")
print(f"📊 Summary:")
print(f"   - Events processed: {len(events_data)}")
print(f"   - Events with signals: {len(processed_events)}")
print(f"   - Total signals: {sum(len(event['signals']) for event in processed_events)}")
print(f"🚀 Script completed successfully!")

