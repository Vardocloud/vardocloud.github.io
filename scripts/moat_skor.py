#!/usr/bin/env python3
"""
Moat Skorlama Sistemi — Buffett'ın Ekonomik Hendek Analizi
v1.0 — 27 Haziran 2026

5 faktör: Marka Gücü, Switching Cost, Ağ Etkisi, Maliyet Avantajı, Gizli Varlıklar
Her faktör 1-5 puan. Toplam skor → portföy ağırlığı.

Kullanım:
  python3 moat_skor.py                         # Interaktif
  python3 moat_skor.py --file sirket.json      # JSON dosyasından
  python3 moat_skor.py --ticker AAPL           # yfinance ile
"""

import json
import sys

# Moat faktörleri ve açıklamaları
FAKTORLER = {
    "marka_gucu": {
        "ad": "Marka Gücü",
        "soru": "Müşteriler bu markaya prim ödemeye razı mı?",
        "seviyeler": [
            (1, "Hiç bilinmeyen marka, emtia ürün"),
            (2, "Yerel bilinirlik, düşük marka sadakati"),
            (3, "Tanınan marka, orta sadakat"),
            (4, "Güçlü marka, müşteriler prim öder"),
            (5, "Kült ikon, müşteriler başka alternatifi düşünmez (Apple, Coca-Cola)"),
        ]
    },
    "switching_cost": {
        "ad": "Müşteri Bağımlılığı (Switching Cost)",
        "soru": "Müşteriler rakibe geçmekte zorlanır mı?",
        "seviyeler": [
            (1, "Tek tıkla rakibe geçilebilir"),
            (2, "Düşük geçiş maliyeti (birkaç gün)"),
            (3, "Orta geçiş maliyeti (veri taşıma, eğitim)"),
            (4, "Yüksek geçiş maliyeti (entegrasyon, sözleşme)"),
            (5, "Geçiş imkansıza yakın (işletim sistemi, SAP)"),
        ]
    },
    "ag_etkisi": {
        "ad": "Ağ Etkisi",
        "soru": "Her yeni kullanıcı ürünü/hizmeti değerli kılıyor mu?",
        "seviyeler": [
            (1, "Ağ etkisi yok veya negatif"),
            (2, "Zayıf ağ etkisi (kalabalık kötü)"),
            (3, "Orta ağ etkisi (lokasyon bazlı)"),
            (4, "Güçlü ağ etkisi (pazar yeri)"),
            (5, "Çift taraflı ağ etkisi (platform tekel - Meta, Visa)"),
        ]
    },
    "maliyet_avantaji": {
        "ad": "Düşük Maliyet Avantajı",
        "soru": "Rakiplerden daha düşük maliyetle üretebiliyor mu?",
        "seviyeler": [
            (1, "Rakiplerle aynı maliyet"),
            (2, "Küçük avantaj (<%5)"),
            (3, "Orta avantaj (%5-15)"),
            (4, "Büyük avantaj (%15-30)"),
            (5, "Ezici avantaj (>%30, ölçek ekonomisi)"),
        ]
    },
    "gizli_varliklar": {
        "ad": "Gizli Varlıklar (Patent/Lisans/Düzenleme)",
        "soru": "Rakiplerin girmesini engelleyen yasal/gizli varlıklar var mı?",
        "seviyeler": [
            (1, "Hiçbir koruma yok"),
            (2, "Zayıf patent/koruma (kolay atlatılır)"),
            (3, "Orta koruma (patent, düzenleme)"),
            (4, "Güçlü koruma (uzun süreli patent, lisans)"),
            (5, "Yasal tekel (devlet lisansı, doğal tekel)"),
        ]
    }
}

def moat_skorla(puanlar: dict) -> dict:
    """5 faktörlü moat skorlaması yap"""
    if not puanlar:
        return {"hata": "Puan girilmedi"}
    
    toplam = 0
    detay = {}
    
    for faktor, puan in puanlar.items():
        if faktor in FAKTORLER:
            info = FAKTORLER[faktor]
            toplam += min(max(puan, 1), 5)  # 1-5 arası
            detay[faktor] = {
                "puan": puan,
                "max": 5,
                "seviye": info["seviyeler"][puan-1][1] if 1 <= puan <= 5 else "Geçersiz"
            }
    
    max_puan = len(FAKTORLER) * 5
    yuzde = (toplam / max_puan) * 100
    
    if yuzde >= 85:
        seviye = "🟢 GENİŞ HENDEK (Wide Moat)"
        aciklama = "Buffett'ın favorisi. Rakip girmesi çok zor."
    elif yuzde >= 65:
        seviye = "🔵 DAR HENDEK (Narrow Moat)"
        aciklama = "Rekabet avantajı var ama sürdürülebilirliği test edilmeli."
    elif yuzde >= 45:
        seviye = "🟡 HENDEK YOK / BELİRSİZ"
        aciklama = "Rekabet avantajı sınırlı. Fiyat avantajı aranmalı."
    else:
        seviye = "🔴 HENDEK YOK (No Moat)"
        aciklama = "Emtia işi. Sadece çok düşük fiyattan alınabilir."
    
    return {
        "toplam_puan": toplam,
        "max_puan": max_puan,
        "yuzde": round(yuzde, 1),
        "seviye": seviye,
        "aciklama": aciklama,
        "detay": detay,
        "faktor_sayisi": len(puanlar),
        "portfoy_agirligi_onerisi": f"Portföyün %{min(yuzde/5, 20):.0f}-%{min(yuzde/3, 30):.0f}'ı"
    }

def interaktif():
    print("\n" + "="*60)
    print("  🛡 MOAT SKORLAMA SİSTEMİ (Buffett — Ekonomik Hendek Analizi)")
    print("="*60)
    
    puanlar = {}
    for key, info in FAKTORLER.items():
        print(f"\n{info['ad']}")
        print(f"  {info['soru']}")
        for p, desc in info["seviyeler"]:
            print(f"  [{p}] {desc}")
        
        while True:
            try:
                puan = int(input("\n  Puan (1-5): ") or "3")
                if 1 <= puan <= 5:
                    puanlar[key] = puan
                    break
                else:
                    print("  Lütfen 1-5 arası girin.")
            except ValueError:
                print("  Geçersiz giriş.")
    
    sonuc = moat_skorla(puanlar)
    raporla(sonuc)
    return sonuc

def raporla(sonuc: dict):
    print(f"\n{'='*60}")
    print(f"  {sonuc['seviye']}")
    print(f"{'='*60}")
    print(f"  Toplam Puan: {sonuc['toplam_puan']}/{sonuc['max_puan']} (%{sonuc['yuzde']})")
    print(f"  {sonuc['aciklama']}")
    print(f"  Önerilen Portföy Ağırlığı: {sonuc['portfoy_agirligi_onerisi']}")
    
    print(f"\n  📋 Faktör Detayı:")
    for faktor, detay in sonuc['detay'].items():
        ad = FAKTORLER[faktor]['ad']
        print(f"  • {ad:<30s} {detay['puan']}/5 — {detay['seviye'][:40]}")

def ticker_analiz(ticker: str):
    """yfinance ile hisse moat analizi (temel gösterge)"""
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        info = t.info
        
        print(f"\n📡 {ticker} moat analizi...")
        
        # Finansal göstergelerden moat çıkarımı
        gross_margin = info.get('grossMargins', 0) or 0
        net_margin = info.get('profitMargins', 0) or 0
        roe = info.get('returnOnEquity', 0) or 0
        de = (info.get('totalDebt', 0) or 0) / (info.get('totalStockholderEquity', 1) or 1)
        
        print(f"\n  📊 Finansal Göstergeler:")
        print(f"  • Brüt Marj: %{gross_margin*100:.1f}")
        print(f"  • Net Marj: %{net_margin*100:.1f}")
        print(f"  • ROE: %{roe*100:.1f}")
        print(f"  • D/E: {de:.2f}")
        
        # Kabaca moat skoru
        puanlar = {
            "marka_gucu": 3 if net_margin > 0.15 else 2,
            "switching_cost": 3,
            "ag_etkisi": 2,
            "maliyet_avantaji": 3 if gross_margin > 0.4 else 2,
            "gizli_varliklar": 2 if de < 0.5 else 1,
        }
        
        # Net marj yüksekse → marka gücü veya switching cost yüksek
        if net_margin > 0.20:
            puanlar["marka_gucu"] = 4
        if gross_margin > 0.60:
            puanlar["maliyet_avantaji"] = 4
        
        sonuc = moat_skorla(puanlar)
        raporla(sonuc)
        
    except ImportError:
        print("yfinance kurulu değil.")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--ticker' and len(sys.argv) > 2:
            ticker_analiz(sys.argv[2])
        elif sys.argv[1] == '--file' and len(sys.argv) > 2:
            with open(sys.argv[2]) as f:
                data = json.load(f)
            sonuc = moat_skorla(data.get("puanlar", {}))
            raporla(sonuc)
        else:
            print("Kullanım: python3 moat_skor.py [--ticker HISSE | --file data.json]")
    else:
        # Test modu
        print("\n🧪 TEST MODU — Apple (AAPL) Moat Analizi")
        print("="*60)
        
        ornek_puanlar = {
            "marka_gucu": 5,        # Apple — kült ikon
            "switching_cost": 5,    # iOS ekosistemi, iCloud, App Store
            "ag_etkisi": 4,         # App Store geliştirici ağı
            "maliyet_avantaji": 3,  # Ölçek ekonomisi var ama premium
            "gizli_varliklar": 3,   # Patentler, tedarik zinciri
        }
        
        sonuc = moat_skorla(ornek_puanlar)
        raporla(sonuc)
        
        print(f"\n🧪 TEST 2 — BIST Şirketi (Örnek)")
        
        bist_ornek = {
            "marka_gucu": 2,
            "switching_cost": 2,
            "ag_etkisi": 1,
            "maliyet_avantaji": 3,
            "gizli_varliklar": 1,
        }
        sonuc2 = moat_skorla(bist_ornek)
        raporla(sonuc2)
