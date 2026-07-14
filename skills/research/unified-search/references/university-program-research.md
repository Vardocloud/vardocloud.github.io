# University Program Research — Cross-Check Methodology

## Problem

University program pages often contain **inconsistent or conflicting information** across different pages on the same website. A specific program page may claim one thing (e.g., "English instruction available") while the faculty or general admissions page says another (e.g., "Languages: Kazakh, Russian only").

## Cross-Check Checklist (en az 2 kaynak doğrula)

### 1. Dil — En Çok Çelişen Alan

| Kontrol Noktası | Nereye Bakılır | Örnek Uyarı |
|-----------------|----------------|-------------|
| Program sayfası | Programın kendi alt sayfası (ör. `/en/obrprogramms/clinical-psychology`) | "Languages of Instruction: Kazakh, Russian, or English" |
| Ana program sayfası | Faculty/master genel sayfası (ör. `/en/magistratura/`) | "Languages of training: Kazakh, Russian" |
| Ücret sayfası | `/en/price` — İngilizce branş varsa ayrı ücret listelenir | "English branch" sütunu var mı? |
| Yabancı öğrenci sayfası | `/en/page/foreign-students` veya benzeri | Genelde İngilizce programları listeler |

**⚠️ Uyarı:** Eğer program sayfası İngilizce seçeneği sunuyor ama ana master sayfası "Kazakh, Russian" diyorsa:
- İngilizce opsiyonel (sadece bazı dersler) olabilir
- Sadece belirli programlarda (MBA gibi) İngilizce olabilir
- İngilizce seçeneği eski/yeni versiyon farkı olabilir
- **Çözüm:** E-posta ile teyit et (üniversitenin uluslararası ofisine)

### 2. Ücret — Çok Katmanlı Doğrulama

| Adım | Yöntem |
|------|--------|
| 1. Tavily deep search | Resmi ücret sayfasını bul, AI özetini al |
| 2. web_extract | Sayfanın kendisini çek, SÜTUN BAŞLIKLARINI gör |
| 3. Brave cross-check | Başka bir kaynaktan (topuniversities, edurank) teyit |
| 4. Kur dönüşümü | Güncel kuru kontrol et (exchangerate-api.com) |
| 5. Branş farkı | Aynı programın Kazakh/Russian vs English fiyatı varsa not et |

### 3. Süre ve Track Farkları

| Track | Süre | Amaç | Program Kodu |
|-------|------|------|-------------|
| Scientific/Pedagogical | 2 yıl | Araştırma + akademik kariyer | Genelde "08" sonlu |
| Specialized/Profile | 1-1.5 yıl | Profesyonel uygulama | Genelde "09" sonlu |

**⚠️ Not:** 1 yıllık track klinik psikoloji için kısa olabilir — staj+tez sıkışabilir. Edel'e belirt.

### 4. YÖK Denklik

| Yöntem | Nasıl |
|--------|-------|
| e-Devlet | Edel'in kendisi e-Devlet'ten sorgular — Vanitas sadece yönlendirir |
| YÖK sayfası | `yok.gov.tr/en/international-relations/recognition-of-diplomas` — bazen erişilir |
| Bologna süreci | Kazakistan Bologna üyesi → genelde tanınır. Özel ünilerde dikkat. |

### 5. Deadline ve Başvuru

- Üniversiteler genelde deadline'ı ana sayfada değil, ayrı bir "Admission" alt sayfasında verir
- Kazak ünilerinde yaz dönemi (Haziran-Ağustos) online görüşme/danışmanlık dönemidir
- Eğer deadline bulunamazsa: "Belirtilmemiş" yaz + "Bunu üniversiteye sormak lazım" uyarısı

---

## Türkiye Üniversite Araştırması — Ek Metodoloji

### 6. Instagram Birincil Kaynaktır

Türkiye'deki üniversite enstitüleri (SBE, SBE, EBE) güncel başvuru ilanlarını **Instagram hesaplarında** web sitesinden önce yayınlar. Web sitesi genelde güncellenmemiş olabilir.

| Ne Zaman | Ne Yap |
|----------|--------|
| Web sitesinde eski tarih görüyorsan | `site:instagram.com ÜniversiteAdı Enstitü başvuru 2026-2027` ara |
| Instagram'da gördüğün tarih web'den farklıysa | Instagram'daki daha günceldir. WebExtract ile doğrula. |
| Instagram linki kırık/kaybolmuşsa | Post ID'sini not et, yine de referans olarak kullan |

**Örnek:** Ege Üniversitesi SBE'nin web sayfasında Mayıs 2026 tarihi varken, Instagram duyurusu "02-25 Haziran 2026" diyordu — Instagram doğruydu.

### 7. Erken Başvuru vs Normal Başvuru

Türk devlet üniversitelerinde genelde **iki başvuru dönemi** olur:

| Dönem | Tipik Zamanı | Amaç |
|-------|-------------|------|
| **Erken Başvuru** (1. dönem) | Mayıs ortası | Sınırlı kontenjan, erkenci adaylar |
| **Normal Başvuru** (2. dönem) | Haziran sonu – Temmuz | Asıl başvuru dönemi |

- Erken dönemde başvurmayanlar için normal dönem açık olur
- İki dönem arasında değerlendirme kriterleri aynıdır
- Eğer sadece bir tarih görüyorsan, normal başvuru dönemi olma ihtimali yüksek

### 8. Yabancı Dil Muafiyeti (Türkiye — Kritik)

**Kural:** YÖK lisansüstü yönetmeliğine göre, **%100 İngilizce lisans programından mezun olanlar** YDS/YÖKDİL'den muaftır.

| Üniversite | Politikası | Kaynak |
|-----------|-----------|--------|
| **İzmir Ekonomi Üniv.** | %100 İngilizce lisanstan son 3 yılda mezun → muaf | [İEÜ Başvuru Koşulları](https://lisansustu.ieu.edu.tr/klinik_psikoloji/tr/programa-basvuru) |
| **Ege Üniversitesi** | İngilizce lisans bitirenler muaf | [EÜ Bilgi Paketi](https://ebp.ege.edu.tr/DereceProgramlari/Detay/2/60620/4820/932001) |
| **DEÜ / İKÇÜ / Bakırçay / Tınaztepe** | YÖK mevzuatına tabi → İngilizce lisans muafiyet sağlar | Genel YÖK regülasyonu |

**⚠️ Dikkat:** Bazı vakıf üniversiteleri kendi dil sınavlarını yapabilir. Her zaman program sayfasındaki "yabancı dil koşulu" bölümünü oku.

**Edel için not:** DAÜ %100 İngilizce Psikoloji lisansı (mezuniyet 2023) → tüm İzmir üniversitelerinden muaf. YÖKDİL'e girmesine gerek yok.

### 9. Değerlendirme Formülleri (Türkiye)

Türk üniversitelerinde klinik psikoloji YL değerlendirmesinde kullanılan tipik formüller:

| Üniversite | Formül |
|-----------|--------|
| Ege Üniversitesi | ALES %50 + Mezuniyet Notu %25 + Mülakat %25 |
| Tınaztepe | ALES %30 + Not %20 + Niyet Mektubu+Mülakat %30 + Dil %20 |
| Genel devlet üniversitesi | ALES %50 + Not %25 + Mülakat %25 (yaygın) |

ALES puan türü klinik psikoloji için genelde **EA (Eşit Ağırlık)** olur. Minumum ALES: 55 (devlet), 55-60 (vakıf).

### 10. Enstitü Türleri

Klinik psikoloji yüksek lisansı Türkiye'de farklı enstitülerde açılabilir:

| Enstitü | Örnek Üniversite |
|---------|-----------------|
| **Sosyal Bilimler Enstitüsü (SBE)** | Ege, DEÜ, İKÇÜ, İEÜ |
| **Sağlık Bilimleri Enstitüsü** | Bazı üniversiteler |
| **Lisansüstü Eğitim Enstitüsü** | Bakırçay, Tınaztepe (yeni yapılanma) |
| **Eğitim Bilimleri Enstitüsü** | DEÜ (alternatif) |

Hangi enstitüde olduğu, başvuru yapılacak sayfayı ve takvimi belirler. Yanlış enstitüye başvuru yapmak zaman kaybettirir.

### 11. Başvuru Adımları (Türkiye)

1. **Enstitüyü belirle** — Program hangi enstitü altında?
2. **Web + Instagram çapraz kontrol** — Güncel başvuru tarihlerini teyit et
3. **Eksiksiz belgeleri hazırla** — Diploma, transkript, ALES, kimlik, niyet mektubu
4. **Online başvuru sistemine gir** — Genelde `ebasvuru.universiteadi.edu.tr` veya `basvuru.universiteadi.edu.tr`
5. **Ödeme yap** — Başvuru ücreti (varsa)
6. **Başvuruyu tamamla** — Son başvuru tarihini kaçırma

---

## Output Template

Her üniversite için aşağıdaki gibi yapılandırılmış bir yanıt ver:

| Başlık | Detay |
|--------|-------|
| Program | Adı + kodları |
| Şehir/Ülke | |
| Tür | Devlet/Özel |
| Süre | Track bazında |
| Dil | ✅/⚠️/❌ (uyarı notuyla) |
| Ücret | Yerel para + USD dönüşümü |
| Ön Koşul | |
| YÖK | ✅/⚠️/❌ (belirtilmişse) |
| Deadline | (varsa) |
| İletişim | Telefon + e-posta |
| Değerlendirme | Formül (varsa) |
| Dil Muafiyeti | İngilizce lisans muaf mı? |

## Examples from Sessions

**Turan University (Almatı) case:**
- Program sayfası: "Kazakh, Russian, or English" ✅
- Ana master sayfası: "Kazakh, Russian" ❌
- Sonuç: ⚠️ Çelişki — İngilizce teyit gerekli

**Ege Üniversitesi (İzmir) case:**
- Web sayfası: Erken başvuru 11-14 Mayıs 2026 (güncellenmemiş)
- Instagram: Normal başvuru 02-25 Haziran 2026 ✅
- Sonuç: Instagram daha günceldi. Normal başvuru dönemi açıktı.

**İngilizce lisans muafiyeti (Edel case):**
- DAÜ %100 İngilizce Psikoloji lisansı (2023 mezunu)
- İEÜ, Ege, DEÜ → tam muafiyet
- YÖKDİL 9 Ağustos sınavına gerek kalmadı
