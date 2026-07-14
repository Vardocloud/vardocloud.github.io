# Instagram Karusel Yazım Krokisi (Bardo Psikoloji)

## Referans: @izmirsanspsikoloji (13K takipçi, İzmir)
Bilgilendirici foto postları + karusel formatıyla büyüyen psikolog hesabı.

## Karusel Yapısı (7-9 slayt)
- **1. slayt:** Dikkat çeken başlık / problem cümlesi (soru eki fiilden sonra!)
- **2-3:** Konu tanımı + neden önemli
- **4-6:** 2-3 temel bilgi + örnekler + yanlış inanışlar
- **7:** Günlük hayata uyarlama / mini farkındalık
- **8-9:** Özet + kapanış sorusu / düşündürücü cümle

## Görsel Format
- **Renkler:** Krem, bej, açık gri, pastel mavi, soft yeşil, toprak tonları
- **Tipografi:** Sans-serif, başlıklar kalın, gövde yüksek kontrastlı
- **Dil:** Temiz boşluk, tek slayt = tek fikir

## Yazı Katmanları
- **%20 slayt üstü:** 5-12 kelime, sadece ana mesaj
- **%80 caption:** 3 parça: giriş → detay+örnek → özet+soru

## Bilgi Sunum Tekniği
> **Duygu/Problem → Açıklama → Örnek → Farkındalık**

1. **Hook:** Merak uyandıran yaygın bir his
2. **Sade açıklama:** Psikolojik terimler günlük dile çevrilir
3. **Örnek:** Gerçek hayattan kısa bir senaryo
4. **Takeaway:** "Bunu fark etmek ne sağlar?"

## Başlık & Kapanış Kalıpları
**Açılış (reklamsız):**
- "Bunu yaşıyorsan yalnız değilsin"
- "Bazı duygular sessiz çalışır"
- "Aslında yorgunluk sandığın şey bu olabilir"

**Kapanış (reklamsız, YTA/PROMOSYON YASAK):**
- "Fark etmek, değişimin ilk adımıdır"
- "Kendini anlamak, kendine alan açmaktır"
- Asla "DM'den yazın", "destek alın", "profesyonel yardım" gibi ifadeler kullanma

## Üretim Workflow'u
1. NotebookLM cross_notebook_query() ile zengin bilgi çek (BDT, ÇÖZ, Okul PD notebook'ları)
2. Yazar ajanına (GPT 5.4 Mini, Pollinations :19999) yazdır — yazım krokisine uygun prompt ver
3. NotebookLM studio_create(slide_deck) ile görselleştir — BDT notebook'u (a4fe729d) çalışıyor
4. CLI ile indir: `nlm download slide-deck <notebook_id> --id <artifact_id> -o <path>`
5. Edel'e MEDIA: ile gönder + onay iste

## Dil Kuralları
- Soru eki (mi/mı/mu/mü) her zaman FİİLDEN sonra gelir. "Seni mi yoruyor?" yanlış → "Seni yoruyor mu?" doğru
- "Sen" dili kullan, "siz" değil
- Akademik jargon yok — terimleri günlük dile çevir
- Warm, doğal, samimi ama profesyonel
- Kaynak/araştırma referansı doğal geçsin, reklam gibi durmasın
