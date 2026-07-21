# Prompt Engineering Kaynakları (Temmuz 2026)

Bu kaynaklar yalnızca görsel üretim için değil, **tüm prompt mühendisliği görevlerinde** kullanılır. Üç doküman Edel tarafından sağlanmıştır.

---

## 1. Google Prompt Engineering Whitepaper (Lee Boonstra, Eylül 2024)

65 sayfa, Gemini/Vertex AI odaklı. Kapsamlı referans.

### Önemli Çıkarımlar

**Konfigürasyon:**
| Parametre | Deterministik İşler | Kreatif İşler |
|-----------|-------------------|---------------|
| Temperature | 0 (greedy) / 0.1 | 0.9 |
| Top-P | 0.95 | 0.99 |
| Top-K | 30 | 40 |
- CoT (Chain of Thought) için temperature **0** olmalıdır
- Token limit: gereksiz uzun çıktıyı önlemek için makul sınır koy

**Temel Teknikler:**
- **Zero-shot**: En basit, örneksiz prompt. Modelin eğitimiyle yapabilmesi gereken işlerde kullan.
- **Few-shot**: 3-5 örnek ver, pattern'i göster. Edge case'leri de örneklerde göster.
- **System prompting**: Modelin büyük resimde ne yapması gerektiğini tanımla (rol + amaç).
- **Role prompting**: Spesifik bir kimlik ver (sen bir Pixar animatörüsün, sen bir editörsün).
- **Contextual prompting**: Anlık göreve özel, dinamik bilgi ver.
- **CoT (Chain of Thought)**: Modeli adım adım düşünmeye zorla. Sıcaklık=0. Cevabı reasoning'den ayır.
- **ReAct (Reason + Act)**: Düşün → Aksiyon al → Gözlemle döngüsü. Araç kullanan ajanlar için.
- **Self-consistency**: CoT'yi N kere çalıştır, en tutarlı cevabı seç.
- **ToT (Tree of Thoughts)**: Birden fazla düşünce yolunu dene, en iyisini seç.

**Best Practices:**
- **Instructions over Constraints**: "Şunu yapma" yerine "şunu yap" de.
- **Simplicity**: Prompt karmaşıksa model de karmaşık çıktı verir.
- **Output spesifikasyonu**: JSON/XML gibi yapılı format iste — halüsinasyon azalır.
- **Variables kullan**: `{city}` gibi değişkenlerle prompt'u tekrar kullanılabilir yap.
- **Dokümante et**: Her prompt denemesini tablo formatında kaydet (Name, Goal, Model, Temp, Prompt, Output).

---

## 2. Nano Banana 2 Işıklandırma Promptları (9 Adet)

Image-to-image için optimize edilmiş prompt yapısı. Her prompt şu şablona uyar:

### Şablon

```
Use the uploaded image as the exact base reference.
Apply [EFFECT] lighting only.

Lighting:
● [directional/positional/color details]
● [preserve/enhance specifics]

Color treatment:
● [color palette]
● [contrast/saturation specs]

Quality:
● [texture preservation requirements]
● [sharpness/noise handling]

Hard rules:
● Do NOT change [environment, objects, pose, framing]
● Do NOT add [props, light sources, accessories]
● Only modify [lighting, color grading, mood]
```

### Prompt Listesi

| # | Name | Mood | Key Characteristics |
|---|------|------|-------------------|
| 1 | BLUE SCREEN LIGHTING | Cool, cinematic | Soft cool blue from front/side, diffused, desaturated |
| 2 | SUNLIGHT BLINDS LIGHTING | Dramatic warm | Stripe bands, golden, strong contrast |
| 3 | NEON PINK AESTHETIC LIGHTING | Editorial, intimate | Magenta-pink, 30° angle, romantic |
| 4 | IPHONE FLASH LIGHTING | Candid, harsh | Cool-white direct flash, deep blacks |
| 5 | CINEMATIC AESTHETIC LIGHTING | Painterly, arthouse | ARRI ALEXA Mini LF, 85mm Master Prime, f/1.4 |
| 6 | WARM GOLDEN LIGHTING | Warm, soft | Golden-orange from one side |
| 7 | SOFT MOONLIGHT AESTHETIC | Contemplative, serene | Blue-silver, 45° back-right, Wong Kar-wai |
| 8 | SILVER CHROME LIGHTING | Editorial, glossy | Silver-white reflections on anatomical planes |
| 9 | CYBER GREEN LASER LIGHTING | Cyberpunk, dark | Emerald green, Blade Runner, smoke haze |

### Ne Zaman Kullanılır
- **BerZoo görsellerinde**: ortam ışığını iyileştirmek için
- **Image-to-image görevlerinde**: referans görsel + ışık efekti
- **Prompt yapısı olarak**: "Hard rules" bölümü her prompt için iyi bir prensip

---

## 3. Hikaye Anlatıcılığı Pratik Kitapçığı (Korzay Koçak)

Storytelling yapısı — video scriptleri, anlatımlı içerikler ve karakter diyalogları için.

### Ana Yapı (Başlangıç-Orta-Sonuç)
- **Başlangıç**: Karakterleri, yeri ve bağlamı tanıt. Merak uyandır.
- **Orta**: Çatışma, dönüm noktası, gerilim. Duygusal iniş-çıkışlar.
- **Sonuç**: Çözüm, mesaj, karakter değişimi. Tatmin edici kapanış.

### Teknikler
- **Duyusal betimleme**: Görsel + işitsel + dokunsal detaylar
- **Ses tonu ve vurgu**: Anlatıcı sesine uygun tonlama
- **Karakter gelişimi**: Fiziksel özellikler, değerler, hedefler

### BerZoo US İçin Uyarlama
Her Ezop masalı için:
1. Başlangıç → Karakter tanıtımı + sorun
2. Orta → Çatışma / ders
3. Sonuç → Moral mesajı

---

## Kullanım Prensibi

Bu üç kaynak birbirini tamamlar:
- **Whitepaper** → prompt'u NASIL yazacağını söyler (teknik, konfigürasyon, yapı)
- **Işık promptları** → görsel prompt'un NASIL yapılandırılacağını gösterir (şablon, hard rules)
- **Kitapçık** → NE anlatacağını söyler (hikaye yapısı, karakter, duygu)

Herhangi bir prompt yazarken:
1. Önce whitepaper'daki tekniği seç (zero-shot / few-shot / CoT / system)
2. Sonra ışık promptlarındaki yapıyı kullan (base reference + instructions + hard rules)
3. İçeriği kitapçıktaki storytelling prensipleriyle doldur
