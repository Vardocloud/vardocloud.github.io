# Visual Hardware Diagnosis — Pitfalls & Best Practices

When Edel sends photos of disassembled hardware and asks for repair guidance.

## 🔴 SIN: False-Positive Diagnosis from Photos

**The mistake (19 Jul 2026):** 2730p anakart fotoğrafında siyah mylar koruyucu tabakayı "kahverengi sıvı lekesi" olarak yanlış teşhis ettim. Vision_analyze da aynı hatayı yaptı — koruyucu plastik tabaka + loş ışık = sıvı gibi göründü. Edel düzeltti: "sıvı dediğin siyah jelatin mi?"

**Kural:** Fotoğraftan donanım teşhisi yaparken:
1. **Gördüğünü söyle, yorumladığını ayrıca belirt.** "Siyah bir yüzey var, üzerinde dalgalı desenler görünüyor" ≠ "Bu sıvı hasarı." 
2. **Kesin teşhis koymadan önce kullanıcıya sor:** "Bu siyah alan plastik kaplama mı yoksa ıslak mı?"
3. **Vision_analyze'a güvenme — o da halüsinasyon yapabilir.** Senin görevin onun çıktısını sorgulamak.
4. **Yanlış teşhis durumunda hemen kabul et, düzelt, özür dile.** Savunmaya geçme.

## 🔴 SIN: Confident Hardware Location Claims Without Verification

**The mistake:** DC jack'in "sol alt köşede, HDD'nin altında" olduğunu söyledim ama servis kılavuzundan doğrulayamadım. Edel bulamadı.

**Kural:** Donanım parçasının yerini tarif ederken:
1. **Önce servis kılavuzuna bak** — HP'nin resmi PDF'ini indir, ilgili sayfayı bul
2. **YouTube söküm videosunu tara** — video timestamp'leri ile birlikte referans ver
3. **Bulamazsan DÜRÜST OL:** "Bu modelde bu parçanın tam yerini kılavuzdan/netten çıkaramadım" de
4. **Tahmin yürütme.** Yanlış tarif, kullanıcının saatlerini boşa harcar ve güveni sarsar.

## 🔴 SIN: Too Many Steps → User Confusion

**The mistake:** Shield sökümü, DC jack kontrolü, multimetre ölçümü, anakart sökümü hepsini aynı mesajda saydım. Edel: "kafam karıştı."

**Kural (SIN #7'nin donanım özelinde tekrarı):**
- Donanım tamirinde **tek seferde en fazla 2-3 adım** ver
- Her adımın sonucunu bekle, sonra sıradakine geç
- "Sadece X yap, sonucu söyle" formatını kullan
- "Şunları yap: 1-2-3-4-5" kalıbı donanım tamirinde çalışmaz — kullanıcı fiziksel olarak uğraşıyor, zihinsel yükü azalt

## Best Practices for Hardware Repair Sessions

### Photo Analysis Prompt Template

Vision_analyze için soru sorarken:
```
"Bu [cihaz modeli] fotoğrafında:
1. [X parçası] nerede? Tam koordinat ver.
2. Bu alan [açıklama] — bu normal mi yoksa hasar mı?
3. Anakart üzerinde yanık, şişme, çatlak var mı?
4. Emin değilsen 'net görünmüyor' de."
```

### YouTube/Internet Research Strategy

1. `web_search` ile "[model] [sorun] repair fix" ara
2. YouTube sonuçlarını `web_extract` ile transcript'ini çıkar (video izlemek yerine oku)
3. Servis kılavuzu için `web_search "[model] service manual PDF"`
4. Forum sonuçları için `site:badcaps.net` veya `site:reddit.com` ekle
5. Hiçbir şey bulamazsan: "Bu model için spesifik kaynak bulamadım, genel prensiplerle ilerleyelim" de

### Escalation Decision Tree

| Durum | Aksiyon |
|-------|---------|
| Servis kılavuzu var, parça yeri net | Tarif et, ilerle |
| Servis kılavuzu var, parça yeri net değil | Kılavuz sayfa numarasıyla referans ver, kullanıcı baksın |
| Servis kılavuzu YOK | "Net bilgim yok" de, genel prensiplerle ilerle veya tamirci öner |
| Kullanıcı multimetre istemiyor/yok | Anakart seviyesinde ilerlemek MÜMKÜN DEĞİL — bunu net söyle |
| Kullanıcı lehim yapamaz | MOSFET/kondansatör değişimi gerekiyorsa tamirci öner |
