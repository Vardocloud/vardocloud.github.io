#!/usr/bin/env python3
"""
Makro Veri Çekme Aracı — BIST + Emtia + Forex
v1.0 — 27 Haziran 2026

Kullanım:
  python3 makro_veri.py                     # Tüm verileri çek
  python3 makro_veri.py --format json       # JSON çıktı
  python3 makro_veri.py --bist              # Sadece BIST
"""

import sys
import json
from datetime import datetime

def makro_veri_cek(output_format='text'):
    """Tüm makro verileri çek"""
    import yfinance as yf
    
    results = {}
    
    # === VARLIK SEMBOLLERİ ===
    symbols = {
        # Emtia
        "Altın (ons)": "GC=F",
        "Gümüş": "SI=F",
        "Bakır": "HG=F",
        "Petrol (Brent)": "BZ=F",
        
        # Forex
        "USD/TRY": "USDTRY=X",
        "EUR/TRY": "EURTRY=X",
        "EUR/USD": "EURUSD=X",
        "DXY (Dolar Endeksi)": "DX-Y.NYB",
        
        # BIST
        "BIST100": "XU100.IS",
        "BIST Banka": "XBANK.IS",
        "BIST Sinai": "XUSIN.IS",
        "BIST Teknoloji": "XUTEK.IS",
        "BIST Hizmetler": "XUHIZ.IS",
        "BIST Mali": "XUMAL.IS",
        "BIST Gıda": "XGIDA.IS",
        
        # ABD
        "S&P500": "^GSPC",
        "NASDAQ": "^IXIC",
        "Dow Jones": "^DJI",
        
        # Kripto
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD",
        
        # Tahvil
        "ABD 10Y": "^TNX",
    }
    
    # === TÜM SEMBOLLERİ DENE ===
    basarili = 0
    basarisiz = 0
    
    for name, symbol in symbols.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                basarisiz += 1
                continue
            
            last_close = hist["Close"].iloc[-1]
            prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else last_close
            change = last_close - prev_close
            change_pct = (change / prev_close) * 100 if prev_close else 0
            
            # Hacim
            volume = hist["Volume"].iloc[-1] if "Volume" in hist else 0
            
            results[name] = {
                "symbol": symbol,
                "son_fiyat": round(last_close, 4),
                "degisim": round(change, 4),
                "degisim_yuzde": round(change_pct, 2),
                "hacim": int(volume) if volume else 0,
                "tarih": str(hist.index[-1].date()),
                "durum": "✅"
            }
            basarili += 1
            
        except Exception as e:
            results[name] = {
                "symbol": symbol,
                "durum": "❌",
                "hata": str(e)[:50]
            }
            basarisiz += 1
    
    # === MAKRO GÖSTERGELER (web'den) ===
    # TCMB faizi — güncel veri yok, sabit değer kullan
    # Gerçek veri için web scraping gerek
    
    meta = {
        "timestamp": datetime.now().isoformat(),
        "toplam_sembol": len(symbols),
        "basarili": basarili,
        "basarisiz": basarisiz
    }
    
    if output_format == 'json':
        output = {"meta": meta, "veriler": results}
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*65}")
        print(f"  📊 MAKRO VERİ PANOSU — {datetime.now().strftime('%d %B %Y %H:%M')}")
        print(f"{'='*65}")
        
        print(f"\n🏅 BAŞARILI: {basarili}/{len(symbols)} | ❌ BAŞARISIZ: {basarisiz}")
        
        # Emtia
        print(f"\n{'─'*65}")
        print(f"  🪙 EMTİA")
        print(f"{'─'*65}")
        for name in ["Altın (ons)", "Gümüş", "Bakır", "Petrol (Brent)"]:
            r = results.get(name)
            if r and r["durum"] == "✅":
                arrow = "📈" if r["degisim_yuzde"] > 0 else "📉"
                print(f"  {arrow} {name:<15s} {r['son_fiyat']:>10,.2f}  ({r['degisim_yuzde']:>+.2f}%)")
            elif r:
                print(f"  ❌ {name:<15s} — {r.get('hata', 'Veri yok')[:30]}")
        
        # Forex
        print(f"\n{'─'*65}")
        print(f"  💵 FOREX")
        print(f"{'─'*65}")
        for name in ["USD/TRY", "EUR/TRY", "EUR/USD", "DXY (Dolar Endeksi)"]:
            r = results.get(name)
            if r and r["durum"] == "✅":
                arrow = "📈" if r["degisim_yuzde"] > 0 else "📉"
                print(f"  {arrow} {name:<20s} {r['son_fiyat']:>10,.4f}  ({r['degisim_yuzde']:>+.2f}%)")
            elif r:
                print(f"  ❌ {name:<20s} — {r.get('hata', 'Veri yok')[:30]}")
        
        # BIST
        print(f"\n{'─'*65}")
        print(f"  🏢 BIST")
        print(f"{'─'*65}")
        for name in sorted(results.keys()):
            if "BIST" in name:
                r = results[name]
                if r["durum"] == "✅":
                    arrow = "📈" if r["degisim_yuzde"] > 0 else "📉"
                    print(f"  {arrow} {name:<20s} {r['son_fiyat']:>10,.2f}  ({r['degisim_yuzde']:>+.2f}%)")
                elif r:
                    print(f"  ❌ {name:<20s} — {r.get('hata', 'Veri yok')[:30]}")
        
        # ABD & Kripto
        print(f"\n{'─'*65}")
        print(f"  🌍 ABD & KRİPTO")
        print(f"{'─'*65}")
        for name in ["S&P500", "NASDAQ", "Dow Jones", "ABD 10Y", "Bitcoin", "Ethereum"]:
            r = results.get(name)
            if r and r["durum"] == "✅":
                arrow = "📈" if r["degisim_yuzde"] > 0 else "📉"
                if "ABD 10Y" in name:
                    print(f"  {arrow} {name:<20s} %{r['son_fiyat']:.2f}")
                else:
                    print(f"  {arrow} {name:<20s} {r['son_fiyat']:>12,.2f}  ({r['degisim_yuzde']:>+.2f}%)")
            elif r:
                print(f"  ❌ {name:<20s} — {r.get('hata', 'Veri yok')[:30]}")
        
        # Başarısız semboller
        basarisiz_list = [(n, r) for n, r in results.items() if r["durum"] == "❌"]
        if basarisiz_list:
            print(f"\n{'─'*65}")
            print(f"  ❌ ÇALIŞMAYAN SEMBOLLER")
            print(f"{'─'*65}")
            for name, r in basarisiz_list:
                print(f"  • {name:<20s} ({r['symbol']}) — {r.get('hata', 'Bilinmiyor')}")
        
        print(f"\n{'='*65}\n")

if __name__ == "__main__":
    fmt = 'json' if '--json' in sys.argv or '--format' in sys.argv and 'json' in sys.argv else 'text'
    makro_veri_cek(fmt)
