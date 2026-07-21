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

### Web Sitesi
- `paradergi.com.tr` ana sayfasını `web_extract` ile tara — en kapsamlı içerik buradan gelir
- Alt kategoriler: `/finans/` (çalışıyor, zengin içerik), `/teknoloji` (çalışıyor, güncel içerik)
- **Kırık kategoriler (404):** `/ekonomi/`, `/son-dakika/`, `/saglik/`, `/seyahat/` — taşınmış veya kaldırılmış
- KVKK çerez bildirimi gelebilir — içerik yine de okunabilir
- Sayfa yapısı Turkuvaz Medya altyapısı (gazete/dergi formatı)
- URL yapısı: `paradergi.com.tr/{kategori}/{YYYY}/{MM}/{GG}/{makale-basligi}`
- **AMP sürümleri:** `/amp/` uzantılı sayfalarda "GÜNCELLEME: GG.AA.YYYY" ve "GİRİŞ TARİHİ: GG.AA.YYYY" timestamp'leri bulunur — hangi haberin bugüne ait olduğunu teyit etmek için AMP bağlantısını kontrol et
- **Tarih bazlı keşif:** `web_search` ile `"paradergi.com.tr" "YYYY/MM/GG"` sorgusu (ör: `"2026/07/21"`) bugünün makalelerini doğrudan bulur. Tarih URL'de olduğu için güvenilir bir keşif yöntemidir.

### X/Twitter (@ParaDergisi)
- Hesap günde 1-2 tweet atıyor, web içeriğini linkliyor
- **Önemli teknik:** X'te oturum açmadan kronolojik olmayan sıralama gösterilir (eski pinned tweet'ler önce gelir). Oturumsuz ana sayfayı taramak kronolojik içerik getirmez. Bunun yerine:
  1. Önce `web_search` ile `"site:x.com/ParaDergisi" "anahtar-kelime"` (veya boş) sorgusuyla güncel tweet ID'lerini bul
  2. Her tweet için `web_extract(url="https://x.com/ParaDergisi/status/{ID}")` yap — bu çalışır ve tam timestamp + içerik + görüntülenme sayısını döndürür
  3. Alternatif: `browser_navigate` ile doğrudan tweet URL'sine git
- En yüksek etkileşim "Para Dergisi'nde bu hafta" kapak duyurularında olur (1K+ görüntülenme)
- Twitter taraması web taramasını tamamlayıcı niteliktedir — web'de olmayan ek içerik nadiren gelir

### Genel
- `web_extract` aynı anda 5 URL'e kadar destekler — tweet'leri ve makaleleri gruplayarak tara
- `web_search` limit=10 kullanarak maksimum kapsama al
- Taramaya ana sayfadan başla, sonra `/finans/` alt kategorisi, sonra Twitter

## Tarama Geçmişi

### 21 Temmuz 2026 (Salı — Cron)
**2 yeni makale bulundu (bugün yayınlanmış):**

| # | Makale | Kategori | Öne Çıkan |
|---|--------|----------|-----------|
| 1 | **Otomat patlaması!** | Girişimcilik | Yeni nesil akıllı otomatlar (IoT + AI + temassız ödeme). Yatırım: 500K-1M TL, ROI 10-24 ay. Sıcak gıda otomatlarının Avrupa/ABD'ye ihraç potansiyeli. |
| 2 | **Batı Afrika'nın 'Mutluluk Adaları': Cabo Verde** | Dünya/Turizm | Batı Afrika'nın en istikrarlı demokrasisi. Türkiye ile ticaret 9,5M$. Turizm + yenilenebilir enerji fırsatları. Doğrudan uçuş yok, vize gerekli. |

**Aynı haftadan devam eden güncel içerikler (16-20 Temmuz):**
- Saat&Saat (SSAAT) BIST'te işlem görmeye başladı: 3,75 milyar TL halka arz, 56 TL, 709 bin başvuru, 45 ülke, %32,4 FAVÖK marjı
- Uzun vade için önerilen 23 hisse listesi: TSKB, ISCTR, GARAN, ASTOR, FROTO, KCHOL, SAHOL, THYAO, PGSUS, TCELL, MPARK, MGROS, SISE vb.
- IGEXX 2026: 3-5 Eylül, Haliç Kongre Merkezi, 60+ ülke, 6,4 milyar $ e-ihracat
- Bulls Yatırım Holding → Escar Filo: %77,62 hisse, 141,4 milyon $
- Yapı Kredi: 700 milyon $ uluslararası fon
- Yandex Go: 100 milyon $ yatırımla İstanbul'da
- Hayat Finans: KOBİ'lere 40 milyar TL ek finansman
- Garanti BBVA: 30 milyon € yeşil tahvil
- Tosyalı: 1,2 GW GES için 187 milyon € finansman
- QNB Türkiye: "Mavi Repo" ile su/mavi ekonomi finansmanı
- Turknet: 141 milyon $ altyapı yatırımı

**Güncel piyasa spotları (21 Temmuz):**
- BIST: 14.070,98 | USD/TRY: 47,20 | EUR/TRY: 53,94
- Altın Ons: $4.065,79 | Faiz: %41,71 | Brent: $88,96

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
