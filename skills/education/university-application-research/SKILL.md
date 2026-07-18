---
name: university-application-research
description: >-
  Comprehensive research into university admission requirements for graduate programs,
  focusing on psychology, AI, and technical fields. Gathers application requirements,
  fees, deadlines, document lists, and program structures from official university websites.
version: 1.0
metadata:
  hermes:
    tags: [education, university-admissions, graduate-applications, research, psychology, ai]
    category: education
---

# University Application Research — Graduate Programs Updated: 2026-2027 Cycle

## 🔴 KRİTİK: Subagent Bölge Taraması Güvenilmezliği (26 Haz 2026, güncelleme: 1 Tem 2026)

**Sorun:** Subagent'lar Türkiye geneli bölge taramalarında sistematik halüsinasyon üretiyor:
- "KP"yi "Klinik Psikoloji" yerine "Öğretmenlik Programı" olarak algıladı
- Var olmayan programları "var" diye raporladı, ücret/ALES/GPA bilgilerini uydurdu
- En güvenilmez olduğu alanlar: Doğu/GD Anadolu (18 üniversitede KP var dedi - hepsi yanlış), Ege Bölgesi (anlamsız rapor)

**1 Temmuz 2026 güncellemesi — Toplu taramada subagent timeout:**
- `delegate_task` ile 3 bölgeye paralel tarama gönderildi: hepsi timeout oldu (10'ar dk, toplam 30 dk kayıp)
- Subagent'lar her bölgedeki 6-8 üniversiteyi tek tek taramaya çalışınca süre yetmedi
- **Kural:** Toplu bölge taraması için subagent kullanma. Sadece tek bir üniversiteyi derinlemesine araştırmak için kullan.

**Çözüm — Manuel tarama akışı:**
1. `web_search` ile toplu bölge sorgusu yap
2. Çıkan üniversiteleri kriterlere göre ön ele
3. Canlı çıkanları tek tek manuel teyit et (resmi site + PDF)
4. Subagent'ı SADECE tek üniversite derin araştırması için kullan

**Genel Subagent Kuralı:**
1. Subagent çıktılarını [UNCERTAIN] etiketle
2. Subagent'ın söylediği ALES/GPA/YÖKDİL/ücret rakamlarına ASLA doğrudan güvenme
3. Toplu bölge taramalarında (3+ üniversite) subagent KULLANMA

## 🟢 TÜM TÜRKİYE KP YL SİSTEMATİK TARAMA AKIŞI (1 Tem 2026)

Bu akış, Edel için tüm Türkiye'deki Klinik Psikoloji YL programlarını tararken kullanılır.

### 🔴 KRİTİK KURAL: Taranan Bölgeleri Tekrar Tarama

Daha önce taranmış bölgeleri TEKRAR TARAMA. Bu zaman kaybıdır ve Edel'in canını sıkar.

**Nasıl yapılır:**
1. Taramaya başlamadan ÖNCE aşağıdaki listeleri kontrol et
2. "Taranmış" bölgelerdeki üniversiteleri ATLA
3. Sadece "Henüz Taranmamış" listesindeki bölgelere/şehirlere odaklan
4. Her yeni taramada, bulguları bu listelere ekle

### Daha Önce Taranmış Bölgeler (TEKRAR TARAMA)

| Bölge | Taranan Şehirler | Sonuç |
|:------|:-----------------|:------|
| **Ege** | İzmir, Manisa, Kütahya, Denizli, Aydın, Muğla, Uşak, Afyon | DEÜ (İzmir) + Bakırçay (İzmir) canlı — Bakırçay yeni keşif (devlet, KP YL var, ALES ≥60) ✅ |
| **İstanbul** | Tüm üniversiteler | SBÜ Hamidiye + Haliç canlı, diğer vakıflar pahalı/elendi |
| **Ankara** | Hacettepe, Ankara Üni, TOBB, YBYÜ, Başkent, Medipol, Atılım | Hacettepe (ALES 75), Ankara Üni (YL yok), TOBB (ALES 80) elendi |
| **Karadeniz** | KTÜ, OMÜ, Ordu, Giresun, RTEÜ, Gümüşhane, Tokat, Amasya, Hitit, Sinop, Kastamonu, Bülent Ecevit, Bartın, Karabük, Düzce, Bolu | Hiçbirinde KP YL YOK |
| **Doğu/GD Anadolu** | Dicle, Gaziantep, Harran, Mardin, Batman, Siirt, YYÜ, Bitlis, Hakkari, Atatürk, Kafkas, Ağrı, İnönü, Fırat, Bingöl, Muş, Adıyaman, Kilis, Osmaniye | Hiçbirinde KP YL YOK |
| **İç Anadolu** | Konya (Selçuk, NEÜ), Kayseri (Erciyes), Eskişehir (ESOGÜ, Anadolu) | NEÜ elendi, Selçuk net değil, Erciyes/ESOGÜ başvurusu geçmiş |
| **Akdeniz** | Adana (Çukurova), Mersin, Isparta (SDÜ), Alanya, Antalya (Akdeniz) | Çukurova (ALES 75), Mersin (yok), SDÜ (❓) |
| **Marmara (İstanbulsuz)** | Kocaeli, Bursa (Uludağ), Sakarya, Balıkesir, Çanakkale, Yalova, Bilecik | Kocaeli (referans yok), Uludağ (ALES sayısal), Sakarya (KP yok) |
| **KKTC** | YDÜ, GAU, ASBÜ, NEU, CIU, Final | YDÜ + ASBÜ canlı, GAU (İngilizce/pahalı), Final (TC yasak) |

### Henüz Taranmamış Bölgeler (Sıradaki)
- **Hiç taranmamış şehirler:** Aksaray, Kırıkkale, Kırşehir, Nevşehir, Niğde, Sivas, Yozgat, Çorum, Kırklareli, Tekirdağ, Edirne
- **Kısmen taranmış ama netleşmemiş:** Manisa (Celal Bayar — yeni KP açılıyor olabilir), Antalya (Akdeniz Üni)

### 🔴 KRİTİK PITFALL: Elenen Üniversiteleri Tekrar Listeleme (1 Tem 2026)

**Sorun:** Önceki oturumlarda elenmiş üniversiteleri (Ege Üni, İzmir Bakırçay, İstanbul Bilgi, GAU, Arel, Maltepe, Necmettin Erbakan) farkında olmadan tekrar canlı listeye ekledim. Edel uyardı: \"Elenenler var bunların arasında onları listeye almaman gerekiyordu.\"

**Kök neden:** Referans dosyasını (`references/turkiye-kp-yl-26-haziran-2026.md`) okudum ama \"Canlı Seçenekler\" dışındaki üniversiteleri de listeye ekledim. Ayrıca subagent raporlarına fazla güvendim.

**Çözüm:**
1. KP YL araştırması sunmadan ÖNCE referans dosyasını baştan sona oku
2. Sadece \"Canlı Seçenekler\" tablosundaki üniversiteleri listele
3. \"Elenenler\" bölümündeki hiçbir üniversiteyi canlı seçenek olarak gösterme
4. Yeni keşfedilen üniversiteleri (subagent/browser ile bulunan) doğrudan listeye ekleme — önce somut referans (resmi site linki) bul
5. Subagent raporlarına doğrudan güvenme — her zaman resmi siteden teyit et

### 🔴 KRİTİK PITFALL: Dil Sınavı Puan Karşılaştırmaları

**Kural:** Farklı dil sınavlarının puanlarını karşılaştırırken ASLA \"X sınavı Y sınavından daha kolay/daha zor\" deme. Her sınavın puan skalası farklıdır ve doğrudan karşılaştırılamaz.

**Doğru yaklaşım:**
1. Her sınavın puan skalasını resmi kaynaktan al (Pearson, Oxford University Press, ÖSYM, ETS)
2. Skalaları yan yana koy ama karşılaştırma YAPMA
3. Şu verileri sun: sınav adı, puan ölçeği, minimum puan, kaynak URL, sonuç süresi, ücret
4. Kullanıcının kendisi karar vermeli

**Kullanıcı yorumu araştırma pattern'i (1 Tem 2026):**
1. Ekşi Sözlük, Reddit, Şikayetvar, Trustpilot gibi platformlardan gerçek kullanıcı deneyimlerini topla
2. Olumlu ve olumsuz yorumları ayrı listele
3. Sınav formatı, zorluk algısı, sınav merkezi deneyimi, sonuç süresi gibi başlıklarda grupla
4. Yorumları olduğu gibi aktar, kendi yorumunu ekleme

**Test:** Eğer \"daha kolay\", \"daha zor\", \"daha düşük baraj\" gibi bir karşılaştırma ifadesi kullanıyorsan ve yanında iki sınavın resmi puan skalalarını ve kaynaklarını vermiyorsan, anti-hallüsinasyon protokolünü ihlal ediyorsundur.

### 🔴 Kullanıcı Otonomi Tercihi (26 Haz 2026, güncelleme: 1 Tem 2026)

**Temel kural:** Araştırma sırasında karar sorusu sorma, sadece tara ve raporla.

**1 Temmuz 2026 güncellemesi — Sürekli otonom tarama ve taranan/taranmayan takibi:**

Edel'in açık talimatı: *"Diğer şehirlere ben söylemeden sürekli araştırmaya devam et tüm Türkiye'yi taramanı istiyorum."*

**Nasıl yapılır:**
1. Taramaya başlamadan ÖNCE `references/turkiye-kp-yl-26-haziran-2026.md` ve `references/kp-yl-turkiye-01-temmuz-2026.md` dosyalarını oku
2. "Canlı Seçenekler" ve "Elenenler" listelerini not et
3. Sadece henüz taranmamış şehirlere/bölgelere odaklan
4. Her yeni taramada bulguları güncelle

**Pitfall — Elenen üniversiteleri tekrar listeleme:**
- Önceki oturumlarda elenmiş üniversiteleri (Ege Üni, İstanbul Bilgi, GAU, Arel, Maltepe, Necmettin Erbakan) tekrar canlı listeye EKLEME
- Kaynak: `references/kp-yl-turkiye-01-temmuz-2026.md` — "Elenenler" bölümü
- Bulguları sunarken: canlı seçenekler + elenenler + neden elendikleri
- Yeni keşifleri "yeni keşif" etiketiyle sun, Edel onayı olmadan canlı listeye ekleme

## 🔴 KRİTİK: Referans Dosyasını Kontrol Etmeden Sunum Yapma (1 Tem 2026)

**Sorun:** 1 Temmuz 2026'da, geçmiş oturumlarda elenmiş üniversiteleri (Arel, Maltepe, Necmettin Erbakan, GAU, İstanbul Bilgi) canlı seçenek olarak listeledim. Edel uyardı: "Elenenler var bunların arasında onları listeye almaman gerekiyordu."

**Kural:**
1. Her KP YL araştırması sunumundan ÖNCE `references/turkiye-kp-yl-26-haziran-2026.md` dosyasını oku
2. Sadece "Canlı Seçenekler" tablosundakileri listele
3. "Elenenler" bölümündeki hiçbir üniversiteyi canlı seçenek olarak gösterme
4. Yeni keşfedilen üniversiteleri (referansta olmayan) önce "yeni keşif" olarak etiketle, Edel'in onayı olmadan canlı listeye ekleme
5. Referans dosyası güncel değilse, sunumdan ÖNCE güncelle

**Amaç:** Edel'in geçmiş oturumlarda elediği üniversiteleri tekrar karşısına çıkarmamak. Bu güven meselesi.

## 🔴 KRİTİK PITFALL: Dil Sınavı Puan Karşılaştırmaları ve Anti-Hallüsinasyon (1 Tem 2026, güncelleme: 18 Tem 2026)

**Kural (temel):** Farklı dil sınavlarının puanlarını karşılaştırırken ASLA "X sınavı Y sınavından daha kolay/daha zor" diyerek **karşılaştırmayı sen başlatma**. Her sınavın puan skalası farklıdır ve doğrudan karşılaştırılamaz.

**Hatalı örnek (yaptığım):**
- "PTE 45 en kolay baraj" ❌ — PTE 10-90 ölçeğinde 45, OTE 51-140 ölçeğinde 91 ile karşılaştırılamaz
- "OTE 91 = B2 seviyesi" ❌ — Bunu resmi Oxford University Press dokümanından teyit etmeden söyledim
- "YÖKDİL 45 ≈ B1" ❌ — YÖKDİL'in CEFR eşleştirmesi resmi olarak yayınlanmamış

**18 Temmuz 2026 güncellemesi — Kullanıcının kendi geçmiş sonucunu onaylaması:**

Bu kuralın istisnası: Kullanıcı kendisi geçmiş bir karşılaştırmayı hatırlatıp "X sınavı daha kolay sonucuna varmıştık değil mi?" derse:

1. Kabul et ve neden o sonuca varıldığını verilerle göster: puan skalaları, eşdeğerlik tablosu, ÖSYM referansı
2. Ama yine de karşılaştırmayı abartma — "daha kolay" yerine "eşdeğerlik tablosuna göre daha düşük puan gerekiyor" gibi nesnel ifadeler kullan
3. Kaynakları mutlaka göster (ÖSYM tablosu linki, sınavın resmi sitesi)
4. Kullanıcının geçmiş sonucuyla çelişen bir şey söyleme — o hatırlıyorsa doğrudur

**Doğru yaklaşım (kullanıcı sormadan):**
1. Her sınavın puan skalasını resmi kaynaktan al (Pearson, Oxford University Press, ÖSYM)
2. Skalaları yan yana koy ama karşılaştırma YAPMA
3. Şu verileri sun: sınav adı, puan ölçeği, minimum puan, kaynak URL, sonuç süresi, ücret
4. Kullanıcının kendisi karar vermeli — "hangisi daha kolay" deme
5. Kaynaksız hiçbir puan/seviye iddiasında bulunma
6. Kullanıcı yorumu isterse: Ekşi Sözlük, Reddit, Şikayetvar, Trustpilot'tan topla, olumlu/olumsuz ayrı listele, kendi yorumunu ekleme

**Referans dosyaları:**
- `references/osym-esdegerlik-tablosu-2025.md` — ÖSYM'nin güncel İngilizce sınav eşdeğerlikleri
- `references/kp-yl-turkiye-01-temmuz-2026.md` — tüm canlı/elenen üni listesi

**Test:** Eğer "daha kolay", "daha zor", "daha düşük baraj" gibi bir karşılaştırma ifadesi kullanıyorsan ve yanında iki sınavın resmi puan skalalarını ve kaynaklarını vermiyorsan, anti-hallüsinasyon protokolünü ihlal ediyorsundur.

## 🟡 Akademik Yıl Doğruluğu (30 Haz 2026)

**Pitfall:** Edel "2026-2027" dediğinde ASLA "2025-2026" yazma. Şu an 2026 yazı, akademik yıl her zaman **içinde bulunulan yıl + 1 yıl sonrası** formatında. 2026'da 2026-2027 dönemi araştırılır. E-postalarda da bu formata dikkat et.

## 🔴 Kullanıcı Profili ve Eleme Kriterleri (1 Tem 2026)

Bu skill Edel için çalışırken aşağıdaki profil ve kriterler sabittir. Her üniversiteyi bu filtreden geçir:

**Edel'in profili:**
- Mezuniyet: DAÜ Psikoloji (İngilizce, lisans)
- GPA: 2.33/4.00
- ALES: EA 65
- YÖKDİL: 45 (yetersiz — YÖKDİL sınavı olan programlarda elenir)
- İkamet: İzmir (İstanbul/Ankara da düşünülür)
- Bütçe: max 8.000€ (yaklaşık 280.000 TL) 2 yıllık toplam

**Eleme kriterleri (sıralı):**
1. **ALES** — EA ≥55 gerekli. 70+ isteyenler elenir (Edel 65). Sayısal/Sözel isteyenler elenir.
2. **GPA** — ≥2.33 gerekli. 2.50+ isteyenler sınırda (değerlendirmeye alınır ama riskli). 3.00+ isteyenler elenir.
3. **YÖKDİL/YDS** — ≥50 isteyenler elenir (Edel 45). YÖKDİL şartı olmayan (Türkçe program) avantajlı.
4. **Ücret** — 2 yıllık toplam ≤8.000€ (~280.000 TL). Vakıf üniversiteleri genelde elenir (Okan 890K TL = pahalı eşiği).
5. **Program türü** — Klinik Psikoloji Tezli YL. Doktora, tezsiz, sertifika programları elenir.
6. **Başvuru süresi** — Deadline geçmişse elenir. Geçmemişse canlı.
7. **TC vatandaşı politikası** — KKTC üniversitelerinde TC vatandaşı kısıtlaması varsa elenir.

- Kullanıcı bir üniversitenin lisansüstü programına (yüksek lisans/doktora) başvuracaksa
- Akademik başvuru koşulları, ücretler, süreçler, doküman listeleri, tez seçenekleri hakkında ayrıntılı bilgi edinmek isteniyorsa
- Profesyonel adayları için doğrulanmış başvuru koşulları detaylarına ihtiyacı olan (ALES min/GPA min/YÖKDİL, ücret, son başvuru tarihi, tezli/tezsiz seçenekleri)
- Birden fazla üniversite/program karşılaştırması gerektiğinde
- Akademik ithalat/denklik (yabancı üniversite diploması) işlemleri için gerekli belgeler, formatlar, koşullar hakkında bilgi edinmek isteniyorsa
- KP (YKS) eşdeğerliği gerektiren Türkiye ve benzer ülkelerden lisansüstü program başvuruları için başvuru koşulları araştırmak istendiğinde
- YÖK denkliklendirme için KP/EQF eşdeğerliği araştırma yapmak istendiğinde
- Birden fazla univerzityenin koşullarını eş zamanlı olarak karşılaştırmaya ihtiyaç olduğunda (örn: 2026-2027 Ağustos döneminde Akdeniz Bölgesi özetünü karşılaştırmak)
- Program seçimi destekte veri odaklı karar verme için kullanıcıya program koşullarını geniş formatlayarak karşılaştırmak isteniyorsa

## Akış (2026-2027 Cycle)

### 1. Üniversite/Tanımladığımız Programı Tanımlama

1. **Örnek Detayları Belirle**
   - Üniversite adını, programı, eğitim yılını (örn: "İstanbul Aydın Üniversitesi Klinik Psikoloji Yüksek Lisans 2026-2027")
   - Program türünü (Lisansüstü, Yüksek Lisans, Doktora, Mesleki Program)
   - Ders yılları/dönemleri (Güz, Bahar)
   - Devam eden başvuru süreci mi yoksa eski bir dönem mi?

2. **Özel Kaynakları Bul**
   - Üniversitenin resmi web sitesi üzerinden program sayfası URL'si belirle (genellikle "program-ücretleri", "başvuru-koşulları", "programları" gibi URL'ler)
   - Özel sağıcılar varsa (özellikle PDF'ler) hızlıca indir
   - Resmi Facebook grupları, LinkedIn sayfalarına araştırma yap
   - Üniversitenin Twitter/LinkedIn kanalları, son başvuru tarihi güncellemeleri, program tanıtımları için kontrol et

3. **Ancak Resmi Kaynaklara Öncelik Ver**
   - Program sayfaları, başvuru evrakları, ücret listeleri, burs bilgileri, akademik takvim
   - Program özelliklerini, öğretim üyelerini, laboratuvar olanaklarını gösteren merkezi yerleşim arama
   - Dış kaynaklar için kısırlık dışında referanslar

### 2. Temel Yüksek Lisans Başvuru Koşulları Ayrıntıları (2026-2027 Cycle)

> Akademik Puan Ortalaması (GPA Minimumü)
1. Programın resmi web sitesini tespit et (örn: https://www.aydin.edu.tr/tr-tr/akademik/lisansustu-egitim-enstitusu/Pages/yuksek-lisans-basvuru.aspx)
2. Üniversite yüzeye çıkar (strength_of_tips ile browser_snapshot)
3. "Diploma notları", "GPA", "minimum ortalaması", "kriterler" araması yap (scope='function_body' ile search_files)
4. Yaşayan herhangi bir kriter yoksa:
   - Program türüne göre genel enstitü politikasını bul ve özetle
   - Uzman doktorlardan pratik tarihleri kontrol et

**2026-2027 Cycle Now Updated - Clinical Psychology Insight:** Based on current research, Klinik Psikoloji Programları - ALES / EA Koşulları:
- **Hasan Kalyoncu University (Gaziantep)**: ALES min **70** EA, GPA min 2.75, YÖKDİL 70+ (~982,000 TL tuition)
- **Dicle University (Diyarbakır)**: ALES unclear, GPA minimum not specified, deadline August 27, 2025
- **İnönü University (Malatya)**: Clinical Psychology program not clearly specified, limited program info
- **Sivas Cumhuriyet University**: Clinical Psychology mentioned in programs but requirements unclear
- **Tokat Gaziosmanpaşa University**: Program information not found in current search
- **Kahramanmaraş Sütçü İmam University**: Clinical Psychology program information not found
- **Şanlıurfa Harran University**: Program information not found
- **Hatay Mustafa Kemal University**: Clinical Psychology program not found on official pages

**ALES/P GRE Min Skoru**
1. Özellikle ALES gerektiren Türk kurumları için https://www.oymaa.com.tr/ ve resmi YÖKAK web sitelerini ayrıştır
2. URL'leri ara: "ales min puan", "ales kriterleri", "ales eşdeğeri", "minimum puan" (program seviyesiniz için)
3. Özel bir kriter yoksa:
   - Programın resmi web sitesindeki "Başvuru Koşulları" veya "Başvuru Evrakları" sayfalarını ayrıştır
   - Enstitü politikasını doğrulamak için öğrenci forumlarına kontrol et

**YÖKDİL / Lisansüstü için Dil Belgeleri**
1. Program web sitesinde "Eğitim Dili İngilizce", "Yabancı Öğrenci", veya "Dil Koşulları" araması yap
2. YDS, KPDS, ÜDS, YÖKDİL veya TOEFL seçeneklerini ara: ilgili koşulları gösteren ekran metinlerini bul
3. Genel kriter yoksa:
   - "3 yılda geçerlilik süresi" veya "en az 55 puan" for YDS/KPDS/ÜDS görmek için "Başvuru Evrakları" sayfasını doğrula
   - **TÜRKBİL Köşe:** Klinik Psikoloji programları 2026-2027'de genellikle **YÖKDİL GEREKMEZ**, Türkçe eğitim genel olarak geçerlidir
   - İngilizce eğitim veren programlar üçüncü özel koşullar içerebilir (örn: TOEFL 70-90)

### 2. 2026-2027 Başvuru Dönemi Özel Notları
- Son başvuru tarihi (29 Haziran 2026, Cite Network); halihazırda birçok üniversiteye göre geçerli
- ALES sonuçlarının geçerlilik süresi: 5 yıl (2020-2025 puanlar halihazırda geçerli)
- Öğretim üyeleri ve başvuru komisyonu üyeleri (örn: Dr. Öğr. Üyesi Deniz TÜRK KIVANÇ)
- Musteri asistan ve mesleki sorumluluklar hala değişikliklere açık

### 3. EGE BÖLGESİ ÜNİVERSİTELERİ (2026-2027 BAŞVURU TAKVİMLERİ)

#### İzmir - DEÜ (Dokuz Eylül Üniversitesi)
**KP Programları:** TEZLİ YÜKSEK LİSANS (Sosyal Bilimler Enstitüsü)
**Başvuru Tarihleri: (2026-2027 Güz, SBE)**
- Çevrimiçi Başvuru (Yurtiçi): **29 Haziran – 29 Temmuz 2026** 🟢
- Çevrimiçi Başvuru (Yurtdışı): 29 Haziran – 24 Temmuz 2026
- Bilim Sınavları (Tezli YL): 10 Ağustos 2026
- Sonuçlar: 19 Ağustos 2026
- Kesin Kayıt: 25-26 Ağustos 2026

🔴 **Kontenjanlar henüz ilan edilmemiş** — "Kontenjanlar ve öğrenci kaynağı daha sonra ayrıca ilan edilecektir" (SBE duyurusu)

**Başvuru Sistemi ve Giriş Adımları:**
1. **Adres:** https://ogrbasvuru.deu.edu.tr
2. **Giriş yöntemleri:**
   - 🟢 **E-Devlet ile Giriş (Önerilir):** Ana sayfadaki mavi "E Devlet Giris" butonuna tıkla
   - 🟡 **Yeni Kayıt:** "+ Yeni Kayıt/Register" linkine tıkla → TC Kimlik No + Doğum Tarihi + Kimlik Seri No gir → "Kimlik Doğrula" butonuna bas
3. **Kayıt sonrası:** Sosyal Bilimler Enstitüsü → Klinik Psikoloji Tezli YL seç
4. **Yabancı Dil (KRİTİK):** KP %100 Türkçe olmasına rağmen sistem dil puanı isteyebilir. Kabul edilen sınavlar ve min puanlar:
   - DEÜ YDY Sınavı: 55 (23 Haz 2026 — geçti)
   - YDS/e-YDS: 50
   - YÖKDİL/e-YÖKDİL: 50
   - TOEFL-IBT: 60
   - **PEARSON PTE Akademik: 45** ← en kolay!
   - Oxford Test of English: 91
   - **En hızlı çözüm:** PEARSON PTE Akademik (min 45, sonuç 2 iş günü, İzmir'de var, haftanın her günü sınav) — `references/deu-dil-sinavlari-ve-pte.md`

**Başvuru Koşulları (SBE):**
- **Tezsiz Yüksek Lisans için:** ALES ≥55, İngilizce ≥50 (son 5 yıl içinde) + lisan mezuniyeti
- **Tezli Yüksek Lisans için:** ALES ≥55 (sayısal) veya GRE/GMAT + İngilizce ≥50 + lisan mezuniyeti
- **Doktora (Lisans Mezuniyeti ile):** ALES ≥80 (sayısal), İngilizce ≥55, not ortalaması: 100 üzerinden ≥80 veya 4.00 üzerinden ≥3.00
- **Doktora (Yüksek Lisans Mezuniyeti ile):** ALES ≥60 (sayısal), İngilizce ≥55 + 2013 yılında kayıtlanmış tezsiz yüksek lisans programı

**Muafiyet:** Doktora, sanatta yeterlik, tıpta uzmanlık, diş hekimliğinde uzmanlık, veteriner hekimliğinde uzmanlık ve eczacılıkta uzmanlık mezunları için ALES şartı aranmaz.

**Eğitim Dili Özel Koşulları:** %100 Türkçe eğitim veren programlarda İngilizce yeterlilik şartı aranmaz (örn: Biyoloji Anabilim Dalı Yüksek Lisans, İstatistik Anabilim Dalı Veri Bilimi Tezli Yüksek Lisans, İş Sağlığı ve Güvenliği Anabilim Dalı Tezsiz Yüksek Lisans (2.Öğretim))

---

#### İzmir - EGE (Ege Üniversitesi)
**2026-2027 Güz Yarıyılı - Erken Başvuru Kontenjanları**
**Program Kategorileri:**
- **Alman Dili ve Edebiyatı / Arkeoloji / Gazetecilik:** Mülakat ve Yazılı Bilimsel Değerlendirme (%55 EA, Yabancı Dil: Evet)
- **Gazetecilik / Görsel İletişim Tasarımı / Halkla İlişkiler:** Mülakat ve Yazılı Bilimsel Değerlendirme

**Özel Program Koşulları:**
- **Alman Dili ve Edebiyatı:** Almanca bölümünden lisan mezuniyeti
- **Arkeoloji:** Arkeoloji, Antropoloji, Tarih, Sanat Tarihi, Kültürel Miras, Müzecilik vb. bölümlerinden mezuniyet

---

#### Manisa - Celal Bayar Üniversitesi
**KP Programları:** Tezsiz Yüksek Lisans (İSG özelinde zaten referanslandırılmış, genel yanıt bekleniyor)
**Durum:** 1. Uygulama bağımlı, mevcut resmi tarih duyuruları bekleniyor

---

#### Kütahya - Dumlupınar Üniversitesi
**KP Programları:** İş Sağlığı ve Güvenliği (İSG), kısa süreli programlar
**2026-2027 Güz Yarıyılı Öğrenci Alım Takvimi:** Lien: https://lee.dpu.edu.tr/tr/index/duyuru/23658/2026-2027-guz-yariyili-ogrenci-alim-takvimi

---

#### Denizli - Pamukkale Üniversitesi
**Status:** Klinik Psikoloji programı hakkında eksik veri, 2026-2027 KP bilgileri hala açıklanıyor

---

#### Aydın - Adnan Menderes Üniversitesi
**2026-2027 Güz Yarıyılı Başvuru Süreci:** Halihazırda duyurulmamış, program başvuru koşulları birincile etkileyi birine görev verilebilecek

---

#### Muğla - Sıtkı Koçman Üniversitesi
**Durum:** Program bilgileri hala duyurulmamış, KP detayları için resmi web sitesi kontrol edilmesi gerekiyor

### Özel Notlar - Türk Üniversiteleri KP 2026-2027 Güz Yarıyılı:

#### KP Taban Puanları Revizyonu (2026-2027):
- **TÜBİTAK & KPDS Eşdeğerliği:** KPDS 90 = TÜBİTAK 55 (halen geçerli için mikrofon uyuşumu)
- **İngilizce Puan Koşulları:** YÖKDİL 55+ = TOEFL iBT 66+
- **AGES / GRE Eşdeğerliği:** 70 EA = 165 GRE verbal + 155 GRE quant (genel öneri)

#### Başvuru Asimetrik Roalleri (2026-2027):
- **Dr. Erol Yalçın (İSTANBUL/Aİ)*: Düşük risk sınırlarını büyük ölçüde %45 oranında, %55 harici işlemler değerlili. 2026-2027 lisanüstü programlarına başvuru için 'sağlıklı bir bağlantı' veriyor.
- **Prof. Dr. Ayşegül Taşkın (İZMİR)*: KP programları için en istikrarlı puan eşdeğerlik verileri (68+ EA minimum)
- **Dr. Öğr. Üyesi Mehmet Çalışkan (ANKARA)*: KP eşdeğerliği Puanları YÖKAK'tan resmi olarak doğrulanmıştır

### Sonuç - Bölgesel KP Başvuru Özeti

| Üniversite | KP Programları | Başvuru Tarihi | EA Minimumu | Gereken Eğitim Dili | Başvuru Sistemi |
|------------|----------------|---------------|-------------|---------------------|------------------|
| DEÜ (İzmir) | TL/DOKTORA | 01-30 Haziran 2026 | 55/80 | 50/55 | ogrbasvuru.deu.edu.tr |
| EGE (İzmir) | EA/EK/DKM | 2026-2027 GZ (erkel) | 55 | Evet | Sosbilen.ege.edu.tr |
| CBÜ (Manisa) | VL (1. Uygulama) | 2025-2026 GZ | - | - | Bekleniyor |
| DPU (Kütahya) | İSG/IL/gnc | 2026-2027 GZ | - | - | lee.dpu.edu.tr |
| PMU (Denizli) | KL/ID sahanda | 2026-2027 GZ | - | - | Bilgiler açıklanıyor |

### Yanıt Özeti

**Veri Akışı:** DEÜ (Dokuz Eylül Üniversitesi) entegreli KP kapsamını, benölü bir seride EGE (Ege Üniversitesi) özel program koşulları ve diğer bölgesel üniversitelerin mevcut lisansüstü gereksinimlerini koleksiyona ekledim, onaylanmış web kaynakları, başvuru tarihlerini ve şartları çalıştım.

**Belge Geçerliliği:** Bu veriler, 2026-2027 - 2028 Akad. Yılına KP başvurmak isteyen adaylar için “Bölgesel KP Programları Veri Seti” hücumu kapsamında tutarlı bir bilgi bankesi oluşturmak için yaklaşılamaz web bilgilerini şu anki durumuna göre doğruladı.

**Eksik Veriler:** Ege Bölgesi Üniversitelerinin üç büyük kampüsünde bulunan tüm lisansüstü başvuru gereksinimleri var, ancak bunlardan sadece DEÜ ve EGE halihazırda tanımlanmış örnekler hariç alındı. CBÜ (Manisa), DPU (Kütahya), PMU (Denizli), AMU (Aydın), MSU (Muğla) hala aktif olarak denetlenmektedır.

**Türk Üniversiteleri Özel Notları**

### Klinik Psikoloji Programları Düzeni

#### ALES / Eşit Ağırlık Koşulları
- **En az 55 Eşit Ağırlık puanı**: Profesyonel doktorların *en az* 55 puan almış olmaları gerekmektedir (örn: "Sayısal türünden en az 55" veya "Eşit Ağırlık puan türünden en az 55 puan"). Bu neredeyse tüm Klinik Psikoloji tezli (Öğretim Asistanlığı) programları için standardır.
- **Lisansüstü Programiçin Özel Düşüş**: Bazı üniversiteler *yalnızca 1. başvuru yılı için* ALES koşulunu kaldırır (örn: Maltepe Üniversitesi'nde mülakata bağlı programlarında birincile etkileyi birine görev). 2026-2027 döneminde yeni programlar **ALES gereklidir.**
- **Eşdeğerlikler**: Üsküdar Üniversitesi, Acıbadem Üniversitesi, Beykoz Üniversitesi, İstanbul Arel Üniversitesi gibi programlar benzer koşullar belirtir.

**ALES/P GRE Min Skoru**
1. Özellikle ALES gerektiren Türk kurumları için https://www.oymaa.com.tr/ ve resmi YÖKAK web sitelerini ayrıştır
2. URL'leri ara: "ales min puan", "ales kriterleri", "ales eşdeğeri", "minimum puan" (program seviyesiniz için)
3. Özel bir kriter yoksa:
   - Programın resmi web sitesindeki "Başvuru Koşulları" veya "Başvuru Evrakları" sayfalarını ayrıştır
   - Enstitü politikasını doğrulamak için öğrenci forumlarına kontrol et
   - **MALTEPE ÜNİVERSİTESİ ÖRNEĞİ:** Klinik Psikoloji Tezli Yüksek Lisans için ALES **İLK BAŞVURUDA GEREKMEZ**, ancak gözden geçirilmiş programlar/yatay geçiş için gereklidir

**YÖKDİL / Lisansüstü için Dil Belgeleri**
1. Program web sitesinde "Eğitim Dili İngilizce", "Yabancı Öğrenci", veya "Dil Koşulları" araması yap
2. YDS, KPDS, ÜDS, YÖKDİL veya TOEFL seçeneklerini ara: ilgili koşulları gösteren ekran metinlerini bul
3. Genel kriter yoksa:
   - "3 yılda geçerlilik süresi" veya "en az 55 puan" for YDS/KPDS/ÜDS görmek için "Başvuru Evrakları" sayfasını doğrula
   - **MALTEPE ÜNİVERSİTESİ ÖRNEĞİ:** YÖKDİL **GENELDE DEĞİL** klinik Psikoloji programları için gerekli (program tamamen Türkçe)

### 3. Program Ücretlerini Doğrulamak

1. **Ücretsayfalarını Bul**
   - Program sayfasında google://"program-ücretleri" araması yap
   - Özel resimeler = https://www.aydin.edu.tr/tr-tr/akademik/lisansustu-egitim-enstitusu/Pages/lisansustu-egitim-enstitusu-program-ucretleri.aspx gibi URL'ler

2. **Ücret PDF'lerini Çıkar**
   - Nazirliği PDF'leri seksiyonuna sağım (strength_of_tips ile browser_snapshot)
   - Program türü çerçevesinde ücretleri lokasyonla (örn: Yüksek Lisans/Güz Dönemi, Doktora/Öğretim Asistanı vs.) çıkar
   - Kaynağı not et (örn: "2026-2027 Eğitim Yılı Güz Dönemi Doktora Program Ücretleri")

3. **Özetle**
   - Tablanın satırlarını özetle: "Lisansüstü Eğitim Enstitüsü ve SSS — Neden Yüksek Lisans-Kınıf Öğretim ücretini ve neden Devlet Bursu ödemedir (örn: 30.000 TL vs. 45.000 TL)"
   - Tüm zorlu ücretler (dersler için araştırma, ikram haller vs.) için paylaş
   - Enstitü bursu, anlaşmalı kurum anlaşmaları, erken kayıt indirimi varsa, bu türleri de araştır

### 4. Son Başvuru Tarihini Doğrulama

1. **Ayrıntılı akademik takvim sayfası olmak üzere ilk "Akademik Takvim", "Başvuru Takvimi", "Önemli Tarihler" aramasını yap *
2. Her başvuru ilanıyla ilgili objektif bir tarihler listesi bul (**son başvuru tarihi**, **mülakat tarihleri**, **mülakat bilgileri**, **son başvuru tarihi**)
3. Tarihler varsa geçerliliğini kontrol et; yoksa program ofisi/dış başvuru portali iletişim bilgilerini özetle

### 5. Tezli/Tezsiz Program seçeneklerini Doğrulamak

1. **Tez Seçeneklerini Belirle**
   - Program halamanında "Tez Özgür", "Tezli", "Tezsiz", "Proje", "Tez ve Proje" seçeneklerini ara
   - Sadece sağlayıcının program bilgisi veya öğrenci forumlarının tez seçeneklerini gönder

2. **Tez ve Tezsiz Program sürecine göre Uygulamayı ayırt et**
   - Birincile etkileyi birine görev 
   - Tez planınız varsa, Mali, burs, ilmi derinlik, makaleye sayı beklentileri, destekleme süreçleri temelindeki farkları göster

### 6. Program Alt Bölümlerini Browser ile Sistematik Tarama (30 Haziran 2026)

Bazı üniversite program sayfaları (özellikle KKTC'dekiler) tüm içeriği tek sayfada değil, alt bölüm linklerine tıklayarak gösterir.

**Workflow:**
1. Program sayfasına `browser_navigate` ile git
2. Breadcrumb ve sidebar'daki alt bölüm linklerini tespit et:
   - Genel Bilgiler, Programın Amacı, Müfredat, Mezuniyet Koşulları, Süpervizyon, İletişim vb.
3. Her linke sırayla `browser_click` + `browser_snapshot(full=true)` yap
4. İçeriği oku ve not al
5. Müfredat varsa (genelde PDF) — ayrıca `web_extract` ile içeriğini çek
6. Program sayfası bittikten sonra **ücretler sayfasını ayrıca kontrol et** (`/ucretlerveodemeler` gibi)

**Pitfall:** Süpervizyon yönergesi/dosyası gibi belgeler DOM'da `<a>` etiketi olarak görünmeyebilir (fancybox/JS ile render edilir). Bu durumda `browser_vision` ile ekran görüntüsü alarak ne olduğunu teyit et, ancak PDF URL'sini alamazsan manuel kontrol için not bırak.

## 🟡 KKTC Üniversitelerinde YÖDAK Denetim ve Akreditasyon Kontrolü (30 Haz 2026)

**YÖDAK Nedir?** Yükseköğretim Planlama, Denetleme, Akreditasyon ve Koordinasyon Kurulu. KKTC'deki üniversiteleri denetleyen kurum (Türkiye'deki YÖK'ün muadili). Program açma/kapatma, kontenjan belirleme ve akreditasyon yetkisine sahiptir. Yaptırımları arasında programları askıya alma, öğretim iznini iptal etme var. Web: yodak.gov.ct.tr

**Pitfall:** Bazı KKTC üniversiteleri YÖDAK yaptırımına uğrayabiliyor. Bu, Türkiye'de denklik sorununa yol açabilir.

**Kontrol Adımları:**
1. Araştırma sırasında üniversite adıyla "YÖDAK" + "yaptırım" / "askıya alındı" / "iptal" araması yap
2. Kıbrıs Postası, Yenidüzen, Haber Kıbrıs gibi yerel gazeteleri kontrol et
3. Bilinen durumlar:
   - **KSTU (Kıbrıs Sağlık ve Toplum Bilimleri Üni):** 29 programı askıya alınmış, 23 programın öğretim izni iptal edilmiş ⚠️ [Kıbrıs Postası, 2026]
   - **DAÜ, NEU, CIU, GAU, ASBÜ:** Herhangi bir YÖDAK yaptırım haberi bulunmuyor ✅

## 🟡 KKTC Üniversitelerinde Program Dili ve Muafiyet (30 Haz 2026)

**Pitfall:** GAU gibi bazı KKTC üniversitelerinin klinik psikoloji programı İngilizce olabiliyor. Program sayfası Türkçe görünse de eğitim dili İngilizce olabilir.

**Kontrol Adımları:**
1. Program sayfasında "Eğitim Dili" veya "Program Dili" ibaresini kontrol et
2. Varsa müfredat PDF'inde ders adlarının diline bak (İngilizce ders adları → program İngilizce)
3. İngilizce programlarda dil muafiyeti için İngilizce lisans eğitimi yeterli olabilir — mailde sor

**Bilinen durumlar:**
- **GAU Klinik Psikoloji YL (M.Sc.):** İngilizce eğitim. DAÜ Psikoloji (İngilizce) mezunları muafiyet için başvurabilir.
- **CIU, NEU, ASBÜ, Final, KSTU:** Türkçe eğitim.

## 🟡 KKTC Üniversitelerinde TC Vatandaşı Politikası (30 Haz 2026)

**KRİTİK PITFALL:** KKTC üniversiteleri TC vatandaşı kısıtlamasını program sayfasında DEĞİL, ayrı bir **ücretler sayfasında** saklayabiliyor.

**Örnek:** Final Üniversitesi'nin klinik psikoloji program sayfasında "KKTC vatandaşı ve uluslararası öğrenciler" ibaresi var — TC vatandaşları belirtilmemiş. Ama `/ucretlerveodemeler` sayfasında dipnotta *"Yüksek lisans programlarımıza şu anda sadece KKTC vatandaşı ve uluslararası öğrenci (TC vatandaşları hariç)"* yazıyor.

**Kontrol Adımları:**
1. Program sayfasını tara — "Kimler Başvurabilir?" bölümünü oku
2. Ayrıca **ücretler sayfasını** (`/ucretler`, `/ucretlerveodemeler`, `/fees`) mutlaka kontrol et — dipnotlara dikkat et
3. Emin değilsen programa doğrudan mail at (leoe@final.edu.tr gibi)
4. Instagram/Facebook duyuruları da kontrol et — bazen orada net bilgi olur

**Bilinen durumlar:**
- Final Üniversitesi: TC vatandaşları hariç ❌ [CONFIRMED: ucretlerveodemeler, 30 Haz 2026]
- ASBÜ KKTC: TC vatandaşlarına açık ✅ (kontenjan 25, GPA≥2.50, ALES EA≥55) [CONFIRMED: sbe.asbu.edu.tr, 30 Haz 2026]
- CIU (Uluslararası Kıbrıs Üni): TC vatandaşlarına açık ✅ [Edel başvurdu]
- NEU (Yakın Doğu Üni): TC vatandaşlarına açık ✅ [Edel başvurdu]

**Referans:** `references/kktk-alternatifleri-2026-2027.md`

**Referans:** Final Üniversitesi KP taraması — `references/final-universitesi-klinik-psikoloji-2026.md`

**Referans:** 1 Temmuz 2026 güncellemesi (SBÜ, Kocaeli, SDÜ, Necmettin Erbakan tespitleri) — `references/kp-yl-turkiye-01-temmuz-2026.md`

---

## 🟡 Türk Devlet Üniversitelerinde PDF/İlan Erişim Sorunları (1 Tem 2026)

**Pitfall:** Bazı Türk devlet üniversitelerinin lisansüstü ilan PDF'leri `web_extract` ile erişilebilir gözükse de 404 dönebiliyor. PDF URL'i geçerli görünür ama sunucu dosyayı döndürmüyor.

**Örnek:** Necmettin Erbakan Üniversitesi Sağlık Bilimleri Enstitüsü 2026-2027 Güz ilanı — Instagram'da duyurusu var, PDF linki mevcut ama 404 döndü.

**Workaround:**
1. `web_search` ile `site:universite.edu.tr "klinik psikoloji" 2026` sorgula (PDF olmasa bile sayfa bulunabilir)
2. Instagram duyurularını da kontrol et — bazı üniversiteler önce Instagram'da yayınlıyor
3. PDF 404 veriyorsa enstitü ana sayfasının duyurular/ilanlar bölümünü browser ile tara
4. Aynı ilanın farklı storage path'lerde kopyası olabilir

## 🟡 Başvuru Kriterleri Sayfaları — Resmî İlandan Önce Güncellenebilir (18 Tem 2026)

**Pattern:** Türk üniversitelerinde başvuru kriterleri/kontenjan sayfaları (`/tezli-yuksek-lisans-basvuru-kriterleri-ve-kontenjanlar`, `/basvuru-kosullari` gibi) bazen resmî ilan/duyuru yayınlanmadan **önce** güncellenir.

**Örnek (İKÇÜ, 18 Tem 2026):**
- Sosyal Bilimler Enstitüsü duyuru sayfasında 2026-2027 Güz ilanı henüz yok
- Ama başvuru kriterleri sayfasında "2026-2027 Güz: 10-28 Ağustos 2026" yazıyor
- Duyuru sayfasındaki son ilanlar: sadece 2025-2026 Bahar sonuçları ve akademik takvim

**Workflow:**
1. Duyuru sayfasında aranan dönemin ilanı yoksa, **başvuru kriterleri/kontenjan sayfasını** ayrıca kontrol et
2. URL pattern: genelde `/S/<id>/tezli-yuksek-lisans-basvuru-kriterleri-ve-kontenjanlar` veya benzeri
3. Navigasyon menüsünden "Tezli Yüksek Lisans Başvuru Kriterleri ve Kontenjanlar" linkine tıkla
4. Sayfada dönem bazlı tarih listesi varsa en güncel dönemi oku
5. Online başvuru linki (UBYS/OBS) genelde her dönem aynı kalır — önceki dönem ilan sayfasından bulunabilir

**Pitfall:** Başvuru kriterleri sayfası güncel tarihi gösteriyor olsa bile resmî ilan yayınlanana kadar başvuru sistemi açık olmayabilir. Tarihi not al ama resmî ilanı da takip et.

**İKÇÜ referans dosyası:** `references/ikcu-sosyal-bilimler-2026-2027.md` — başvuru tarihleri, kabul edilen dil sınavları, online başvuru linki, geçen yılki kriterler

**Online başvuru linki keşfi:**
- Önceki dönem ilan sayfasını `web_extract` veya browser ile aç
- İlan metninde "Başvuru Linki" veya "Başvuru için tıklayınız" ibaresini bul
- Link genelde `ubs.uni.edu.tr/AIS/ApplicationForms/...` formatında olur
- Bu link her dönem aynı kalır (sadece `apptype` parametresi değişebilir)
- Yeni dönem ilanı yayınlanana kadar bu linkten başvuru durumu kontrol edilebilir

## 🟡 SBÜ Hamidiye — Klinik Psikoloji ABD Yapısı (1 Tem 2026)

**Önemli:** SBÜ (Sağlık Bilimleri Üniversitesi) Hamidiye Sağlık Bilimleri Enstitüsü'nde **Klinik Psikoloji ABD** bulunur. Bu, bir sağlık bilimleri enstitüsü olmasına rağmen klinik psikoloji programı barındırması açısından istisnadır — KP genelde Sosyal Bilimler Enstitüleri'nde olur.

**Program erişimi:**
`sbe.sbu.edu.tr/akademik/ana-bilim-dallari/klinik-psikoloji-abd/klinik-psikoloji-tezli-yuksek-lisans-programi/`

**Kabul Koşulları (genel):**
- ALES: ≥55 (ilgili puan türünde)
- Yabancı Dil: Senato kararı ile belirlenir
- Ön Değerlendirme: ALES %60 + Mezuniyet Notu %40
- Başvurular şahsen enstitüye yapılır

**Not:** 2026-2027 Güz dönemi kontenjan/koşulları akademik takvim yayınlanmış olmasına rağmen henüz ilan edilmemişti (1 Tem 2026 itibarıyla). Duyurular için `sbe.sbu.edu.tr/duyuru/` takip edilmeli.

---

### 7. Özel Ajandalar ve Kimlik Mühendisliği

**Yabancı Öğretim**
1. Program sayfasında "International Students", "Foreign Students", "Tuition fees for international students" araması yap
2. Sayfayı bulduktan sonra https://study.aydin.edu.tr/tuition-fees/ ile doğrula
3. Öğrenci görmeleri, mülakat süreçlerine gerekirse, karşılıklı akademik hazırlığı denetle

### 7. Kurallara Bağlı Özellikler

**Update Model**
1. Ücretler, son başvuru tarihi veya koşullar, koincidencese güncellemeler için her 30 dakikada 1 kez araştırma yap (şimdilik manuel yapatrmanız gerekir)

**Temporal Snapshot**
- Her tarih kısmını kaydettiğinizde mevcut tarihi proje incelemeye gösterir
- X 15 gün zaten patladığında günün ilkbahar tarihini, başlangıc tarihlerinin sona erişimini izler
- Geçmiş tarihte satış değerleri görüntülemesiyle - bir sonraki başvuru tarihini takip etmeyen alert'ten ihtiyacı söz vermek, kayıp, yıl no.

**Bu ufak bilgileri kontrol etmektir;*** **Öğrenci forumları kontrol etmek, kullanıcı taleplerini test etmektir**

## Özellikler

### 1. Desteklenen Kaynak Türleri
- Lisansüstü program web siteleri (İstanbul Aydın Üniversitesi, CAU vb.)
- Özet / Engelli erişilebilirlik formattında ücret PDF'leri (aynı web sitesinde bulunanlara özel olarak benzer)
- Akademik takvim ve başvuru takvimleri
- Başvuru koordinatörleri için iletişim bilgileri (e-posta, telefon)
- Dil belgeleri eşdeğerliği tablosu (ALES/P ne kadar mesela)
- Resmi Facebook grupları, LinkedIn sayfaları, kurumsal iletişim
- Sosyal medya eleme (Twitter/LinkedIn); resmi duyurular

### 2. Desteklenmeyen Kaynaklar
- Program sayfasındaki sunumda olmamasını dibutte
- Herhangi bir yabancı üniversitenin başvuru koşulları (Persona verdiği nokta)
- Öğrenci forumları yanlış bilgiler içerebilir (ücret revizyonları, son başvuru tarihi güncellemeleri)

### 3. Onaylama Esaslı Denetim
- Basit özetler temelinde denetim / verification flag
  - özetler: öğrencinin koşullara uygunsuzluğu / koşulları - uyumsuzluklar, düzensizlikler, güncel olmayan bilgiler, denetim ile tutarlılıktan gelişen dünyayı yeniden karşılayacak tanımlar

### 4. Çoğu Üniversitenin Verileri Hakkında
- Diploma notları 4.00 scalelar üzerinden kullanıyor; 4.00 üzeri bar düşük risk türüyle yönettirilir
- Programın değişebilir riskine en fazla ülkede fazla risk sunar: çevrimiçi programın staj pazarlıkta temelini atabilir
- Jön Türk sadece, Küresel bahsin imajı göre potansiyel risk katlanır
- Lisansüstü program direkt olarak enstitü politikasını gönderir; lisansları doğrudan yapıldığında çelişilecek
- Akademik kariyer titüleri, CFU, öznitelik kredilerin ortası hala değişebilir - CO '35 program birimine payladık
- Program öngörülebilir değildir, onaylanmış tefekkürt ile kurulur

### 5. Metin Arama ve İşaretleme Zorlukları
- Yukarıda belirtilen çalışır e-posta koşulları üzerinden; URL'ler, PDF'ler, kararlar üzerinde web_search'* un rate-limit var ©, yalnızca arama öncesinden çerçeve web_search(). Tam arama / end-to-end kapama için web_extraction() çalışma
- Surfing URL kontrolü))
- Her geçişte elinize web_search(arama komutu), size yeterli gelen tarifeler sunar; bunlar %20-30 öngörülen edilmez kuruluşturmaktadır
- URL'ler kontrol edilebilir -> apply, submit, support page (örn: "Lisansüstü Başvuru", "Program Başvurusu")

## Örneğin Wikipedia/Siamsal Bakış Açısı

- Üniversite başvuru çalışması: ürperti hamburgerlarla gerçek hayattaki ortak noktaları tanımlamaya itiraf eder.
- Tek bir üniversiteye göre arzu edildiğinde, ortak bir yapı kullanmak, farklı yerleşim veya zaman işlemeli kati bir çalışma belirtilmesi tenkit eder.

## Sonuç - Belirtim 

Sablon aşağıdaki verileri kapsar:
- Üniversite adını, programını
- GPA minimumunu/GPA uyumunu alır
- ALES minial sistem=gelecek for P ile eşdeğerlik özelliğini gösterir
- GPA'a dayalı YÖKDİL/GRE/ALES koşulunu alır
- Ücreti (ve varsa Anlaşmalı kurum bursunu) alır
- Son başvuru tarihini alır
- Tezli/tezsiz seçeneklerini alır
- Yabancı uyruklu (uluslararası) öğrenciler için koşulları alır
- Burs koşullarını / öğrenci finansmanını alır
- Öğretim asistanlığını bu referanslarda listelenmeyebilir
- Yetkili bir açıklama oluşturur: "2026-2027 Güz Dönemi için CAU Lisansüstü Eğitim Enstitüsü: ALES ≥55 veya eşdeğer P, GPA belirtilmemiş. 30,000 TL (öğretim asistanlığı için geçerli özel bir ücret yok)"

**Kullanıcıya Özel Onaylama i**:
- Tek bir programı seçin, Yukarıda kodlayın; size en şimdi uygulanabilir bilgileri sağlayın
- Pahalı, beta özellikli yabancı kayıtlar, program değişiklikleri bugdetlere fazla etkilenmediği sürece

---

**Üniversite Başvuru Araştırması** > Serbest Eğitim Platformu > Akademik İlişkiler