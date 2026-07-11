#!/usr/bin/env python3
"""
BIST (Borsa İstanbul) Simülasyonu — Hisse Takip ve Paper Trading
Vanitas — 1 Temmuz 2026

Kullanım:
  python3 borsa-simulasyonu.py --hisse KCAER --adet 245 --alis 14.625
  python3 borsa-simulasyonu.py --hisse KCAER --analiz
  python3 borsa-simulasyonu.py --portfoy
  python3 borsa-simulasyonu.py --hisse KCAER,THYAO,EREGL --toplu
"""

import json
import os
import sys
from datetime import datetime
from urllib.request import Request, urlopen

VERI_DIZINI = os.path.expanduser("~/.hermes/data/borsa")
os.makedirs(VERI_DIZINI, exist_ok=True)
PORTFOY_DOSYASI = os.path.join(VERI_DIZINI, "portfoy.json")


def log(msg):
    print(f"[BIST] {msg}", file=sys.stderr)


# BIST hisseleri için yfinance ticker eşlemesi
BIST_MAP = {
    "KCAER": "KCAER.IS", "THYAO": "THYAO.IS", "EREGL": "EREGL.IS",
    "AKBNK": "AKBNK.IS", "GARAN": "GARAN.IS", "ISCTR": "ISCTR.IS",
    "ASELS": "ASELS.IS", "SASA": "SASA.IS", "KCHOL": "KCHOL.IS",
    "TUPRS": "TUPRS.IS", "KOZAL": "KOZAL.IS", "KOZAA": "KOZAA.IS",
    "BIMAS": "BIMAS.IS", "HEKTS": "HEKTS.IS", "FROTO": "FROTO.IS",
    "PETKM": "PETKM.IS", "TCELL": "TCELL.IS", "VESTL": "VESTL.IS",
    "TOASO": "TOASO.IS", "SAHOL": "SAHOL.IS", "YKBNK": "YKBNK.IS",
    "HALKB": "HALKB.IS", "VAKBN": "VAKBN.IS", "ALBRK": "ALBRK.IS",
    "SISE": "SISE.IS", "EKGYO": "EKGYO.IS", "ISMEN": "ISMEN.IS",
}


def bist_fiyat(sembol):
    """yfinance ile BIST hissesinin güncel fiyatını çek"""
    import yfinance as yf
    ticker = BIST_MAP.get(sembol, f"{sembol}.IS")
    try:
        hisse = yf.Ticker(ticker)
        df = hisse.history(period="5d")
        if df.empty:
            return None, None
        guncel = df['Close'].iloc[-1]
        onceki = df['Close'].iloc[-2] if len(df) > 1 else guncel
        degisim = ((guncel - onceki) / onceki) * 100
        return round(guncel, 3), round(degisim, 2)
    except Exception as e:
        log(f"{sembol} fiyat hatası: {e}")
        return None, None


def bist_gecmis(sembol, gun=90):
    """BIST hissesinin geçmiş verisini çek"""
    import yfinance as yf
    ticker = BIST_MAP.get(sembol, f"{sembol}.IS")
    try:
        hisse = yf.Ticker(ticker)
        df = hisse.history(period=f"{gun}d")
        return df
    except Exception as e:
        log(f"{sembol} geçmiş hatası: {e}")
        return None


def portfoy_yukle():
    """Portföyü yükle"""
    if os.path.exists(PORTFOY_DOSYASI):
        try:
            with open(PORTFOY_DOSYASI) as f:
                return json.load(f)
        except:
            pass
    return {'hisseler': {}, 'toplam_maliyet': 0, 'toplam_guncel': 0}


def portfoy_kaydet(portfoy):
    """Portföyü kaydet"""
    with open(PORTFOY_DOSYASI, 'w') as f:
        json.dump(portfoy, f, ensure_ascii=False, indent=2)


def hisse_ekle(sembol, adet, alis_fiyati):
    """Portföye hisse ekle"""
    sembol = sembol.upper()
    portfoy = portfoy_yukle()
    
    if sembol in portfoy['hisseleri'] if 'hisseleri' in portfoy else {}:
        # Mevcut hisseyi güncelle
        h = portfoy['hisseler'][sembol]
        toplam_adet = h['adet'] + adet
        toplam_maliyet = (h['adet'] * h['alis_fiyati']) + (adet * alis_fiyati)
        h['adet'] = toplam_adet
        h['alis_fiyati'] = round(toplam_maliyet / toplam_adet, 3)
    else:
        if 'hisseler' not in portfoy:
            portfoy['hisseler'] = {}
        portfoy['hisseler'][sembol] = {
            'adet': adet,
            'alis_fiyati': alis_fiyati,
            'eklenme_tarihi': datetime.now().isoformat(),
        }
    
    portfoy_kaydet(portfoy)
    
    # Güncel fiyatı sorgula
    fiyat, degisim = bist_fiyat(sembol)
    
    toplam_maliyet = adet * alis_fiyati
    toplam_deger = adet * (fiyat or 0)
    kar = toplam_deger - toplam_maliyet
    kar_yuzde = (kar / toplam_maliyet) * 100 if toplam_maliyet > 0 else 0
    
    print(f"\n✅ {sembol} portföye eklendi")
    print(f"📊 {adet} adet x {alis_fiyati} TL = {toplam_maliyet:,.0f} TL maliyet")
    if fiyat:
        print(f"💰 Güncel: {fiyat} TL ({degisim:+.2f}%)")
        print(f"📈 Değer: {toplam_deger:,.0f} TL | K/Z: {kar:+,.0f} TL (%{kar_yuzde:+.1f})")
    
    return portfoy


def portfoy_goster():
    """Portföy durumunu göster"""
    portfoy = portfoy_yukle()
    hisseler = portfoy.get('hisseler', {})
    
    if not hisseler:
        print("📭 Portföyde hisse bulunmuyor.")
        return
    
    print(f"\n{'='*50}")
    print(f"📊 BİST PORTFÖY")
    print(f"{'='*50}")
    
    toplam_maliyet = 0
    toplam_guncel = 0
    
    for sembol, h in sorted(hisseler.items()):
        fiyat, degisim = bist_fiyat(sembol)
        
        maliyet = h['adet'] * h['alis_fiyati']
        guncel = h['adet'] * (fiyat or 0)
        kar = guncel - maliyet
        kar_yuzde = (kar / maliyet) * 100 if maliyet > 0 else 0
        
        toplam_maliyet += maliyet
        toplam_guncel += guncel
        
        emoji = "🟢" if kar >= 0 else "🔴"
        fiyat_str = f"{fiyat} TL" if fiyat else "—"
        
        print(f"\n{emoji} {sembol}")
        print(f"   Adet: {h['adet']} | Maliyet: {h['alis_fiyati']} TL")
        print(f"   Güncel: {fiyat_str} ({degisim:+.2f}%)" if fiyat else "")
        print(f"   Toplam: {maliyet:,.0f} TL → {guncel:,.0f} TL | K/Z: {kar:+,.0f} TL (%{kar_yuzde:+.1f})")
    
    toplam_kar = toplam_guncel - toplam_maliyet
    toplam_kar_yuzde = (toplam_kar / toplam_maliyet) * 100 if toplam_maliyet > 0 else 0
    emoji_t = "🟢" if toplam_kar >= 0 else "🔴"
    
    print(f"\n{'-'*50}")
    print(f"{emoji_t} TOPLAM: {toplam_maliyet:,.0f} TL → {toplam_guncel:,.0f} TL")
    print(f"{'='*50}")


def hisse_analiz(sembol, gun=180):
    """BIST hissesini teknik analiz et (kripto-teknik-analiz skill'i formatında)"""
    df = bist_gecmis(sembol, gun)
    if df is None or len(df) < 30:
        print(f"⚠️  {sembol}: Yetersiz veri")
        return
    
    import pandas as pd
    
    guncel = df['Close'].iloc[-1]
    
    # Direnç/Destek seviyeleri
    son_30 = df[-30:]
    destek = son_30['Low'].min()
    guclu_destek = df[-60:]['Low'].min()
    direnc = son_30['High'].max()
    guclu_direnc = df[-60:]['High'].max()
    
    # Hareketli ortalamalar
    df2 = df.copy()
    df2['MA20'] = df2['Close'].rolling(20).mean()
    df2['MA50'] = df2['Close'].rolling(50).mean()
    ma20 = df2['MA20'].iloc[-1]
    ma50 = df2['MA50'].iloc[-1] if len(df2) > 50 else 0
    
    # RSI
    delta = df2['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, float('nan'))
    rsi = (100 - (100 / (1 + rs))).iloc[-1]
    
    # Hacim analizi
    hacim_ort = df2['Volume'].rolling(20).mean().iloc[-1]
    hacim_son = df2['Volume'].iloc[-1]
    hacim_anomali = hacim_son / hacim_ort if hacim_ort > 0 else 1
    
    # Değişim
    degisim_1h = ((guncel - df2['Close'].iloc[-5]) / df2['Close'].iloc[-5]) * 100
    degisim_1a = ((guncel - df2['Close'].iloc[-22]) / df2['Close'].iloc[-22]) * 100 if len(df2) > 22 else 0
    
    # Bitcoin Arısı formatında çıktı
    print(f"\n{'='*50}")
    print(f"📈 {sembol} — TEKNİK ANALİZ ({datetime.now().strftime('%d %B %Y')})")
    print(f"{'='*50}")
    print(f"💰 Güncel: {guncel:.3f} TL")
    print(f"📉 1 Hafta: %{degisim_1h:+.2f} | 1 Ay: %{degisim_1a:+.2f}")
    print(f"━━━━━━━━━━━━━━━━━━━━")
    print(f"📈 DİRENÇ: {direnc:.3f} TL (ilk), {guclu_direnc:.3f} TL (zorlu)")
    print(f"📉 DESTEK: {destek:.3f} TL (ilk), {guclu_destek:.3f} TL (güçlü)")
    print(f"━━━━━━━━━━━━━━━━━━━━")
    print(f"📊 GÖSTERGELER:")
    print(f"  RSI(14): {rsi:.1f} " + ("(aşırı satım 🔵)" if rsi < 30 else "(aşırı alım 🔴)" if rsi > 70 else "(nötr ⚪)"))
    print(f"  MA20: {ma20:.3f} | MA50: {ma50:.3f}" if ma50 > 0 else f"  MA20: {ma20:.3f}")
    trend_str = "YUKARI 📈" if ma20 > ma50 else "AŞAĞI 📉" if ma20 < ma50 else "YATAY ⚪"
    print(f"  Trend: {trend_str}")
    print(f"  Hacim: {'YÜKSEK 🔴' if hacim_anomali > 1.5 else 'NORMAL ⚪' if hacim_anomali > 0.5 else 'DÜŞÜK 🔵'}")
    print(f"━━━━━━━━━━━━━━━━━━━━")
    
    # Bitcoin Arısı tarzı yorum
    print(f"🔮 YORUM:")
    
    if rsi < 30:
        print(f"  • RSI aşırı satım bölgesinde — tepki alımı gelebilir")
    elif rsi > 70:
        print(f"  • RSI aşırı alım bölgesinde — kar satışı gelebilir")
    
    if guncel < ma20:
        print(f"  • Fiyat MA20 altında — kısa vadede zayıf")
    elif guncel > ma20:
        print(f"  • Fiyat MA20 üstünde — kısa vadede pozitif")
    
    print(f"  • Destek: {destek:.3f} TL | Direnç: {direnc:.3f} TL")
    print(f"  • {direnc:.3f} üstünde kapanış = yukarı yön | {destek:.3f} altında = aşağı yön")
    print(f"  🎯 Orta vade hedef: {direnc*1.1:.2f} TL (direnç kırılırsa)")
    print(f"  ⚠️ Yatırım tavsiyesi değildir.")


def toplu_analiz(hisseler=None):
    """Birden çok hisseyi analiz et"""
    if hisseler is None:
        hisseler = ["KCAER", "THYAO", "EREGL", "AKBNK", "ASELS"]
    
    for h in hisseler:
        hisse_analiz(h.strip().upper(), gun=180)


def main():
    if '--portfoy' in sys.argv:
        portfoy_goster()
        return
    
    if '--hisse' in sys.argv:
        idx = sys.argv.index('--hisse')
        sembol = sys.argv[idx + 1].upper() if idx + 1 < len(sys.argv) else "KCAER"
        
        if '--adet' in sys.argv:
            adet_idx = sys.argv.index('--adet')
            adet = int(sys.argv[adet_idx + 1]) if adet_idx + 1 < len(sys.argv) else 0
            alis_idx = sys.argv.index('--alis') if '--alis' in sys.argv else None
            alis = float(sys.argv[alis_idx + 1]) if alis_idx and alis_idx + 1 < len(sys.argv) else 0
            
            if adet > 0 and alis > 0:
                hisse_ekle(sembol, adet, alis)
                return
        
        if '--analiz' in sys.argv or '--teknik' in sys.argv:
            hisse_analiz(sembol.replace(',', ''))
            return
        
        if '--toplu' in sys.argv or ',' in sembol:
            hisseler = sembol.split(',')
            toplu_analiz(hisseler)
            return
        
        # Tek hisse analizi
        hisse_analiz(sembol)
        return


if __name__ == '__main__':
    main()
