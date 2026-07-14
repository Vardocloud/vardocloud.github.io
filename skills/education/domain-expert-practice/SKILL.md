---
name: domain-expert-practice
description: >-
  AI Trainer / Domain Expert hazırlık programı — platform araştırması, prompt engineering pratik
  programı tasarımı, alan bilgisi tazeleme ve AI çıktısı değerlendirme egzersizleri. Psikoloji
  odaklı test edildi ancak her domain için uyarlanabilir.
version: 1.2
metadata:
  hermes:
    tags: [education, domain-expert, prompt-engineering, ai-training, practice]
    category: education
---

# Domain Expert Practice — AI Trainer Hazırlık

## Ne Zaman Kullanılır

- Kullanıcı AI Trainer / Domain Expert pozisyonuna hazırlanıyorsa (Prolific vb.)
- Kullanıcı prompt engineering pratiği yapmak istiyorsa
- Kullanıcının alan bilgisi (psikoloji, hukuk, tıp vb.) tazelemeye ihtiyacı varsa
- Kullanıcı AI çıktısını değerlendirme becerisi geliştirmek istiyorsa
- Kullanıcı "pratik programı hazırla" dediğinde

## Akış

### 1. Platform Araştırması
Kullanıcı bir AI Trainer pozisyonuna başvurduysa veya bir platformdan bahsediyorsa:

1. **İlanı/pozisyonu analiz et** — LinkedIn, Greenhouse vb. kaynaklardan (CV gerekli mi? Skills assessment var mı? Hangi yetkinlikler ölçülüyor?)
2. **Platform araştırması yap:**
   - `web_search` ile platform hakkında güncel bilgi topla
   - `web_extract` ile resmi dokümanları oku (participant help pages, FAQ, iş tanımı)
   - Trustpilot/Reddit gibi kullanıcı yorumlarını tara
3. **Domain Expert programını anla:** Ne işi, ne kadar ödeme, nasıl süreç?
4. **Skills assessment/mülakat sürecini AYRI AYRI araştır:** Platformun değerlendirme formatı ne? Hangi beceriler ölçülüyor? (Bu bilgi bazen paylaşılmaz — paylaşılmıyorsa dürüstçe söyle.)
5. **Özet sun:** Güvenilirlik, ödeme, süreç akışı, gereken beceriler, assessment detayı (biliniyorsa)
6. **Program ile assessment arasındaki ilişkiyi netleştir:** Program, assessment'e mi yoksa sonraki görevlere mi hazırlık yapacak?

### 2. Pratik Programı Tasarımı

Kullanıcı "program hazırla" dediğinde:

**⚠️ KRİTİK — Önce Platformun Gerçek Değerlendirme Sürecini Araştır**

Program tasarlamadan ÖNCE:
1. **Platformun skills assessment/mülakat sürecini resmi kaynaklardan araştır:** Ne soruyorlar? Hangi format? Ne kadar sürüyor?
2. **İş tanımını analiz et:** Hangi yetkinlikler ölçülüyor? Beklenen beceriler neler?
3. **Kullanıcıya sorma:** Kullanıcı "doğru idman mı bu?" diye sorduğunda cevabın hazır olmalı. Soruyu o sormadan önce sen söyle: "Bu programı platformun şu değerlendirme sürecine göre tasarladım: [araştırma sonucu]"
4. **Emin değilsen itiraf et:** "Skills assessment'in içeriğini net bilmiyorum, platform paylaşmıyor. Bu program Domain Expert olduktan sonraki görevler için pratik sağlar. Assessment için en iyi hazırlık psikoloji bilgisi tazeleme olabilir — ya da direkt başvurup sınavı görmek."
5. **İdman/assessment ayrımını net yap:** 
   - **Skills assessment (10-15 dk):** Psikoloji bilgisi + AI değerlendirme yeteneği — ne sorulduğu bilinmiyorsa, en iyi hazırlık alan bilgisi tazeleme
   - **Domain Expert görevleri (sonrası):** Prompt engineering, AI çıktısını değerlendirme, psikoloji içeriği yazma — 5 günlük program bunun için

**Planlama kuralları:**
- **Bugünden başlat** — Pazartesi varsayımı yapma, içinde bulunduğumuz günden başlat
- Günlük süre: 30-45 dk (çok uzun olmasın, sürdürülebilir olsun)
- Toplam: 5 gün ideal (çok kısa olmaz, çok uzun da olmaz)
- Saat: Kullanıcıya bırak veya akşam 21:00 gibi makul bir saat öner
- **Takvim:** Tüm günleri bir kerede takvime ekleme. İlk günü kullanıcıyla BİRLİKTE yap — onay al, sonra bir sonraki günü planla. Kullanıcı "hepsini sil / baştan başlat" derse: önce tüm takvim etkinliklerini sil, sonra güncel hedefini sor ve yeni programı ona göre tasarla

**Her gün şunları içermeli:**
1. **Konu başlığı** — net ve tek bir odak
2. **Araştırma** — `web_search` ile o günün konusuyla ilgili kaynak bul, link ver
3. **Pratik** — elle yapılacak alıştırma (AI'ya prompt yaz, çıktıyı değerlendir)
4. **Not al** — ne öğrendiğini yazması için hatırlatma

**5 günlük progresif yapı:**
- Gün 1 🟢: Temel — psikoeğitim prompt'ları (rol/bağlam/görev)
- Gün 2 🟡: Orta — müdahale planı prompt'ları (yapılandırma)
- Gün 3 🟠: Orta-ileri — AI çıktısını değerlendirme & düzeltme
- Gün 4 🔵: İleri — zincirleme prompt (chain of thought), karmaşık vaka
- Gün 5 🔴: Final simülasyonu — gerçek Domain Expert görevi provası

**Her günün pratik aktivitesinde:**
- Adım adım talimat ver (AI'ya ne sorulacak, çıktıda ne aranacak)
- Değerlendirme kriteri ekle: Doğruluk? Derinlik? Etik? Yapı?
- Karşılaştırma yaptır: önce ham prompt, sonra gelişmiş prompt

### 2b. Tamamlayıcı: Context Engineering Bootcamp

Prompt Engineering pratiğiyle birlikte **Context Engineering Bootcamp** kullanılabilir. İkisi farklı kasları çalıştırır:
- **Prompt Engineering** = AI'ya doğru soruyu sormak (ne istediğini bilmek)
- **Context Engineering** = AI'ya doğru bağlamı vermek (neye göre üreteceğini bilmek)

Bootcamp 5 günlük progresif bir formattır. Detay: `references/context-engineering-bootcamp.md`

**Önerilen program:** Prompt Engineering pratiği (30dk sabah) + Context Engineering pratiği (15dk akşam) — ya da dönüşümlü günlerde. Her iki programda da *iteration speed pratiği* uygula: çıktıyı al → "şunu düzelt" de → 2-3 hızlı revizyon.

### 3. Domain Knowledge Refresh

Kullanıcı "bilgim taze değil" derse:

1. **Konuyu küçük parçalara böl** (örn: YAB → psikoeğitim/bilişsel yeniden yapılandırma/maruz bırakma)
2. **Her parçayı AI'ya sordurarak tazele** — kullanıcı AI'dan öğrenirken aynı anda prompt pratiği yapmış olur
3. **Ezberden çok yapıyı hatırlat** — basamaklar, akış şemaları, kontrol listeleri

### 4. AI Çıktısı Değerlendirme Rehberi

Kullanıcıya şu kriterleri kullanmasını söyle:

| Kriter | Soru |
|--------|------|
| ✅ Doğruluk | Bilimsel olarak doğru mu? Güncel literatürle uyumlu mu? |
| 🎯 Spesifiklik | Genel geçer mi yoksa spesifik bir duruma göre mi? |
| 📐 Derinlik | Yüzeysel mi, teorik temelli mi? |
| 🔒 Etik | Etik sınırları koruyor mu (tıbbi tavsiye verme, vs.)? |
| 🧱 Yapı | Organize mi, takip etmesi kolay mı? |

## Kullanıcı Tercihleri

- **Schedule başlangıcı:** Bugünden başlat, pazartesi varsayımı yapma
- **Restart handling:** Kullanıcı "hepsini sil / baştan başlat" derse — panik yapma, direkt uygula: önce takvim etkinliklerini sil, sonra kullanıcının güncel hedefini sor. Eski programı sorgulama, varsayımları sıfırla.
- **İleriye dönük planlama yapma:** Kullanıcı Gün 1'i tamamlamadan Gün 2-3-4-5'i schedule etme. Her günü bir önceki tamamlandıktan sonra planla.
- **Budget:** Ücretli tool/API'lerden önce ücretsiz alternatifleri araştır
- **Bilgi tazeleme:** Kullanıcı dürüstçe "bilmiyorum/unuttum" diyebilir — önce konuyu beraber tazele, sonra pratiğe geç

## Referanslar

- `references/prolific-platform-arastirmasi.md` — Prolific Domain Expert program araştırması
- `references/sokuji-realtime-translation.md` — Sokuji canlı çeviri aracı araştırması
- `references/context-engineering-bootcamp.md` — 5 günlük progresif context engineering pratiği (Prompt Engineering ile birlikte kullanım için)
