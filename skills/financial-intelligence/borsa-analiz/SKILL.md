---
name: borsa-analiz
description: "BIST hisseleri için analiz sistemi — teknik + temel + makro verileri birleştirerek portföy önerileri ve DCA stratejisi üretir"
version: 1.0.0
metadata:
  hermes:
    tags: [borsa, bist, hisse, analiz, dca, turkiye]
    category: financial-intelligence
---

# Borsa Analiz Sistemi

## Amaç
Edel'in BIST hisselerini analiz etmek, portföy önerileri sunmak ve DCA stratejisini yönetmek.

> **Platform:** Edel İş Bankası üzerinden hisse alım-satımı yapar. Aracı kurum araştırması gereksizdir. Doğrudan İş Bankası mobil/web uygulaması üzerinden işlem yapılır.

## 🔍 Analiz Katmanları

### 1. Makro Katmanı (Her hafta güncellenir)
- **TCMB faiz oranı:** Güncel politika faizi ve değişim trendi
- **Enflasyon:** TÜFE/ÜFE aylık ve yıllık veriler
- **USD/TRY kuru:** Güncel seviye ve beklentiler
- **BIST 100 endeksi:** Güncel seviye, haftalık/aylık/yıllık değişim
- **Kaynaklar:** TCMB, TÜİK, Bloomberg HT, Para Dergi

### 2. Sektör Katmanı (Her hafta taranır)
Takip edilen sektörler:
- **Savunma Sanayi:** ASELS, ALTNY, SDT
- **Bankacılık:** ISCTR, GARAN, ENPRA, AKBNK
- **Demir-Çelik:** KOCER, EREGL, KRDMD
- **İnşaat:** (faiz indirimi dönemlerinde öne çıkar)

Sektör analizinde:
- Sektördeki son gelişmeler
- Faiz indiriminin sektöre etkisi
- Küresel emtia fiyatları (demir-çelik için)
- Devlet teşvikleri ve politikalar

### 3. Hisse Katmanı (Her analizde)
Her hisse için:
- **Teknik:** TradingView grafiği, destek/direnç seviyeleri, hacim
- **Temel:** F/K, PD/DD, FD/FAVÖK, özsermaye karlılığı
- **Aracı Kurum Raporları:** İş Yatırım, Ak Yatırım, Ata Yatırım hedef fiyatları
- **YZ Analizleri:** USC Markets, Fintables hedef fiyatları

### 4. Portföy Katmanı (Her hafta güncellenir)
- Mevcut pozisyonlar (hisse, adet, maliyet, güncel fiyat, kar/zarar)
- Portföy dağılımı (sektör bazında)
- DCA planı (ne zaman, hangi hisse, ne kadar)
- Fırsat kolayı (düşüşlerde ek alım sinyalleri)

## 🛠️ Analiz Adımları

1. **Makro kontrol:** TCMB kararı var mı? Enflasyon verisi geldi mi?
2. **Sektör tarama:** Takip edilen sektörlerde son haberler, hisse hareketleri
3. **Hisse seçimi:** DCA için uygun fiyat seviyeleri
4. **Portföy raporu:** Güncel durum, kar/zarar, öneriler
5. **DCA planı:** Aylık alım miktarı, hisse dağılımı, nakit oranı

### Hisse Pozisyonu Değerlendirme Metodu

Mevcut bir pozisyon değerlendirilirken:
1. **Güncel zarar/kâr:** (Güncel fiyat - Maliyet) × Adet
2. **Aracı kurum hedef fiyat karşılaştırması:** En az 3 kaynaktan hedef fiyat topla (İş Yatırım, Fintables ortalama, TradingView/YZ analizi)
3. **Ortalama hedef fiyat:** Tüm kaynakların ortalaması → potansiyel getiri
4. **Temel değerleme:** F/K, PD/DD oranlarını sektör ortalamalarıyla karşılaştır
5. **Makro etki:** Faiz indirimi/döviz/seçim ekonomisi pozisyonu nasıl etkiler?
6. **Karar:** Bekle / ek alım yap / çık (panik satışı önerilmez — DCA mantığı)

**KOCER vaka çalışması — gerçek pozisyon:**
- Maliyet: 14.625 TL | Güncel: 13.39 TL | Zarar: ~%8.4 (~302 TL)
- Hedef fiyatlar: İş Yatırım 18.83, Fintables 20.11, YZ 19.70
- F/K: 90.76 (yüksek — değerleme riski)
- Karar: Bekle (panik satışı yapma, tüm aracı kurum hedefleri pozitif)

### DCA Stratejisi — Türkiye İçin

**Platform:** Edel İş Bankası üzerinden hisse alır. Yeni aracı kurum gerekmez.

**Portföy dağılımı önerisi (Temmuz 2026):**
- %50 Savunma (ASELS ~370 TL, hedef 450 TL, %25 potansiyel)
- %30 Bankacılık (ISCTR ~14 TL, faiz indiriminden beslenir)
- %20 Nakit (sert düşüşlerde fırsat kolayı)

**Aylık DCA takvimi (2000-3500 TL bütçe):**
- Ayın 1'i: 1 adet ASELS + 100 adet ISCTR (~1.770 TL)
- Ayın 15'i: kalan bütçeyle ek alım
- Sert düşüş günlerinde nakit havuzundan ek alım
- En az 12 ay devam, süreklilik kâr etmekten önemli

## 📖 Kaynak Kütüphanesi

### Veri Kaynakları
- `investing.com` — hisse fiyatları, endeksler, makro veriler
- `tradingview.com` — teknik görünüm, topluluk beklentileri
- `isyerim.com.tr` — İş Yatırım analiz raporları
- `fintables.com` — aracı kurum hedef fiyat ortalamaları
- `atayatirim.com.tr` — hisse analiz sayfaları
- `gcmyatirim.com.tr` — sektör analiz makaleleri

### Haber Kaynakları
- Bloomberg HT
- Para Dergi
- Ekonomi Ekranı (YouTube)
- ForInvest (YouTube)
- Kanal Finans (YouTube)

### Aracı Kurum
- Edel hisseleri **İş Bankası** üzerinden alıp satıyor. Yeni bir aracı kurum araştırmasına gerek yok.

### SPK Forex Engeli (Önemli)
Türkiye'de SPK düzenlemesi: forex için minimum 50.000 TL teminat, maksimum 10:1 kaldıraç, zorunlu 6 gün/50 işlem demo. Edel'in 10.000 TL bütçesi bu şartı karşılamaz. Forex canlı hesap şimdilik **rafa kalktı**.

## ⚠️ Uyarılar
- Aracı kurum hedef fiyatları tavsiye değildir, referanstır.
- F/K oranı yüksek hisselerde (ör. 90+) değerleme riski yüksektir.
- Her yatırım kararı Edel'in onayına sunulur, otomatik işlem yapılmaz.
- Kısa vadeli dalgalanmalarda panik satışı yapılmaz — DCA mantığıyla hareket edilir.

## 📊 Rapor Formatı

Her hafta:
```
📅 [Tarih] — BIST Haftalık Durum
────────────────────────────
📌 Makro: Faiz %, Enflasyon %, Dolar/TL
📌 BIST 100: ... puan (haftalık %...)
📌 Sektör: ... önde, ... geride

📂 Portföy
Hisse | Adet | Maliyet | Güncel | K/Z
───── | ──── | ─────── | ────── | ───
...   | ...  | ...     | ...    | ...

📋 DCA Planı
- Ayın 1'i: ... TL ... hisse
- Ayın 15'i: ... TL ... hisse
- Nakit havuzu: ... TL
```
