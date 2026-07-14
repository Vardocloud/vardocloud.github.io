---
name: linkedin-writing
description: "LinkedIn post yazma metodolojisi — Hakan Türkçapar üslubu, 6 katman yapısı, NotebookLM ile transkript tabanlı post üretimi"
version: 1.1.0
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

1. **Vurucu giriş** — 1 cümle, okuyucuyu içine çeken, düşündüren. Günlük hayattan bir gözlemle bağlantı kur.
2. **Kaynak referansı** — "APA'nın [tarih]'daki [başlık] panelinde..."
3. **Yani / çıkarım** — **ASLA ATLANMAZ.** Bu katman olmazsa post anlamsızlaşır.
4. **Araştırma detayı** — Spesifik bulgu, panelden çarpıcı nokta.
5. **Dahası / ek detay** — "Dahası..." ile bağlanan ikincil bulgu.
6. **Vurucu kapanış** — "Belki de asıl mesele..." ile başlayan akılda kalan son cümle.

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
```

5. **Citation'ları temizle** — NotebookLM yanıtındaki [1], [2] gibi referans işaretlerini kaldır
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
- ❌ "sen" veya "siz" hitabı
- ❌ Seminere giriş vermeden atlama
- ❌ Sadece görüş sıralayıp sonuç vermeden bitirme

## Paylaşım Öncesi Kontrol Listesi

- [ ] 500-750 karakter mi?
- [ ] 6 katman yapısına uyuyor mu? (Katman 3 "Yani" var mı?)
- [ ] Toplantı postuysa: giriş + içerik + sonuç yapısı tam mı?
- [ ] İlk okumada anlaşılıyor mu?
- [ ] Gereksiz benzetme/analoji var mı?
- [ ] Emoji, hashtag, CTA yok mu?
- [ ] Hashtag eklendiyse 3-4 adet ve konuya uygun mu?
- [ ] Edel onayladı mı? (ASLA onaysız paylaşma)
- [ ] Görsel üretildi mi? Post içeriğiyle uyumlu mu?
- [ ] Arşive kaydedildi mi? (`linkedin_posts_archive.json`)
