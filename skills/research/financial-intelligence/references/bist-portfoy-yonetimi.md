# BIST Hisse Portföy Yönetimi

**Oluşturma:** 1 Temmuz 2026
**Script:** `~/.hermes/scripts/borsa-simulasyonu.py`
**Veri:** `~/.hermes/data/borsa/portfoy.json`

## Kullanım

```bash
# Hisse ekle (adet + alış fiyatı)
python3 ~/.hermes/scripts/borsa-simulasyonu.py --hisse KCAER --adet 245 --alis 14.625

# Teknik analiz (direnç/destek + RSI + trend)
python3 ~/.hermes/scripts/borsa-simulasyonu.py --hisse KCAER --analiz

# Portföy durumu (tüm hisseler + güncel K/Z)
python3 ~/.hermes/scripts/borsa-simulasyonu.py --portfoy

# Toplu analiz (birden çok hisse)
python3 ~/.hermes/scripts/borsa-simulasyonu.py --hisse KCAER,THYAO,EREGL --toplu
```

## BIST Teknik Analiz Formatı

`kripto-teknik-analiz` skill'indeki 3 katmanlı direnç/destek yönteminin BIST uyarlaması:

```
📈 [HİSSE] — TEKNİK ANALİZ (tarih)
💰 Güncel: X.XX TL
📉 1 Hafta: %+X.XX | 1 Ay: %+X.XX
━━━━━━━━━━━━━━━━━━━━
📈 DİRENÇ: X.XX TL (ilk), Y.YY TL (zorlu)
📉 DESTEK: A.AA TL (ilk), B.BB TL (güçlü)
━━━━━━━━━━━━━━━━━━━━
📊 GÖSTERGELER:
  RSI(14): X.X (durum)
  MA20: X.XX | MA50: Y.YY
  Trend: YUKARI/AŞAĞI/YATAY
  Hacim: NORMAL/YÜKSEK/DÜŞÜK
━━━━━━━━━━━━━━━━━━━━
🔮 YORUM:
  • Fiyat MA20 üstünde — kısa vadede pozitif
  • X.XX üstünde kapanış = yukarı yön
  • Y.YY altında = aşağı yön
  🎯 Orta vade hedef: Z.ZZ TL
  ⚠️ Yatırım tavsiyesi değildir.
```

## Örnek: KCAER (Kocaer Çelik)

Edel'in portföyü (1 Temmuz 2026):
- **245 adet** x **14.625 TL** = 3,583 TL maliyet
- **Güncel:** 15.08 TL (+%1.68)
- **Değer:** 3,695 TL | **K/Z:** +111 TL (%+3.1) 🟢
- **RSI:** 58.8 (nötr)
- **Trend:** Yukarı (MA20: 14.81 > MA50: 13.34)
- **Direnç:** 15.62 TL | **Destek:** 10.82 TL

## Desteklenen Hisseler

yfinance `.IS` suffix ile çalışan tüm BIST hisseleri. Hazır mapped:
KCAER, THYAO, EREGL, AKBNK, GARAN, ISCTR, ASELS, SASA, KCHOL, TUPRS, KOZAL, KOZAA, BIMAS, HEKTS, FROTO, PETKM, TCELL, VESTL, TOASO, SAHOL, YKBNK, HALKB, VAKBN, ALBRK, SISE, EKGYO, ISMEN
