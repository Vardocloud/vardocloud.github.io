# APA Alternative Sources & Content Rotation

> Edel'in isteği: "aynı yazıları tekrar tekrar işleme" — daha spesifik, ilginç ve çeşitli içerik getir.
> 25 Haziran 2026

## Problem

Standart APA kanalları (Gmail bültenleri, Monitor dergisi, Events sayfası) günde 3 kez tarandığında:
- Aynı etkinlikler 3 ayrı cronda raporlanıyor
- Bültenler haftada 1-2 kez geliyor, diğer zamanlarda [SILENT]
- Aynı makaleler farklı bültenlerde (Editor's Choice + Science Spotlight) tekrarlanabiliyor
- Monitor yeni sayı ayda 1 kez çıkıyor (Temmuz-Ağustos sayısında sadece 2 makale)

Sonuç: Cron günde 3 kez çalışıyor ama çoğu zaman [SILENT] veya daha önce bildirilen etkinlikleri tekrar gösteriyor.

## Çözüm: Döngü Sistemi

Standart kanalları HER seferde tara ama [SILENT] dönüyorsan — aşağıdaki alternatif kaynaklardan birine yönel. Günde 3 run'ı farklı içerik türlerine dağıt:

| Run | Öncelik | Alternatif (standart kanal boşsa) |
|-----|---------|-----------------------------------|
| **Sabah (09:15)** | Gmail bültenleri + Güncel haberler | APA Speaking of Psychology podcast — son bölüm |
| **Öğlen (15:15)** | APA Monitor + Etkinlikler | APA Division blogları (Div 12, 29) |
| **Akşam (22:15)** | Gün boyu gelen mailler | APA Clinical Practice Guidelines — güncelleme var mı? |

## Alternatif Kaynaklar (Standart Kanallar Boş Olduğunda)

### 1. 🎧 Speaking of Psychology Podcast

APA'nın resmi podcast'i. Haftalık yeni bölüm.

- **URL**: https://www.apa.org/news/podcasts/speaking-of-psychology
- **Tüm bölümler**: https://www.apa.org/news/podcasts/speaking-of-psychology/listen
- **İçerik türü**: Uzman röportajları, güncel araştırma derinlemesine
- **Kontrol sıklığı**: Haftada 1-2 kez (yeni bölüm çıktıysa)
- **Klinik değer**: Yüksek — doğrudan klinik pratiğe uygulanabilir konular

**Edel için değeri:** Konuşma formatında, dinlemesi kolay, klinik pratikle bağlantılı. Transcript alınıp wiki'ye eklenebilir.

**Workflow**:
1. `web_extract` ile podcast listesini çek (son 5 bölüm)
2. Daha önce işlenmiş bölümlerle karşılaştır (wiki'de `~/wiki/apa-podcast/` altında)
3. Yeni bölüm varsa: bölüm sayfasını `web_extract` ile aç, özet çıkar
4. Klinik anlam: "Bu bölüm terapide nasıl kullanılır?"
5. Wiki'ye kaydet: `~/wiki/apa-podcast/YYYY-MM-DD-episode-slug.md`

### 2. 🏛️ APA Division Blogları ve Yayınları

APA'nın 54 division'ı (alt birimi) kendi alanlarında blog/yayın yapar. Edel için en kritik olanlar:

| Division | Alan | Blog/Yayın | URL |
|----------|------|------------|-----|
| **Div 12** | Klinik Psikoloji | Society of Clinical Psychology blog | https://div12.org/blog/ |
| **Div 12** | Klinik Psikoloji | Treatments (kanıt temelli tedaviler) | https://div12.org/treatments/ |
| **Div 29** | Psikoterapi | Psychotherapy Bulletin | https://div29.org/ |
| **Div 17** | Kariyer Psikolojisi | SCP Blog | https://div17.org/ |
| **Div 35** | Psikoloji ve Kadın | Feminism & Psychology blog | https://www.apadivisions.org/division-35/ |
| **Div 43** | Aile Psikolojisi | Family Psychology blog | https://www.apadivisions.org/division-43/ |

**Edel için değeri:** Division blogları, Monitor'dan daha spesifik, alan-derinlemesine içerik sunar. Div 12 özellikle kanıt temelli tedaviler için birincil kaynak.

**Workflow**:
1. `web_extract` ile Div 12 blog'unu tara (son 5 post)
2. Daha önce işlenmiş postları kontrol et (wiki `~/wiki/apa-divisions/` altında)
3. Yeni post varsa: içeriği özetle + klinik anlam çıkar
4. **Sadece Div 12 ve Div 29** — diğerleri sadece belirgin bir konu varsa

### 3. 📋 APA Clinical Practice Guidelines (CPG)

APA'nın kanıt temelli klinik rehberleri.

- **URL**: https://www.apa.org/practice/guidelines
- **Güncelleme sıklığı**: Yılda 1-3 kez yeni rehber veya revizyon
- **Mevcut rehberler**: Depresyon, OKB, PTSD, Yeme Bozuklukları, Ağrı Yönetimi
- **Edel için değeri**: Çok yüksek — doğrudan klinik protokoller

**Workflow**:
1. Ayda 1 kez kontrol et (her seansta değil)
2. Güncelleme/seçki varsa: rehberin özetini çıkar + Bardo'da uygulanabilirliğini değerlendir
3. Wiki'ye kaydet: `~/wiki/apa-cpg/`
4. [SILENT] dönmektense bu kanala bakılabilir

### 4. 📰 APA PsycNet — En Çok Okunanlar

PsycNet'te trend olan araştırmalar.

- **URL**: https://psycnet.apa.org/
- **Popüler makaleler**: https://psycnet.apa.org/search/results?sort=popularity
- **Yeni yayınlar**: https://psycnet.apa.org/search/results?sort=dateDesc
- **Kontrol sıklığı**: Haftada 1 kez (sabah run'ında)
- **Edel için değeri**: Güncel araştırma trendlerini gösterir

**⚠️ NOT**: PsycNet Incapsula benzeri bir koruma kullanabilir. `web_extract` çalışmazsa zorlama — atla.

### 5. 📧 APA Membership e-news (sadece özel sayılar)

Normalde APA üyelik/promosyon mailleri ATLANIR. Ancak ayda 1 kez gelen özel sayıları (örn: "APA 2024 Trend Report", "Member Benefits Guide") değerlendirmeye alınabilir.

**Workflow**:
- Newsletter değil, rapor/özel yayın ise → değerlendir
- Promosyon/indirim ise → ATLA
- Karar: içeriğe bak, başlığa değil

### 6. 🌐 APA'nın Diğer Web Kanalları

| Kaynak | URL | Ne İçin |
|--------|-----|---------|
| APA News | https://www.apa.org/news | Güncel psikoloji haberleri |
| APA Science | https://www.apa.org/science | Araştırma fonları, bilim politikası |
| APA Education | https://www.apa.org/education | Eğitim kaynakları, CE |
| APA Monitor (doğrudan) | https://www.apa.org/monitor | Monitor dergisi online |

## Rotasyon Mantığı

Amaç: Her run'da farklı bir kanaldan içerik getir. Aynı kanalı günde 3 kez kontrol etme.

```
Run 1 (sabah): Standart Gmail bültenleri + varsa Speaking of Psychology
Run 2 (öğlen): Standart Monitor/Events + varsa Div 12 blog
Run 3 (akşam): Standart gün içi mailler + varsa PsycNet popüler
-- Hepsinde [SILENT]? → Hiçbir şey yok, sessiz kal.
```

## Output Format (Alternatif Kaynaklardan)

Standart APA bülten formatı dışında, alternatif kaynaklardan gelen içerik şu formatta sunulur:

```
📡 ALTERNATİF KANAL: [Kaynak Adı]
─────────────────────────

🎧 [Podcast Bölüm Başlığı] — Speaking of Psychology

📋 Konu: ...
🎙 Konuşmacı: [Uzman ismi + kurum]
💡 Klinik Anlam: ...
🔗 [Link]

🆕 vs ❄️ etiketi: İlk kez görülen bir kaynaksa "🆕", daha önce işlenmişse ve güncelleme varsa "❄️"
```

**Önemli:** Alternatif kaynaklardan içerik getirdiğinde bunun standART bültenden FARKLI olduğunu belirt. "Standart kanallarda yeni içerik yoktu, bunun yerine APA Speaking of Psychology'de yeni bölüm buldum" gibi bir giriş cümlesi koy.
