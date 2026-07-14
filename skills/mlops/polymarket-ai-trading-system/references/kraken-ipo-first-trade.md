# Kraken IPO — İlk Paper Trade Deneyimi (27 Haz 2026)

## Setup
- `pm-trader init --balance 10000` → $10K sanal bakiye
- Market: Kraken IPO by December 31, 2026? (slug: `kraken-ipo-by-december-31-2026-513`)
- Gamma API event: Kraken IPO by ___ ? (id: 16183)
- Condition ID: `0xced0cb8725bad43d78fda0cd0e5fa9e31804625cb3502b2c7897f8e8f7fa9e1f`

## Market Discovery

### Yöntem: Gamma API Events (doğru yol)
```bash
# Events endpoint ile en yüksek hacimli event'leri bul
curl -s 'https://gamma-api.polymarket.com/events?closed=false&limit=20&order=volume_usd&asc=false'

# Belirli bir event'in market yapısını gör
# Her event birden çok zaman dilimli market içerir:
# - Kraken IPO by March 31, 2026? → closed (geçti)
# - Kraken IPO by June 30, 2026? → closed (geçti)
# - Kraken IPO by December 31, 2026? → AÇIK, YES: 29.5¢, $541K hacim
```

### Yanlış Yol: pm-trader markets search
```bash
pm-trader markets search "kraken"  # GTA VI meme marketlerini döndürür!
pm-trader markets search "ipo"      # Aynı sorun
```
Skill'de belirtildiği gibi, `pm-trader markets search` genel terimlerde alakasız sonuçlar döndürüyor (Gamma API'yi direkt kullan).

## Order Book Analizi (Trade Öncesi)

```bash
pm-trader book "kraken-ipo-by-december-31-2026-513"
```

**Bids (YES satın almak isteyenler):**
| Kademe | Fiyat | Share |
|--------|:-----:|:-----:|
| 1 | 28¢ | 10 |
| 2 | 27¢ | 483 |
| 3 | 26¢ | 998 |
| 4 | 25¢ | 10 |

**Asks (YES satmak isteyenler):**
| Kademe | Fiyat | Share |
|--------|:-----:|:-----:|
| 1 | 31¢ | 6 |
| 2 | 32¢ | 5 |
| 3 | 47¢ | 19 |
| 4 | 48¢ | 106 |

**Spread Gap:** 31¢ - 47¢ arasında 15¢'lik boşluk (çok az share var).

## Trade ve Slippage

```bash
pm-trader buy "kraken-ipo-by-december-31-2026-513" yes 50
```

**Sonuç:**
| Metrik | Değer |
|--------|-------|
| Emir tipi | market (fok) |
| Doldurulan kademe | 4 |
| Ortalama maliyet | 46.14¢ |
| Alınan share | 108.37 |
| Midpoint fiyat | 29.5¢ |
| Anlık unrealized PnL | -$18.03 (-%36) |

**Neden bu kadar slippage?**
- 31¢'de sadece 6 share, 32¢'de 5 share vardı
- $50'lik talep bu 11 share'i anında yedi
- Kalan 97 share için 47¢, 48¢, 49¢, 50¢ gibi çok daha yüksek fiyatlardan almak zorunda kaldı
- Ortalama maliyet 46.14¢'ye fırladı

## Dersler

1. **$500K+ hacim yanıltıcıdır** — Kraken IPO'nun $541K hacmi var ama YES tarafındaki likidite çok ince
2. **Order book her zaman kontrol edilmeli** — Görünür hacim ile gerçek derinlik farklı
3. **$50 bile büyük** — Bu markette $10-20 ideal başlangıç
4. **Limit order kurtarır** — 28¢'den bid koysaydık spread'i yememiş olurduk
5. **Paper trader gerçekçi** — Slippage simülasyonu gerçek Polymarket verisiyle çalışıyor, bu iyi bir özellik

## Gamma API Veri Yapısı (Multi-Market Event)

```python
# Gamma API events → birden çok zaman dilimli market
{
  "id": 16183,
  "title": "Kraken IPO by ___ ?",
  "markets": [
    {"question": "Kraken IPO by March 31, 2026?", "closed": True},
    {"question": "Kraken IPO by June 30, 2026?", "closed": True},
    {"question": "Kraken IPO by December 31, 2026?", 
     "closed": False,
     "outcomePrices": "[0.295,0.705]",  # double-encoded JSON string
     "volume": 541488
    }
  ]
}
```
