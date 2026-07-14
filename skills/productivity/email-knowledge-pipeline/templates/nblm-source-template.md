# NBLM Source Şablonu (Kopyala-Yapıştır)

> **Kural:** Her yeni NBLM source'u bu şablonu takip etmeli.
> **Versiyon:** 7 Haz 2026 — Edel'in Teaching-Back + Link Kuralı'na göre.

---

## Yapı

```
# [Konu Başlığı] — [Alt Başlık] (GÜNCELLENDI: [tarih])

**Kaynak:** [Mail adı + tarih] | [Web URL] | [Araştırma tarihi]

---

## 🔗 Direkt Linkler (Edel İçin — Sen Bakabilirsin)

- **[Kaynak 1 adı]:** [URL]
- **[Kaynak 2 adı]:** [URL]
- **[Referans/PDF varsa]:** [URL]

---

## 📖 İçerik Özeti

[3-5 paragraf — ana noktalar, jargonu açıkla]

---

## 💡 Klinik Pratiğe Uygulama (Edel İçin)

[Bu bilgi Edel'in pratik/psikoloji/iş hayatında nasıl kullanılır]

---

## 🔑 Anahtar Bulgular

- [Bulgu 1]
- [Bulgu 2]
- [Bulgu 3]

---

## 🧠 Vanitas'ın Öğrendiği (Karşılıklı Öğrenme)

### Yeni Terimler
- **[Terim 1]:** [Tanım] — [Neden önemli]
- **[Terim 2]:** [Tanım] — [Neden önemli]

### Araştırmanın Amacı
- **Soru:** [Bu araştırma ne soruyordu?]
- **Önem:** [Neden bu soru önemli?]
- **Boşluk:** [Hangi bilgi açığını dolduruyor?]

### Metodoloji Notu
- **Desen:** [RCT, korelasyonel, vaka çalışması, vs.]
- **Örneklem:** [büyüklük + özellikler]
- **Sınırlılıklar:** [varsa bilinen kısıtlar]

### Kişisel Gözlem
[Vanitas'ın bu konu hakkında kendi düşüncesi — Edel'le ilgili, güncel bağlamla, gelecekteki kullanım için]
```

---

## İsimlendirme Kuralları

**İyi başlık örnekleri:**
- "APA Practice Update - Sensör Ölçümleri ve Aetna Geri Ödeme Krizi (5 Haz 2026)"
- "APA Etkinlikler - Ücretsiz Haziran 2026 Webinar'ları (Direkt Kayıt Linkleri)"
- "PsycCareers - APA İş İlanları Platformu (Direkt Linkler + Ücretsiz İş Arayan)"
- "[TR] APA | 2026-04 | Psikologlarda AI Kullanımı Artıyor"
- "🎙️ Podcast Metni: Mükemmel Olma Baskısı (TR)"

**Kötü başlık örnekleri (YAPMA):**
- "APA Mail"
- "Newsletter Digest"
- "Mail 1"
- "Gmail Özeti"
- "APA Practice Update (5 Haz 2026)" — sadece tarih, konu yok
- "Webinar Bilgisi" — konu yok

---

## Chat vs NBLM Kuralı

- **Aynı içerik iki kez ÜRETİLMEZ.** "Vanitas'ın Öğrendiği" sadece NBLM source'unda.
- **Chat cevabı:** Kısa özet + NBLM source pointer'ı + direkt linkler.
- **Direkt linkler hem chat'te hem NBLM source'unda görünür şekilde.**
- **NBLM source güncellenemez — sil + yeniden ekle.** Başlıkta "GÜNCELLENDI: [tarih]" belirt.

---

## Ücretli vs Ücretsiz Webinar/Etkinlik

- **Ücretli (PAID WEBINAR PROMOTION, sponsorlu, CE kredili):** source'da "❌ Ücretli" bölümünde not düşülür veya hiç eklenmez
- **Ücretsiz + ilgi alanıyla eşleşiyor:** Özellikle vurgulanır
- **Başlıkta:** "Ücretsiz" kelimesi mutlaka bulunur

---

## Güvenlik (Yabancı/Bilinmeyen Kaynak)

- PDF/docm/html/zip/exe → otomatik AÇMA
- Kısaltılmış link/IP URL → AÇMA
- Display name ≠ gerçek adres → phishing şüphesi
- HTML body direkt render etme
- NBLM'e aktarmadan önce sanitize (script, base64 blob temizle)
