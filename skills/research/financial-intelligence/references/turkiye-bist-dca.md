# Türkiye BIST DCA ve Yatırım Stratejisi

> Türkiye'de küçük bütçeyle uzun vadeli yatırım rehberi. SPK düzenlemeleri, DCA stratejisi, sektör analizi ve pozisyon yönetimi.
>
> Kaynak: Temmuz 2026 oturumu — Edel'in portföy planlaması

---

## 1. SPK Düzenlemeleri — Forex Kısıtları

| Madde | Değer | Kaynak |
|-------|-------|--------|
| **Forex min. teminat** | 50.000 TL | SPK / Investing.com Türkiye |
| **Forex max kaldıraç** | 10:1 | SPK regülasyonu |
| **Forex stopaj (vergi)** | %10 (3 aylık net kar üzerinden) | SPK |
| **Forex demo zorunluluğu** | 6 gün / 50 işlem | SPK |
| **Müşteri fon koruması** | Takasbank ayrıştırılmış hesap + YTM sigortası | SPK |

**⚠️ Pratik Sonuç:** 10.000 TL sermaye ile forex canlı hesap açılamaz. Demo hesap ücretsizdir ve strateji testi için kullanılabilir. Gerçek forex işlemi için alternatif:
- Offshore broker (yasal değil, riskli — önerilmez)
- BIST hisse senedi alımı (SPK kısıtlaması yok, düşük bütçeyle başlanabilir)
- Kripto (SPK kapsamı dışı, kendi platformları üzerinden)

---

## 2. Küçük Bütçeyle BIST DCA Stratejisi

### Varsayımlar
- Aylık yatırım bütçesi: 2.000-3.500 TL
- Başlangıç sermayesi: 10.000 TL
- Ufuk: 3-5 yıl
- Faiz indirimi döngüsü: TCMB %50 → %37'ye düşürdü, yıl sonuna kadar ~1000 bp daha bekleniyor

### Portföy Dağılımı (Önerilen)

| Hisse | Sektör | Pay | Gerekçe |
|-------|--------|-----|---------|
| **ASELS** | Savunma Sanayi | %50 | Devlet desteği, küresel trend, İş Yatırım hedef 450 TL (%25 potansiyel) |
| **ISCTR** | Bankacılık | %30 | Faiz indiriminden en çok beslenen sektör, düşük lot fiyatı (~14 TL) |
| **Nakit** | Bekleme | %20 | Düşüşlerde fırsat alımı için rezerv |

### Aylık DCA Uygulaması (3.000 TL ile)
1. Her ayın 1. işlem günü: **1 adet ASELS** (~370 TL) + **100 adet ISCTR** (~1.400 TL)
2. Kalan ~1.230 TL nakit havuzuna eklenir
3. Düşüş günlerinde (günlük -%3+): nakit havuzundan ek alım
4. Her 6 ayda bir portföy dengesi kontrolü ve yeniden dağılım

### Neden Bu Sektörler?

**Savunma Sanayi:**
- ASELSAN dünyada ilk 15 savunma şirketi arasında (piyasa değeri)
- Son 1 yılda %144 artış, 2 trilyon TL piyasa değeri (Mayıs 2026)
- İş Yatırım hedef: 450 TL | YZ analizi hedef: 427 TL | TradingView max: 495 TL
- Faiz indiriminden bağımsız büyüme dinamiği (devlet sözleşmeleri, ihracat)
- **Risk:** F/K 47.5 — pahalı, düzeltme riski var

**Bankacılık:**
- QNB Invest raporu: "Banka hisseleri öncülüğünde yükseliş bekleniyor"
- Tarihsel pattern: faiz indirimi döngülerinde bankalar öncü sektör
- ISCTR düşük fiyat (~14 TL) sayesinde küçük bütçeyle alınabilir
- Diğer banka opsiyonları: GARAN (~140 TL), AKBNK (~70 TL)

### Alternatif Sektörler
- **Demir-Çelik:** KOCER, EREGL — inşaat sektörü canlanmasından beslenir
- **İnşaat:** Faiz indirimi → kredi maliyeti düşer → konut talebi artar
- **Perakende:** İç tüketim canlanmasından beslenir

### Aracı Kurum Seçimi
| Kurum | Komisyon (0-750K TL) | Platform | Not |
|-------|---------------------|----------|-----|
| Yapı Kredi Yatırım | %1.99 | İnternet şubesi | Geniş şube ağı |
| Ak Yatırım | %1.99 (güncel) | Ak Yatırım Mobile | Model portföy raporları |
| İntegral Yatırım | Değişken | İntegral Trader | Düşük komisyonlu |
| Garanti BBVA Yatırım | Güncel oran | Garanti Trader | Banka entegrasyonu |

**Öneri:** Küçük bütçeyle Yapı Kredi veya Ak Yatırım (komisyon oranları düşük, araştırma raporları kaliteli).

---

## 3. Pozisyon Yönetimi — Zarardaki Hisse Senaryosu

### Gerçek Örnek: KOCAER ÇELİK (KCAER)
```
Alış: 14.625 TL × 245 adet = 3.584 TL maliyet
Güncel: 13.39 TL × 245 adet = 3.280 TL
Zarar: 302 TL (%8.4)
```

### Karar Çerçevesi
| Soru | Analiz |
|------|--------|
| Aracı kurum hedefleri ne? | İş Yatırım: 18.83 TL (AL), USC: 19.7 TL, Fintables: 20.11 TL |
| Sektör görünümü? | Demir-çelik sektörü faiz indiriminden beslenir (inşaat talebi) |
| Zarar büyük mü? | 302 TL toplam portföyün ~%2'si — taşınabilir |
| Satmalı mı? | Panik satışı gerekmez, hedef fiyatlar %35-45 potansiyel gösteriyor |

### Ne Zaman Satılır?
1. **Stop-loss ihlali:** Önceden belirlenmiş seviye kırılırsa (örn. 12.00 TL altı)
2. **Temel değişiklik:** Şirket finansalları bozulursa (F/K daha da yükselirse)
3. **Daha iyi fırsat:** Sermayeyi daha yüksek getirili bir hisseye kaydırmak için
4. **Hedefe ulaşma:** Aracı kurum hedefine (18-20 TL) ulaşılırsa kâr alma

---

## 4. Makro Görünüm (Temmuz 2026)

### Pozitif Faktörler
- TCMB faiz indirimi döngüsü başladı (%37, devamı bekleniyor)
- BIST 100 son 12 ayda %38 yükseldi
- Dezenflasyon süreci sinyalleri var (Mayıs: %1.53, Haziran: %1.37)
- Seçim ekonomisi yaklaşırken genişlemeci politikalar bekleniyor
- Yabancı yatırımcı ilgisi artıyor

### Negatif Faktörler
- USD/TRY ~46 seviyesinde — TL'deki değer kaybı devam ediyor
- Jeopolitik riskler (savunma sektörü için hem fırsat hem risk)
- CDS primi yüksekliği
- Önümüzdeki dönemde seçim belirsizliği

---

## 5. Takip Edilecek Kaynaklar

### YouTube Kanalları
| Kanal | İçerik |
|-------|--------|
| **ForInvest** | BIST analiz, portföy yönetimi |
| **Kanal Finans** | Hisse yorumları, temel analiz |
| **Devrim Akyıl** | Sektör analizleri, makro değerlendirme |
| **Kayıt Dışı İktisat (Ceyhun Elgin)** | Makro ekonomi |
| **Ak Yatırım** | Model portföy, strateji raporları |

### Diğer Kaynaklar
- **Bloomberg HT** — Canlı borsa, ekonomi yorumları, uzman konuklar
- **Dünya Gazetesi** — Günlük ekonomi haberciliği
- **TradingView BIST sayfası** — Teknik analiz, topluluk yorumları
- **İş Yatırım / Ak Yatırım raporları** — Aracı kurum hedef fiyatları
- **QNB Invest araştırma** — Faiz/borsa ilişkisi analizi
- **Para Dergisi** — Piyasa yorumları, sektör analizi

---

## 6. Hata ve Uyarılar

### Yapılmaması Gerekenler
- ❌ Mevduat faizinden yüksek getiri garantisi veren tavsiyelere itibar etme
- ❌ Tek hisseye aşırı konsantrasyon (max %50)
- ❌ Düşüşte panik satışı — zarar küçükse pozisyonu kapatma
- ❌ Kaldıraçlı forex (50K TL teminat yoksa)
- ❌ YouTube fenomenlerine körü körüne güvenme — her öneriyi kendi araştır

### Önemli Hatırlatmalar
- Bu bir yatırım tavsiyesi değildir
- Backtest ≠ gelecek performans garantisi
- Küçük bütçeyle başlamak öğrenme sürecinin parçasıdır
- Düzenli alım (DCA) zamanlama riskini azaltır
- Her yatırım kararından önce güncel verileri kontrol et
