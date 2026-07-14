# Turkish Job Search — Platform Reference

## Platform URL Patterns

### Kariyer.net
- Ana liste: `https://www.kariyer.net/is-ilanlari/{pozisyon}+{sehir}`
  - Örn: `https://www.kariyer.net/is-ilanlari/izmir-makine+muhendisi`
- İlçe bazlı: `https://www.kariyer.net/is-ilanlari/{sehir}-{ilce}-{pozisyon}`
  - Örn: `https://www.kariyer.net/is-ilanlari/izmir-karsiyaka-makine+muhendisi`
- Sektör: `https://www.kariyer.net/is-ilanlari/{sektor}+sanayi`
- Filtre parametreleri: Tarih, çalışma şekli, pozisyon seviyesi, departman
- **Site operator:** `site:kariyer.net makine mühendisi İzmir`
- URL'de pozisyon: `makine+muhendisi` (boşluk yerine +, i yerine normal harf)
- Doğrudan ilan linki: `https://www.kariyer.net/is-ilani/{firma-adi}-{pozisyon}-{ilanNo}`

### Indeed Türkiye
- Ana arama: `https://tr.indeed.com/q-{pozisyon}-is-ilanlari.html`
- Şehirli: `https://tr.indeed.com/q-{pozisyon}-l-{sehir}-is-ilanlari.html`
  - Örn: `https://tr.indeed.com/q-makine-mühendisi-l-İzmir-is-ilanlari.html`
- İlçeli: `https://tr.indeed.com/q-makine-mühendisi-l-{ilçe}-is-ilanlari.html`
- Sıralama parametresi: `?sort=date` (tarihe göre)
- **Site operator:** `site:tr.indeed.com "makine mühendisi"`
- Not: web_extract bazen ilan listesini değil, sadece arayüzü döner. O zaman browser ile aç.

### LinkedIn Jobs Türkiye
- Tümü: `https://tr.linkedin.com/jobs/{pozisyon}-jobs`
  - Örn: `https://tr.linkedin.com/jobs/makine-mühendisi-jobs`
- Şehir bazlı: `https://tr.linkedin.com/jobs/{pozisyon}-jobs-{sehir}`
  - Örn: `https://tr.linkedin.com/jobs/makine-mühendisi-jobs-izmir`
- URL'de Türkçe karakterler URL-encoded olabilir: `m%C3%BChendisi` = "mühendisi"
- **web_extract often fails** (403/blocked) → use `site:linkedin.com` in web_search instead
- Filtre: `?countryRedirected=1` for Türkiye

### Eleman.net
- Şehir + pozisyon: `https://www.eleman.net/is-ilanlari/{sehir}/{pozisyon}`
  - Örn: `https://www.eleman.net/is-ilanlari/izmir/makine-muhendisi`
- Doğrudan ilan: `https://www.eleman.net/is-ilani/{baslik}-i{ilanNo}`
- **Site operator:** `site:eleman.net makine mühendisi İzmir`

### İŞKUR (Türkiye İş Kurumu)
- Meslek kodu ile: `https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?mid={meslekKodu}&il={ilKodu}`
  - `mid=3556` = Makine Mühendisi
  - `il=35` = İzmir
- Örn tüm İzmir makine mühendisi: `https://esube.iskur.gov.tr/Istihdam/AcikIsIlanAra.aspx?mid=3556&il=35`
- İşyeri adı görmek için: e-Devlet ile sisteme üye girişi gerekli
- Her ilanın bir "İlan No"su var → favorilere ekleme/paylaşma için kullanılır
- Son başvuru tarihine dikkat (genelde kısa süreli)

### Common İŞKUR Meslek Kodları
| Meslek | Kod |
|--------|:----:|
| Makine Mühendisi | 3556 |
| Makine ve Teçhizat Mühendisi | 3557 |
| Endüstri Mühendisi | 3562 |
| Elektrik Mühendisi | 3534 |
| İnşaat Mühendisi | 3225 |
| Yazılım Mühendisi | 3517 |
| Mekatronik Mühendisi | 3563 |

### Common İl Kodları (İŞKUR)
| İl | Kod |
|:--:|:---:|
| İzmir | 35 |
| İstanbul | 34 |
| Ankara | 6 |
| Bursa | 16 |
| Kocaeli | 41 |
| Manisa | 45 |
| Aydın | 9 |
| Muğla | 48 |

### Diğer Platformlar
| Platform | URL Pattern | Site Operator |
|----------|-------------|---------------|
| Yenibiriş | `yenibiris.com/is-ilanlari/{pozisyon}` | `site:yenibiris.com` |
| SecretCV | `secretcv.com/is-ilanlari/{sehir}/{pozisyon}` | `site:secretcv.com` |
| Jooble | `tr.jooble.org/iş-ilanları-{pozisyon}/{sehir}` | `site:tr.jooble.org` |
| Careerjet | `careerjet.com.tr/{pozisyon}-is-ilanlari` | `site:careerjet.com.tr` |
| Savunma Kariyer | `savunmakariyer.com/ilanlar` | `site:savunmakariyer.com` |

## 🚨 Indeed JS Extraction (Kariyer.net bot korumasını bypass yöntemiyle aynı prensip)

**Kariyer.net arama sayfaları bot korumasına takılır → Google site: araması kullan**
**Indeed arama sayfaları da bot korumasına takılır → browser_console JS extraction kullan**

**Ne zaman:** web_extract ile Indeed'den ilan linklerini çıkaramadığında (boş sayfa, authenticate sayfası, JS render sorunu).

**Yöntem:**
1. Browser ile Indeed arama sayfasını aç:
   ```
   browser_navigate(url="https://tr.indeed.com/jobs?q={pozisyon}&l=Türkiye")
   ```
2. İlan listesinin yüklendiğini teyit et (scroll down gerekebilir)
3. Browser console'da şu JavaScript'i çalıştır:
   ```javascript
   var results = []; 
   var links = document.querySelectorAll('a[data-jk]'); 
   for (var i = 0; i < links.length; i++) { 
     var a = links[i]; 
     var jk = a.getAttribute('data-jk'); 
     results.push({title: a.textContent.trim(), jk: jk, url: 'https://tr.indeed.com/viewjob?jk=' + jk}); 
   } 
   JSON.stringify(results);
   ```
4. Her `jk` değeri -> `https://tr.indeed.com/viewjob?jk={JK}` formunda doğrudan ilan linki
5. **Uyarı:** Bu linkler browser'da authenticate sayfasına yönlendirebilir (bot koruması) ama gerçek kullanıcı Indeed'te oturum açınca doğrudan ilanı gösterir
6. Şirket adını ve lokasyonu eklemek için sayfadan ayrıca extrakte et (browser_snapshot veya browser_console ile)

**Örnek çıktı:**
```
[
  {"title": "Satış Mühendisi", "jk": "344f9c5846f1cebd", "url": "https://tr.indeed.com/viewjob?jk=344f9c5846f1cebd"},
  {"title": "Proje Satış Yöneticisi (GES)", "jk": "f08ca47fa2820a20", "url": "https://tr.indeed.com/viewjob?jk=f08ca47fa2820a20"}
]
```

**Not:** Indeed'deki ilan sayısı sınırlı olabilir (15-20 civarı). Daha spesifik anahtar kelimelerle yeni bir arama açıp tekrar et.

## 🚀 Büyük Firmaların Kariyer Siteleri — Parallel Scanning

**Ne zaman:** Aday büyük/köklü firmaları hedefliyorsa ve Kariyer.net/Indeed'de yeterli sonuç yoksa.

**Yöntem:**
1. Hedef firmaları belirle (adayın sektörüne göre: Camfil, Donaldson, Freudenberg, Pall, Alfa Laval, ABB, Siemens vs.)
2. delegate_task ile 3 firmayı PARALEL tara:
   ```
   delegate_task(tasks=[
     {goal: "Camfil kariyer sayfasını tarayıp Türkiye açık pozisyonlarını bul"},
     {goal: "Donaldson kariyer sayfasını tarayıp Türkiye açık pozisyonlarını bul"},
     {goal: "Freudenberg kariyer sayfasını tarayıp Türkiye açık pozisyonlarını bul"}
   ])
   ```
3. Her birinde: browser_navigate -> career sayfasını bul -> country filter (Turkey/Türkiye) -> sonuçları kontrol et
4. **Tecrübe:** Global filtrasyon firmalarında Türkiye için açık pozisyon bulma oranı DÜŞÜK (%0-10). Genelde EMEA bölgesinde açık pozisyonlar İngiltere/Almanya merkezli.
5. Sonuçları özetle: her firma için "açık pozisyon var/yok, varsa linki" formatında raporla
6. Alternatif: LinkedIn'de bu firmaları `site:linkedin.com/jobs "Camfil" Turkey` ile tara

**User rejects your search results as "başarılı değil / unsuccessful"**

This is a FIRST-CLASS signal. Do NOT defend or re-present. Follow this protocol:

1. **ACKNOWLEDGE** — Own the gap. "Haklısın, özür dilerim."
2. **IDENTIFY THE ROOT CAUSE** — Most common reasons:
   - Searched only by title ("makine mühendisi") instead of domain keywords
   - Listed closed/expired listings
   - Didn't match the person's REAL expertise area (e.g., filtration, not general machinery)
   - Wrong location granularity
3. **PIVOT WITH DOMAIN KEYWORDS** — Extract from CV:
   - Sektör spesifik: "filtrasyon", "toz toplama", "baca gazı", "enerji verimliliği"
   - Rol spesifik: "proje satış mühendisi", "application engineer", "technical service"
   - Rakip firmaları tara (BWF → Fersan Filtre, MAT Filtrasyon, Alfer gibi)
4. **RE-VERIFY EVERY LISTING** — Don't assume old search results are correct
5. **RE-PRESENT WITH STATUS** — Only active listings. Mark closed ones explicitly.

### Senior Engineer Rejection Pattern ("Çok küçük firmalar" / "Basic ilanlar")

**Signal:** User says "bunlar çok küçük firmalar", "basic/junior ilanlar", "benim seviyeme uygun değil".

**Root Cause:** İlanlar küçük ölçekli firmalardan, aday büyük/köklü firmalarda çalışmış (20M€+ ciro), üst düzey pozisyon arıyor.

**Recovery Protocol:**

1. **ACKNOWLEDGE + APOLOGIZE** — Haklısın, özür dilerim.
2. **PIVOT TO BIG PLAYERS ONLY:**
   - Global firmalar (Camfil, Pall, Freudenberg, Donaldson gibi) — cirosu €500M+ olanlar
   - Büyük holdingler (OYAK, Koç, Sabancı gibi)
   - Uluslararası endüstriyel firmalar (ABB, Siemens, Alfa Laval, GEA)
3. **INCLUDE COMPANY PROFILE** — Her ilanın yanında: çalışan sayısı, yaklaşık yıllık ciro, sektör
4. **PLATFORM SHIFT:** Kariyer.net basic ilanlar → LinkedIn global firmaların kariyer sayfaları + doğrudan firma career bölümleri + ISO 500 filtresi
5. **CHECK SIZE BEFORE LISTING** — KOBİ ise listeleme, sadece büyük ölçekliler

**Output Format:**
```
**Firma Adı — Pozisyon**
🌐 Global filtrasyon lideri | 4.000+ çalışan | €2B+ ciro
📍 Lokasyon | 🔗 Başvuru linki
```

### LinkedIn Number Inflation Warning
Web search results showing "298 Project Sales Engineer jobs" or similar COUNTRY-WIDE numbers.
Always check if the number is city-specific (İzmir) or Turkey-wide.
LinkedIn city-filtered pages usually show much smaller numbers (e.g. 11-15 vs 298).
For İzmir-specific: use `site:linkedin.com "Project Sales Engineer" İzmir` or navigate with city filter.

### Presentation Rules
- **NEVER list closed/inactive jobs without a clear status marker**
- Filter: `closingDate` geçmişse → KAPALI
- Filter: "başvuruları artık kabul etmiyor" varsa → KAPALI
- Filter: `lastPublishDate` 30+ gün eski → muhtemelen KAPALI
- Only present ACTIVE listings in the main list; put closed ones in a footnote if at all

## CRITICAL: CV-Based Keyword Extraction (Read This First)

**EN BÜYÜK HATA:** Sadece pozisyon unvanıyla arama yapmak (örn. "makine mühendisi"). Bunun yerine:

1. **Önce kişinin CV'sini/profilini oku** — pdftotext veya pypdf ile
2. **Deneyim alanından anahtar kelimeler çıkar:**
   - Sektör: filtrasyon, çimento, çelik, enerji, otomotiv, gıda, kimya
   - Rol tipi: proje satış mühendisi, application engineer, technical service, kalite kontrol
   - Beceriler: SolidWorks, ANSYS, SAP, AutoCAD
   - Teknik terimler: toz toplama, baca gazı, torbalı filtre, enerji verimliliği
3. **Birden çok sorgu seti oluştur:**
   - Unvan bazlı: "makine mühendisi"
   - Sektör bazlı: "filtrasyon makine mühendisi"
   - Rol bazlı: "proje satış mühendisi"
   - İngilizce: "project sales engineer Turkey"
   - Platform spesifik: `site:kariyer.net "toz toplama" makine mühendisi`
4. **Kişinin mevcut/ son işindeki rolüne bak** — benzer hibrit roller ara (örn. technical + sales hybrid)
5. **LinkedIn'de de aynı şirketlerin rakiplerine bak** — BWF çalışanı varsa, rakip filtre firmalarını da tara

## Listing Status Verification (CRITICAL)

**Kariyer.net ilanlarının çoğu KAPALI olabilir.** web_extract ile her ilan linkini açıp şunları kontrol et:

- Sayfada **"Bu ilan başvuruları artık kabul etmiyor."** yazısı var mı?
- `closingDate` geçmiş mi? (web_extract çıktısında görünür)
- `lastPublishDate` ne kadar eski? 30+ gün eskiyse muhtemelen kapalı
- **Sadece aktif olduğundan emin olduğun ilanları listele**

Kontrol akışı:
```python
# web_extract ile ilan sayfasını aç
# "kabul etmiyor" stringi varsa → KAPALI / geçmiş ilan olarak işaretle
# closingDate varsa ve bugün > closingDate → KAPALI
```

## Role Type Matching (vs Title Matching)

Unvan aynı olsa bile rol tipi farklı olabilir. Kişinin CV'sindeki **fiili iş tanımına** bak:

| Kişinin Yaptığı İş | Uygun Pozisyonlar |
|---|---|
| Saha servisi + teknik satış (BWF) | Application Engineer, Technical Sales Engineer, Service Engineer |
| Proje bazlı satış + maliyetlendirme (Ed-Van Fan) | Project Sales Engineer, Sales Engineer, Proposal Engineer |
| Üretim + kalite (Raytek) | Production Engineer, Quality Engineer, Process Engineer |
| Hibrit: teknik + ticari | Internal Sales Engineer, Key Account Engineer, Business Development |

**Filtre/Filtrasyon sektörü özel:** BWF, Fersan Filtre, Filtras, MAT Filtrasyon, Alfer Mühendislik gibi firmalar aynı ekosistemdir. Birinde çalışmış kişi diğerlerine de uyum sağlar.

### Multi-Platform Parallel Search
```python
# Parallel search across platforms with site: operators
queries = [
    f"site:kariyer.net makine mühendisi İzmir",
    f"site:tr.indeed.com makine mühendisi İzmir",
    f"site:linkedin.com makine mühendisi İzmir",
    f"site:eleman.net makine mühendisi İzmir",
]
# Then extract actual listing pages with web_extract
# For LinkedIn, rely on web_search SERP since scrape is blocked
```

### Output Format (for email/forwarding)
Group by platform with headings. Each listing:
```
**Şirket Adı — Pozisyon**
📍 Şehir / İlçe
🔹 Kısa nitelik (deneyim, yazılım, sektör)
📅 Tarih / Güncellik
🔗 https://...
```

### Location Adjustment Pattern
When user says "X için bak" mid-search:
1. Acknowledge the correction
2. Replace city name in all platform URLs
3. Re-run searches with new city filter
4. Rebuild output

### Araba/Ehliyet Filter
- Arkas Heavy type listings often require B class license + active driving
- Many İzmir OSB jobs require a car (spread-out industrial zones)
- Note "🚗 araba avantajı" when listing jobs with driving requirements
