#!/usr/bin/env python3
"""
Risk Hesaplama Aracı — Pozisyon Büyüklüğü + Stop-Loss + Portföy Riski
v1.0 — 27 Haziran 2026

Buffett prensipleri: Margin of Safety >= %25, Max pozisyon = portföy %5'i
Kullanım:
  python3 risk_hesapla.py                         # Interaktif
  python3 risk_hesapla.py --portfoy 100000 --fiyat 50 --intrinsic 75
"""

import sys
import json
from typing import Optional

RISK_PARAMETRELERI = {
    "max_pozisyon_orani": 0.05,        # Portföyün %5'i
    "max_es_zamanli_pozisyon": 5,
    "stop_loss_orani": 0.10,           # -%10
    "max_gunluk_kayip_orani": 0.03,    # Portföyün %3'ü
    "min_margin_of_safety": 0.25,      # %25
    "min_roe": 0.15,
    "max_de": 0.5,
}

def pozisyon_buyuklugu(portfoy_degeri: float, fiyat: float = None, 
                       intrinsic_deger: float = None) -> dict:
    """Buffett risk kurallarına göre pozisyon büyüklüğü hesapla"""
    
    # Max pozisyon (portföyün %5'i)
    max_tl = portfoy_degeri * RISK_PARAMETRELERI["max_pozisyon_orani"]
    
    # Margin of Safety kontrolü
    mos_sonuc = {}
    if fiyat and intrinsic_deger and intrinsic_deger > 0:
        mos = (intrinsic_deger - fiyat) / intrinsic_deger
        mos_sonuc = {
            "margin_of_safety": f"%{mos*100:.1f}",
            "mos_yeterli": mos >= RISK_PARAMETRELERI["min_margin_of_safety"],
            "buffett_standardi": "✅ MoS >= %25" if mos >= 0.25 else
                                ("⚠️ Sınırda" if mos >= 0.15 else "❌ Yetersiz")
        }
        if mos < RISK_PARAMETRELERI["min_margin_of_safety"]:
            max_tl *= (mos / RISK_PARAMETRELERI["min_margin_of_safety"])
    
    return {
        "portfoy_degeri": portfoy_degeri,
        "max_pozisyon_tl": round(max_tl, 2),
        "max_pozisyon_oran": f"%{RISK_PARAMETRELERI['max_pozisyon_orani']*100}",
        "stop_loss_seviyesi": f"%{RISK_PARAMETRELERI['stop_loss_orani']*100}",
        "gunluk_kayip_limit": round(portfoy_degeri * RISK_PARAMETRELERI["max_gunluk_kayip_orani"], 2),
        **mos_sonuc
    }

def portfoy_riski(pozisyonlar: list, portfoy_degeri: float) -> dict:
    """Portföydeki tüm pozisyonların toplam riskini hesapla"""
    
    toplam_pozisyon = sum(p.get("maliyet", 0) * p.get("adet", 0) for p in pozisyonlar)
    toplam_risk = 0
    pozisyon_rapor = []
    
    for p in pozisyonlar:
        poz_deger = p.get("maliyet", 0) * p.get("adet", 0)
        poz_oran = poz_deger / portfoy_degeri if portfoy_degeri else 0
        stop_loss = poz_deger * RISK_PARAMETRELERI["stop_loss_orani"]
        
        pozisyon_rapor.append({
            "isim": p.get("isim", "Bilinmeyen"),
            "deger": poz_deger,
            "portfoy_orani": f"%{poz_oran*100:.1f}",
            "stop_loss_tutari": round(stop_loss, 2),
            "limit_asiyor": poz_oran > RISK_PARAMETRELERI["max_pozisyon_orani"],
        })
        toplam_risk += stop_loss
    
    return {
        "toplam_pozisyon": round(toplam_pozisyon, 2),
        "toplam_pozisyon_orani": f"%{toplam_pozisyon/portfoy_degeri*100:.1f}" if portfoy_degeri else "N/A",
        "toplam_stop_loss_riski": round(toplam_risk, 2),
        "max_es_zamanli_pozisyon": RISK_PARAMETRELERI["max_es_zamanli_pozisyon"],
        "pozisyon_sayisi": len(pozisyonlar),
        "limit_asan_pozisyon": sum(1 for p in pozisyon_rapor if p["limit_asiyor"]),
        "pozisyonlar": pozisyon_rapor,
        "portfoy_degeri": portfoy_degeri
    }

def finansal_saglik(roe: float = None, debt_equity: float = None,
                     net_kar_mari: float = None, fcf: float = None) -> dict:
    """Finansal sağlık kontrolü (Buffett standartları)"""
    
    skor = 0
    max_skor = 0
    kontroller = []
    
    if roe is not None:
        max_skor += 1
        if roe >= RISK_PARAMETRELERI["min_roe"]:
            skor += 1
            kontroller.append(f"✅ ROE: %{roe*100:.1f} >= %15")
        else:
            kontroller.append(f"❌ ROE: %{roe*100:.1f} < %15")
    
    if debt_equity is not None:
        max_skor += 1
        if debt_equity <= RISK_PARAMETRELERI["max_de"]:
            skor += 1
            kontroller.append(f"✅ D/E: {debt_equity:.2f} <= 0.5")
        else:
            kontroller.append(f"❌ D/E: {debt_equity:.2f} > 0.5")
    
    if net_kar_mari is not None:
        max_skor += 1
        if net_kar_mari >= 0.10:
            skor += 1
            kontroller.append(f"✅ Net Kar Marjı: %{net_kar_mari*100:.1f} >= %10")
        else:
            kontroller.append(f"❌ Net Kar Marjı: %{net_kar_mari*100:.1f} < %10")
    
    if fcf is not None:
        max_skor += 1
        if fcf > 0:
            skor += 1
            kontroller.append("✅ FCF: Pozitif (nakit üretiyor)")
        else:
            kontroller.append("❌ FCF: Negatif (nakit yakıyor)")
    
    saglik_yuzde = (skor / max_skor * 100) if max_skor else 0
    
    if saglik_yuzde >= 75:
        deger = "✅ SAĞLIKLI — Buffett yatırım yapabilir"
    elif saglik_yuzde >= 50:
        deger = "⚠️ ORTA — Detaylı analiz gerekli"
    else:
        deger = "🔴 RİSKLİ — Buffett yatırım yapmaz"
    
    return {
        "skor": skor,
        "max_skor": max_skor,
        "yuzde": f"%{saglik_yuzde:.0f}",
        "degerlendirme": deger,
        "kontroller": kontroller
    }

def interaktif():
    print("\n" + "="*60)
    print("  🛡 RİSK YÖNETİMİ HESAPLAMA ARACI")
    print("  Buffett Standartları: MoS>=%25 | Pozisyon<=%5 | D/E<0.5 | ROE>%15")
    print("="*60)
    
    portfoy = float(input("\n💰 Portföy Değeri (TL/$): ") or "100000")
    
    print(f"\n📊 Pozisyon Hesaplama")
    fiyat = float(input("  Hisse Fiyatı (opsiyonel): ") or "0") or None
    intrinsic = float(input("  İçsel Değer (opsiyonel): ") or "0") or None
    
    sonuc = pozisyon_buyuklugu(portfoy, fiyat, intrinsic)
    
    print(f"\n{'='*60}")
    print(f"  Maks Pozisyon: {sonuc['max_pozisyon_tl']:,.2f} ({sonuc['max_pozisyon_oran']})")
    print(f"  Stop-Loss: {sonuc['stop_loss_seviyesi']}")
    print(f"  Günlük Kayıp Limiti: {sonuc['gunluk_kayip_limit']:,.2f}")
    if 'margin_of_safety' in sonuc:
        print(f"  Margin of Safety: {sonuc['margin_of_safety']}")
        print(f"  {sonuc['buffett_standardi']}")
    
    # Finansal sağlık
    print(f"\n🏥 Finansal Sağlık Kontrolü")
    roe = float(input("  ROE (%, opsiyonel): ") or "0") or None
    de = float(input("  D/E Oranı (opsiyonel): ") or "0") or None
    marj = float(input("  Net Kar Marjı (%, opsiyonel): ") or "0") or None
    if roe or de or marj:
        saglik = finansal_saglik(
            roe=roe/100 if roe else None,
            debt_equity=de,
            net_kar_mari=marj/100 if marj else None
        )
        print(f"\n  {saglik['degerlendirme']}")
        for k in saglik['kontroller']:
            print(f"  {k}")

if __name__ == "__main__":
    if "--portfoy" in sys.argv:
        idx = sys.argv.index("--portfoy")
        portfoy = float(sys.argv[idx+1]) if len(sys.argv) > idx+1 else 100000
        fiyat = float(sys.argv[sys.argv.index("--fiyat")+1]) if "--fiyat" in sys.argv else None
        intrinsic = float(sys.argv[sys.argv.index("--intrinsic")+1]) if "--intrinsic" in sys.argv else None
        sonuc = pozisyon_buyuklugu(portfoy, fiyat, intrinsic)
        print(json.dumps(sonuc, indent=2))
    else:
        # Test modu
        print("\n🧪 TEST MODU — Örnek Portföy")
        print("="*60)
        
        sonuc = pozisyon_buyuklugu(
            portfoy_degeri=100000,
            fiyat=50,
            intrinsic_deger=75
        )
        print(f"\n📊 Pozisyon Büyüklüğü:")
        print(f"  Portföy: $100,000")
        print(f"  Hisse Fiyatı: $50")
        print(f"  İçsel Değer: $75")
        print(f"  MoS: {sonuc['margin_of_safety']}")
        print(f"  {sonuc['buffett_standardi']}")
        print(f"  Maks Pozisyon: ${sonuc['max_pozisyon_tl']:,.2f}")
        print(f"  Stop-Loss Riski: ${sonuc['gunluk_kayip_limit']:,.2f}/gün")
        
        # Portföy riski
        pozisyonlar = [
            {"isim": "Hisse A", "maliyet": 50, "adet": 100},
            {"isim": "Hisse B", "maliyet": 30, "adet": 200},
            {"isim": "Hisse C", "maliyet": 100, "adet": 50},
        ]
        risk = portfoy_riski(pozisyonlar, 100000)
        print(f"\n📊 Portföy Risk Analizi:")
        print(f"  Toplam Pozisyon: ${risk['toplam_pozisyon']:,.2f} ({risk['toplam_pozisyon_orani']})")
        print(f"  Max Stop-Loss Riski: ${risk['toplam_stop_loss_riski']:,.2f}")
        print(f"  Pozisyon Sayısı: {risk['pozisyon_sayisi']}/{risk['max_es_zamanli_pozisyon']}")
        print(f"  Limit Aşan: {risk['limit_asan_pozisyon']} pozisyon")
        
        # Finansal sağlık
        saglik = finansal_saglik(roe=0.20, debt_equity=0.35, net_kar_mari=0.15, fcf=100000)
        print(f"\n🏥 Finansal Sağlık: {saglik['degerlendirme']}")
        for k in saglik['kontroller']:
            print(f"  {k}")
