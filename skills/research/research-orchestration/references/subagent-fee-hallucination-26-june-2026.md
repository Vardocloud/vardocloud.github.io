# Subagent Fee Hallucination — ALWAYS Verify from Official Source (26 June 2026)

## Critical Pattern Discovered This Session

### Known Bug: Subagent Fee Hallucination
**Subagent'lar sürekli yanlış ücret bildiriyor:**

- **Gedik Üniv**: subagent "130 bin TL" dedi → gerçek **1,285,000 TL** (10x fark!)
- **Altınbaş Üniv**: subagent "550,000 TL" dedi → gerçek **1,100,000 TL**
- **İşık Üniv**: subagent eski fiyat verdi (980K), güncel kontrol edilmedi

### Why This Happens
Subagent'lar (delegate_task) şunları yapıyor:
- Önceki bilgileri doğrulama
- Aktif olarak takip edilebilecek program sayılarından dolayı eksik veri getirme
- Açıkgözlü kodlama ile yanlış veriler üretme
- Program granüllüğünün fazla olması nedeniyle yönlendirilebilirlikle ilgili sorunlar genellikle bazılarının ücretini yansıtır

### New Pattern: Parallel Subagent + Manual Gap-Fill (26 June 2026)

#### This session discovered a need for a high-performance parallel scanning + manual gap-fill pattern that adapts to the subagent fee hallucination problem.

**Workflow:**

1. **Subagent'ları toplu gönder** (delegate_task ile 4-6 paralel) — her biri farklı bir üniversiteyi araştırır
2. **Subagent sonuçlarını tara** — hangi alanlar eksik? (ücret, GPA, ALES, deadline, YÖKDİL)
3. **Doğrudan resmi kaynağa git** — subagent'ın bulamadığı/yanlış getirdiği verileri elle doğrula:
   - Ücret PDF'ini manuel aç (subagent 404 alabilir, sen direkt URL'den oku)
   - Başvuru takvimini resmi siteden kontrol et
   - Ders kataloğundan program varlığını teyit et
4. **Birleştir ve sun** — subagent bulguları + senin doğruladığın veriler

#### When to Use This Pattern
**Çok sayıda üniversite/program paralel taranırken.** Subagent'lar keşif içindir, doğrulama için değil.

#### Critical Pitfall: Subagent Fee Hallucination

**Geciken ders (25 Haziran 2026):** Subagent'lar sürekli yanlış ücret bildiriyor:

- Gedik Üniv: subagent "130 bin TL" dedi → gerçek **1,285,000 TL** (10x fark!)
- Altınbaş Üniv: subagent "550,000 TL" dedi → gerçek **1,100,000 TL**
- Işık Üniv: subagent eski fiyat verdi (980K), güncel kontrol edilmedi

**Kural:** Ücret bilgisi için subagent'a ASLA güvenme. Sadece şu kaynaklar geçerlidir (sıralı):

1. 🥇 **Resmi ücret tablosu** (Excel/PDF — üniversitenin kendi yayınladığı)
2. 🥈 **Resmi web sayfası** (üniversitenin lisansüstü enstitü sayfası)
3. 🥉 **Instagram duyurusu** (resmi üniversite hesabından)
4. ❌ **Third-party toplayıcılar** (StudyLeo, uni4edu, northcypruseducation, Scribd) — KULLANMA

**Nasıl doğrulanır:**

- Resmi sitede "Ücretler" sayfasını bul
- PDF/Excel dosyasını indir ve içinde program adını ara
- Tarih kontrolü yap — 2026-2027 için güncel mi?
- Farklı kaynaklar arasında tutarsızlık varsa: RESMİ KAYNAK KAZANIR

**NE zaman subagent kullanma:** Sadece ön tarama / keşif için. Keşif sonucunu asıl kaynaktan doğrula.

### Updated University Program Research References (25 June 2026)

Now `references/university-program-search.md` includes the following critical updates:

- **Subagent Reliability Warnings** — Verify ALL subagent outputs
- **Fee Hallucination Fix** — Manual verification pattern for critical numbers
- **Parallel Subagent + Manual Gap-Fill** — New scanning pattern for high-performance multi-university research

**Subagent model selection — Edel's preference ignored**

Edel explicitly corrected: **deepseek-v4-flash-free** kullanılmalı, north-mini-code-free veya mimo-v2.5-free kullanma. `delegate_task` alt ajanlarında model override dene. `opencode run -m opencode/deepseek-v4-flash-free` önce dene, 45sn timeout yerse delegate_task'e geç. Preference sırası: deepseek-v4-flash-free >> north-mini-code-free >= mimo-v2.5-free.

### Next Steps

For university program research:

1. **Always prioritize soonest deadline** with 🔥/🆕 indicators
2. **Always verify fee amounts with PDFs/documents** (CRITICAL due to subagent hallucinations)
3. **Always check YÖK recognition status** rather than assuming
4. **Always document source inconsistencies** for future reference
5. **Use parallel subagent + manual gap-fill pattern** for high-performance scanning

### References

- University program research pattern: `references/university-program-search.md`
- Subagent fee hallucination fix: This file
- Pattern enforcement: Parallel subagent + manual gap-fill pattern