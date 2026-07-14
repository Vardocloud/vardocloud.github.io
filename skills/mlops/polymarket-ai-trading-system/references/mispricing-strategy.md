# Obvious Mispricing Strategy — Detaylı Referans

## ⚠️ ÖNEMLİ DÜZELTME (25 Haz 2026)

Bu referansın orijinal versiyonundaki edge hesaplamaları **hatalıydı.** Aşağıdaki doğru analiz okunmalıdır.

---

## Teori
Polymarket'te bazı marketler, sorunun doğası gereği bir yöne aşırı eğik olasılık içerir ama market fiyatı bunu yansıtmaz. Bunların çoğu eğlence amaçlıdır — "önce hangisi olur?" yarışları.

**Ancak:** GTA VI "before" comparison marketlerinde **50/50 fallback clause** tüm edge'i ortadan kaldırır. Bu marketler efficient pricing'dedir.

## Resolution Rules - Doğru Analiz

GTA VI yarış marketlerinde resolution şöyle işler:
- **YES** = Olay X, GTA VI'dan **önce** gerçekleşirse
- **NO** = GTA VI, Olay X'ten **önce** gerçekleşirse  
- **50/50** = 31 Temmuz 2026'ya kadar **hiçbiri olmazsa**

50/50'de **her iki outcome da $0.50 kazanır.** Bu "para iade" değildir — her iki taraf da eşit değerlenir.

## Kritik Bilgi: GTA VI Çıkış Takvimi

- Rockstar Games / Take-Two Interactive resmi açıklaması: **Fall 2026**
- Fall 2026 = Eylül-Aralık 2026 aralığı
- 31 Temmuz 2026 = **yaz ortası**, Fall'dan aylar önce
- **GTA VI'nın 31 Temmuz'dan önce çıkma ihtimali: ~%0**

## Fair Value Hesaplaması (DOĞRU)

```
P(GTA VI before Jul 31) = G ≈ 0 (onaylanmış Fall 2026)
P(Olay X before Jul 31) = p (bilinmeyen)
P(neither) = 1 - G - p = 1 - p (G≈0 olduğu için)

NO için expected value:
= G × $1.00 + p × $0.00 + (1-G-p) × $0.50
= 0 + 0 + (1-p) × $0.50
= $0.50 × (1-p)

YES için expected value:
= p × $1.00 + G × $0.00 + (1-G-p) × $0.50
= p + (1-p) × $0.50
= $0.50 + $0.50p
```

## Gerçek Edge Tablosu

| Market | NO Fiyatı | p (olay ihtimali) | Fair NO | Edge |
|---|---|---|---|---|
| Rihanna before GTA VI | 48.5¢ | ~%5-10 (albüm 10 yıldır yok) | 45.0-47.5¢ | -3.5¢ ile +1.0¢ arası |
| Carti before GTA VI | 48.0¢ | ~%5-10 | 45.0-47.5¢ | -3.0¢ ile +1.5¢ arası |
| Jesus before GTA VI | 50.5¢ | ~%0 | 50.0¢ | -0.5¢ |
| BTC $1M before GTA VI | 50.45¢ | ~%0 | 50.0¢ | -0.45¢ |
| Trump out before GTA VI | 50.5¢ | ~%0 | 50.0¢ | -0.5¢ |
| China invades Taiwan | 49.5¢ | ~%1-5 | 47.5-49.5¢ | -2.0¢ ile 0¢ arası |

**Sonuç:** Tüm marketler efficient fiyatlanmıştır. Max edge (en iyimser senaryoda) Carti NO'da ~%3'tür — spread ve slippage'ı geçmez.

## Orijinal Hatadaki Yanlış Varsayımlar

1. **P(GTA VI before Jul 31) = %95** ❌ → Gerçek: ~%0. GTA VI Fall 2026 için onaylı.
2. **50/50 = "para iade"** ❌ → 50/50'de YES ve NO **eşit değer alır** ($0.50), sıfırlanmaz.
3. **Formül: 0.95 × $1 + 0.05 × $0.50 = $0.975** ❌ → Bu formül GTA VI'nın çıkacağını varsayar. Oysa çıkmazsa 50/50'de her iki taraf $0.50 alır—NO $1 almaz.
4. **Edge ~%40-47** ❌ → Gerçek: %0-4 arası.

## Python Detection (GÜNCELLENMİŞ)

```python
# GTA VI "before" marketleri: ARTIK trade açılmaz
# Edge maksimum %4, spread/slippage bunu yer
# Bu marketleri tamamen filtrele

def analyze(market):
    q = market['question'].lower()
    
    if 'before gta' in q:
        return None  # 50/50 floor nedeniyle sinyal yok
    if 'gta vi' in q:
        return None  # GTA VI ile ilgili tüm marketleri filtrele
        
    # Gerçek mispricing fırsatları: sport, finance, crypto kategorilerinde ara
    return None
```

## Trade Yönetimi

- Her markete max $200 (düşük risk, çünkü 50/50 koruması var)
- Pozisyonları kârdayken kapatma: GTA VI çıkana veya 31 Temmuz'a kadar bekle
- %50'den alıp %95'e satmak yerine resolution'a kadar bekle (spread'lerden kaçın)
- Edge %15'in altına düşerse trade açma
