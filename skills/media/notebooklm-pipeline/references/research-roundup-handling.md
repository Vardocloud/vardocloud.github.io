# Research Roundup Page Handling (16 Tem 2026)

## What Is a Research Roundup?

APA Monitor sayfalarında bazen tek bir URL altında **birden çok bağımsız çalışmanın özeti** yayınlanır. Belirtiler:

- Başlıkta "and more scientific findings" veya "and more" ibaresi
- Sayfada 5+ farklı başlık/çalışma özeti, her biri ayrı DOI ile
- Genellikle "Social Dynamics & Relationships", "Health & Well-being" gibi alt bölümlere ayrılmış
- Her bölüm altında 3-5 çalışma

## Handling Rules

### DO:
1. **Tek wiki dosyası oluştur** — ana başlığı kullan (örn. `2026-07-16-friends-influence-outgroup-prejudice.md`)
2. **3-5 en klinik anlamlı bulguyu seç** — "Key Takeaways" olarak öne çıkar:
   - Doğrudan terapi/pratikte kullanılabilir olanlar
   - Çarpıcı istatistik içerenler
   - Edel'in ilgi alanına girenler (klinik psikoloji, AI, çocuk/ergen)
3. **"Clinical Relevance" bölümü ekle** — her seçilen bulgu için ayrı klinik çıkarım yaz
4. **Kalan bulguları "Additional Findings" altında liste** — başlık + 1 cümle
5. **Tüm DOI'ları tek listede topla** — "Key Research Citations" bölümü

### DO NOT:
- ❌ Her bulgu için ayrı .md dosyası açma (17 dosya = israf)
- ❌ Her bulguyu ayrı ayrı NotebookLM'e ekleme
- ❌ Her bulgu için ayrı notebook_query yapma (gerek yok)
- ❌ Tüm bulguları aynı anda "işlendi" olarak işaretleme — sadece seçtiklerin

## Dedup Warning:
Roundup sayfasındaki bulgulardan bazıları daha önce başka kanallardan işlenmiş olabilir:

| Önceki Kanal | Roundup'daki Olası Karşılığı |
|-------------|------------------------------|
| Science Spotlight | Aynı çalışma, farklı özet |
| Editor's Choice | Aynı çalışma, Monitor versiyonu |
| Practice Update | Aynı konu, farklı açı |

**Dedup stratejisi:** Roundup'daki her bulgunun KONUSUNU (ör. "friendship prejudice", "teen sleep") al, index.md'de topic bazında tara. Aynı konu işlenmişse roundup dosyasında "ayrıca bak" notu düş ama tekrar işleme.

**Added:** 2026-07-16 — First documented instance: "Friends may influence prejudice toward outgroups, and more scientific findings" (17 studies in one URL).

17 bulgu içeren roundup → seçilenler:
1. Friends' influence on prejudice (max 3%) → social psychology
2. Hasslers and biological aging → stress/health
3. Teen sleep crisis (15.8% → 23.0%) → adolescent health
4. Laughing at gaffes (harm vs no-harm distinction) → social perception
5. Cognitive enrichment delays Alzheimer's ~5 years → aging

Kalan 12 bulgu: "Additional Findings" altında tek cümleyle geçildi.
Tüm DOI'lar tek "Key Research Citations" listesinde toplandı.
