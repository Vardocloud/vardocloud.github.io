---
name: ekonomi-zekasi
description: "Makroekonomik analiz ve yorumlama sistemi — TCMB, enflasyon, döviz, faiz ve seçim ekonomisini birleştirerek stratejik öngörü üretir"
version: 1.0.0
metadata:
  hermes:
    tags: [ekonomi, makro, faiz, enflasyon, tcmb, döviz, analiz]
    category: financial-intelligence
---

# Ekonomi Zekası

## Amaç
Türkiye ve küresel makroekonomik verileri analiz ederek BIST ve kripto stratejilerine yön vermek.

> ⚠️ **KRİTİK: "Ekonomi zekası" sadece cron/otomasyon değildir.** Edel'in tanımıyla: veri toplamak yetmez, anlık analiz yapıp yorumlayabilmek gerekir. Cron sadece veri toplama aracıdır; asıl zeka, soru geldiğinde veriyi bağlama oturtup yorumlamaktır. Her analiz talebinde bu skill yüklenir ve güncel verilerle anlık sentez yapılır.

## Edel'in Beklentileri
- Kanıtlanmış stratejileri araştır, sıfırdan icat etme
- Direkt sonuç getir, ara bildirimlerle zaman kaybetme
- Türkiye şartlarını (enflasyon, faiz, döviz, SPK düzenlemeleri) her zaman hesaba kat
- "Duruma göre değişir" yerine net yorum yap
- **İçerik analizinde önce TAMAMINI oku/izle, sonra yorum yap.** Parça bilgiyle çıkarım yapma — Edel eksik/aceleci özetten rahatsız olur. Bir video/makale/rapor analiz edilecekse önce kaynağın tamamına eriş, sonra sentezle.

## 🧠 Temel İlkeler

1. **Veri önce gelir:** Yorumlar kişisel fikir değil, güncel veriye dayanır.
2. **Bağlam önemlidir:** Aynı faiz indirimi farklı dönemlerde farklı anlam taşır.
3. **Neden-sonuç zinciri:** "Faiz düştü → bankalar kâr eder → hisse yükselir" gibi
4. **Çoklu senaryo:** Kesin tahmin yok, olasılıklar var.
5. **Güncelleme:** Her hafta veriler tazelenir, yorum güncellenir.

## 🤖 Model Seçimi — Türkçe Ekonomi İçin

Edel'in uyarısı: Ekonomi analizi Türkçe kavram hassasiyeti gerektirir (enflasyon, faiz, cari açık, portföy dengesi). Tüm modeller bu konuda eşit başarılı değildir.

**NVIDIA üzerinden kullanılan modeller:**
- `mistralai/mistral-small-4-119b-2603` — ⭐ **Önerilen** (hızlı ~1sn, Türkçesi iyi, 119B)
- `meta/llama-3.3-70b-instruct` — Türkçesi zayıf, ekonomi kavramlarında hata payı yüksek
- `minimaxai/minimax-m3` — çok yavaş (~139sn), cron limitini aşar

**Kural:** Türkçe ekonomi içeriği üretilecekse Mistral Small 4 kullan. Llama 3.3 sadece İngilizce içerik için uygundur.

**Cron ayarı:** Sabah (08:00) ve Akşam (18:00) bültenleri `nvidia-free-mistral-small` model alias'ı ile NVIDIA üzerinden çalışır. Provider model whitelist'e takılmamak için config.yaml'da `discover_models: false` ve `models:` listesinde model adı bulunmalıdır.

Videodan ekonomi zekasına entegre edilen prensipler:

### Temel Felsefe
> **"Para değil, varlık biriktir."**
- Enflasyonun kaynağı paradır — parayla enflasyon yenilmez.
- Değer kazanan varlıklar (altın, gümüş, konut, hisse, RWA tokenleri) uzun vadede kazandırır.
- "Yatırım sabun gibidir; dokundukça erir" — sık al-sat yapma, sabret.

### 📰 Para Dergisi Analiz Metodolojisi

**Kaynak:** Haftalık ekonomi dergisi, günlük site/X güncellemesi

### Para Dergisi'nin Analiz Çerçevesi

1. **Makro Öncelikli**: Önce büyük resim (faiz, enflasyon, büyüme, jeopolitik), sonra hisse seçimi
2. **Sektör Rotasyonu**: Banka/finans öncülüğünde başlayan yükseliş, sanayi ile genişler
3. **Değerleme Bazlı Seçim**: 23 hisse listesi — temel analiz, spekülasyon değil
4. **Teknik Destek/Direnç**: BIST için net bantlar (12.500-13.000 destek, 15.500-16.000 direnç)
5. **Şirket Bazlı Hedefler**: FAVÖK marjı, gelir beklentisi, 12 aylık hedef fiyat
6. **Küresel Bağlam**: Fed/ECB politikaları, AI bubble vs dot.com karşılaştırması
7. **Halka Arz Analizi**: Büyüklük, talep oranı (bireysel/kurumsal), gelir kullanım planı
8. **Uzun Vadeli Trendler**: Demografi (yaşlanan nüfus, genç nüfus azalışı), HIT-30 teşvikleri

### Para Dergisi'nden Alınan Kilit İçgörüler

- **"Uzun vadede banka ve finans öncülüğü bekleniyor"** — Faiz indirim döngüsünde bankalar ilk kazanan
- **"İmalat sanayinde kapasitenin %60'ı değer üretmiyor"** — Sanayi hisselerinde seçici ol
- **"Dezenflasyon güçlendikçe BIST'te seçici fırsatlar doğar"** — Kısa vadede DİBS/mevduat, uzun vadede hisse
- **"AI balonu dot.com ile kıyaslanıyor ama şirketler daha kârlı"** — ABD teknoloji hisselerinde temkinli iyimserlik
- **"Nüfus yenileme eşiğinin altında (1.42)"** — Uzun vadeli yatırımlar yaşlanan nüfusa göre şekillenecek

### Güncel Piyasa Referansları (Para Dergisi, 16 Temmuz 2026)
- BIST: 14.251 (+%1,22) — Hedef: 19.500-20.000 (2027)
- USD/TRY: 47,05
- EUR/TRY: 53,93
- Faiz: %41,10
- Altın Ons: $3.982
- Sanayi Üretimi: Aylık -%2,9 daralma

### Para Dergisi 23 Hisse Listesi (Uzun Vade)
TSKB, ISCTR, GARAN, ASTOR, SOKM, FROTO, KCHOL, SAHOL, MAVI, TURSG, ULKER, TAVHL, CIMSA, ARCLK, TUPRS, MPARK, MGROS, DOAS, TCELL, TOASO, PGSUS, THYAO, SISE

### 3 Katmanlı Hisse Filtresi (Para Dergisi Metodolojisi)
1. **Geniş Liste (50-69 hisse):** Tüm sektörler — aylık güncelleme
2. **Orta Liste (23 hisse):** Uzman mutabakatı — 2-3 ayda bir
3. **Dar Liste (5-15 hisse):** En yüksek potansiyel — sektör bazlı

Seçim kriterleri: FAVÖK marjı, ROE, PD/DD iskontosu, döviz geliri, bilanço sağlığı

### Sektör Rotasyonu Modeli (Para Dergisi Çerçevesi)
1. **Banka/Finans** → Faiz indirimi başlangıcında ilk kazanan
2. **Sanayi/Holding** → Büyüme beklentileriyle genişler
3. **Perakende/Gıda** → Tüketici güveniyle canlanır
4. **Savunma** → Devlet teşvikiyle bağımsız büyür (HIT-30)
5. **GYO** → Faiz düşüşüyle kredi erişimi artar

### Para Dergisi'nden Alınan Dersler (Desen Analizi)
**Instagram kapak temaları (2024-2026):**
- "23 HİSSE" / "TEMETTÜ 20 HİSSE" — periyodik liste güncellemesi
- "Ev mi arsa mı?", "Kapışılan köyler" — gayrimenkul trend takibi
- "Endeks gerilerken girilir mi?" — borsa psikolojisi yönetimi
- "Borsada kazanma mevsimi Temmuz-Ağustos" — mevsimsel strateji

**Trend değişimleri:** 2024 gayrimenkul → 2025 hisse → 2026 jeopolitik fırsatçılık

### Uzman Konsensüsü (En Çok Önerilen Hisseler)
ASELS, ASTOR, BIMAS, FROTO, GARAN, ISCTR, KCHOL, MAVI, MGROS, MPARK, PGSUS, SAHOL, TAVHL, TCELL, THYAO, TSKB, TUPRS

## 🌞 Mevsimsel Analiz Çerçevesi

### Temmuz-Ağustos "Kazanma Sezonu"
Para Dergisi'nin yıllık desen tespiti: Her yıl Temmuz-Ağustos aylarında bazı sektörler düzenli olarak prim yapar.

| Sektör | Neden | Örnek Hisse |
|--------|-------|-------------|
| **Turizm** | Yaz sezonu, döviz girişi, 9 aylık bilanço beklentisi | THYAO, PGSUS, TAVHL |
| **Havacılık** | Okullar kapandı, tatil trafiği zirve | THYAO, PGSUS |
| **Enerji** | Sıcaklar, klima kullanımı, elektrik tüketimi patlaması | ASTOR, AKSA |
| **Perakende/Gıda** | Bayram + tatil harcamaları | BIMAS, MGROS, SOKM |
| **Sigorta** | Yaz tatili öncesi artan talep | TURSG, ANSGR |

**Önemli uyarı:** Geçmiş veridir, garanti değildir. Global konjonktür (savaş, kriz, faiz kararı) her an her mevsimsel deseni geçersiz kılabilir.

### Sektörel Dönemsel Desenler (Uzun Vadeli Gözlem)
| Sektör | Güçlü Dönem | Katalizör |
|--------|-------------|-----------|
| Holding | Bilanço dönemleri (3-6-9-12 ay) | Öz sermaye kârlılığı artışı |
| Spor | Sezon başı ve sonu | Transfer, şampiyonluk beklentisi |
| Havacılık | Ekim-Kasım (9 aylık bilanço) | Yaz satış hacminin bilançoya yansıması |
| Yazılım/Teknoloji | Global buluş/haber sonrası | ABD teknoloji trendleri |
| Otomotiv | Aralık-Mart | Yeni model yılı, yılbaşı satışları, iskontolar |

### Kullanım Kuralı
Bir yatırım sorusu geldiğinde:
1. Şu an hangi aydayız? Mevsimsel desen bu dönemi kapsıyor mu?
2. Global bir istisna var mı? (savaş, pandemi, seçim)
3. Cevabı "dönemsel fırsat" olarak sun, "kesin kazanç" olarak değil.

## 💰 Küçük Portföy Analiz Çerçevesi (Edel İçin)

### 10.000 TL ile Yatırım Senaryosu
Edel'in mevcut durumu: 10.000 TL nakit, günlük faizde ~8 TL/gün (240 TL/ay), düzenli gelir yok.

**Risk/Getiri Tablosu (2 aylık dönem):**
| Senaryo | Olasılık | 10.000 TL'ye Etkisi |
|---------|----------|---------------------|
| Çok iyi (%15-20 kâr) | Düşük | +1.500-2.000 TL |
| İyi (%10 kâr) | Orta | +1.000 TL |
| Ortalama (%5 kâr) | Orta | +500 TL |
| Kötü (%5-10 zarar) | Orta | -500-1.000 TL |
| Çok kötü (%10+ zarar) | Düşük | -1.000+ TL |

**Altın Kural:** "Kazanma sezonu" olsa bile, birikimin tamamıyla trade yapılmaz. Acil durum fonu HİÇBİR ZAMAN hisseye bağlanmaz.

### Karar Çerçevesi
- **Düzenli gelir VARSA** → Maaşın bir kısmıyla mevsimsel fırsat değerlendirilebilir
- **Düzenli gelir YOKSA** → Acil durum fonu korunur, sadece takip edilir
- **Para acil ihtiyaç için duruyorsa** → Günlük faizde kalması en doğrusu
- **Para kaybedilirse hayat etkileniyorsa** → Asla girme

### Kritik Dar Gelirli İçin Bölüm
Video **düzenli geliri olan** (maaşlı) kişi için yazılmıştır. Edel'in durumu (düzenli gelirsiz, ara sıra baba gönderimi) farklıdır:

| Video'daki Varsayım | Edel'in Gerçeği | Uyarlama |
|---------------------|-----------------|----------|
| Düzenli maaş var | Yok, baba ara sıra gönderir | Acil durum fonu öncelikli |
| Maaşın 2/3'ü yatırıma | Tek seferlik 10.000 TL | Nakit akışı planlaması şart |
| Kredi çekip kaldıraç kullan | Kredi notu/gelir yok | Kaldıraçsız, temkinli |
| 2 yılda ev sahibi olmak | Önce eğitim (PTE, üniversite) | "Kendine yatırım" aşaması |

### Entegre Edilen 5 Kural (Uyarlanmış)

1. **Küçük başla:** 10.000 TL'nin tamamını yatırma — önce yaşam akışını güvence altına al
2. **Değer kaybedeni bırak:** Nakit TL'de uzun süre bekleme — ama acil durum fonu olarak nakit şart
3. **Ek geliri değerlendir:** Baban gönderdiğinde veya bir gelir olduğunda, hepsini harcama — bir kısmını yatır
4. **Trendi takip et:** 2024-2028 değerli metaller + RWA — portföyde küçük bir altın/Gümüş fonu düşünülebilir
5. **Trade etme:** Panik satışı yok, DCA ile devam

### Uyarı Entegrasyonu
- **"Yolu kısaltmaya çalışırken yoldan çıkmak"** — forex, kaldıraç, kriptoda trade tuzağı. 10.000 TL ile asla girme.
- **"Yatırım yapacak gücün yoksa kendine yatırım yap"** — Edel için: PTE sınavı, üniversite başvuruları, İngilizce, mesleki gelişim. Bunlar en yüksek getirili yatırımlardır.

## 📊 Takip Edilen Göstergeler

### Türkiye (Haftalık)
| Gösterge | Kaynak | Frekans |
|----------|--------|---------|
| Politika Faizi | TCMB | Aylık (PPK toplantıları) |
| TÜFE/ÜFE | TÜİK | Aylık |
| USD/TRY | TCMB/Merkez | Anlık |
| BIST 100 | BIST | Anlık |
| 5Y CDS | Bloomberg | Anlık |
| Kredi Notu | Moody's/S&P/Fitch | Dönemsel |
| İşsizlik | TÜİK | Aylık |
| Cari Açık | TCMB | Aylık |

### Küresel (Haftalık)
| Gösterge | Kaynak | Frekans |
|----------|--------|---------|
| Fed Faizi | Fed | Dönemsel |
| ECB Faizi | ECB | Dönemsel |
| DXY (Dolar Endeksi) | Bloomberg | Anlık |
| Emtia (Petrol, Altın) | Bloomberg | Anlık |
| VIX (Korku Endeksi) | CBOE | Anlık |

## 🔄 Analiz Akışı

### 1. Veri Toplama (Haftalık cron)
- TCMB kararı geldi mi? → Analiz et
- TÜİK verisi geldi mi? → Analiz et
- ABD verileri (FOMC, CPI, NFP) → Etki analizi
- CDS ve kredi notu değişimi → Risk analizi

### 2. Sentez (Her analizde)
- Verileri birbirine bağla: "Faiz indirimi + enflasyon düşüşü = pozitif"
- Döviz etkisini hesapla: "TL değer kaybı ihracatçıyı besler"
- Sektörel etki dağılımı çıkar

### 3. Stratejik Yorum
- Kısa vadeli (1 ay): Hızlı etkilenecek hisseler
- Orta vadeli (3-6 ay): Trend değişimleri
- Uzun vadeli (1 yıl+): Yapısal dönüşümler

### 4. Portföy Uyarlama
- Bulguları borsa-analiz ve kripto-analiz skill'lerine aktar
- DCA planını güncelle (sektör ağırlıkları, nakit oranı)

## 🎯 Kullanım Kalıpları

### "Bu faiz kararı ne anlama geliyor?"
1. Mevcut faiz seviyesini tespit et (örn: %37)
2. Beklenti neydi? Gerçekleşen ne? (sürpriz mi?)
3. Enflasyonla ilişkisini kur (reel faiz pozitif/negatif?)
4. Dolar/TL'ye etkisini tahmin et
5. Hangi sektörler kazanır/kaybeder?
6. Kısa-orta-uzun vadeli portföy etkisi

### "Seçim ekonomisi yaklaşıyor, ne yapmalıyız?"
1. Kalan süre: 2028 seçimlerine ~1.5 yıl
2. Tipik genişleme politikalarını tanımla (vergide indirim, teşvikler, kamu harcaması)
3. Kazanan sektörleri belirle (inşaat, savunma, perakende)
4. Riski yönet (seçim öncesi volatilite artışı)

### "Dolar 46 olmuş, bu ne demek?"
1. Reel kur endeksine bak (TL aşırı değerli mi?)
2. TCMB rezervlerine bak (swap hariç net rezerv)
3. İhracatçı şirketlere etkisi
4. Enflasyon üzerinden ikinci tur etki
5. Portföyde döviz geliri yüksek şirketler

## Sektörel Faiz İndirimi Etkileri

Temmuz 2026 itibarıyla TCMB politika faizi %37. 2026'da 8 toplantıda ~1000 baz puan indirim bekleniyor. [kaynak: QNB Invest, Bloomberg HT, BBC Türkçe]

**Faiz indiriminden en çok etkilenen sektörler:**
- **Bankacılık:** Kredi büyümesi artar, fonlama maliyeti düşer. BIST'te banka hisseleri öncülüğünde yükseliş beklenir.
- **İnşaat/Demir-Çelik:** Düşük faiz → krediye erişim kolaylaşır → inşaat talebi artar
- **Perakende:** Tüketici güveni artar, harcama canlanır
- **Savunma Sanayi:** Faiz indiriminden bağımsız, devlet desteği ve küresel trendlerle büyür

### Türkiye DCA Portföy Dağılımı (Temmuz 2026)

**Bütçe:** 10.000 TL nakit, aylık 2000-3500 TL ekleme

| Hisse | Sektör | Fiyat | Pay | Gerekçe |
|-------|--------|-------|-----|---------|
| ASELS | Savunma | ~370 TL | %50 | İş Yatırım hedef 450 TL (%25↑) |
| ISCTR | Bankacılık | ~14 TL | %30 | Faiz indirimi + düşük giriş |
| Nakit | — | — | %20 | Düşüşlerde fırsat kolayı |

**DCA takvimi:** Ayın 1'i ve 15'i olmak üzere ayda 2 alım.

### SPK Düzenlemeleri (Sabit Referans)
- Forex min. teminat: 50.000 TL
- Maks. kaldıraç: 10:1
- Zorunlu demo: 6 gün / 50 işlem
- Stopaj: 3 aylık net kâr %10
- Kaynak: SPK, Investing.com Türkiye

### Kurumsal Kaynaklar
- TCMB (PPK karar metinleri, enflasyon raporu)
- TÜİK (enflasyon, büyüme, işsizlik)
- SPK (aracı kurum listesi, düzenlemeler)
- BDDK (bankacılık düzenlemeleri)

### Medya & Analiz
- Bloomberg HT — canlı piyasa yayını
- **Para Dergi** — analiz ve yorum (günlük cron taraması aktif, detay: `references/para-dergisi-monitoring.md`)
- BBC Türkçe — ekonomi haberleri
- Ekonomi Ekranı (YouTube) — piyasa yorumları
- ForInvest (YouTube) — günlük borsa analizi
- Kanal Finans (YouTube) — hisse yorumları

### Aracı Kurum Raporları
- İş Yatırım — günlük bülten + hisse raporları
- Ak Yatırım — model portföy + strateji raporları
- QNB Invest — makro analiz
- Şeker Yatırım — strateji raporları
- Garanti BBVA Yatırım — piyasa stratejisi

## ⚠️ Sınırlamalar
- Makroekonomik tahminler kesin değildir, olasılıktır.
- Siyasi gelişmeler (sürpriz seçim, kriz) tüm senaryoları geçersiz kılabilir.
- Küresel gelişmeler (savaş, pandemi) yerel analizi baskılar.
- "Piyasa daha uzun süre irrasyonel kalabilir" — Keynes.
