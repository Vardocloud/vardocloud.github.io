# APA Bilgi Pipeline v5.0 Rapor Formatı (6 Temmuz 2026)

Edel tarafından tanımlanan yeni rapor formatı. v4.0 numerik sıralama ve 5-başlık formatının evrimleşmiş halidir.

## Ne Zaman Kullanılır

APA Monitor sayısı gibi çok kanallı, çok kategorili taramalarda. Birden çok makale aynı anda işlenirken. Tek makale için de kullanılabilir (5-başlık formatına alternatif olarak).

## Rapor Yapısı

```
🧠 APA GÜNLÜK — [TARİH]
────────────────────

📋 KATEGORİ 1: [Kategori Adı]

❶ [Makale Başlığı]
Ne anlatıyor? → [1-2 cümle, temel soru]
Ne diyor? → [temel bulgular, çarpıcı veri]
Bunun anlamı ne? → ["Yani..." ile bağla, klinik/pratik çıkarım]
📎 Kaynak: [Yazar, Kaynak, Tarih]

❷ [İkinci makale]
...

📋 KATEGORİ 2: ...
...

📌 ÖZET: [bir cümle ile günün öne çıkan konusu]

🎙️ **Günün Podcast'i:** [varsa açıklama] — MEDIA:path
```

## Kategoriler

| Emoji | Kategori | İçerik Türü |
|-------|----------|-------------|
| 🤖 | AI × Psikoloji | AI değerlendirme araçları, dijital terapi, yapay zeka etiği |
| 🧠 | Klinik Pratik | Tedavi protokolleri, terapi yöntemleri, vaka çalışmaları |
| 📈 | Kariyer & Gelişim | CE fırsatları, sertifikalar, psikolog hakları, kariyer kaynakları |
| 🔬 | Araştırma | Yeni çalışmalar, meta-analizler, güncel bulgular |
| ⚖️ | Politika/Hukuk | SCOTUS kararları, yasal düzenlemeler, politik gelişmeler |
| 📅 | Etkinlik | Webinar, seminer, konferans (ücretsiz/ücretli belirt) |
| 🎧 | Podcast | Speaking of Psychology bölüm özetleri |

## Format Kuralları

- Kategorilere göre grupla — her kategori kendi başlığı altında
- Her makale: "Ne anlatıyor? → Ne diyor? → Bunun anlamı ne?" şablonu
- "Bunun anlamı ne?" cümlesi "Yani..." ile başlasın — günlük dile çevir, akademik jargonu sadeleştir
- Her makale sonunda **📎 Kaynak:** satırı zorunlu
- Uzunluk esnek: kısa haber 3-5 cümle, normal makale 5-10 cümle (2 paragraf), uzun derleme 10-15 cümle (3-4 paragraf)
- **Alt limit yok** — kısa ve öz tut, akademik dil kullanma
- Son satır: 📌 **ÖZET:** bir cümle ile günün öne çıkan konusu
- Podcast varsa: 🎙️ **Günün Podcast'i:** [açıklama]
- Wiki dosyaları: İngilizce, yapılandırılmış frontmatter'lı .md (bkz. llm-wiki skill)
- NotebookLM: best-effort (auth varsa source ekle, yoksa geç)

## Rapor Formatının Geçmişi

| Versiyon | Tarih | Özellik |
|----------|-------|---------|
| v3 (5-başlık) | 5 Haz 2026 | 💡NE DİYOR / 📖DETAY / 🔑KAVRAMLAR / 🧩SENİN İÇİN / ⭐PRATİK |
| v4.0 (numerik) | 5 Haz 2026 | ❶❷❸ numerik sıralı, bülten bazlı gruplama |
| **v5.0 (kategori)** | **6 Tem 2026** | **Kategori bazlı gruplama, "Ne anlatıyor/Ne diyor/Anlamı ne" şablonu** |

## v4.0 vs v5.0 Farkı

- v4.0: numerik sıralı (❶❷❸), bülten bazlı gruplama
- v5.0: kategori bazlı gruplama (🧠 🤖 📈), "Ne anlatıyor/Ne diyor/Anlamı ne" şablonu
- v5.0: her makale sonunda 📎 Kaynak: satırı zorunlu
- v5.0: 📌 ÖZET satırı zorunlu
- v5.0: podcast bölümü 🎧 kategorisi altında veya ayrı bölüm olarak

## Örnek Kullanım

```
🧠 APA PAZARTESİ — 6 TEMMUZ 2026
────────────────────

📋 AI × PSİKOLOJİ

❶ How AI Is Reshaping Human Skills and Thinking (Cover Story)
Ne anlatıyor? — Yapay zekaya aşırı güvenmenin eleştirel düşünme ve iş becerilerini nasıl köreltebileceğini araştırıyor.
Ne diyor? — 319 bilgi çalışanıyla araştırma: AI'a güven arttıkça eleştirel düşünme azalıyor. EEG çalışması: AI ile yazı yazanlarda beyin bağlantısallığı zayıflıyor.
Bunun anlamı ne? — Yani sorun AI'ın kendisi değil, nasıl kullanıldığı. Üstbiliş becerisi yüksek olanlar AI'ı daha bilinçli kullanıp daha yaratıcı iş çıkarıyor.
📎 Kaynak: Zara Abrams, APA Monitor, Temmuz 2026
```
