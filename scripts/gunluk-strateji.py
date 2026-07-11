#!/usr/bin/env python3
"""
Günlük Kazanç Stratejisi Testi — Kısa Vadeli, Sık İşlem
Her gün için ayrı karar: günlük mumda al/sat, gün sonu kapat.

Kullanım:
  python3 gunluk-strateji.py --coin BTC --test
  python3 gunluk-strateji.py --coin XRP --test
  python3 gunluk-strateji.py --hepsi
"""

import json
import os
import sys
from datetime import datetime, timedelta

RAPOR_DIZINI = os.path.expanduser("~/.hermes/data/kaldirac-simulasyonu")


def log(msg):
    print(f"[GÜNLÜK] {msg}", file=sys.stderr)


def veri_cek(sembol, gun=90):
    """yfinance ile günlük veri çek"""
    import yfinance as yf
    ticker = f"{sembol}-USD"
    hisse = yf.Ticker(ticker)
    df = hisse.history(period=f"{gun}d")
    return df


def gunluk_strateji(df, baslangic=500, kaldırac=5):
    """
    Günlük kazanç stratejisi:
    - Her gün için fiyat yönüne karar ver
    - Günün açılışında pozisyon aç
    - Gün sonunda kapat
    - Hedef: günlük %1-3
    """
    import pandas as pd
    
    sermaye = float(baslangic)
    islem_sayisi = 0
    kazanan = 0
    kaybeden = 0
    toplam_kar = 0
    max_drawdown = 0
    zirve = sermaye
    
    df = df.copy()
    df['Onceki_kapanis'] = df['Close'].shift(1)
    df['Onceki_yuksek'] = df['High'].shift(1)
    df['Onceki_dusuk'] = df['Low'].shift(1)
    
    # Teknik göstergeler
    df['EMA5'] = df['Close'].ewm(span=5).mean()
    df['EMA10'] = df['Close'].ewm(span=10).mean()
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=7).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=7).mean()
    rs = gain / loss.replace(0, float('nan'))
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Güncek aralık
    df['Aralik'] = df['High'] - df['Low']
    df['Aralik_yuzde'] = df['Aralik'] / df['Open'] * 100
    df['Volatilite'] = df['Aralik_yuzde'].rolling(5).mean()
    
    gunluk_sonuclar = []
    
    for i in range(21, len(df)):
        if sermaye <= 0:
            break
        
        gun = df.index[i]
        acilis = df['Open'].iloc[i]
        yuksek = df['High'].iloc[i]
        dusuk = df['Low'].iloc[i]
        kapanis = df['Close'].iloc[i]
        
        onceki_ema5 = df['EMA5'].iloc[i-1]
        onceki_ema10 = df['EMA10'].iloc[i-1]
        ema5 = df['EMA5'].iloc[i]
        ema10 = df['EMA10'].iloc[i]
        ema20 = df['EMA20'].iloc[i]
        rsi = df['RSI'].iloc[i]
        onceki_aralik = df['Aralik_yuzde'].iloc[i-1] if i > 0 else 0
        
        # Fiyatın EMA'lara göre konumu
        fiyat_ema20_ustu = acilis > ema20
        
        # Trend yönü
        trend_yonu = 1 if ema5 > ema10 > ema20 else (-1 if ema5 < ema10 < ema20 else 0)
        
        # Sinyal üret
        sinyal = 0  # 1 = LONG, -1 = SHORT, 0 = BEKLE
        
        # 1. Trend takip: Trend yönünde git, RSI aşırı değilse
        if trend_yonu == 1 and rsi < 70:
            sinyal = 1  # LONG
        elif trend_yonu == -1 and rsi > 30:
            sinyal = -1  # SHORT
        
        # 2. Breakout: Önceki günün aralığından çıkış
        onceki_yuksek = df['High'].iloc[i-1]
        onceki_dusuk = df['Low'].iloc[i-1]
        
        if acilis > onceki_yuksek and trend_yonu == 1:
            sinyal = 1  # Yukarı breakout
        elif acilis < onceki_dusuk and trend_yonu == -1:
            sinyal = -1  # Aşağı breakout
        
        # 3. Düşük volatilite sıkışmasından çıkış
        if onceki_aralik < df['Aralik_yuzde'].quantile(0.2) and df['Aralik_yuzde'].iloc[i] > onceki_aralik * 1.5:
            if df['Close'].iloc[i] > df['Open'].iloc[i]:
                sinyal = 1
            else:
                sinyal = -1
        
        if sinyal == 0:
            continue  # Sinyal yok, bekle
        
        # İşlem yap
        komisyon = sermaye * kaldırac * 0.001 * 2  # Giriş + çıkış komisyonu
        
        if sinyal == 1:  # LONG
            kar_yuzde = (kapanis - acilis) / acilis
        else:  # SHORT
            kar_yuzde = (acilis - kapanis) / acilis
        
        kar = sermaye * kaldırac * kar_yuzde - komisyon
        sermaye += kar
        
        islem_sayisi += 1
        if kar > 0:
            kazanan += 1
        else:
            kaybeden += 1
        
        toplam_kar += kar
        zirve = max(zirve, sermaye)
        dd = (zirve - sermaye) / zirve * 100
        max_drawdown = max(max_drawdown, dd)
        
        gunluk_sonuclar.append({
            'tarih': str(gun.date()),
            'yon': 'LONG' if sinyal == 1 else 'SHORT',
            'acilis': round(acilis, 4),
            'kapanis': round(kapanis, 4),
            'kar_zarar': round(kar, 2),
            'sermaye': round(sermaye, 2),
        })
    
    win_rate = (kazanan / islem_sayisi * 100) if islem_sayisi > 0 else 0
    net_kar = sermaye - baslangic
    getiri_yuzde = (net_kar / baslangic) * 100
    
    return {
        'baslangic': baslangic,
        'son_sermaye': round(sermaye, 2),
        'net_kar_zarar': round(net_kar, 2),
        'getiri_yuzde': round(getiri_yuzde, 2),
        'toplam_islem': islem_sayisi,
        'kazanan': kazanan,
        'kaybeden': kaybeden,
        'win_rate': round(win_rate, 1),
        'max_drawdown': round(max_drawdown, 1),
        'ort_kar': round(net_kar/islem_sayisi, 2) if islem_sayisi > 0 else 0,
        'gunluk_sonuc': gunluk_sonuclar[-10:] if gunluk_sonuclar else [],
    }


def test_et(sembol, baslangic=500, kaldırac=5, gun=60):
    """Tek coin için test"""
    print(f"\n{'='*50}")
    print(f"📊 GÜNLÜK KAZANÇ TESTİ — {sembol}")
    print(f"{'='*50}")
    print(f"Sermaye: ${baslangic} | Kaldıraç: x{kaldırac} | Süre: {gun} gün")
    
    df = veri_cek(sembol, gun)
    if df is None or len(df) < 30:
        print(f"⚠️  {sembol}: Yetersiz veri")
        return None
    
    sonuc = gunluk_strateji(df, baslangic, kaldırac)
    
    emoji = "🟢" if sonuc['net_kar_zarar'] > 0 else "🔴"
    print(f"\n{emoji} Net K/Z: ${sonuc['net_kar_zarar']:.2f} (%{sonuc['getiri_yuzde']:+.1f})")
    print(f"📈 İşlem: {sonuc['toplam_islem']} | WR: %{sonuc['win_rate']} ({sonuc['kazanan']}W/{sonuc['kaybeden']}L)")
    print(f"💰 Ortalama: ${sonuc['ort_kar']:.2f}/işlem | DD: %{sonuc['max_drawdown']}")
    
    # Günlük kazanç potansiyeli
    gunluk_ortalama = sonuc['net_kar_zarar'] / gun * 30  # aylık projeksiyon
    print(f"\n📅 Günlük ort: ${sonuc['net_kar_zarar']/max(sonuc['toplam_islem'],1):.2f}/işlem")
    print(f"📅 Aylık projeksiyon: ${gunluk_ortalama:.2f}")
    
    return sonuc


def hepsini_test_et(baslangic=500, kaldırac=5, gun=60):
    """Tüm hedef coin'lerde test"""
    coinler = ["BTC", "ETH", "XRP", "SOL", "DOGE", "ADA", "LINK", "DOT", "AVAX", "MATIC", "LTC", "BCH", "ATOM", "UNI", "NEAR"]
    
    print(f"\n{'='*50}")
    print(f"🔄 TOPLU GÜNLÜK KAZANÇ TESTİ — {len(coinler)} coin")
    print(f"{'='*50}")
    print(f"Sermaye: ${baslangic} | Kaldıraç: x{kaldırac} | Süre: {gun} gün\n")
    
    sonuclar = []
    for sembol in coinler:
        df = veri_cek(sembol, gun)
        if df is not None and len(df) >= 30:
            sonuc = gunluk_strateji(df, baslangic, kaldırac)
            if sonuc:
                sonuclar.append((sembol, sonuc))
                emoji = "🟢" if sonuc['net_kar_zarar'] > 0 else "🔴"
                print(f"{emoji} {sembol:<6} ${sonuc['net_kar_zarar']:<7.2f} (%{sonuc['getiri_yuzde']:<+6.1f}) İşlem:{sonuc['toplam_islem']:<3} WR:%{sonuc['win_rate']:<5}")
    
    if not sonuclar:
        return
    
    sonuclar.sort(key=lambda x: x[1]['net_kar_zarar'], reverse=True)
    
    print(f"\n{'='*50}")
    print(f"🏆 SIRALAMA — En iyiden en kötüye")
    print(f"{'='*50}")
    for sembol, s in sonuclar:
        emoji = "🟢" if s['net_kar_zarar'] > 0 else "🔴"
        print(f"{emoji} {sembol:<6} ${s['net_kar_zarar']:<7.2f} (%{s['getiri_yuzde']:<+6.1f}) WR:%{s['win_rate']:<5} DD:%{s['max_drawdown']:<5}")
    
    kazanan = sum(1 for _, s in sonuclar if s['net_kar_zarar'] > 0)
    print(f"\n📈 Kazanan: {kazanan}/{len(sonuclar)} (%{kazanan/len(sonuclar)*100:.0f})")


def main():
    if '--hepsi' in sys.argv:
        hepsini_test_et()
        return
    
    sembol = "BTC"
    for i, arg in enumerate(sys.argv):
        if arg == '--coin' and i+1 < len(sys.argv):
            sembol = sys.argv[i+1].upper()
    
    test_et(sembol)


if __name__ == '__main__':
    main()
