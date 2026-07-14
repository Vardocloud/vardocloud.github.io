---
name: email-workflow
description: "E-posta gönderme onay akışı ve Türkçe mail üslubu. Gmail API, SMTP veya herhangi bir e-posta kanalı kullanmadan ÖNCE uygulanması gereken adımlar."
version: 1.0.0
author: Vanitas (Edel için)
---

# E-posta İş Akışı — Edel İçin

## Neden Bu Skill Var?
**2026-06-11:** Google Workspace Gmail API'yi kullanarak NEU'ya (`burs@neu.edu.tr`) direkt mail gönderdim. Edel'in taslağı görüp onaylamasını beklemeden terminal'den `gmail send` çalıştırdım. Edel'in tepkisi: *"Kafayı yedin, nereye göndereceğini sorup onay alsana."*

Bu skill, aynı hatayı tekrarlamamak için zorunlu adımları tanımlar.

## Mail İçerik Kuralları (15 Haziran 2026, güncelleme: 24 Haziran 2026)

### Kural 8: GPA Muafiyet Talebi Mili — Güçlü Yanları Öne Çıkar

GPA şartını karşılamadığın durumlarda mail atarken:
- GPA'yı savunma ("aslında iyiydi ama...") — bunu yapma
- Diğer güçlü yanları sırala: ALES puanı, iş deneyimi, İngilizce lisans, sertifikalar
- "Şartı karşılamasam da değerlendirmeye alınabilir miyim?" diye kısa ve net sor
- Uzun açıklama yapma, akademisyenler kısa mail okur

**Örnek mail taslağı:** `references/gpa-muafiyet-talebi-maili.md` — FSMVÜ'ye atılan gerçek mail (24 Haziran 2026)

### Kural 9: Mailde Program Türünü Doğru Belirt

### Kural 9: Mailde Program Türünü Doğru Belirt

Sayfada tezsiz program yoksa mailde "tezsiz" diye belirtme. Sayfada ne varsa onu yaz.
Siteden teyit ettikten sonra maili yaz.

### Kural 10: Başvuru/Ücret Sayfasında Uyruk Kısıtlamasını Kontrol Et (30 Haziran 2026)

### Pitfall: Maili Atan Kişi ile İmza İsmi Farklı Olabilir (30 Haziran 2026)

**Durum:** Himalaya/SMTP config'inde display-name (örn: "Edel Reister") ile mail imzasındaki isim (örn: "Sudenaz Kara") farklı olabilir. Bu teknik olarak mailin gönderilmesini engellemez ama karşı tarafın kafasını karıştırabilir.

**Yapılacaklar:**
- [ ] İmza ismi Edel'in belirttiği kişiye aitse ve bu kişi config'deki display-name'den farklıysa, Edel'e bildir: "Mail [config'deki isim] hesabından gidecek ama imzada [farklı isim] yazacak. Sorun olur mu?"
- [ ] Edel onaylarsa sorun yok — devam et
- [ ] Edel onaylamazsa: ya config'deki display-name'i değiştir ya da imzayı config'deki isme uyarla

### Kural 11: Mailde Sadece En Kritik Soruları Sor (30 Haziran 2026)

**Kural:** Mail taslağında 7'den fazla madde varsa, Edel'in kısaltma talebi gelme olasılığı yüksektir.

**Doğru:** Maksimum 5-7 soru, en kritik olanlara odaklan.
**Yanlış:** Sitede net olmayan her şeyi tek mailde sormak (müfredat, kontenjan gibi teyit edilebilecek detaylar dahil).

**Kontrol listesi:**
- [ ] Her soruyu ele: "Bu soruyu çıkarsam Edel'in kararını etkiler mi?"
- [ ] Etkilemiyorsa çıkar (ör: müfredat detayı, kontenjan sayısı)
- [ ] Sitede kısmen de olsa erişilebilen bilgileri mailde sorma (ör: PDF bulunabiliyorsa müfredatı oradan oku)

Not: Bu kural Kural 1'in (sitede olmayan bilgileri sor) daraltılmış versiyonudur. Sitede olmasa bile, Edel'in kararını etkilemeyecek detayları sorma.

### Kural 12: Mailde Program Türünü Doğru Belirt

Sayfada tezsiz program yoksa mailde "tezsiz" diye belirtme. Sayfada ne varsa onu yaz.
Siteden teyit ettikten sonra maili yaz.

### Kural 13: Başvuru/Ücret Sayfasında Uyruk Kısıtlamasını Kontrol Et (30 Haziran 2026)

Bazı üniversiteler (özellikle KKTC'dekiler) başvuru/ücret sayfalarında **uyruk kısıtlaması** belirtir. Bunu mail taslağını hazırlamadan önce kontrol et ve varsa mailde sorulacak sorulara ekle.

**Örnek:** Final Üniversitesi ücretler sayfasında: *"Yüksek lisans programlarımıza şu anda sadece KKTC vatandaşı ve uluslararası öğrenci (TC vatandaşları hariç) öğrenci kaydı alınmaktadır."*

**Yapılacaklar:**
- [ ] Program sayfasından sonra **ücretler sayfasını** da mutlaka tara (`/ucretlerveodemeler` gibi)
- [ ] Uyruk kısıtlaması varsa mail sorularına EKLE: "TC vatandaşları başvurabiliyor mu?"
- [ ] KKTC üniversitelerinde bu kontrole özellikle dikkat et

**Kontrol listesi — ücret/başvuru sayfasında ara:**
- "TC vatandaşları hariç"
- "sadece KKTC vatandaşı"
- "uluslararası öğrenci"
- "yalnızca ... uyruklu öğrenciler"

**Pitfall:** Bu bilgi genellikle program sayfasında DEĞİL, ücretler sayfasında veya başvuru koşulları sayfasında yer alır. Program sayfasını taradıktan sonra ayrıca ücretler sayfasını da kontrol et.

## Mail İçerik Kuralları (15 Haziran 2026)

### Kural 1: Sadece Sitede Olmayan Bilgileri Sor

Mailde sorulacak sorular, yalnızca web sitesinde bulunamayan veya ulaşılamayan cevaplar olmalıdır.

**Doğru:** Sitede ücret, deadline, ALES şartı yok → mailde sor
**Yanlış:** Sitede ders içeriği/süre varsa bile mailde tekrar sorma

**Kontrol listesi:**
- [ ] Web sitesini tara — hangi bilgiler mevcut?
- [ ] Web_extract ile program sayfasını, ücret sayfasını, admission sayfasını oku
- [ ] Sitede olan bilgileri mailden ÇIKAR
- [ ] Sadece sitede OLMAYAN veya NET OLMAYAN bilgileri sor

**İstisna:** Web sitesi çok eski (2+ yıl güncellenmemiş) veya erişilemez durumdaysa, doğrulama amaçlı sorulabilir.

### Kural 2: İmza — Sadece İsim Soyisim

Mail altına sadece ad ve soyad yazılır. Ünvan, okul bilgisi, telefon, bölüm eklenmez.

**Doğru:**
> Edel Reister

**Yanlış:**
> Edel Reister | DAÜ Psikoloji Mezunu | 05XX XXX XX XX

**Gerekçe:** Aşırı bilgi vermek gereksizdir. Karşı taraf ihtiyaç duyarsa zaten sorar.

### Kural 3: İmza Adını Edel'e Teyit Ettir (PITFALL — 15 Haziran 2026)

Maili atan kişi, konuşmayı yapan kişi olmayabilir. Edel başkası adına veya farklı bir isimle mail atıyor olabilir.

**Doğru akış:**
- Taslağı yazarken imzayı varsayma — Edel'in ismini kullanma
- Taslağı gösterirken imzayı sor: "İmzaya ne yazayım?"
- Edel ismi söylediğinde kullan — "Edel Reister" beklerken "Mertcan Siyah" diyebilir

**Yanlış:**
- Konuşma Telegram'da Edel'le → "Edel Reister" yaz → Edel düzeltir
- Bir önceki mailde "Edel Reister" kullanıldı diye her seferinde aynı ismi kullanma

**Kontrol listesi:**
- [ ] Edel'e imzaya hangi ismi yazacağını SOR
- [ ] İsmi değiştirdikten sonra taslağı son kez göster
- [ ] Değişiklik yapıldıysa "gönder" onayını YENİDEN al (eski onay geçersizdir)

### Kural 4: Yapmadığın Başvuruyu Yapmış Gibi Yazma (17 Haziran 2026)

Burs başvurusu, kayıt gibi idari işlemleri **henüz yapmadıysan mailde yapmış gibi gösterme**. Karşı taraf kontrol ettiğinde tutarsızlık çıkar, güven sıfırlanır.

**Doğru:** "Başvurmayı değerlendiriyorum" / "Burs imkanlarını araştırıyorum"
**Yanlış:** "Burs başvurumu da ilettim" (henüz iletmediysen)

**Kontrol listesi:**
- [ ] Mailde geçen her "başvurdum" / "gönderdim" ifadesi gerçekten yapıldı mı?
- [ ] Emin değilsen "değerlendiriyorum" / "planlıyorum" gibi kesin olmayan ifade kullan

### Kural 5: Ücret Sorusu — Burssuz ve Burslu Toplam 2 Yıllık İste (17 Haziran 2026)

Program ücreti sorarken **ders başı değil, toplam 2 yıllık maliyeti sor**. Ayrıca burslu ve burssuz farkını aynı soruda birleştir.

**Doğru:**
> TC uyruklu öğrenciler için Klinik Psikoloji Tezli YL'nin toplam 2 yıllık ücreti net olarak nedir? Ders başı €450 üzerinden mi hesaplanıyor, yoksa dönemlik sabit ücret mi var? Toplam kaç ders alınıyor? Ayrıca lisansüstü eğitim bursu kapsamında neler karşılanıyor, burssuz ve burslu toplam maliyet ne olur?

**Yanlış:**
> "Ders ücreti €450 mi?" (eksik — toplam maliyet bilinmez)
> "Burs ne kadar?" (eksik — burssuz kıyaslama yok)

### Kural 7: İş Sıralaması — Önce Mevcut İşi Bitir (21 Haziran 2026)

Mail/görev akışında **yeni bir konuya geçmeden önce mevcut mail işini bitir**. Edel "mail işini bitirmemiz lazım" derken yeni bir araştırmaya/konuya dalmamalısın.

**Doğru:**
- Mail taslağını göster → kişisel notları bekle → onay al → gönder → sonra diğer konu
- Edel "ben şimdi şuna da bakarım" derse bile, sen mail işini tamamlamış ol

**Yanlış:**
- Mail taslağı hazır, kişisel not bekleniyor → araya İtalya araştırması sıkıştır
- Edel "mail işini bitirelim" dediğinde hâlâ başka konularla meşgul olmak

**Tetikleyici:** Edel "bekle", "hemen başlama", "önce şunu bitirelim" gibi sıralama sinyali verdiğinde anında dur, mevcut göreve odaklan.

### Kural 6: Mail Atma Sebebini Kısaca Belirt (17 Haziran 2026)

Telefonla ulaşamadıysan, **neden mail attığını bir cümleyle açıkla**. Bu hem insani bir bağlam kurar hem de "neden aramadı da mail attı" sorusunu önler.

**Doğru:**
> "KKTC'yi aramak için yurt dışı paketi gerektiğinden telefonla ulaşamadım, o yüzden size yazıyorum."

**Ne zaman eklenir:** Yurt dışı numarası söz konusuysa, ofisin telefonuna ulaşılamadıysa, WhatsApp'tan cevap alınamadıysa.

### Adım 0: Alıcı Adresini Doğrula

Maili göndermeden önce alıcı adresinin geçerli olduğunu teyit et:

**Kontrol yöntemi:**
1. Kullanıcı bir email adresi verdiğinde (örn: "adaylisansustu@ciu.edu.tr") → web_search ile site:domain.com "email@domain.com" yap
2. Adresin üniversitenin resmi "İletişim" sayfasında listelendiğini doğrula
3. Eğer adres resmi sitede yoksa veya bulunamazsa → kullanıcıya bildir: "Bu adresi resmi sitede teyit edemedim, yine de göndereyim mi?"
4. Adres doğrulandıktan sonra normal akışa devam et

**Pitfall:** Kullanıcının verdiği adres eski/yanlış olabilir (üniversite adres değiştirmiş olabilir). Her zaman resmi siteden doğrula. Doğrulama 10 saniyeden uzun sürmez.

## ZORUNLU — Her E-posta Öncesi 4 Adım (+ Adım 0)

### Adım 1: Taslağı Telegram'da Göster
Mail taslağını yaz, `send_message` ile Edel'e Telegram'dan gönder. Taslakta şunlar olmalı:
- Kime: (alıcı adresi)
- Konu:
- Tam metin
- Not: "Taslak — onaylarsan göndereyim"

### Adım 2: Açık Onay Bekle
Ancak **Edel'in açıkça "gönder" veya "at" demesi** durumunda bir sonraki adıma geç.

Aşağıdakiler **onay değildir**, sadece inceleme sinyalidir:
| Sinyal | Anlamı |
|--------|--------|
| "göster" / "show me" | Sadece görmek istiyor |
| "değiştir" | Daha düzeltilecek şey var |
| "olmuş mu" | Onay değil, geri bildirim istiyor |
| "tamam" (tek başına) | Belirsiz — teyit et: "göndereyim mi?" |
| Sessizlik | CEVAP BEKLE — asla kendin atlama |

**Kesin onay sinyalleri:**
| Sinyal | Anlamı |
|--------|--------|
| "gönder" | ✅ |
| "at" | ✅ |
| "evet" (bir önceki soruya yanıt olarak) | ✅ |
| "oldu gönder" | ✅ |

### Adım 3: Son Kez Göster + Net Onay Sorusu Sor\nTaslağın son halini gösterip NET bir seçenek sun:\n\n**Doğru:**\n> \"Onaylıyorsan yeşil tuş — gönder veya gönderme, karar senin.\"\n\n**Yanlış (muğlak):**\n> \"Nasıl buldun?\"\n> \"Eklemek istediğin bir şey var mı?\"\n\nEdel'den beklenti: \"gönder\", \"at\", \"oldu gönder\" gibi net bir komut. Net komut gelmezse sormaya devam et.\n\n**Düzeltme (2026-06-15):** Edel \"onay mekanizması yazsaydın keşke\" dedi — yani butonlu/net seçenekli bir onay adımı bekliyor. Sadece \"nasıl buldun?\" sormak yeterli değil, gözüne \"gönder / vazgeç\" seçeneğini koy.\n\n### Adım 4: Onaydan Sonra Gönder\nAncak Adım 3'te net onay alındıktan sonra Gmail API veya herhangi bir e-posta aracını çalıştır.

## Kritik Kural: Önceki Maille Benzerlik

Daha önce aynı kuruma farklı bir mail gönderildiyse, **yeni mail hiçbir cümle yapısını, kelime seçimini veya tonu tekrar etmemeli**. Aynı kurumdaki kişiler iki maili karşılaştırıp "aynı kişi yazmış" diyebilir.

**Kontrol listesi:**
- Giriş cümlesi tamamen farklı kelimelerle yazıldı mı?
- Sorular aynı olsa da ifade ediliş biçimi değişti mi?
- Resmi adlar (program adı, kurum adı) dışında ortak kelime var mı?
- Kapanış/ hitap farklı mı?
- Test: "Bu iki metni aynı kişi mi yazdı?" sorusuna cevap "hayır" olmalı.

## Kural İhlali = Güven Kaybı
Bu akışı atlamak Edel'in Vanitas'a olan güvenini doğrudan zedeler. Kural:
- Memory'de kayıtlı
- Bu skill'de kayıtlı
- Google Workspace skill'inde de kayıtlı (oraya erişilemiyorsa bu skill yedek)

## Türkçe Mail Üslubu
Edel doğal, insansı, robotik olmayan bir dil bekler. Detaylar için `references/edel-mail-uslubu.md` dosyasına bak.

- **GPA muafiyet maili şablonu:** `references/gpa-muafiyet-maili.md` — FSMVÜ örneği üzerinden GPA şartını karşılamadığında atılacak mail formatı (24 Haz 2026)

## Referans Mektubu Talebi

Referans mektubu prosedürü hakkında detaylı bilgi: `references/referans-mektubu-proseduru.md`
- Generic (genel) vs spesifik referans mektubu farkı
- NEU burs başvurusunda referans mektubu teslim şekli
- Ülkelere göre prosedür karşılaştırması

Referans isteyeceğin hocalar için hazır şablon: `templates/referans-maili.md` (iki versiyon — temel ve gelişmiş).
Çalışan ve onaylanmış versiyon: `templates/referans-maili-calisan.md` (Gökçe Yılmaz Akdoğan ve Hasan Ergüler için, DAÜ Psikoloji).

### Referans Mektubu Prosedürü Araştırma Yöntemi

Edel referans mektubunun nasıl işlediğini sorduğunda:
1. **Bilmiyorsan "bilmiyorum, araştırayım" de** — halüsinasyon görme
2. Üniversitenin başvuru sayfasını web_extract ile kontrol et
3. Hâlâ net değilse Claude.ai prompt'u hazırla (Edel kendisi sorar)
4. Claude prompt formatı: durumu anlat + spesifik sorular + "kaynaklara dayanarak cevapla"
5. Edel'in sorusu "halisünasyon görmeden cevapla" uyarısı içeriyorsa — kesin bilmediğin konuda "bilmiyorum, araştırayım" yanıtını ver

### ⚠️ KRİTİK: Vanitas Mail Yazmaz — AI Aracına Yönlendir

**2026-06-13:** Edel'in net düzeltmesi: *"Mail yazmada iyi değilsin bunu daha iyi yapacak bir araç bulabilir misin?"*

Bu nedenle **referans mektubu talebi de dahil tüm profesyonel/akademik maillerde** şu kural geçerlidir:

**Vanitas taslağı kendisi yazmaz.** Bunun yerine:
1. Bir AI email writing tool bul (Mailmeteor, DraftEmail vb.)
2. Tool'u kullanarak maili yazdır
3. Çıktıyı Edel'e Telegram'da göster
4. Onay al → gönder

Detaylı araç listesi: `references/ai-email-writing-tools.md`

**Tool çalışmazsa** (headless bot koruması, CORS, JS hatası) → Fallback'e geç: Vanitas kendi yetenekleriyle doğal dilde yazar (detay: `references/ai-email-writing-tools.md` → Fallback bölümü)

### Bu Oturumdan Dersler (2026-06-13) — WARP + Headless Chrome

Edel, Mailmeteor aracını kullanmamı istedi. Headless Chrome'da submit butonu disabled kaldı. İlk tepkim "çalışmıyor" oldu — Edel'in tepkisi:

> *"WARP bazı sitelerin açılmasını önleyebiliyor haberin olsun ya modunu değiştir ya da kapatıp dene. Headless tarayıcıda çalışmıyor ne demek alternatif yöntemin var mı?"*

**Dersler:**

1. **"Çalışmıyor" deme** — alternatif yöntemleri sırayla dene:
   - WARP kapat (`ALL_PROXY=""`)
   - JS native value setter ile React state güncelle
   - browser_console ile programmatic click dene
   - Farklı araç dene
   - En sonda Fallback'e geç

2. **WARP her şeyi çözmez** — aslında Mailmeteor WARP yüzünden değil, bot detection yüzünden çalışmıyordu. WARP'ı kapatmak bu sorunu çözmedi. Ama yine de denemek lazım.

3. **JS hack çalıştı** — native value setter ile buton aktif hale geldi (`document.querySelector('button.submit-btn').disabled = false`). API call'ı muhtemelen CORS/Cloudflare yüzünden başarısız oldu.

4. **Pollinations API key sorunu:** API key `sk_` ile başlıyor ama `setApiKey` auth hatası verdi. Muhtemelen key süresi dolmuş veya endpoint değişmiş. `getBalance` ile kontrol edilebilir.

**Çözüm:** AI mail yazma araçları için önce web aracını dene, çalışmazsa Vanitas kendi yetenekleriyle yaz — ama doğal dilde, önceki hatalardan ders alarak. `references/ai-email-writing-tools.md`'de detaylı akış ve JS hack'leri var.

Edel, Gökçe Yılmaz Akdoğan ve Hasan Ergüler'den (DAÜ Psikoloji) referans mektubu isteyecek. CV'lerini analiz ettim ve taslak geliştirme sürecinde şu noktalar öğrenildi:

**1. Doğal dil + akademik derinlik dengesi:**
- Sadece "doğal/insancıl" yetmez — akademisyenler deadline, tablo, CV teklifi gibi somut detaylar bekler
- Ama "Sayın Yetkili" tonu da itici — ikisinin arası bulunmalı

**2. Referans mailinde olmazsa olmazlar:**
- Hocayı hatırlatma (ders adı + dönem + varsa proje/not hatırlatması)
- Program adı, üniversite, deadline
- CV + transkript + niyet mektubu teklifi
- Zaman planı: "En geç X'te tüm belgeleri göndereceğim"
- Proaktif: "İhtiyacınız olursa bildirin"

**3. İlk maili hocanın beyninde yer etmeli:**
- Hocanın sizi hatırlamasını sağlayacak ipucu bırak
- "Dersinizde şu projeyi yapmıştım" gibi somut bir detay
- Çok genel olursa hoca "kimdi bu?" diye bakar

**4. Kaynak:** Stanford Academic Advising ve MIT Drennan Lab rehberleri — `templates/referans-maili.md`'de detaylı

## Niyet Mektubu (SOP) Yazımı

Yüksek lisans başvuruları için Statement of Purpose / Niyet Mektubu yazarken uygulanacak workflow.

### SOP Yapısı — 4 Sinyal (Admit-lab / Dr. Philippe Barr)

Komitenin baktığı 4 sinyal ve her biri için gereken bilgiler:

| Sinyal | İhtiyaç | ❌ Jenerik | ✅ Somut |
|---|---|---|---|
| **1. Entelektüel motivasyon** | Spesifik anı/deneyim | "İnsanlara yardım etmek" | "Adliyede velayet davasında şu an..." |
| **2. Akademik hazırlık** | Öne çıkan dersler, tez, araştırma | "Psikoloji okudum" | "Klinik Psikoloji, Psikopatoloji, Araştırma Yöntemleri" |
| **3. Uygulamalı deneyim** | Staj, gönüllülük, pratik — NE öğrendin? | "Staj yaptım" | "VR'la fobi terapisinde ön görüşme senaryosu hazırladım" |
| **4. Program uyumu** | Neden BU program? Spesifik neden | "İyi üniversite" | "KKTC'de konumlanması, Türkçe eğitim, süpervizyon imkanı" |

### SOP Yazım Workflow'u

```
1. VERİ TOPLAMA → transkript + LinkedIn/CV + sertifikalar (tümünü oku)
2. İÇERİK → GPT 5.4 Mini (Yazar ajanı) ile taslak yazdır
   (Memory kuralı: Karusal metinler için sohbet modeli DEĞİL, özel ajan kullan)
3. HUMANIZE → humanizer skill'i ile AI izlerini temizle (29 pattern)
4. DOĞRULAMA → her iddiayı kaynağa karşı kontrol et (PITFALL aşağıda)
5. SON DOKUNUŞ → Edel kendi sesini eklesin
```

### PITFALL: Doğrulanmamış Bilgiyi SOP'a Koyma (17 Haziran 2026)

**Hata:** NEU Hastane'de staj imkanı olduğunu SOP'ta kesin bilgi gibi sundum. Edel sordu: "Emin olduğumuz bilgi mi?" Web'de teyit edemedim — varsayımdı.

**Kural:** SOP'ta geçen her kurumsal iddia (staj imkanı, laboratuvar, hoca ismi, kontenjan) **web_extract ile doğrulanmış** olmalı. Doğrulanamayan bilgi SOP'a GİRMEZ.

**Kontrol listesi:**
- [ ] "X üniversitede Y imkanı var" → site:edu.tr'de doğrulandı mı?
- [ ] "Şu hoca şu alanda çalışıyor" → akademik sayfada teyit edildi mi?
- [ ] Emin değilsen ÇIKAR — yokluğu, yanlışın varlığından iyidir

### PITFALL: Sayısal Veride Trend Yönünü Ters Okuma (17 Haziran 2026)

**Hata:** Transkriptte CGPA 2.57'den 2.33'e düşmüş. SOP'ta "GPA yükseliş trendi" diye yazdım. Edel düzeltti: "GPA yükselmedi düştü."

**Kural:** Transkript okurken:
- CGPA sütununun İLK ve SON değerini karşılaştır
- "Yükseliş" demeden önce genel trendi kontrol et (tek dönem GPA'si yüksek olabilir ama CGPA düşmüş olabilir)
- Düşük GPA'yı SOP'ta savunma — komite transkripti zaten görecek. Onun yerine deneyimlere odaklan

**Kontrol listesi:**
- [ ] CGPA ilk değer → son değer: artış mı, düşüş mü?
- [ ] "Yükseldi" demeden önce iki değeri yan yana yazıp kontrol et
- [ ] Düşüş varsa SOP'ta GPA'dan bahsetme — sessiz geç

### PITFALL: LinkedIn Profili Eksik Veri (17 Haziran 2026)

**Hata:** LinkedIn "Save to PDF" çıktısı Projects, Volunteer, Recommendations, Courses bölümlerini içermedi. CV'de bu bölümler eksik kaldı.

**Çözümler (sırayla dene):**
1. Edel'den tam profil çıktısı iste
2. puppeteer + CDP 9222 ile profile git — ama login duvarı çıkabilir
3. web_extract LinkedIn'i DESTEKLEMEZ — zaman kaybetme
4. Fallback: Edel eksik bölümleri manuel kopyalar

**Kontrol listesi:**
- [ ] PDF çıktıda kaç sayfa var? 4 sayfa az — bölümler eksik olabilir
- [ ] Projects, Volunteer, Recommendations, Courses bölümleri CV'ye eklendi mi?
- [ ] Eksik bölüm varsa Edel'e sor — varsayımla doldurma

### AI Detection Bypass

SOP ve diğer akademik metinlerde AI detection'dan kaçınmak için:
- **Humanizer skill'i:** 29 AI pattern'ini temizler (em dash, "pivotal", "additionally", "not only but also", vs.)
- **Harici araçlar:** StudyAgent (Turnitin bypass, akademik ton korumalı), StealthGPT
- **Tespit mantığı:** Modern dedektörler perplexity + burstiness ölçer

Detaylar: `references/ai-detection-araclari.md` ve `references/sop-yapisi.md`
- **NEU'ya özel bilgi bankası:** `references/neu-bilgi-bankasi.md` — doğrulanmış/doğrulanmamış NEU bilgileri, iletişim hiyerarşisi, mail takvimi
