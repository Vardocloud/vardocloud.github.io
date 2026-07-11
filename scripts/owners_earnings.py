#!/usr/bin/env python3
"""
Owner's Earnings Calculator — Buffett Metrik Hesaplama Aracı
v1.0 — 27 Haziran 2026

Formül: Net Gelir + Amortisman & İtfa - Sermaye Harcamaları (Capex) - İşletme Sermayesi Değişimi

Kullanım:
  python3 owners_earnings.py                    # Interaktif
  python3 owners_earnings.py --file data.json   # JSON dosyasından
  python3 owners_its.py --ticker AAPL           # yfinance ile canlı
"""

import json
import sys
import argparse
from typing import Optional

def owners_earnings(
    net_income: float,
    depreciation: float,
    capex: float,
    working_capital_change: float = 0,
    non_cash_items: float = 0,
) -> dict:
    """
    Owner's Earnings hesapla (Buffett formülü)
    
    Owner's Earnings = Net Gelir + Amortisman & İtfa + Diğer Nakit Dışı Giderler 
                       - Sermaye Harcamaları (Capex) - İşletme Sermayesi Değişimi
    """
    oe = net_income + depreciation + non_cash_items - capex - working_capital_change
    
    return {
        "owner_earnings": round(oe, 2),
        "net_income": round(net_income, 2),
        "depreciation": round(depreciation, 2),
        "non_cash_items": round(non_cash_items, 2),
        "capex": round(capex, 2),
        "working_capital_change": round(working_capital_change, 2),
        "components": {
            "net_income_ratio": f"{net_income/oe*100:.1f}%" if oe != 0 else "N/A",
            "depreciation_ratio": f"{depreciation/oe*100:.1f}%" if oe != 0 else "N/A",
            "capex_ratio": f"{capex/oe*100:.1f}%" if oe != 0 else "N/A",
        }
    }

def margin_of_safety(intrinsic_value: float, market_price: float) -> dict:
    """Güvenlik marjı hesapla"""
    if market_price <= 0:
        return {"error": "Piyasa fiyatı 0 veya negatif olamaz"}
    
    mos_pct = (intrinsic_value - market_price) / intrinsic_value * 100
    return {
        "intrinsic_value": round(intrinsic_value, 2),
        "market_price": round(market_price, 2),
        "margin_of_safety_pct": round(mos_pct, 2),
        "undervalued": mos_pct > 0,
        "assessment": "ALIM FIRSATI" if mos_pct >= 30 else 
                     ("DEGERLI" if mos_pct > 0 else "PAHALI"),
        "buffett_standard": "✅ Margin of Safety > %25" if mos_pct >= 25 else
                           ("⚠️ Sınırda (%15-25)" if mos_pct >= 15 else "❌ Yetersiz (< %15)")
    }

def dc_valuation(
    current_oe: float,
    growth_rate: float,  # yıllık büyüme oranı (ondalık: 0.10 = %10)
    years: int,  # tahmin yılı sayısı
    terminal_growth: float,  # terminal büyüme oranı
    wacc: float,  # ağırlıklı ortalama sermaye maliyeti
) -> dict:
    """
    Basit DCF Değerleme (Owner's Earnings bazlı)
    
    2 aşamalı: öngörü dönemi + terminal değer
    """
    # Öngörü dönemi nakit akışları
    cash_flows = []
    oe = current_oe
    for year in range(1, years + 1):
        oe *= (1 + growth_rate)
        discounted = oe / ((1 + wacc) ** year)
        cash_flows.append({
            "year": year,
            "owners_earnings": round(oe, 2),
            "discounted": round(discounted, 2)
        })
    
    # Terminal değer
    final_oe = current_oe * ((1 + growth_rate) ** years)
    terminal_value = final_oe * (1 + terminal_growth) / (wacc - terminal_growth)
    discounted_tv = terminal_value / ((1 + wacc) ** years)
    
    # Toplam içsel değer
    total_pv = sum(cf["discounted"] for cf in cash_flows) + discounted_tv
    
    return {
        "intrinsic_value": round(total_pv, 2),
        "present_value_cash_flows": round(sum(cf["discounted"] for cf in cash_flows), 2),
        "present_value_terminal": round(discounted_tv, 2),
        "terminal_value": round(terminal_value, 2),
        "terminal_pct_of_total": f"{discounted_tv/total_pv*100:.1f}%" if total_pv else "N/A",
        "cash_flows": cash_flows,
        "assumptions": {
            "current_owners_earnings": round(current_oe, 2),
            "growth_rate": f"{growth_rate*100:.1f}%",
            "projection_years": years,
            "terminal_growth": f"{terminal_growth*100:.1f}%",
            "wacc": f"{wacc*100:.1f}%"
        }
    }

def roe_analysis(net_income: float, equity: float) -> dict:
    """ROE analizi"""
    roe = net_income / equity if equity else 0
    return {
        "roe": f"{roe*100:.1f}%",
        "buffett_standard": "✅ ROE > %15 (Buffett standardı)" if roe > 0.15 else 
                           ("⚠️ ROE %10-15 arası" if roe > 0.10 else "❌ ROE < %10"),
        "net_income": round(net_income, 2),
        "equity": round(equity, 2)
    }

def debt_equity_ratio(total_debt: float, equity: float) -> dict:
    """Borç/Öz Sermaye oranı"""
    de = total_debt / equity if equity else float('inf')
    return {
        "debt_equity": round(de, 2),
        "buffett_standard": "✅ D/E < 0.5 (düşük borç)" if de < 0.5 else
                           ("⚠️ D/E 0.5-1.0 arası" if de < 1.0 else "🔴 D/E > 1.0 (yüksek borç)"),
    }

def interactive_mode():
    """Interaktif kullanım"""
    print("\n" + "="*60)
    print("  OWNER'S EARNINGS HESAPLAMA ARACI (Buffett Metrikleri)")
    print("="*60)
    
    print("\n📊 Temel Finansal Veriler")
    ni = float(input("  Net Gelir: ") or "0")
    dep = float(input("  Amortisman & İtfa: ") or "0")
    capex = float(input("  Sermaye Harcamaları (Capex): ") or "0")
    wc = float(input("  İşletme Sermayesi Değişimi (opsiyonel): ") or "0")
    non_cash = float(input("  Diğer Nakit Dışı Giderler (opsiyonel): ") or "0")
    
    result = owners_earnings(ni, dep, capex, wc, non_cash)
    
    print(f"\n{'='*60}")
    print(f"  🔑 OWNER'S EARNINGS: ${result['owner_earnings']:,.2f}")
    print(f"{'='*60}")
    print(f"  Net Gelir:                ${result['net_income']:>12,.2f}")
    print(f"  + Amortisman:             ${result['depreciation']:>12,.2f}")
    print(f"  + Nakit Dışı Giderler:    ${result['non_cash_items']:>12,.2f}")
    print(f"  - Sermaye Harcamaları:    ${result['capex']:>12,.2f}")
    print(f"  - İşletme Sermayesi Değiş:${result['working_capital_change']:>12,.2f}")
    print(f"{'─'*60}")
    print(f"  = OWNER'S EARNINGS:       ${result['owner_earnings']:>12,.2f}")
    
    # ROE
    print("\n📈 ROE Analizi")
    equity = float(input("  Öz Sermaye: ") or "0")
    if equity:
        roe = roe_analysis(ni, equity)
        print(f"  ROE: {roe['roe']}")
        print(f"  {roe['buffett_standard']}")
    
    # Borç Analizi
    print("\n🏦 Borç Analizi")
    debt = float(input("  Toplam Borç: ") or "0")
    if debt and equity:
        de = debt_equity_ratio(debt, equity)
        print(f"  D/E: {de['debt_equity']}")
        print(f"  {de['buffett_standard']}")
    
    # Değerleme
    print("\n💰 DCF Değerleme")
    val = input("  DCF hesaplaması yapılsın mı? (e/h): ").lower()
    if val == 'e':
        wacc = float(input("  WACC (%, örn: 12): ") or "12") / 100
        growth = float(input("  Büyüme Oranı (%, örn: 8): ") or "8") / 100
        years = int(input("  Tahmin Yılı: ") or "5")
        tg = float(input("  Terminal Büyüme (%, örn: 3): ") or "3") / 100
        
        dcf = dc_valuation(result['owner_earnings'], growth, years, tg, wacc)
        print(f"\n  İçsel Değer: ${dcf['intrinsic_value']:,.2f}")
        
        # Margin of Safety
        price = float(input("\n  Piyasa Fiyatı (şirket değeri): ") or "0")
        if price:
            mos = margin_of_safety(dcf['intrinsic_value'], price)
            print(f"  Güvenlik Marjı: {mos['margin_of_safety_pct']:.1f}%")
            print(f"  Değerlendirme: {mos['assessment']}")
            print(f"  {mos['buffett_standard']}")


def main():
    parser = argparse.ArgumentParser(description="Owner's Earnings Calculator")
    parser.add_argument('--file', help='JSON dosyasından veri yükle')
    parser.add_argument('--ticker', help='yfinance ile canlı veri çek')
    parser.add_argument('--output', choices=['text', 'json'], default='text', help='Çıktı formatı')
    
    args = parser.parse_args()
    
    if args.file:
        with open(args.file) as f:
            data = json.load(f)
        result = owners_earnings(**data)
        print(json.dumps(result, indent=2))
    
    elif args.ticker:
        print(f"📡 yfinance ile {args.ticker} verisi çekiliyor...")
        try:
            import yfinance as yf
            ticker = yf.Ticker(args.ticker)
            info = ticker.info
            
            ni = info.get('netIncome', 0) or info.get('netIncomeToCommon', 0) or 0
            dep = info.get('depreciation', 0) or 0
            capex = info.get('capitalExpenditures', 0) or 0
            wc = info.get('workingCapital', 0) or 0
            
            result = owners_earnings(ni, dep, capex, wc)
            
            print(f"\n  {args.ticker} — Owner's Earnings")
            print(f"  {'='*40}")
            print(f"  Net Gelir:        ${ni:>12,.0f}")
            print(f"  Amortisman:       ${dep:>12,.0f}")
            print(f"  Capex:           -${abs(capex):>11,.0f}" if capex < 0 else f"  Capex:            ${capex:>12,.0f}")
            print(f"  İşletme Sermayesi: ${wc:>12,.0f}")
            print(f"  {'─'*40}")
            print(f"  Owner's Earnings: ${result['owner_earnings']:>12,.0f}")
            
        except ImportError:
            print("❌ yfinance kurulu değil. pip install yfinance")
        except Exception as e:
            print(f"❌ Hata: {e}")
    
    else:
        interactive_mode()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        # Test modu — örnek veri
        print("\n🧪 TEST MODU — Örnek Şirket Verisi")
        
        result = owners_earnings(
            net_income=1000000,
            depreciation=200000,
            capex=300000,
            working_capital_change=50000,
            non_cash_items=10000
        )
        
        print(f"\n📊 Owner's Earnings: ${result['owner_earnings']:,.2f}")
        print(f"   Net Gelir: ${result['net_income']:,.2f}")
        print(f"   + Amortisman: ${result['depreciation']:,.2f}")
        print(f"   + Nakit Dışı: ${result['non_cash_items']:,.2f}")
        print(f"   - Capex: ${result['capex']:,.2f}")
        print(f"   - İşletme Sermayesi: ${result['working_capital_change']:,.2f}")
        
        # DCF hesapla
        dcf = dc_valuation(
            current_oe=result['owner_earnings'],
            growth_rate=0.08,
            years=5,
            terminal_growth=0.03,
            wacc=0.12
        )
        print(f"\n💰 DCF Değerleme:")
        print(f"   İçsel Değer: ${dcf['intrinsic_value']:,.2f}")
        print(f"   Terminal Değer PV: ${dcf['present_value_terminal']:,.2f} ({dcf['terminal_pct_of_total']})")
        
        # Margin of Safety
        mos = margin_of_safety(dcf['intrinsic_value'], 8000000)
        print(f"\n🛡 Margin of Safety:")
        print(f"   Piyasa Fiyatı: $8,000,000")
        print(f"   Güvenlik Marjı: %{mos['margin_of_safety_pct']:.1f}")
        print(f"   {mos['assessment']}")
        print(f"   {mos['buffett_standard']}")
        
        # ROE
        roe = roe_analysis(1000000, 5000000)
        print(f"\n📈 ROE: {roe['roe']}")
        print(f"   {roe['buffett_standard']}")
        
        # D/E
        de = debt_equity_ratio(1500000, 5000000)
        print(f"\n🏦 D/E: {de['debt_equity']}")
        print(f"   {de['buffett_standard']}")
