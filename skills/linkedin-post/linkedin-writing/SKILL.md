---
name: linkedin-writing
description: "LinkedIn post yazma metodolojisi — Hakan Türkçapar üslubu, 6 katman yapısı, NotebookLM ile transkript tabanlı post üretimi"
version: 1.3.0
metadata:
  hermes:
    tags: [linkedin, writing, content, psychology, turkish]
    category: linkedin-post
---

# LinkedIn Post Yazma Metodolojisi

Bu skill, LinkedIn postlarının **içerik ve üslup** boyutunu yönetir. API paylaşımı ve OAuth için `linkedin` skill'ine başvur.

## Referans Dosyaları

- `references/turkcapar-writing-samples.md` (üst skill'de: `linkedin-post/linkedin/references/turkcapar-writing-samples.md`) — Hakan Türkçapar'ın gerçek blog yazıları

## Ne Zaman Kullanılır

- Edel için LinkedIn postu yazarken
- APA semineri / etkinlik transkripti varsa post üretirken
- Post üslubu konusunda emin değilsen

## Yazım Stili: Hakan Türkçapar

**Temel prensipler:**
- Sıcak, samimi, sohbet eder gibi anlatım. Okuyucuyla "birlikte düşünelim" havası kur.
- Akademik altyapılı ama herkesin anlayacağı günlük dil. Jargonu sadeleştir.
- Soruyla açmak iyi bir tekniktir: "Peki bunun işe yaradığını nereden bileceksiniz?"
- KISA paragraflar (maks 1-2 cümle). Uzun paragraflar okuyucuyu kaybettirir.
- Otoriter değil, merak uyandıran, düşündüren bir ton.
- Anlatımda sıralama şart: önce giriş → sonra detay → sonra sonuç. Atlama yapma.
- İngilizce terimleri Türkçeleştir (AI → yapay zeka, ama her yerde değil — akıcılığa göre karar ver).
- Doğal bağlaçlar kullan: "Yani...", "Dahası...", "Bu demek oluyor ki...", "Belki de..."
- Postun ne anlattığı ilk okumada anlaşılmalı.

**Stil referansı:** Üst skill'in `references/turkcapar-writing-samples.md` dosyasındaki örnekleri birebir incele. O örneklerdeki:
- Soruyla açma tekniği
- Kısa paragraf yapısı
- Günlük dilden akademik derinlik
- "Birlikte düşünelim" hissi
- Hiçbir zaman uzun ve karmaşık cümle kullanılmaması

### Seminer/Toplantı Postları İçin Zorunlu Yapı

Şu üç bölüm EKSİKSİZ olmalı:

1. **SEMİNERİN KÜNYESİ:** Tam adı, tarihi, düzenleyen kurum, panelistler ve hangi kurumdan oldukları. Örn: "APA'nın 24 Haziran'da düzenlediği panelde Meadows Institute'tan Kacie Kelly, APA'dan Aubrey ve FDA'da görev yapmış Audrey bir araya geldi."

2. **İÇİNDE KONUŞULANLAR:** Panelistlerin spesifik söyledikleri, çarpıcı noktalar, verdikleri örnekler. Her panelistin katkısını ayrı ayrı belirt. Sadece isim sayma — ne dediklerini de anlat.

3. **SONUÇ / ANA MESAJ:** Panelden ne çıktı, neden önemli, okuyucuya kalan düşünce ne? "Panelin ortak mesajı şuydu..." veya "Panelin bana sorduğu soru şu..." ile bağla.

**Uyarı — Kaçınılması Gerekenler:**
- Seminere giriş vermeden direkt panelist görüşlerine atlama
- Sadece "X şöyle dedi, Y böyle dedi" sıralaması yapma, sonucu anlatmadan bitirme
- Gereksiz benzetmeler (örn: "pencil for brain surgery" gibi zorlama analojiler)
- Akademik jargonu sadeleştirmeden olduğu gibi bırakma

### 6 Katman Yapısı (Alternatif Yapı)

1. **Vurucu giriş** — 1 cümle, okuyucuyu içine çeken, düşündüren. Dolambaçsız olsun, "düşünelim istedim" gibi kibar filler kullanma.
2. **Kaynak referansı** — "APA'nın [tarih]'daki [başlık] panelinde..."
3. **Yani / çıkarım** — **ASLA ATLANMAZ.** Bu katman olmazsa post anlamsızlaşır. Veriyi sıralayıp bırakma — anlamı da anlat.
4. **Araştırma detayı** — Spesifik bulgu, panelden çarpıcı nokta.
5. **Dahası / ek detay** — "Dahası..." ile bağlanan ikincil bulgu.
6. **Vurucu kapanış** — Okuyucunun aklında kalan tek bir fikir bırak. Asla havada bırakma.

### Makale/Araştırma Tabanlı Post Yapısı

Bir APA makalesini veya araştırma raporunu (Datapoint, araştırma özeti, literatür taraması) post olarak işlerken seminer yapısından farklı bir yaklaşım gerekir:

1. **VERİYİ KOY** — Doğrudan araştırmanın ne olduğunu söyle. Kim, nerede, kaç kişiyle, ne buldu? Giriş dolambaçsız olsun — "düşünelim istedim" gibi fazla kibar girişlerden kaçın.

2. **SOMUT RAKAMLARI VER** — En çarpıcı 1-4 veriyi sayılarıyla göster. Sadece liste yapma, cümle içinde akıt.

3. **ANLAMI AÇIKLA** — En kritik katman. Bu olmazsa post havada kalır. Verdiğin sayıların ne anlama geldiğini söyle. "Yani..." ile bağla.

4. **VURUCU KAPANIŞ** — Postu bir cümlede toparla. "Aynı beceriler. Sadece etiket farklı." gibi akılda kalan bir kapanış.

**Kritik uyarılar:**
- "Bu sayılar bana bir şey hatırlattı" gibi yapay geçiş cümleleri kullanma — doğrudan anlamı anlat.
- Veriyi sıralayıp bırakma — okuyucu "ee?" diye sorar.
- Giriş + veri + sonuç döngüsü tamamlansın. Eksik katman varsa post yarım kalır.

## Uluslararası Araştırma Kaynaklarıyla Çalışma

Ne zaman ki postun kaynağı ABD/uluslararası bir araştırma (APA Monitor, Lightcast, PubMed, yabancı üniversite yayını vb.), **dili ve çerçeveyi Türkiye okuyucusuna göre yapılandır.** Aksi halde okuyucu "bu benimle mi ilgili?" diye düşünür.

### Kritik Kural: Coğrafi Çerçeveyi Netleştir

Kaynak hangi ülkede/örneklemde yapıldıysa, BUNU İLK PARAGRAFTA belirt. Belirtmezsen:

- ❌ "Mezunlarımızın en sık kullandığı beceriler..." → Kimin mezunları? Okuyucu Türkiye'deki kendi mezuniyetini düşünür.
- ✅ "APA'nın Amerika'da 1.26 milyon psikoloji lisans mezunu üzerinde yaptığı araştırmaya göre..." → Çerçeve net.

### Üç Adımlı Dönüşüm

1. **Kaynağın coğrafyasını tanımla** — "Amerika'da yapılan bu araştırma...", "APA'nın ABD verilerine dayanan çalışması..."
2. **Sayıları/örneklemi olduğu gibi ver** — Veri nereden geliyorsa oraya ait olduğunu gizleme. "1.26 milyon profil" dendiğinde okuyucu zaten ABD ölçeği olduğunu anlar.
3. **Köprüyü son paragrafta kur** — "İster Amerika'da olun ister Türkiye'de..." veya "Bu becerilerin karşılığı her yerde var" gibi bir kapanışla okuyucuya bağla. Araştırma yabancı ama mesaj evrensel.

### Örnek Kullanım

Uluslararası kaynak için **yanlış:**
> "Psikoloji lisans mezunlarımızın iş hayatındaki kıymeti üzerine düşünelim..."

Uluslararası kaynak için **doğru:**
> "APA'nın geçtiğimiz günlerde yayımladığı Datapoint makalesi, Amerika'da 1.26 milyon psikoloji lisans mezununun profilini analiz ederek çarpıcı bir tablo çiziyor."
> [...]
İster Amerika'da olun ister Türkiye'de — bu becerilerin karşılığı her yerde var.

### Lightcast/LinkedIn Veri Süsü

APA'nın Datapoint serisi gibi Lightcast/LinkedIn profil verileriyle çalışırken yüzdelerin toplamı 100 değildir — çünkü her profil birden fazla beceri etiketleyebilir. Okuyucunun kafasında soru işareti kalmasın diye açıklama ekle:

> "Toplam 100 değil — aynı kişi birden fazla beceriye sahip olabiliyor, bu yüzden yüzdeler ayrı ayrı hesaplanıyor."

Bu açıklamayı ya doğrudan sayıların yanında ya da hemen altındaki paragrafta ver.

### NotebookLM'de Dikkat

NotebookLM'e prompt gönderirken **uluslararası kaynak olduğunu açıkça belirt** ve post dilinin buna göre yapılandırılmasını iste. Yoksa NotebookLM veriyi "bizim mezunlarımız" gibi genel bir dille yazar.

## Hashtag Kullanımı

- Post sonuna ayrı satırda 3-4 hashtag eklenebilir
- Konuya uygun seç: #Psikoloji #YapayZeka #RuhSağlığı #DijitalSağlık #AI #MentalHealth gibi
- Her zaman Edel'e onaylat — onaysız ekleme yapma
- Eski kural (hashtag yasaktı) güncellendi, Edel onayıyla artık kullanılıyor

## Görsel Üretim Prosedürü

1. **Önce post metnini yaz** — Hakan Türkçapar stilinde
2. **Post metninin ANA FİKRİNİ 1-2 cümlede özetle** — en vurucu mesaj ne?
3. **Bu ana fikre uygun görsel prompt'u oluştur** — İngilizce, betimleyici, 3-5 cümle. Post içeriğiyle doğrudan ilgili olmalı.
4. Renk paleti post'un tonuna uygun olsun (sıcak/soğuk/profesyonel)
5. "no text no letters no words no watermarks" ZORUNLU
6. "minimalist professional clean composition" ekle
7. SOYUT/SEMBOLİK yaklaş — gerçekçi insan figürü yerine minimal kompozisyon
8. 1-2 ana unsur yeterli, karmaşık sahneler saçmalıyor

**Model:** kontext (FLUX.1 Kontext — prompt'u en iyi takip eden)
**Boyut:** 1200×628
**Seed:** Her seferinde RASTGELE (1-999999) — asla sabit seed kullanma!
**Yöntem:** `generateImage` KULLAN (MCP API key'ini otomatik kullanır, base64 döner)
**Kullanma:** `generateImageUrl` — URL 401 döner (API key eklenmez)

## APA Makale Tabanlı Post Üretimi (Web → Wiki → NotebookLM Workflow)

APA Monitor makaleleri üzerinden post üretirken izlenecek adımlar:

### Adımlar

1. **Browser ile sayfaya git** — `web_extract` APA sayfalarında çoğu zaman özet döndürür, tam metin için browser kullanılır
   - `browser_navigate(url)` ile sayfayı aç
   - `browser_snapshot(full=true)` ile tam metni al
   - Grafik varsa `vision_analyze` ile sayısal verileri oku
2. **Tam metni wiki'ye yaz** — `~/wiki/apa-articles/<baslik>.md` olarak kaydet
3. **NotebookLM'e dosyadan ekle** — URL olarak değil, `source_add(file_path=..., source_type="file")` ile. URL olarak eklendiğinde NotebookLM bazen sayfanın sadece özetini alır.
4. **NotebookLM'e sorgu gönder** — aşağıdaki prompt'u kullan
5. **Citation'ları temizle ve kaynak kontrolü yap**

### NotebookLM Prompt'u

```text
Bu kaynağa dayanarak, Hakan Türkçapar üslubunda bir LinkedIn postu yaz.

KURALLAR:
- Dil: Türkçe, sıcak, samimi, günlük konuşma dili
- Akademik altyapılı ama herkesin anlayacağı sadelikte
- "Birlikte düşünelim" havası, otoriter değil
- 500-750 karakter
- KISA paragraflar (maks 1-2 cümle)
- HASHTAG KULLANMA (sonra elle eklenir), emoji KULLANMA, soru sorma (CTA yasak)
- "terapi" ve "#terapi" kelimesini KULLANMA
- Gereksiz benzetmelerden kaçın
- Makale adı, APA ve (varsa) örneklem büyüklüğünü REFERANS VER
- En çarpıcı 2-4 veriyi sayılarıyla belirt
- Sadece veriyi sıralama, altındaki anlamı da anlat
- Kaynak uluslararası bir araştırmaysa, coğrafi çerçeveyi net belirt (örn: "Amerika'da 1.26 milyon profil üzerinde yapılan araştırma"), "bizim mezunlarımız" gibi Türkiye'ye özgü ifadeler KULLANMA
```

### Kaynak Kontrolü (ÖNEMLİ)

NotebookLM kalabalık notebook'larda (20+ kaynak) bazen yeni eklenen kaynak yerine eski bir kaynaktan yanıt üretebilir. Yanıtın doğru kaynağa dayandığından emin olmak için:
- `sources_used` alanını kontrol et — yeni eklediğin kaynağın ID'si orada mı?
- Şüphe varsa, citation'ları temizle ve yanıtı elle düzelt

## Transkript Tabanlı Post Üretimi (NotebookLM Workflow)

Bir APA/etkinlik transkripti varsa, postu elle yazmak yerine NotebookLM'e yazdır.

### Adımlar

1. **Transkripti al** — Google Drive'dan indir veya mevcut transkript dosyasını kullan
2. **NotebookLM'de yeni notebook oluştur** — `notebook_create()`
3. **Transkripti kaynak olarak ekle** — `source_add(file_path=..., source_type="file")`
4. **NotebookLM'e sorgu gönder** — aşağıdaki prompt'u kullan

### NotebookLM Prompt'u

```text
Bu transkripte dayanarak, Hakan Türkçapar üslubunda bir LinkedIn postu yaz.

KURALLAR:
- Dil: Türkçe, sıcak, samimi, günlük konuşma dili
- Akademik altyapılı ama herkesin anlayacağı sadelikte
- "Birlikte düşünelim" havası, otoriter değil
- 500-750 karakter
- KISA paragraflar (maks 1-2 cümle)
- HASHTAG KULLANMA (sonra elle eklenir), emoji KULLANMA, soru sorma (CTA yasak)
- "terapi" ve "#terapi" kelimesini KULLANMA
- Gereksiz benzetmelerden kaçın
- Seminere giriş (tarih, isim, panelistler) mutlaka ver
- Panelistlerin spesifik söylediklerine yer ver
- Sadece görüşleri sıralama, toplantının ana sonucunu da anlat
- Kaynak uluslararası bir araştırmaysa, coğrafi çerçeveyi net belirt (örn: "Amerika'da 1.26 milyon profil üzerinde yapılan araştırma"), "bizim mezunlarımız" gibi Türkiye'ye özgü ifadeler KULLANMA
```

5. **Citation'ları temizle ve kaynak kontrolü yap** — NotebookLM yanıtındaki [1], [2] gibi referans işaretlerini kaldır.

   **ÖNEMLİ: NotebookLM kalabalık notebook'larda (20+ kaynak) bazen yeni eklenen kaynak yerine eski bir kaynaktan yanıt üretebilir.** Yanıtın doğru kaynağa dayandığından emin olmak için:
   - `sources_used` alanını kontrol et — yeni eklediğin kaynağın ID'si orada mı?
   - `references` alanındaki alıntılanan metnin, yeni eklediğin kaynakla eşleştiğini doğrula
   - Şüphe varsa, notebook'u yalnızca o kaynakla bırakıp yeniden dene veya yanıtı elle düzelt
   - Özellikle APA Bilgi notebook'u gibi eski ve kalabalık notebook'larda bu risk yüksektir
6. **Hashtag ekle** — elle 3-4 uygun hashtag ekle
7. **Edel'e göster** — Post metnini sun, onay bekle

## Post Revize İçin NotebookLM Kullanımı (4 Temmuz 2026)

Edel hazırlanan post taslağını beğenmezse, **önce NotebookLM MCP ile yeniden yazdır**, alternatif yöntemlere atlamadan.

### Workflow

1. Mevcut post metnini `linkedin_posts_archive.json`'dan al (status: pending_approval)
2. NotebookLM MCP `ask_question` tool'una şu prompt'u gönder:
   ```text
   Şu LinkedIn post metnini daha akıcı, profesyonel ve ilgi çekici şekilde yeniden yaz. APA referansını koru. Türkçe, doğal sohbet havasında, kısa paragraflar. Hakan Türkçapar tarzı: soruyla başla, Yani..., Dahası... bağlaçları kullan.

   Post metni:
   "[post metni buraya]"
   ```
3. NotebookLM MCP auth sorunu varsa (authenticated: false):
   - `delegate_task` ile subagent'a dene — subagent'lar MCP tool'larını görebilir
   - Subagent da çalışmazsa, ancak o zaman arşivdeki diğer pending_approval post'a geç
4. Citation'ları temizle, format kontrolü yap, Edel'e göster

## Yasaklar (Post Metninde)

- ❌ Emoji
- ❌ #terapi veya "terapi" kelimesi
- ❌ CTA / soru ("ne düşünüyorsun?", "yorumlarda buluşalım")
- ❌ Genel referans ("APA'nın araştırmasına göre" gibi)
- ❌ Gereksiz benzetmeler
- ❌ "Bu sayılar bana bir şey hatırlattı" gibi yapay geçiş cümleleri
- ❌ "sen" veya "siz" hitabı
- ❌ Seminere giriş vermeden atlama
- ❌ Sadece görüş sıralayıp sonuç vermeden bitirme

## Paylaşım Öncesi Kontrol Listesi

- [ ] 500-750 karakter mi?
- [ ] 6 katman yapısına uyuyor mu? (Katman 3 "Yani" var mı? Katman 6 kapanış havada kalmamış mı?)
- [ ] Toplantı postuysa: giriş + içerik + sonuç yapısı tam mı?
- [ ] İlk okumada anlaşılıyor mu?
- [ ] Gereksiz benzetme/analoji var mı?
- [ ] Emoji, hashtag, CTA yok mu?
- [ ] Hashtag eklendiyse 3-4 adet ve konuya uygun mu?
- [ ] Kaynak uluslararasıysa coğrafi çerçeve net mi? ("mezunlarımız" gibi Türkiye'ye özgü ifadeler kullanılmamış mı?)
- [ ] Edel onayladı mı? (ASLA onaysız paylaşma)
- [ ] Görsel üretildi mi? Post içeriğiyle uyumlu mu?
- [ ] Arşive kaydedildi mi? (`linkedin_posts_archive.json`)
