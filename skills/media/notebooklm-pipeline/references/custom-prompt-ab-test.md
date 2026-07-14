# Custom Prompt A/B Testi — Tibet Bardo Thödol Videosu

**Tarih:** 27 Mayıs 2026  
**Notebook:** 92cc7d76-6601-4e6f-a760-557b5d30a4ef  
**Kaynak:** YouTube videosu (41K karakter caption), Damla Dönmez

## Study Guide Karşılaştırması

| Metrik | V1 (promptsuz) | V2 (custom prompt'lu) | Fark |
|--------|---------------|----------------------|------|
| Başlık | Tibet'in Ölüler Kitabı (Bardo Thodol) Çalışma Rehberi | Tibet'in Ölüler Kitabı (Bardo Thodol): Bilincin Geçiş Evreleri ve Özgürleşme Rehberi | V2 daha spesifik |
| Karakter | 5.731 | 5.870 | +139 (%2.4) |
| Kelime | 766 | 787 | +21 (%2.7) |
| Satır | 82 | 89 | +7 |

**Niteliksel farklar:**
- V2 girişi daha aksiyon odaklı: "bilincin nasıl yönlendirileceğini kavramak"
- V1 girişi daha akademik: "Tibet Budist geleneğinin en önemli metinlerinden biri"
- V2 sözlüğünde Samsara, Saf Işık, Trikaya öne çıkmış
- V1 sözlüğünde Brahmarandra, Padmasambhava öne çıkmış

## Podcast Karşılaştırması

| Metrik | V1 (promptsuz) | V2 (focus prompt'lu) |
|--------|---------------|---------------------|
| Başlık | Tibet'in Ölüler Kitabı Aslında Yaşayanlar İçin | Tibet'in Ölüler Kitabı ve Ara Geçişler |
| Boyut | ~870KB | 878KB |
| Süre | ~12 dk | 23:36 dk |
| OGG boyutu | — | 5.799KB |

**Niteliksel fark:** V2 başlığı "ara geçişler"e vurgu yapmış — focus_prompt'taki "ikinci geçiş" ve "atlanan detayları yakala" talimatı yönelimi değiştirmiş.

## Kullanılan Custom Prompt (Study Guide)

```
Bu çalışma rehberini oluştururken şu kurallara uy:
1. Kaynak metni en baştan en sona İKİNCİ KEZ oku ve ilk geçişte atladığın mini konuları, ara sözleri, "bu arada" diyerek geçilen detayları yakala.
2. Konuşmacının "geçelim" ya da "hızlıca söyleyeyim" diyerek geçtiği hiçbir konuyu atlama.
3. Verilen tüm analojileri, örnekleri ve somut vakaları rehbere ekle.
4. Bulduğun eksikleri akışın içine, doğru yerine yerleştir — ayrı "Ek Notlar" bölümü açma.
5. Bardo Thödol terminolojisini doğru yazımla koru.
6. Rehber Türkçe olsun.
```

## Kullanılan Focus Prompt (Podcast)

```
Bu podcast'i oluştururken şu kurallara uy:
1. Kaynak metni en baştan en sona İKİNCİ KEZ oku ve ilk geçişte atladığın detayları, ara sözleri, örnekleri yakala.
2. Konuşmacının verdiği tüm analojileri, somut vakaları ve hikayeleri podcast akışına dahil et.
3. "Geçelim" ya da "hızlıca söyleyeyim" diyerek geçilen konulara özellikle dikkat et.
4. Podcast Türkçe olsun, Bardo Thödol terminolojisini doğru kullan.
```

## Sonuç

Custom prompt kesinlikle işe yarıyor — hem içerik yönelimini hem başlıkları etkiliyor. Ancak fark devasa değil (%2-3 civarı hacim artışı). NotebookLM'in kendi iç işleyişi hâlâ baskın. Yine de "ikinci geçiş" pattern'ini eklemek kaliteyi artıran düşük maliyetli bir iyileştirme.
