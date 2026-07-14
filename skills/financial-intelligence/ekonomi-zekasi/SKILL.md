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

## 🧠 Temel İlkeler

1. **Veri önce gelir:** Yorumlar kişisel fikir değil, güncel veriye dayanır.
2. **Bağlam önemlidir:** Aynı faiz indirimi farklı dönemlerde farklı anlam taşır.
3. **Neden-sonuç zinciri:** "Faiz düştü → bankalar kâr eder → hisse yükselir" gibi
4. **Çoklu senaryo:** Kesin tahmin yok, olasılıklar var.
5. **Güncelleme:** Her hafta veriler tazelenir, yorum güncellenir.

## 🧩 Entegre Edilen — Emrah Altınocağı Analizi (Temmuz 2026)

Videodan ekonomi zekasına entegre edilen prensipler:

### Temel Felsefe
> **"Para değil, varlık biriktir."**
- Enflasyonun kaynağı paradır — parayla enflasyon yenilmez.
- Değer kazanan varlıklar (altın, gümüş, konut, hisse, RWA tokenleri) uzun vadede kazandırır.
- "Yatırım sabun gibidir; dokundukça erir" — sık al-sat yapma, sabret.

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
- Para Dergi — analiz ve yorum
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
