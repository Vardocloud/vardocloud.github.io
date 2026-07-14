# APA Makale Derin Okuma Standartları

Cron veya interaktif modda işlenen her APA makalesi için kalite standardı.
5 Haz 2026'da belirlendi — önceki "yüzeysel işleme" sorununa çözüm.

## Minimum Gereksinimler

Her wiki dosyası şunları İÇERMELİ:

### 1. Tam Metin Okuma (sadece özet DEĞİL)
- APA sitesinden JavaScript ile TÜM paragrafları çek: `[...document.querySelectorAll('p')].map(p => p.innerText).filter(t => t.length > 50).join('\n\n')`
- Sadece snippet/abstract ile yetinme
- Araştırmacı isimleri, kurumlar, spesifik sayısal veriler dahil olsun

### 2. Yapılandırılmış Format
```
💡 ANA FİKİR — 2-3 cümle, makalenin temel argümanı
📖 DERİN ÖZET — en az 300-400 kelime, alt başlıklı
🔑 KAVRAMLAR — her kavram için 1-2 cümle AÇIKLAMA (liste değil)
🧩 EDEL BAĞLAMI — 2-3 cümle, spesifik: "senin için neden önemli?"
⭐ KLİNİK ÇIKARIMLAR — 3-5 pratik madde
```

### 3. Edel Bağlamı (ZORUNLU)
Her makale için ŞUNA bağla:
- AI etiği/psikoloji kariyer hedefi
- Klinik psikoloji yüksek lisansı (Eylül 2026)
- Bardo pratiği
- Helsinki Ethics of AI / Sentio / AI Safety kursları
- "Bu makale Edel'in radarında olmalı çünkü..."

### 4. Açıklamalı Kavramlar
❌ YANLIŞ: `• Cognitive Offload • Executive Function • Authorship`
✅ DOĞRU:
```
| Cognitive Offload | Beynin düşünme yükünü dış kaynaklara atması. AI ile aşırıya kaçabiliyor. |
| Executive Function | Planlama, dürtü kontrolü gibi üst düzey bilişsel beceriler. AI'ın en çok devraldığı alan. |
```

### 5. Somut Veriler ve Alıntılar
- Doğrudan alıntı (araştırmacı ismiyle): "Landers: '...'"
- Sayısal veriler: N, %, istatistikler
- Çalışma tasarımı detayları

## Örnek: İyi vs Kötü

### ❌ KÖTÜ (yüzeysel)
```markdown
## Summary
Psychologists are uniquely positioned to shape AI development.
The article argues that psychological expertise must be brought into AI.

## Key Experts
- Richard Landers — I/O psychologist
- Alison Cerezo — mpathic
```

### ✅ İYİ (derin)
```markdown
## 💡 ANA FİKİR
Psikologlar AI geliştirmenin MERKEZİNDE yer almalı — danışman değil lider.
AI'ın özünde insan davranışını anlama yattığı için psikoloji "opsiyonel" değil "zorunlu"dur.

## 📖 DERİN ÖZET
### Amazon'un AI İşe Alım Fiyaskosu
[spesifik hikaye, Landers alıntısı, ders]

### Psikologların 3 Temel Yetkinliği
1. İnsan Karmaşıklığını Anlama [Landers örneğiyle]
2. Risk Tespiti [Naval Academy intihar tespit modeli]
3. Anlamlı Değerlendirme [Morris'ten alıntı]

## 🧩 EDEL BAĞLAMI
Bu makale senin AI ethics researcher + red teamer hedefinle BİREBİR örtüşüyor...
```

## Kalite Kontrol Listesi

Cron raporu göndermeden önce her makale için kontrol et:
- [ ] Tam metin okundu mu? (sadece abstract DEĞİL)
- [ ] En az 3 araştırmacı/kurum ismi geçiyor mu?
- [ ] En az 2 doğrudan alıntı var mı?
- [ ] En az 3 sayısal veri noktası var mı?
- [ ] Edel bağlamı spesifik mi? ("AI etiği kariyerin için..." gibi)
- [ ] Kavramlar açıklamalı mı? (sadece liste DEĞİL)
- [ ] Klinik çıkarımlar pratik mi? ("danışana şunu sor" gibi)
- [ ] Dosya boyutu en az 3KB mi? (yüzeysel = genelde < 2KB)
