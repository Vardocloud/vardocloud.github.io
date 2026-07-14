---
name: kripto-teknik-analiz
description: "Kripto para teknik analiz yöntemleri — direnç/destek mimarisi, kırılım stratejisi, vade bazlı hedefleme, presale değerleme. Bitcoin Arısı (@BitcoinArisi) yorumlama tekniğinden türetilmiştir."
metadata:
  hermes:
    tags: [crypto, technical-analysis, support-resistance, breakout, presale, trading]
    category: research
---

# Kripto Teknik Analiz — Vanitas Yorumlama Çerçevesi

**Kaynak:** @BitcoinArısı Telegram kanalı yorumlama teknikleri (1 Temmuz 2026)
**Amaç:** Coin analizlerinde standart, tekrarlanabilir yorumlama formatı

---

## 🧱 3 Katmanlı Seviye Mimarisi

Her coin analizinde şu yapı kullanılır:

```
[COİN ADI]
→ Direnç noktası: X$
→ Kırılım hedefleri: A$, B$, C$ (kısa vade)
→ Zorlu direnç: Y$ → Orta vade hedef: Z$
→ Alt destekler: D$, E$, F$
⚠️ Yatırım tavsiyesi değildir
```

### Katman 1: Direnç Noktası
- Mevcut fiyatın üstündeki ilk engel
- Kırılırsa hızlı hareket beklenir
- Format: `"X$ seviyesi direnç noktası"`

### Katman 2: Kırılım Hedefleri
- Direnç kırıldığında sırayla test edilecek seviyeler
- Her hedef bir üst direnç olarak çalışır
- Format: `"kırılmasıyla beraber A$, B$, C$ seviyeleri görülecek"`

### Katman 3: Zorlu Direnç + Orta Vade Hedef
- Daha güçlü direnç, hacimli kırılım gerektirir
- Orta vade (haftalar-aylar) hedefi
- Format: `"Zorlu direnç noktası X$ aşılmasıyla Y$ beklenir"`

### Katman 4: Alt Destekler
- Potansiyel stop-loss bölgeleri
- Genelde 3-4 kademeli destek verilir
- Format: `"Alt destekler X$, Y$, Z$ seviyeleridir"`

---

## 🚀 Kırılım Stratejisi (Breakout Trading)

### Kırılım Tipleri

| Tip | İfade | Anlamı | Zaman Beklentisi |
|-----|-------|--------|-----------------|
| **Normal Kırılım** | "kırılmasıyla beraber" | Direnç geçilirse otomatik hızlı hareket | Saatler içinde |
| **Zorlu Kırılım** | "zorlu direnç noktası aşılmasıyla" | Güçlü direnç — hacim ve momentum gerekli | Günler-haftalar |
| **Hacimli Kırılım** | "hacimli aşımıyla" | Hacimle desteklenen kırılım daha güvenilir | Haftalar |

### Kırılım Sırasında Dikkat:
1. BTC'nin genel yönü kırılımın başarısını etkiler
2. Hacimsiz kırılım — yalancı kırılım (fakeout) olabilir
3. Zorlu direnç öncesinde konsolidasyon beklenir

---

## ⏱ Vade Bazlı Hedef Sistemi

### Kısa Vade (Saatler-Günler)
- İlk kırılım hedefleri
- Format: `"kısa süre içinde test edecektir"`
- Spread genelde %15-30 arası

### Orta Vade (Haftalar-Aylar)
- Büyük hedefler
- Format: `"orta vadede hedef X$"`
- Spread genelde %50-200 arası

### Uzun Vade (Aylar-Yıllar)
- Benchmark karşılaştırması
- Format: `"Uzun vadede X ile eş değer"`
- Büyük resim hedefi

---

## 🔗 BTC Trend Filtresi (Kritik)

Her altcoin analizinde Bitcoin'in genel yönü **hesaba katılmalıdır**:

| BTC Trendi | LONG Sinyali | SHORT Sinyali |
|------------|-------------|---------------|
| 📈 YUKARI | ✅ İzin ver | ❌ Engelle |
| 📉 AŞAĞI | ❌ Engelle | ✅ İzin ver |
| ⚪ YATAY | ✅ İzin ver | ✅ İzin ver |

**Neden?** Bitcoin Arısı defalarca *"BTC hareketine dikkat edilmeli"* der. BTC düşüş trendindeyken altcoin LONG kırılımları çoğunlukla başarısız olur (stop-loss yedirir). Aynı şekilde BTC yükseliş trendindeyken SHORT işlemleri risklidir.

### Trend Belirleme Yöntemi (EMA Crossover)
```
EMA5 > EMA10 > EMA20 → Trend YUKARI 📈
EMA5 < EMA10 < EMA20 → Trend AŞAĞI 📉
Diğer               → Trend YATAY ⚪
```
Hesaplama için son 30 günlük kapanış fiyatları kullanılır.

---

## 📊 Volatilite Bazlı Stop-Loss (ATR)

Sabit %3 stop-loss volatil coin'lerde çok dardır — sürekli stop yedirir. Bunun yerine ATR (Average True Range) kullan:

### ATR Formülü
```
TR = max(High - Low, |High - Prior Close|, |Low - Prior Close|)
ATR = 14-günlük TR ortalaması
```

### Dinamik SL/TP
```
SL = ATR(14) × 1.5  (minimum %2)
TP = SL × 2.5       (Risk:Ödül = 1:2.5)
```

| Coin | Günlük Volatilite | Sabit %3 SL | ATR Bazlı SL |
|------|------------------|-------------|--------------|
| BTC | ~%2-3 | ✅ Uygun | ✅ Uygun |
| SOL | ~%4-8 | ❌ Çok dar | ✅ %6-12 |
| DOGE | ~%5-10 | ❌ Çok dar | ✅ %7-15 |

---

## 💰 Presale / Erken Aşama Yatırım Değerleme

Yeni projelerde kullanılan değerleme yöntemi:

### 1. Başarı Hikayesi Referansı
- Daha önceki başarılı presale örneği gösterilir
- Format: `"X'i Y$ dan alıp Z$ bantlarını gördük"`

### 2. Tokenomics Analizi
| Faktör | Kontrol |
|--------|---------|
| Toplam arz | Maksimum supply ne kadar? |
| Kilitli token | Ekip/yatırımcı kilitli mi? Ne kadar süre? |
| Yakım mekanizması | Deflasyonist yapı var mı? |
| Özel satış fiyatı vs Ön satış fiyatı | Erken giren ne kazanmış? |

### 3. Risk Uyarısı
- `"ön satışlar herzaman risklidir"`
- Minimum yatırım miktarı belirtilir
- Satın alma adımları açıklanır

---

## 🛡 Risk Yönetimi

Her analizde bulunması gerekenler:
1. **Destek seviyeleri** = potansiyel stop-loss bölgeleri
2. **Yatırım tavsiyesi değildir** ibaresi (zorunlu)
3. **Presale uyarısı:** riskli yatırım olduğu belirtilir
4. **BTC trend filtresi:** BTC trendine aykırı sinyal üretme
5. **Volatiliteye uygun SL:** Sabit %3 yerine ATR bazlı dinamik stop-loss

---

## 📋 Format Şablonu

### Coin Teknik Analizi
```
🪙 [COIN] — [TARİH]
💰 Fiyat: $X.XX
━━━━━━━━━━━━━━━━━━━━
📈 DİRENÇ: $X (ilk), $Y (zorlu)
📉 DESTEK: $A, $B, $C
━━━━━━━━━━━━━━━━━━━━
🚀 KIRILIM SENARYOSU:
$X kırılırsa → $A → $B (kısa vade)
$Y kırılırsa → $Z (orta vade hedef)
📊 BTC Trendi: [📈/📉/⚪]
🛡 SL (ATR bazlı): %X | TP: %Y
⚠️ Yatırım tavsiyesi değildir.
```

### Presale Değerlendirme
```
🆕 [PROJE ADI] — Ön Satış Analizi
━━━━━━━━━━━━━━━━━━━━
💰 Ön satış: $X
📊 Özel satış: $Y (kazanç: %Z)
🔒 Kilitli token: [süre/adet]
🔥 Yakım: [mekanizma]
📈 Potansiyel: [hedef fiyat / benchmark]
⚠️ Ön satışlar risklidir.
```

---

## 📚 Referans Analizler

Bitcoin Arısı'ndan örnek analiz yapıları:

### SOL Analizi (10 Şubat 2026)
```
Direnç: 87,5$
Kırılım: 94$ → 98$ → 101$ (hızlı)
Zorlu: 103,56$ → 115$ → 120$ → 128$
Orta vade: 240$
Destek: 80,74$ → 78,56$ → 73,15$
BTC korelasyonu: ✓
```

### SUI Analizi (10 Şubat 2026)
```
Direnç: 0,9821$
Kırılım: 1,15$ → 1,28$ → 1,48$ (kısa süre)
Zorlu: 1,57$ → 2,10$ → 2,32$ → 2,42$
Hacimli: 2,42$ → 2,95$ → 3,20$
Orta vade: 4,50$
Destek: 0,901$ → 0,8910$ → 0,8388$ → 0,76$
```

### CHZ Analizi (10 Şubat 2026)
```
Direnç: 0,044$ (zorlu)
Kırılım: 0,056$ → 0,061$ (hızlı)
Orta vade: 0,18$
Destek: 0,03866$ → 0,03655$ → 0,03346$
BTC korelasyonu: ✓
```

---

## 🔄 Ekonomi Zekası Entegrasyonu

Bu skill, Ekonomi Zekası bülteninde "🐝 Kripto Drop & Birikim Fırsatları" bölümünde kullanılır.

Kullanım akışı:
1. @BitcoinArısı kanalından yeni mesajları çek (bitcoin-arisi-tarayici.py)
2. Kanalda analiz edilen coin'leri takip et
3. Vanitas kendi yorumunu eklemek istediğinde bu skill'deki formatı kullan
4. Format: direnç → kırılım → destek → BTC trend filtresi → ATR SL → risk uyarısı

## 📈 Kaldıraçlı İşlem Entegrasyonu

Bu skill'deki sinyaller, `kaldirac-simulator.py` ile backtest edilerek doğrulanır:
- Direnç kırılım sinyali → Breakout stratejisi olarak simüle edilir
- Destek seviyeleri → Stop-loss bölgeleri olarak kullanılır
- Hedef fiyatlar → Take-profit seviyeleri olarak test edilir
- BTC trendi → Risk filtresi olarak uygulanır

**Backtest akışı:**
```bash
python3 ~/.hermes/scripts/kaldirac-simulator.py --coin COIN-USD --karsilastir
```
Detaylı kullanım: `references/backtest-metodolojisi.md`

## 🧪 Paper Trading Sistemi (Canlı)

**Script:** `~/.hermes/scripts/paper-trading.py`
**Cron:** Her saat başı (`8082276086de`)
**Sermaye:** $500 sanal | **Kaldıraç:** x5 | **Strateji:** Breakout + Geçmiş Veri + BTC Filtre

### ⚠️ 3 Katmanlı Doğrulama Pipeline'ı
```yaml
Backtest (geçmiş veri) → Paper Trading (canlı sanal) → Gerçek İşlem
```

### ⚠️ Günlük Kazanç Uyarısı (1 Temmuz 2026 Testi)

Günlük kazanç (günlük al-sat) kaldıraçlı işlemlerde **yüksek risklidir**. 15 coin'de 60 günlük testte sadece 3/15 coin kârlı (%23). Küçük bütçelerde ($50-80) komisyon oranı net kârı sıfırlıyor. **Haftalık/dönemsel işlem daha güvenlidir.**

### ⚠️ Paper Trading Sonucu (6 Temmuz 2026)

Canlı paper trading testi ($500, x5, saat başı cron): 5 günde $500 → $23 (%-95.4), 185 işlem (günde ~37). Win rate %53.5 olmasına rağmen aşırı frekans + kaldıraç portföyü bitirdi.

**Sonuç:** Kaldıraçlı işlemde frekans, kaldıraçtan daha büyük risk faktörüdür. Saat başı sinyal üretmek yerine günde 3-5 işlemle sınırla, ATR bazlı stop-loss kullan, circuit breaker ekle.

---

## 📂 Referans Dosyaları

- `references/bitcoin-arisi-ornek-analizler.md` — @BitcoinArısı'nden çekilen 6 örnek analizin yapısal çözümlemesi
- `references/backtest-metodolojisi.md` — Backtest çalıştırma, BTC trend filtresi, ATR stop-loss, pipeline kuralları
- `references/kaldirac-simulasyonu.md` — Simülatör kullanım kılavuzu, backtest sonuçları, optimum parametreler
- `references/paper-trading.md` — Paper trading sistemi kullanım kılavuzu
- `references/gunluk-kazanc-stratejileri.md` — Günlük kazanç stratejisi test sonuçları

## 🆕 BIST Hisse Senedi Analizi

Bu skill'in BIST hisseleri için uyarlanmış versiyonu `~/.hermes/scripts/borsa-simulasyonu.py` ile kullanılır.

BIST formatı (TL bazlı):
```
📈 [HİSSE] — TEKNİK ANALİZ ({tarih})
💰 Güncel: X.XX TL
📈 DİRENÇ: X.XX TL (ilk), Y.YY TL (zorlu)
📉 DESTEK: A.AA TL (ilk), B.BB TL (güçlü)
📊 RSI: X.X | Trend: YUKARI/AŞAĞI
📊 BTC Trendi: N/A (BIST için geçerli değil)
🎯 Orta vade hedef: Z.ZZ TL (direnç kırılırsa)
⚠️ Yatırım tavsiyesi değildir.
```
