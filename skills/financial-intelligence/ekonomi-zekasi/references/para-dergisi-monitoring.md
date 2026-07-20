# Para Dergisi Günlük Tarama

## Kaynak
- **Web:** https://www.paradergi.com.tr/
- **Twitter/X:** @ParaDergisi (101K takipçi, mavi tikli)
- **Instagram:** @paradergisi (verified)
- **Tür:** Haftalık ekonomi dergisi (günlük site/X güncellemesi)
- **Sahibi:** Turkuvaz Medya Grubu

## Cron Konfigürasyonu
- **Job ID:** 45e8c6b7d2af
- **Schedule:** Her gün 09:00
- **Model:** NVIDIA MiniMax M3
- **Prompt kuralı:** Yeni içerik varsa raporla, yoksa sessiz kal
- **Teslimat:** origin (Edel ile aynı topic)

## Analitik Metodoloji (Para Dergisi Çerçevesi)

### 1. Makro Öncelikli Yaklaşım
Para Dergisi, hisse önerilerine geçmeden önce mutlaka makroekonomik tabloyu çizer:
- TCMB faiz kararları ve beklentiler
- Sanayi üretimi, büyüme verileri
- Dış ticaret, cari açık, ihracat iklimi
- Demografik trendler (uzun vadeli)

### 2. Sektör Rotasyonu
- **Banka/Finans:** Faiz indirim döngüsünde ilk kazanan sektör
- **Sanayi:** Büyüme beklentileriyle sürece sonradan katılır
- **Perakende:** Tüketici güveniyle bağlantılı
- **Savunma:** Devlet teşviği ve küresel trendlerle bağımsız büyür

### 3. Değerleme Bazlı Hisse Seçimi
23 hisse listesi şu kriterlere göre seçilir:
- **FAVÖK marjı:** Yüksek ve sürdürülebilir
- **Gelir büyümesi:** Geçmiş ve beklenen
- **Değerleme:** Sektör ortalamasına göre iskontolu
- **Likidite:** BIST'te yeterli işlem hacmi
- **Kurumsal yönetim:** Şeffaflık ve hissedar değeri

### 4. Teknik Analiz Referansları
- **BIST destek:** 12.500-13.000 (en kötü durum)
- **BIST direnç:** 15.500-16.000 (orta vadeli)
- **Hedef bölge:** 19.500-20.000 (2027 beklentisi)

### 5. Halka Arz Analizi
Her halka arz için:
- Talep toplama oranları (bireysel/kurumsal ayrı)
- Halka açıklık oranı ve büyüklük
- Gelirin kullanım planı (% borç ödeme / % işletme sermayesi)
- Şirketin operasyonel yapısı (mağaza ağı, çalışan, marjlar)

### 6. Küresel Karşılaştırma
- Fed politikalarının BIST'e yansıması
- ABD teknoloji hisseleri (AI bubble vs dot.com karşılaştırması)
- Jeopolitik risklerin emtia/dövize etkisi

### 7. Temel Duruş
- Uzun vadeli, değer odaklı, spekülasyon karşıtı
- "Zengin içeriği ve rahat okunan sayfaları" — yatırımı gündelik hayatın parçası yapma felsefesi
- Sade dil, karmaşık kavramları herkese anlatma hedefi

## Hedef İçerik Türleri
1. Uzman hisse önerileri (23 hisse listesi gibi)
2. Halka arz haberleri ve analizleri
3. BIST piyasa yorumları ve teknik seviyeler
4. Döviz/faiz/emtia beklentileri
5. Bireysel yatırımcı tavsiyeleri
6. Makroekonomik veri yorumları (sanayi üretimi, enflasyon, büyüme)

## Scraping Approach
- `paradergi.com.tr` ana sayfasını web_extract ile tara
- X/Twitter hesabı (@ParaDergisi) postlarını tara (günlük atıyor)
- KVKK çerez bildirimi gelebilir — içerik yine de okunabilir
- Sayfa yapısı Turkuvaz Medya altyapısı (gazete/dergi formatı)
- URL yapısı: paradergi.com.tr/{kategori}/{tarih}/{makale-basligi}

## Tarama Geçmişi

### 20 Temmuz 2026 (Pazar — Kanban Task)
**3 yeni makale bulundu:**

| # | Makale | Kategori | Öne Çıkan |
|---|--------|----------|-----------|
| 1 | **Kritik torba yasa** | Finans/Makro | Emekli maaşı 23.552 TL, Siber Güvenlik Başkanlığı, imalat teşviği 2028'e uzatıldı (188 milyar TL) |
| 2 | **IGEXX 2026** | Sektörler/Dış Ticaret | 3-5 Eylül, 60+ ülke, 40 pazar yeri, 6,4 milyar $ e-ihracat hacmi |
| 3 | **Trakya'nın en trend yatırım rotaları** | Sektörler/Gayrimenkul | Hisseli parsel uyarısı, Halkalı-Kapıkule hattı etkisi, Tekirdağ/Kırklareli/Edirne analizi |

**Aynı hafta (16-19 Temmuz) bulunan diğer içerikler:**
- Üretime sıkılaşma freni (sanayi üretimi aylık -%2,9, büyüme tahmini IMF %2,9'a düşürüldü)
- E-ihracat Türkiye'nin yeni büyüme gücü oldu (TİM ödül töreni, 396 milyar $ ihracat)
- Haftanın kulisleri (Galatasaray Florya/Nivak, Kalamış Marina ertelendi, SharkNinja 100 mağaza hedefi)
- The Dalaman Golf Club (30 Ağustos açılış, 18 delik, TrackMan AI)
- Saat ve Saat A.Ş. BIST'te (SSAAT) — 16 Temmuz halka arz

**Güncel piyasa spotları:**
- BIST: 13.981,05 | USD/TRY: 47,18 | EUR/TRY: 54,01
- Altın Ons: $4.009,58 | Faiz: %41,49 | Brent: $88,10

**Twitter/X performansı:** Hesap günde 1-2 tweet atıyor. En yüksek etkileşim "Para Dergisi'nde bu hafta" kapak duyurusunda (~526 görüntülenme). Diğer tweetler düşük etkileşimli. Tüm web haberleri Twitter'dan da paylaşılıyor — Twitter taraması web taramasını tamamlayıcı nitelikte.

**Site yapısı notu:** URL formatı paradergi.com.tr/{kategori}/{tarih}/{makale-basligi} şeklinde. Tarih URL'de YYYY/AA/GG formatında. /borsa/ ve /emlak/ kategorileri 404 veriyor (taşınmış veya kaldırılmış). Aktif kategoriler: finans/, sektorler/, is-dunyasi-kulis/, life-style/.

## Edel'in Durumuna Uyarlama
- Para Dergisi genelde düzenli geliri olan yatırımcıya hitap eder
- Edel için: "not al, gelecekte kullan" filtresi uygula
- Düzenli gelir başlayana kadar: sadece takip et, aksiyon önerme
- Halka arz fırsatları ve teşvik programları (HIT-30 gibi) ayrıca vurgulanır

## Çıktı Formatı (Cron)
- Sadece **yeni** içerik varsa bildir
- Her öneri için "Edel'in durumuna uygun mu/değil" yorumu ekle
- Türkçe, kısa öz
