#!/usr/bin/env python3
"""
BIST Günlük Takip — Endeks + Portföy + Özet
Günde 1 kere çalışır (sabah 10:00)
"""

import json, os, sys
from datetime import datetime
from urllib.request import Request, urlopen

VERI_DIZINI = os.path.expanduser("~/.hermes/data/borsa")


def log(m): print(f"[BIST] {m}", file=sys.stderr)

def bist_fiyat(sembol):
    import yfinance as yf
    try:
        df = yf.Ticker(f"{sembol}.IS").history(period="5d")
        if df.empty: return None, None
        g = df['Close'].iloc[-1]
        d = ((g - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100 if len(df) > 1 else 0
        return round(g, 3), round(d, 2)
    except: return None, None

def ana():
    import yfinance as yf
    
    print(f"\n📈 BİST GÜNLÜK — {datetime.now().strftime('%d %B %Y %H:%M')}")
    print(f"{'='*50}")
    
    # BIST100 endeksi
    try:
        bist = yf.Ticker("XU100.IS")
        df = bist.history(period="5d")
        if not df.empty:
            son = df['Close'].iloc[-1]
            onceki = df['Close'].iloc[-2]
            deg = ((son - onceki) / onceki) * 100
            print(f"📊 BIST100: {son:.0f} (%{deg:+.2f})")
    except: print("📊 BIST100: —")
    
    print()
    
    # Takip listesi
    hisseler = ["KCAER", "THYAO", "EREGL", "AKBNK", "ASELS", "GARAN", "SASA"]
    
    print(f"{'Sembol':<8} {'Fiyat':<10} {'Değişim':<10}")
    print(f"{'-'*30}")
    
    for h in hisseler:
        f, d = bist_fiyat(h)
        if f:
            emoji = "🟢" if d and d > 0 else "🔴" if d and d < 0 else "⚪"
            print(f"{emoji} {h:<6} {f:<9} %{d:<+6.2f}" if d else f"⚪ {h:<6} {f:<9} —")
    
    # Portföy
    pf = os.path.join(VERI_DIZINI, "portfoy.json")
    if os.path.exists(pf):
        with open(pf) as f: portfoy = json.load(f)
        hisseler_p = portfoy.get('hisseler', {})
        if hisseler_p:
            print(f"\n📁 PORTFÖY:")
            toplam_m = toplam_g = 0
            for s, h in hisseler_p.items():
                f, _ = bist_fiyat(s)
                m = h['adet'] * h['alis_fiyati']
                g = h['adet'] * (f or 0)
                toplam_m += m; toplam_g += g
                k = g - m; ky = (k/m)*100 if m > 0 else 0
                e = "🟢" if k >= 0 else "🔴"
                print(f"  {e} {s}: {h['adet']} adet | Maliyet: {m:,.0f} → {g:,.0f} | K/Z: {k:+,.0f} (%{ky:+.1f})")
            
            tk = toplam_g - toplam_m
            tky = (tk/toplam_m)*100 if toplam_m > 0 else 0
            e = "🟢" if tk >= 0 else "🔴"
            print(f"  {'='*30}")
            print(f"  {e} TOPLAM: {toplam_m:,.0f} → {toplam_g:,.0f} | K/Z: {tk:+,.0f} TL (%{tky:+.1f})")
    
    print(f"\n⚠️ Yatırım tavsiyesi değildir.")

if __name__ == '__main__':
    ana()
