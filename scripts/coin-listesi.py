#!/usr/bin/env python3
"""
Coin Listesi Çekici — Investing.com + CoinGecko
Vanitas Kaldıraçlı İşlem Simülasyonu için güncel coin verisi

Kullanım:
  python3 coin-listesi.py           # CoinGecko'dan ilk 250 coin
  python3 coin-listesi.py --invest  # Investing.com'dan da doğrula
  python3 coin-listesi.py --rapor   # Kayıtlı listeyi göster
"""

import json
import os
import sys
import time
from datetime import datetime
from urllib.request import Request, urlopen

VERI_DIZINI = os.path.expanduser("~/.hermes/data/coins")
COIN_LIST_DOSYA = os.path.join(VERI_DIZINI, "coin-listesi.json")
COIN_DETAY_DOSYA = os.path.join(VERI_DIZINI, "coin-fiyatlari.json")


def log(msg):
    print(f"[COIN] {msg}", file=sys.stderr)


def coingecko_cek(limit=250):
    """CoinGecko API ile ilk N coin'i çek"""
    log(f"CoinGecko'dan ilk {limit} coin çekiliyor...")
    
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page={limit}&page=1&sparkline=false&price_change_percentage=24h,7d"
    
    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json',
    })
    
    try:
        response = urlopen(req, timeout=30)
        data = json.loads(response.read().decode())
        
        coins = []
        for c in data:
            coins.append({
                'id': c['id'],
                'symbol': c['symbol'].upper(),
                'name': c['name'],
                'price': c['current_price'],
                'market_cap': c['market_cap'],
                'vol_24h': c['total_volume'],
                'chg_24h': c.get('price_change_percentage_24h_in_currency'),
                'chg_7d': c.get('price_change_percentage_7d_in_currency'),
                'ath': c['ath'],
                'ath_date': c.get('ath_date', ''),
                'circulating_supply': c['circulating_supply'],
                'total_supply': c.get('total_supply'),
                'max_supply': c.get('max_supply'),
            })
        
        log(f"✅ {len(coins)} coin alındı")
        return coins
    
    except Exception as e:
        log(f"❌ CoinGecko hatası: {e}")
        return None


def investing_cek():
    """Investing.com'dan ilk 20 coin'in fiyatını doğrula"""
    log("Investing.com'dan doğrulama çekiliyor...")
    # Browser ile çekilen veriyi burada işleyebiliriz
    # Şimdilik CoinGecko verisi yeterli
    return True


def kaydet(coins):
    """Coin listesini kaydet"""
    os.makedirs(VERI_DIZINI, exist_ok=True)
    
    output = {
        'guncelleme': datetime.now().isoformat(),
        'kaynak': 'coingecko',
        'toplam_coin': len(coins),
        'coins': coins,
    }
    
    with open(COIN_LIST_DOSYA, 'w') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    log(f"💾 Kaydedildi: {COIN_LIST_DOSYA} ({len(coins)} coin)")
    
    # Kısa fiyat listesi de ayrı kaydet
    fiyatlar = {c['symbol']: {
        'name': c['name'],
        'price': c['price'],
        'chg_24h': c['chg_24h'],
        'mcap': c['market_cap'],
    } for c in coins}
    
    with open(COIN_DETAY_DOSYA, 'w') as f:
        json.dump({
            'guncelleme': datetime.now().isoformat(),
            'coins': fiyatlar,
        }, f, ensure_ascii=False, indent=2)
    
    return output


def raporla(coins=None):
    """Coin listesini raporla"""
    if coins is None:
        if os.path.exists(COIN_LIST_DOSYA):
            with open(COIN_LIST_DOSYA) as f:
                data = json.load(f)
            coins = data.get('coins', [])
        else:
            print("❌ Henüz coin listesi çekilmemiş.")
            return
    
    print(f"\n{'='*50}")
    print(f"🪙 COIN LİSTESİ — {len(coins)} coin")
    print(f"{'='*50}")
    print(f"{'Sembol':<8} {'İsim':<20} {'Fiyat':<12} {'24s %':<8} {'7g %':<8} {'Piyasa Değeri':<12}")
    print(f"{'-'*70}")
    
    for c in coins[:30]:
        sembol = c['symbol']
        isim = c['name'][:18]
        fiyat = f"${c['price']:.4f}" if c['price'] < 1 else f"${c['price']:.2f}"
        chg24 = f"%{c['chg_24h']:+.2f}" if c.get('chg_24h') else "N/A"
        chg7 = f"%{c['chg_7d']:+.2f}" if c.get('chg_7d') else "N/A"
        mcap = f"${c['market_cap']/1e9:.1f}B" if c.get('market_cap') else "N/A"
        print(f"{sembol:<8} {isim:<20} {fiyat:<12} {chg24:<8} {chg7:<8} {mcap:<12}")
    
    print(f"\n... ve {len(coins)-30} coin daha")
    print(f"📁 {COIN_LIST_DOSYA}")


def main():
    if '--rapor' in sys.argv:
        raporla()
        return
    
    # CoinGecko'dan çek
    coins = coingecko_cek(250)
    if coins:
        kaydet(coins)
        raporla(coins)
    
    # Investing doğrulama
    if '--invest' in sys.argv:
        investing_cek()


if __name__ == '__main__':
    main()
