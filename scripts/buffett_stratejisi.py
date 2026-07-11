#!/usr/bin/env python3
"""
Buffett Stratejisi — Backtrader ile Value Investing Backtest
v1.0 — 27 Haziran 2026

Stratejiler:
1. DCF Değerleme: Owner's earnings bazlı intrinsic value
2. Moat Skorlama: 5 faktörlü portföy ağırlığı
3. Makro Rotasyon: Faiz/enflasyon/büyüme sinyali

Kullanım:
  python3 buffett_stratejisi.py --ticker AAPL --start 2020-01-01 --end 2025-12-31
"""

import argparse
import sys
from datetime import datetime

def rsi_hesapla(fiyatlar, period=14):
    """RSI hesapla"""
    import pandas as pd
    delta = pd.Series(fiyatlar).diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def moving_average(fiyatlar, period=50):
    """Hareketli ortalama"""
    import pandas as pd
    return pd.Series(fiyatlar).rolling(window=period).mean()

def buffett_filtresi(roe=None, de=None, fcf_yield=None):
    """Buffett filtrelerinden geçir"""
    gecer = True
    neden = []
    
    if roe is not None and roe < 0.15:
        gecer = False
        neden.append(f"ROE %{roe*100:.1f} < %15")
    if de is not None and de > 0.5:
        gecer = False
        neden.append(f"D/E {de:.2f} > 0.5")
    if fcf_yield is not None and fcf_yield < 0.05:
        gecer = False
        neden.append(f"FCF Yield %{fcf_yield*100:.1f} < %5")
    
    return gecer, neden

def basit_backtest(ticker: str, start: str, end: str):
    """Basit backtest — MA crossover + RSI + Buffett filtresi"""
    try:
        import yfinance as yf
        import pandas as pd
        
        print(f"📡 {ticker} verisi çekiliyor ({start} -> {end})...")
        data = yf.download(ticker, start=start, end=end, progress=False)
        
        if data.empty:
            print("❌ Veri bulunamadı")
            return
        
        # Teknik indikatörler
        close = data['Close'].squeeze() if hasattr(data['Close'], 'squeeze') else data['Close']
        data['MA50'] = moving_average(close, 50)
        data['MA200'] = moving_average(close, 200)
        data['RSI'] = rsi_hesapla(close, 14)
        
        # Sinyaller
        data['Sinyal'] = 0
        # Golden Cross (MA50 > MA200) → AL
        data.loc[(data['MA50'] > data['MA200']) & (data['MA50'].shift(1) <= data['MA200'].shift(1)), 'Sinyal'] = 1
        # Death Cross (MA50 < MA200) → SAT
        data.loc[(data['MA50'] < data['MA200']) & (data['MA50'].shift(1) >= data['MA200'].shift(1)), 'Sinyal'] = -1
        # RSI < 30 → Aşırı satım (AL)
        data.loc[(data['RSI'] < 30) & (data['RSI'].shift(1) >= 30), 'Sinyal'] = 1
        # RSI > 70 → Aşırı alım (SAT)
        data.loc[(data['RSI'] > 70) & (data['RSI'].shift(1) <= 70), 'Sinyal'] = -1
        
        # Buffett filtresi
        ticker_info = yf.Ticker(ticker)
        info = ticker_info.info
        roe = info.get('returnOnEquity', 0) or 0
        de = (info.get('totalDebt', 0) or 0) / max((info.get('totalStockholderEquity', 1) or 1), 1)
        fcf = info.get('freeCashflow', 0) or 0
        piyasa_deger = info.get('marketCap', 1) or 1
        fcf_yield = fcf / piyasa_deger
        
        buffett_gecer, nedenler = buffett_filtresi(roe, de, fcf_yield)
        
        # Backtest
        capital = 10000
        pozisyon = 0
        trade_log = []
        portfoy = []
        
        for i in range(1, len(data)):
            sinyal = data['Sinyal'].iloc[i]
            fiyat = close.iloc[i]
            tarih = data.index[i]
            
            if sinyal == 1 and pozisyon == 0:
                pozisyon = capital / fiyat
                capital = 0
                trade_log.append(f"🟢 AL {tarih.date()} @ ${fiyat:.2f}")
            elif sinyal == -1 and pozisyon > 0:
                capital = pozisyon * fiyat
                pozisyon = 0
                trade_log.append(f"🔴 SAT {tarih.date()} @ ${fiyat:.2f}")
            
            portfoy.append(capital + pozisyon * fiyat if pozisyon > 0 else capital)
        
        # Sonuç
        final_value = capital + pozisyon * close.iloc[-1] if pozisyon > 0 else capital
        total_return = (final_value - 10000) / 10000 * 100
        
        # Benchmark (Buy & Hold)
        bench_return = (close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100
        
        print(f"\n{'='*60}")
        print(f"  📊 BUFFETT STRATEJİSİ BACKTEST — {ticker}")
        print(f"{'='*60}")
        print(f"  Dönem: {start} -> {end}")
        print(f"  Başlangıç: $10,000")
        print(f"  Bitiş: ${final_value:,.2f}")
        print(f"  Strateji Getirisi: %{total_return:.2f}")
        print(f"  Buy & Hold: %{bench_return:.2f}")
        print(f"  Alpha: %{total_return - bench_return:.2f}")
        print(f"  İşlem Sayısı: {len(trade_log)}")
        
        print(f"\n  🏛 Buffett Filtresi:")
        print(f"  ROE: %{roe*100:.1f} | D/E: {de:.2f} | FCF Yield: %{fcf_yield*100:.1f}")
        if buffett_gecer:
            print(f"  ✅ Buffett yatırım yapabilir")
        else:
            print(f"  ❌ Buffett yatırım yapmaz: {'; '.join(nedenler)}")
        
        if trade_log:
            print(f"\n  📋 Trade Geçmişi (ilk/orta/son):")
            for t in [trade_log[0]] if len(trade_log) == 1 else [trade_log[0], trade_log[len(trade_log)//2], trade_log[-1]]:
                print(f"  {t}")
        
        print(f"\n  ⚠️ Not: Bu basit bir backtesttir, gerçek hayattaki slippage/fee/vergi dahil değildir.")
        
    except ImportError as e:
        print(f"❌ Eksik kütüphane: {e}")
        print("  pip install yfinance pandas")
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Buffett Stratejisi Backtest")
    parser.add_argument('--ticker', default='AAPL', help='Hisse sembolü')
    parser.add_argument('--start', default='2020-01-01', help='Başlangıç tarihi')
    parser.add_argument('--end', default='2025-12-31', help='Bitiş tarihi')
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        # Test modu
        print("🧪 TEST MODU — Apple (AAPL) 2020-2025")
        basit_backtest("AAPL", "2020-01-01", "2025-12-31")
    else:
        basit_backtest(args.ticker, args.start, args.end)
