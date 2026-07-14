# Türkiye Piyasa Veri Kaynakları — Karşılaştırma ve En İyi Uygulamalar

**Oluşturan:** Vanitas (financial-intelligence skill)
**Tarih:** 27 Haziran 2026
**Kaynak:** Test sürüşü sırasında keşfedildi (Bloomberg HT vs yfinance karşılaştırması)

## 1. Bloomberg HT (web_extract ile) — BİRİNCİL KAYNAK

**URL:** `https://www.bloomberght.com/`
**Yöntem:** `web_extract(["https://www.bloomberght.com/"])`

### Sağladığı Veriler (yfinance'tan DAHA zengin)
| Veri | Bloomberg HT | yfinance |
|------|-------------|----------|
| BIST100 | ✅ Canlı, % değişim | ✅ XU100.IS |
| BIST Banka | ✅ XBANK | ✅ XBANK.IS |
| BIST Sinai | ✅ XUSIN | ✅ XUSIN.IS |
| BIST 30/50 | ✅ | ✅ |
| USD/TRY | ✅ Canlı, alış/satış | ✅ USDTRY=X |
| EUR/TRY | ✅ Canlı | ✅ EURTRY=X |
| GBP/TRY | ✅ Canlı | ❌ Test edilmedi |
| Altın/ONS | ✅ Canlı, alış/satış spread | ✅ GC=F |
| Gram Altın | ✅ Canlı (₺6,130) | ❌ Yok |
| Cumhuriyet Altını | ✅ Canlı | ❌ Yok |
| TR 2Y Tahvil | ✅ %40.33 | ❌ Yok |
| **TR 10Y Tahvil** | **✅ Canlı (%33.14)** | **❌ Sembol çalışmaz** |
| ABD 10Y | ✅ | ✅ ^TNX |
| Brent Petrol | ✅ $72 | ✅ BZ=F |
| En çok artan/azalan hisseler | ✅ Tablo halinde | ❌ Yok |
| Eurobond (Türkiye) | ✅ 1Y/2Y/3Y | ❌ Yok |
| Son dakika haberleri | ✅ Canlı akış | ❌ Yok |
| Trump/İran/jeopolitik | ✅ Anlık başlıklar | ❌ Yok |

### Avantajları
- **TR 10Y tahvil faizi** — yfinance'te sembol bulunamadı, Bloomberg HT'te canlı (%33.14)
- **Gram altın ve diğer TL bazlı emtialar** — yfinance'ta yok
- **BIST hisse bazlı veri** — en çok artan/azalan, işlem hacmi
- **Güncel haber akışı** — son dakika ekonomi/politika haberleri
- **Tek kaynakta 20+ veri noktası** — BBC + yfinance + Google News'in toplamından fazla

### Dezavantajları
- 403 hatası dönebilir (web_extract ile erişim bazen engellenir)
- Veri anlık ama canlı değil (sayfa yenileme hızında)
- İngilizce haber yok (sadece Türkçe)

## 2. yfinance (Python ile) — İKİNCİL KAYNAK

**Yöntem:** `python3 /home/ubuntu/.hermes/scripts/makro_veri.py --json`

### Çalışan Semboller (21/22 test edildi, 27 Haz 2026)
| Varlık | Sembol | Durum |
|--------|--------|-------|
| Altın (ons) | GC=F | ✅ |
| Gümüş | SI=F | ✅ |
| Bakır | HG=F | ✅ |
| Brent Petrol | BZ=F | ✅ |
| USD/TRY | USDTRY=X | ✅ |
| EUR/TRY | EURTRY=X | ✅ |
| EUR/USD | EURUSD=X | ✅ |
| DXY | DX-Y.NYB | ✅ |
| BIST100 | XU100.IS | ✅ |
| BIST Banka | XBANK.IS | ✅ |
| BIST Sinai | XUSIN.IS | ✅ |
| BIST Teknoloji | XUTEK.IS | ✅ |
| BIST Hizmetler | XUHIZ.IS | ✅ |
| BIST Mali | XUMAL.IS | ✅ |
| BIST Gıda | XGIDA.IS | ✅ |
| S&P500 | ^GSPC | ⚠️ Haftasonu NaN |
| NASDAQ | ^IXIC | ⚠️ Haftasonu NaN |
| Dow Jones | ^DJI | ⚠️ Haftasonu NaN |
| ABD 10Y | ^TNX | ✅ |
| Bitcoin | BTC-USD | ✅ |
| Ethereum | ETH-USD | ✅ |

### Çalışmayan Semboller
- **TR10YT=RR** (Türkiye 10Y tahvil) — Yahoo Finance'te bulunamadı. **Bloomberg HT kullan.**

### Avantajları
- Programatik erişim (JSON çıktı, cron'da kullanılabilir)
- Tarihsel veri (backtest için)
- ABD piyasaları ve kripto

## 3. Dünya Gazetesi (web_extract ile) — ÜÇÜNCÜL KAYNAK

**URL:** `https://www.dunya.com/ekonomi`
**Yöntem:** `web_extract(["https://www.dunya.com/ekonomi"])`

### Kullanım
- Türkiye ekonomi haberleri
- Şirket bazlı gelişmeler
- Sektör analizleri

## 4. BBC Business (web_extract ile) — KÜRESEL KAYNAK

**URL:** `https://www.bbc.com/news/business`
**Yöntem:** `web_extract(["https://www.bbc.com/news/business"])`

### Kullanım
- Uluslararası ekonomi haberleri
- Küresel piyasa trendleri
- İngilizce kaynak (çeviri gerekebilir)

## 5. Önerilen Veri Toplama Stratejisi

```
1. Bloomberg HT (web_extract) → TR verileri + canlı fiyat + haberler
   Başarısız olursa → yfinance (makro_veri.py)
   
2. BBC Business (web_extract) → Küresel haberler
   
3. Dünya Gazetesi (web_extract) → Türkiye haber detayı
   
4. Google News (web_search) → Spesifik konu araştırması
   
5. yfinance (makro_veri.py) → Programatik fiyat verisi (Makro Panel)
```

### Hata Yönetimi
- Bloomberg HT 403 dönerse: yfinance'a geç, eksik TR verilerini not et
- BBC 403 dönerse: Google News ile telafi et
- Tüm kaynaklar başarısız olursa: kısa "veri alınamadı" notu, asla boş bülten gönderme
