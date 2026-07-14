---
name: financial-intelligence
description: "Yatırım araştırması, değer yatırımı metodolojisi, piyasa okuma ve makroekonomik analiz — Warren Buffett felsefesi temelli. Ekonomi verisi toplama, yorumlama, bülten üretimi ve simülasyon."
metadata:
  hermes:
    tags: [investment, value-investing, buffett, market-analysis, economy, macro, simulation, paper-trading, kripto, crypto-technical-analysis]
    category: research
---

# Financial Intelligence — Yatırım Danışmanı Modülü

**Amaç:** Buffett-style value investing perspektifinden ekonomi haberlerini topla, yorumla, yatırım fırsatlarını değerlendir. Günde 2 kere (08:00 & 18:00) bülten üret. Zamanla simülasyon katmanı ekle.

---

## 🧠 Warren Buffett'ın 12 Yatırım Kriteri

### 1. İşletme (Business Tenets)
| Kriter | Açıklama | Sorgu |
|--------|----------|-------|
| **Anlaşılabilirlik** | İş modeli net, basit, açıklanabilir olmalı | "Bu işi 5 yaşındaki bir çocuğa anlatabilir miyim?" |
| **Tutarlılık** | Operasyon geçmişi test edilmiş, istikrarlı | "Son 5-10 yılda tutarlı büyümüş mü?" |
| **Ekonomik Hendek (Moat)** | Sürdürülebilir rekabet avantajı | "Rakipler neden giremiyor?" |

**Moat Türleri:**
- Marka gücü (Coca-Cola, Apple)
- Yüksek switching cost (müşteri bağımlılığı)
- Ağ etkisi (her kullanıcı değer katar)
- Düşük maliyet avantajı (ölçek ekonomisi)
- Gizli varlıklar (patent, lisans, düzenleyici engel)

### 2. Yönetim (Management Tenets)
| Kriter | Açıklama |
|--------|----------|
| **Rasyonellik** | Sermayeyi rasyonel dağıtır (reinvest vs temettü) |
| **Dürüstlük** | Hatalarını şeffafça açıklar |
| **İnovasyon** | Kopyalama değil, stratejik inovasyon yapar |

### 3. Finansal (Financial Tenets)
| Metrik | Formül / Açıklama | Hedef |
|--------|-------------------|-------|
| **Düşük Borç** | Debt/Equity oranı | < 0.5 ideal |
| **Yüksek Marj** | Net kar marjı, FCF marjı | Sektör ortalaması üstü |
| **Owner's Earnings** | Net Gelir + Amortisman - Capex - İşletme Sermayesi | Pozitif ve büyüyen |
| **EVA** | NOPAT - (CI × WACC) | Pozitif |
| **ROE** | Net Gelir / Öz Sermaye | > %15 istikrarlı |

### 4. Değer (Value Tenets)
- **İçsel Değer:** İndirgenmiş nakit akışı (DCF) ile gelecek owner's earnings'i bugüne çek
- **Margin of Safety:** Piyasa fiyatı ile içsel değer arasında en az %25-30 güvenlik marjı
- **Uzun Vade:** "En sevdiğimiz elde tutma süresi sonsuza kadar." — 10 yıl tutamayacaksan 10 dakika bile düşünme
- **Kontrarian:** "Başkaları korkarken açgözlü ol, başkaları açgözlüyken kork."
- **Fiyat/Değer:** "Fiyat ne ödediğin, değer ne aldığındır."

---

## 📊 Piyasa Okuma Çerçevesi

### Makroekonomik Göstergeler (Türkiye)
- **Faiz:** TCMB politika faizi, Fed faizi, reel faiz
- **Enflasyon:** TÜFE (aylık/yıllık), ÜFE, çekirdek enflasyon
- **Büyüme:** GSYİH (çeyreklik), sanayi üretimi, PMI
- **İstihdam:** İşsizlik oranı, istihdam katılımı
- **Döviz:** USD/TRY, EUR/TRY, reel efektif kur
- **Risk:** CDS primi, Türkiye 5Y bond
- **Cari:** Cari açık/fazla, ihracat/ithalat

### Türkiye Yatırım Düzenlemeleri (SPK)
| Konu | Kural | Pratik Sonuç |
|------|-------|--------------|
| **Forex min. teminat** | 50.000 TL | 10.000 TL ile forex canlı hesap açılamaz — demo ile strateji testi yapılır |
| **Forex max kaldıraç** | 10:1 | Kripto kaldıraçsız tercih edilir (SPK kapsamı dışı) |
| **Forex stopaj** | %10 (3 aylık) | Otomatik kesinti, broker tarafından tahsil |
| **Forex demo** | 6 gün / 50 işlem | Zorunlu — strateji test alanı |
| **BIST hisse** | SPK lisanslı aracı kurum | Düşük bütçeyle başlanabilir, komisyon ~%1.99 |
| **Müşteri koruması** | Takasbank + YTM | Ayrıştırılmış hesap zorunlu |
| **BIST DCA** | Küçük bütçeyle | En erişilebilir uzun vadeli araç (detay: `references/turkiye-bist-dca.md`)

### Değer Yatırımı Filtre Sorguları
Her haber/değerlendirme için Buffett filtresi:
1. **Kategorize et:** Fırsat mı, risk mi, nötr bilgi mi?
2. **Moat kontrolü:** Bu şirket/sektörün savunulabilir avantajı var mı?
3. **Fiyat/Değer:** Piyasa fiyatı içsel değerin altında mı?
4. **Uzun Vade:** Bu bilgi 5 yıl sonra hala anlamlı mı?
5. **Margin of Safety:** Yanılırsam kaybım ne olur?

---

## 📥 Veri Toplama Pipeline'ı

### Günde 2 Kere — Zamanlama
- **Sabah 08:00** — Piyasa öncesi bülteni: gece gelişmeleri, Asya piyasaları, ABD vadeli işlemler, makro takvim
- **Akşam 18:00** — Gün sonu bülteni: BIST kapanış, emtia fiyatları, günün özeti, forex

### Adım Adım Veri Toplama (Cron İçinde)

#### a) Küresel Ekonomi — web_extract ile birincil kaynak
```
web_extract(["https://www.bbc.com/news/business"])
```
- En geniş uluslararası ekonomi haber yelpazesi
- Son 24 saatteki haberler ana sayfada

#### b) Türkiye Ekonomisi — web_extract ile ikincil kaynaklar
```
web_extract([
  "https://www.bloomberght.com/",         # Bloomberg HT — canlı borsa/ekonomi
  "https://www.dunya.com/ekonomi",         # Dünya Gazetesi — ekonomi
])
```
- Bloomberg HT: BIST canlı, piyasa verileri, döviz kurları
- Dünya Gazetesi: Türkiye ekonomisi haberleri, şirket haberleri

#### c) Google News — web_search ile üçüncül kaynak
Her sorgu için ayrı web_search çağrısı:
- "BIST 100 endeksi bugün"
- "Türkiye ekonomisi haberleri"
- "altın gümüş bakır fiyatları"
- "dolar euro kuru"
- Sabah ek: "Asya piyasaları" + "ABD vadeli işlemler"
- Akşam ek: "BIST kapanış" + "emtia fiyatları"

#### c) yfinance Canlı Veri
```bash
python3 /home/ubuntu/.hermes/scripts/makro_veri.py --json
```
- 21 varlık: BIST endeksleri, emtia, forex, ABD endeksleri, kripto
- Makro Panel'de kullanılır
- Hata durumunda diğer kaynaklarla devam et

#### d) 🐝 Bitcoin Arısı — Kripto Drop & Birikim Fırsatları (@BitcoinArisi)
- **Kaynak:** @BitcoinArisi Telegram kanalı (t.me/s/BitcoinArisi)
- **Tarama:** Günde 1 kere (sabah 09:00) — no_agent cron job
- **Script:** `~/.hermes/scripts/bitcoin-arisi-tarayici.py --cron`
- **Veri dosyası:** `~/.hermes/data/bitcoin-arisi/birikim-fikirleri.json`
- **Filtreleme:** Reklam/bot tanıtımı mesajları otomatik atlanır
- **Kategoriler:** DROP fırsatı, UCUZ yatırım, Hedef fiyat
- **Kullanım:** Ekonomi bülteninde "🐝 Kripto Drop & Birikim Fırsatları" bölümü

#### e) 🪙 Coin Listesi (Investing.com + CoinGecko)
- **Script:** `~/.hermes/scripts/coin-listesi.py`
- **Kapsam:** 250 coin (BTC, ETH, XRP, SOL, ADA, DOGE vb.)
- **Güncelleme:** Her gün 07:00 (cron: 67f6794f67f7)
- **Veri kaynağı:** CoinGecko API (ücretsiz, API key gerekmez)

#### f) Bundle Entegrasyonu
Mevcut "Bundle Gündem" cron'u (günde 3 kere) genel haber akışını toplar. Ekonomi kategorisi filtrelenerek kullanılabilir. Ancak ekonomi cron'u Bundle'a bağımlı DEĞİLDİR — BBC + Google News ile bağımsız çalışır.

#### g) YouTube Ekonomi Kanalları (CRON AKTİF — 07:00)
5 ekonomi/yatırım kanalı düzenli olarak taranır. Cron job `e0ab298fccc8` her sabah 07:00'de çalışır:
- Kayıt Dışı İktisat (Ceyhun Elgin) — makro ekonomi analizi
- Yatırım 101 — finansal okuryazarlık, portföy yönetimi
- Kendine Milyoner — bireysel yatırım, altın/gümüş
- Borsadan Hisse — BIST, teknik analiz, temel analiz
- Mark Tilbury — uluslararası yatırım, zenginlik stratejileri

### Veri Çekme Yöntemi (API anahtarı gerekmez)

1. **RSS Feed** — Son videoları listele
2. **YouTubeTranscriptApi** — Video altyazılarını çek (Türkçe/İngilizce)
3. **oEmbed** — Video metaverisi
4. **web_extract** — YouTube video sayfasından açıklama, zaman damgaları, beğeni/izlenme sayısı. Transkript olmadığında en iyi alternatif.
5. **Kanal ID keşfi** — Browser console ile
1. RSS feed: `https://www.youtube.com/feeds/videos.xml?channel_id=UC...` → son 15 video
2. Transcript: `YouTubeTranscriptApi().fetch(video_id, languages=['tr'])` → altyazılar

### Hata Yönetimi
- web_extract başarısız olursa (timeout/hata): diğer kaynaklarla devam et, eksik kaynağı atla
- web_search başarısız olursa: kalan sorgularla devam et
- Tüm kaynaklar başarısız olursa: "Bugün dikkat çeken ekonomi haberi bulunamadı" mesajı gönder, boş bülten gönderme
- Haftasonu/resmi tatil: "Bugün piyasalar kapalı" notu düş, bülten gönderme

### Kullanılan Araçlar (enabled_toolsets)
Cron'da: `["web", "terminal", "file", "search"]`
- `web_extract` — BBC Business sayfası için
- `web_search` — Google News sorguları için

---

## 📤 Çıktı Formatı — Bülten Yapısı

### Sabah & Akşam Ayrımı
- Sabah 08:00: 🌅 SABAH BÜLTENİ — Piyasa Öncesi
- Akşam 18:00: 🌆 AKŞAM BÜLTENİ — Gün Sonu

### Bülten Şablonu
```
📈 EKONOMİ ZEKASI — {SABAH/AKŞAM} BÜLTENİ
{DD Month YYYY}

📍 MANŞET
En önemli 1-2 gelişme (max 3 cümle)

📰 HABERLER (max 4-5)
[SEKTÖR] Başlık | 5N1K | Yatırım Gözlüğü | 🟢/🔴/⚪ | Beklenti

🐝 KRİPTO DROP & BİRİKİM FIRSATLARI
@BitcoinArisi verisinden en önemli 1-2 fırsat

📊 MAKRO PANEL
BIST100, USD/TRY, Altın, Bitcoin, vd.

🎯 ÖNE ÇIKAN FIRSAT/RİSK
⚠️ Yatırım tavsiyesi değildir.
```

### Telegram Format Kuralları
- Kısa ve okunabilir: her haber için max 4 satır
- Emoji kullan: 📈 📋 🎯 ⚡ 🔮 📊 🟢 🔴 ⚪
- Tablo kullanma (Telegram tablo desteği yok)
- Uzun analizlerden kaçın, aksiyon odaklı ol
- Her bültenin sonuna "⚠️ Yatırım tavsiyesi değildir" ibaresi

---

## 🎯 Kanıtlanmış Strateji Önceliği

**Kural:** Sıfırdan strateji yazıp test etme. Önce internette işe yaradığı kanıtlanmış stratejileri araştır. Var olan bilgiyi geliştir, yeniden icat etme.

### Araştırma Sırası (3 Seviye)
1. **Web'de kanıtlanmış strateji ara** — Backtest sonucu paylaşılmış, buy & hold'u geçen, aracı kurum raporu olan stratejiler
2. **Kaynak çeşitliliği sağla** — Sadece web araması değil, her kaynağı kullan:
   - YouTube kanalları (Türk ve yabancı yatırımcılar)
   - Ekonomi gazeteleri (Dünya, Bloomberg HT)
   - TV kanalları (Bloomberg HT yayınları, ekonomi programları)
   - Aracı kurum raporları (İş Yatırım, Ak Yatırım, QNB Invest)
   - Akademik makaleler (backtest metodolojileri)
   - Reddit / TradingView toplulukları (kullanıcı backtest sonuçları)
3. **Karşılaştırmalı analiz** — 3+ farklı kaynaktan teyit et, sonra test et

### Strateji Geliştirme Döngüsü
```
Araştır (kanıtlanmış strateji bul) → Backtest (geçmiş veri) → 
Optimize et (parametre ince ayarı) → Paper Trading (canlı sanal) → 
Gerçek İşlem (sadece başarılı olursa)
```

### Hatalar (Yapılmayacaklar)
- ❌ "Kendi stratejimi yazayım, bakarız" — önce var olanı bul, geliştir
- ❌ Tek kaynağa güvenme — 3+ kaynaktan teyit et
- ❌ Backtest sonucu olmayan stratejiyi canlıya alma
- ❌ Kaldıraçlı işlemde günlük işlem sayısını sınırlama — maks 3-5 işlem/gün
- ❌ Küçük bütçeyle yüksek kaldıraç kullanma

### Örnek: Bu Oturumda Uygulanan
1. Kripto için MA+RSI+ADX kanıtlanmış strateji araştırıldı → bulunamadı → alternatif yaklaşımlar
2. Forex broker SPK lisanslı araştırıldı → 50K TL engeli keşfedildi
3. BIST DCA için aracı kurum raporları tarandı → İş Yatırım, QNB Invest, GCM Yatırım raporları
4. YouTube kanalları araştırıldı → ForInvest, Kanal Finans, Devrim Akyıl
5. ASELSAN için 3 farklı hedef fiyat karşılaştırıldı (İş Yatırım, TradingView, USC Markets)

### Uyarı
Backtest sonucu iyi çıkan her strateji canlı piyasada çalışmayabilir. Piyasa koşulları değişir, backtest overfitting riski taşır. Her zaman **margin of safety** bırak.

---

## 🎮 Simülasyon Katmanı

### Araçlar (Kurulu ve Çalışıyor)
| Araç | Kullanım | Durum |
|------|----------|-------|
| `kaldirac-simulator.py` | Kaldıraçlı işlem backtest + strateji karşılaştırma | ✅ 1 Tem |
| `paper-trading.py` | Paper trading motoru (canlı sinyal + pozisyon yönetimi) | ✅ 1 Tem |
| `borsa-simulasyonu.py` | BIST hisse portföy takip + teknik analiz | ✅ 1 Tem |
| `bist-takip.py` | Günlük BIST endeks + portföy özeti | ✅ 1 Tem |
| `coin-listesi.py` | CoinGecko ile 250 coin güncel liste | ✅ 1 Tem |
| `gunluk-strateji.py` | Günlük kazanç stratejisi testi | ✅ 1 Tem |
| `yfinance` | Yahoo Finance veri kaynağı | ✅ |
| `backtrader` | Python backtesting framework | ✅ |

### ⚠️ 3 Katmanlı Doğrulama Pipeline'ı
```
Backtest (geçmiş veri) → Paper Trading (canlı sanal) → Gerçek İşlem
```
- Backtest'te kanıtlanmamış strateji paper trading'e geçmez
- Paper trading'de pozitif K/Z kanıtlanmadan gerçek işleme geçilmez
- Detaylı metodoloji: `references/backtest-metodolojisi.md` (kripto-teknik-analiz skill'inde)

### 🚀 Paper Trading (Canlı)
**Script:** `~/.hermes/scripts/paper-trading.py`
**Cron:** Her saat başı (`8082276086de`)
**Sermaye:** $500 sanal | **Kaldıraç:** x5 | **Strateji:** Breakout + BTC Trend Filtre
**⚠️ Uyarı:** Saat başı cron aşırı işleme sebep olur (günde ~37 işlem — 5 günde 185). Kaldıraçlı işlemde günlük işlem sayısı 3-5 ile sınırlandırılmalıdır. Düşük win rate değil, aşırı frekans portföyü bitirir. Detay: `references/paper-trading-1-hafta-testi.md`

Kullanım:
```bash
# Portföy durumu
python3 ~/.hermes/scripts/paper-trading.py --status

# Geçmiş backtest (ör: 1 Ocak'tan bugüne SOL)
python3 ~/.hermes/scripts/paper-trading.py --backtest 2026-01-01 --coin SOL --sermaye 500

# Sıfırla
python3 ~/.hermes/scripts/paper-trading.py --reset
```

### 🏛️ BIST Hisse Portföy Yönetimi (TL Bazlı)
**Script:** `~/.hermes/scripts/borsa-simulasyonu.py`
**Veri:** `~/.hermes/data/borsa/portfoy.json`

```bash
# Hisse ekle
python3 ~/.hermes/scripts/borsa-simulasyonu.py --hisse KCAER --adet 245 --alis 14.625

# Teknik analiz (kripto-teknik-analiz formatında)
python3 ~/.hermes/scripts/borsa-simulasyonu.py --hisse KCAER --analiz

# Portföy durumu
python3 ~/.hermes/scripts/borsa-simulasyonu.py --portfoy

# Günlük BIST takip (no_agent cron, 10:00)
python3 ~/.hermes/scripts/bist-takip.py
```

**Desteklenen hisseler:** KCAER, THYAO, EREGL, AKBNK, GARAN, ISCTR, ASELS, SASA, KCHOL, TUPRS, KOZAL, BIMAS, FROTO, PETKM, TCELL, SAHOL, YKBNK, HALKB (`.IS` suffix ile yfinance).

### 🎯 Kaldıraçlı İşlem Backtest
```bash
# Tek backtest
python3 ~/.hermes/scripts/kaldirac-simulator.py --coin XRP-USD --baslangic 500 --kaldırac 5

# Strateji + kaldıraç karşılaştırma
python3 ~/.hermes/scripts/kaldirac-simulator.py --coin BTC-USD --karsilastir

# Toplu coin testi
python3 ~/.hermes/scripts/kaldirac-simulator.py --hedef-coinler XRP,SOL,ADA,DOGE --baslangic 500 --kaldırac 5 --gun 180
```

### Optimum Parametreler (1 Tem 2026 Backtest)
| Parametre | Değer | Not |
|-----------|-------|-----|
| Kaldıraç | x3-x5 | x10'da drawdown 2×, x20'de likitasyon riski çok yüksek |
| Stop-loss | ATR(14) × 1.5 (min %2) | Sabit %3 volatil coinlerde çok dar |
| Take-profit | SL × 2.5 | Risk:Ödül oranı 1:2.5 |
| Max eşzamanlı pozisyon | 3 | Daha fazlası riski dağıtır ama kontrolü zorlaştırır |
| Minimum bütçe (gerçek) | $80 | $50'da komisyon oranı çok büyük |

---

## 🤖 Ekonomi Cron'ları Referansı

### ⏰ Ekonomi Zekası Bülteni
**Job ID:** `3acdcd93e3b7`
**Zamanlama:** `0 8,18 * * 1-5` (günde 2 kere, haftaiçi)
**Skills:** financial-intelligence, sohbet, kripto-teknik-analiz
**Model:** deepseek-v4-flash-free @ opencode-zen
**Deliver:** Home kanalı

### 🐝 Bitcoin Arısı Tarama
**Job ID:** `9d515802f2b2` | **Zaman:** 09:00 | **no_agent**

### 🪙 Coin Listesi Güncelleme
**Job ID:** `67f6794f67f7` | **Zaman:** 07:00 | **no_agent**

### 📡 Paper Trading Kontrol
**Job ID:** `8082276086de` | **Zaman:** Her saat başı | **no_agent**

### 📈 BIST Günlük Takip
**Job ID:** `951b4536ee4f` | **Zaman:** 10:00 (haftaiçi) | **no_agent**

### 🎯 1 Haftalık Test Raporu
**Job ID:** `9c1b114d1771` | **Zaman:** 8 Temmuz 12:00 (one-shot)

Detaylı cron prompt'u için: `references/ekonomi-cron-prompt-working.md`

---

## ⚠️ Önemli Uyarılar
- **Yatırım tavsiyesi değildir:** Vanitas bir AI asistanıdır, lisanslı yatırım danışmanı değil.
- **Veri gecikmesi:** Haber kaynakları ve fiyat verileri real-time olmayabilir.
- **Backtest ≠ Gelecek:** Geçmiş veri simülasyonu gelecekteki performansı garanti etmez.
- **Hata toleransı:** Veri kaynağı başarısız olursa diğer kaynaklarla devam et.
- **Takvim bilinci:** Haftasonu ve resmi tatillerde piyasalar kapalıdır — bülten atlama.

## 🛡 Risk Yönetimi Parametreleri
| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| Maks eşzamanlı pozisyon | 3-5 | Aynı anda açık olabilecek max pozisyon sayısı |
| Maks günlük işlem | 3-5 | Kaldıraçlı işlemde günde max 3-5 pozisyon açılır (1. hafta testi: 37 işlem/gün → %95 kayıp) |
| Stop-loss (kripto) | ATR(14) × 1.5 | Volatiliteye göre dinamik |
| Maks günlük kayıp | Portföyün %3'ü | Günlük kayıp limiti aşılırsa trading durur |
| Min Margin of Safety | %25 | Buffett standardı |
| Min ROE | %15 | Buffett standardı |
| Max D/E | 0.5 | Buffett standardı |
| Kaldıraç (kripto) | x3-x5 | x10 max, x20 önerilmez |

---

## 📁 Referanslar
- `references/buffett-12-tenets.md` — Buffett'ın 12 kriteri ve kullanımı detaylı
- `references/ekonomi-cron-mimarisi.md` — Cron yapılandırması ve pipeline tasarımı
- `references/ekonomi-cron-prompt-working.md` — Çalışan cron prompt'unun tam metni
- `references/youtube-ekonomi-kanallari.md` — Takip edilen YouTube kanalları ve kanal ID'leri
- `references/turkish-market-data-sources.md` — Bloomberg HT vs yfinance veri kaynakları karşılaştırması
- `references/turkiye-bist-dca.md` — Türkiye BIST DCA stratejisi, SPK düzenlemeleri, küçük bütçeyle portföy planlaması (Temmuz 2026)
- `references/telegram-kanali-veri-kaynagi.md` — Telegram kanalı scrape edip Ekonomi Zekası'na veri kaynağı olarak ekleme
- `references/kaldirac-simulasyonu.md` — Kaldıraçlı işlem simülasyonu backtest sonuçları
- `references/paper-trading-1-hafta-testi.md` — Paper trading 1. hafta test sonuçları ve dersler (6 Tem 2026)
- `references/bist-portfoy-yonetimi.md` — BIST hisse portföy takip ve teknik analiz
- **Detaylı backtest ve strateji metodolojisi:** `kripto-teknik-analiz` skill'indeki `references/backtest-metodolojisi.md`

## 📜 Scriptler (~/.hermes/scripts/)
| Script | İşlev | Durum |
|--------|-------|-------|
| `makro_veri.py` | 21 varlık canlı veri | ✅ |
| `bitcoin-arisi-tarayici.py` | @BitcoinArisi scrape + birikim fikirleri | ✅ 1 Tem |
| `kaldirac-simulator.py` | Kaldıraçlı işlem backtest + strateji karşılaştırma | ✅ 1 Tem |
| `coin-listesi.py` | CoinGecko ile 250 coin güncel liste | ✅ 1 Tem |
| `paper-trading.py` | Paper trading motoru (canlı) | ✅ 1 Tem |
| `borsa-simulasyonu.py` | BIST hisse portföy + teknik analiz | ✅ 1 Tem |
| `bist-takip.py` | Günlük BIST endeks + portföy özeti | ✅ 1 Tem |
| `gunluk-strateji.py` | Günlük kazanç stratejisi testi | ✅ 1 Tem |
| `youtube_tarama.py` | 5 YouTube kanalı RSS + transcript | ✅ |
| `buffett_stratejisi.py` | Backtrader backtest + Buffett filtresi | ✅ |
