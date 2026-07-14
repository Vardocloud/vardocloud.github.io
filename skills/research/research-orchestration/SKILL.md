---
name: research-orchestration
description: "Genel amaçlı çok aşamalı araştırma — pazar, strateji, teknik keşif. AKADEMİK LİTERATÜR TARAMASI İÇİN DEĞİL (bunun için master-research-pipeline skill'i)."
version: 1.2.0
metadata:
  hermes:
    tags: [research, orchestration, cron, delegation, planning]
    category: research
---

# Research Orchestration

When Edel asks for extensive multi-topic research ("geniş çapta araştırma"), this skill governs
how to structure, execute, and deliver the project.

---

## Phase 0: Unified Search — ZORUNLU Ön Yükleme

**Kural:** Herhangi bir arama/araştırmaya başlamadan ÖNCE şu sırayı takip et:

1. **`unified-search` skill'ini yükle** — `skill_view(name='unified-search')` ile. Hangi arama API'sinin ne zaman kullanılacağı, API limitleri ve karar ağacı bu skill'de tanımlıdır.
2. **İkincil skill'leri yükle** — `tavily-search`, `serper-search`, `brave-search` gibi domain-specific skill'ler.
3. **Ana işe başla** — web_search doğrudan kullanma.

**Pitfall:** web_search'e direkt atlamak arama stratejisini bypass eder. Tavily > Brave > Serper > web_search sırası unified-search skill'inde tanımlıdır. Atlarsan sonuçlar yüzeyde kalır.

## Phase 0b: Pre-Research Clarification (MANDATORY)

**NEVER jump straight into broad research.** Edel explicitly corrected this:

> "Bana strateji planını netleştirmek ve araştırmada odaklanman gereken yolu
>  ve bilgileri belirlemen için sorular sor çünkü çok geniş alan gelen bilgiler
>  genel geçer olabilir."

Before creating any cron jobs or research phases, ask 3-5 targeted questions:

| Category | Example Questions |
|----------|-------------------|
| **Existing assets** | "Web sitenin URL'si ne? Mevcut trafik/SEO durumu?" |
| **Budget** | "Aylık ne kadar ayırabilirsin? Hangi kanala öncelik verelim?" |
| **Target audience** | "Tam olarak kime ulaşmak istiyorsun? Yaş, konum, sorun?" |
| **Past attempts** | "Şimdiye kadar neler denedin? Neler çalıştı, neler çalışmadı?" |
| **Success metrics** | "Başarıyı nasıl ölçeceğiz? Ayda kaç danışan hedef?" |

**Pitfall:** Jumping into broad research without clarification produces generic, unactionable results.
Always narrow the scope with user-specific details first.

**Pitfall:** If user deflects a question (e.g., "O kim boşver"), drop it immediately. Don't probe
personal/identity details that aren't relevant to the research task.

---

## Phase 1: Design Research Phases

Break the research into 3-5 independent phases, each with a clear scope:

```
Faz 1: Pazar & strateji araştırması
Faz 2: Teknik derin dalış (API'ler, repolar, araçlar)
Faz 3: Alternatif kanallar & karşılaştırmalar
Faz 4: Sentez & strateji raporu (reads all files, compiles)
```

Each phase must be **self-contained** — cron jobs run in fresh sessions with no prior context.

---

## Phase 2: Schedule Cron Jobs

Use `cronjob(action='create')` with one-shot schedules (`40m`, `80m`, `180m`).

### Per-phase template:
```yaml
name: "Proje Adı Faz N: Konu"
schedule: "40m"          # one-shot, staggered
repeat: 1
deliver: "local"         # save to file, don't notify user yet
enabled_toolsets: ["web", "terminal", "file", "delegation"]
prompt: |
  # Research prompt with clear headings
  ## Araştırma Başlıkları:
  1. ...
  2. ...
  
  ## Talimatlar:
  - delegate_task ile paralel araştır
  - Bulguları ~/research_PROJE/fazN_konu.md dosyasına kaydet
  - "Öne Çıkan İçgörüler" bölümü ekle
```

### Final synthesis phase template:
```yaml
name: "Proje Adı Faz Final: Sentez & Rapor"
schedule: "180m"         # after all research phases complete
repeat: 1
deliver: "origin"        # deliver to user via Telegram
enabled_toolsets: ["terminal", "file", "delegation"]
prompt: |
  # Synthesis prompt
  
  ### ADIM 1: Tüm faz dosyalarını oku
  cat ~/research_PROJE/faz1_*.md
  cat ~/research_PROJE/faz2_*.md
  
  ### ADIM 2: Nihai raporu oluştur
  - Yönetici Özeti
  - Strateji (kısa/orta/uzun vadeli)
  - Maliyet & ROI tablosu
  - Aksiyon planı (ilk 7 gün)
  
  ### ADIM 3: Raporu gönder
  - Markdown formatında, Türkçe
  - Sıcak ve net dil
```

### Timing guidelines:
- Phase 1: `1m` (immediate)
- Phase 2: `30-40m`
- Phase 3: `65-80m`
- Phase 4: `120-130m` (enough time for all phases to complete)
- Research phases get `deliver: local`, final gets `deliver: origin`
- Add `code_execution` to `enabled_toolsets` if using Tavily or other API calls
- **Schedule format:** Use `once in Xm` for relative scheduling (e.g. `30m`, `120m`). Do NOT use `now` (invalid) or ISO timestamps.

### Depth requirements:
- Each research phase: minimum 10-15 findings
- Each Tavily phase: minimum 10 queries, 12 recommended
- Final report: minimum 25-30 consolidated findings
- Every finding needs: name, link, relevance score (1-5), setup difficulty, one-line value proposition

### Tavily — USE ctx_execute_file (NOT terminal curl)

⚠️ Bash `$(cat file)` and `execute_code` with `builtins.open` both SILENTLY FAIL due to secret redaction / smart approval.

**Load `tavily-search` skill for the canonical working pattern.** Only `ctx_execute_file` with `FILE_CONTENT` works reliably.
Always guard with `if a:` before slicing. Same for `results` — use `or []` fallback. If `d` itself is None
(json.loads failed), the API returned empty — check rate limit or API key validity.
Test with a simple query first before running 3+ parallel Tavily calls.
### Depth requirements:
- Each research phase: minimum 10-15 findings
- Each Tavily phase: minimum 10 queries, 12 recommended
- Final report: minimum 25-30 consolidated findings
- Every finding needs: name, link, relevance score (1-5), setup difficulty, one-line value proposition

### Deep search upgrade: Tavily + NotebookLM combo (RECOMMENDED)
When Edel wants deeper research ("yüzeysel değil", "daha fazla araştır"):
- **Tavily FIRST:** 3-4 parallel searches targeting different angles
- **NotebookLM SECOND:** `research_start(mode="fast")` for structured source discovery  
- **web_extract THIRD:** Pull full pages from best Tavily results for verification
- **web_search LAST:** Only for specific queries Tavily misses
- This layered approach caught all 3 new universities (UNYP, RAU, Padova) that web_search alone missed
- See `references/university-program-search.md` for the search query templates

### University program research specificity (NEW - added July 2025, updated July 2026)

#### This session discovered a need for DOMAIN-SPECIFIC university program research:

**Critical behavioral guardrail discovered (NOT in previous version):** "**All 4 stakeholder questions must be answered before presentation.**"

**Pattern corrected from current version:** 
- User says "babam soracak" (parent/sponsor will ask questions) 
- **CRITICAL: ALL 4 questions MUST be answered BEFORE presenting ANY recommendation** -> deadline, fee, denklik (YÖK recognition), scholarship status
- Incomplete tables frustrate stakeholder approval and COMPLETELY waste research time
- **NEW rule:** If fee not on website → say "net değil" rather than omitting
- **Session enforcement:** If you skip even ONE of these 4, the patron will reject the whole recommendation and call you "medyo düzenbazın" (you're unreliable)

**Critical insight (carry forward):** Universal research = weak, **domain-specific research = strong**
- Must prioritize soonest deadline programmes (Edel: "başvuru tarihi yakın olsun")
- Must verify ALL 4 stakeholder questions upfront
- Must use consolidated sources first (psycholojiarsiv.com type) before individual university sites
- Must check YÖK denklik status for Turkish graduates
- Must track eliminated options across sessions to avoid repetition

**Subagent Fee Hallucination — ALWAYS Verify from Official Source (26 June 2026)

Critical pattern discovered this session: subagents consistently hallucinate fee data (10x discrepancies common).

When Edel says "direct numaraları teyit et" or mentions amount errors:
- **Critical rule:** Never trust subagent fee data
- Fee verification hierarchy (absolute must): 1) Official PDF/Excel, 2) Official website, 3) Official Instagram, 4) Never third-party sites
- Must verify EVERY fee amount in subagent outputs before presenting
- When Edel says "net değil" (fee not on website), accept that rather than guessing
- Expected output format: exact fee amounts, include currency units

Check that the subagent is using the correct model according to Edel preferences:
- First choice: deepseek-v4-flash-free
- Second: north-mini-code-free
- Third: mimo-v2.5-free

### References

- University program research pattern: `references/university-program-search.md`
- Subagent fee hallucination fix: `references/subagent-fee-hallucination-26-june-2026.md`
- Repository structure: Always `unified-search`, `tavily-search` skill, proper filters, meeting Edel preferences exactly as documented in references.

**Critical insight:** Universal research = weak, **domain-specific research = strong**
- English-medium programs: IEÜ (100% English), EGE (70% minimum), YÖKAR (e-YDS/≥50)
- Deadline proximity filtering: user demands "soonest deadline" priority - NOT "most exciting program"
- Multiple source verification: expensive universities still have inconsistent pricing

** Domain-specific workflow (for university program research):**
1. **Explore user-provided URLs first** (Phase 1)
2. **University-specific search** (Phase 2) - Ege, IEÜ, Bakırçay, Yaşar
3. **Cross-verify** with arşiv sites + Instagram announcements (Phase 3)
4. **Check ALL 4 stakeholder questions** (Phase 4 finale) - no exceptions

**Patron'un soracağı sorular:**
| Question | When to ask | Example |
|----------|-------------|---------|
| Ne zaman? | Always first | "30 Haziran 2026 — 20 gün kaldı" |
| Ne kadar? | Always include | "1,995,000 TL peşin (KDV dahil)" |
| Geçerli mi? | Always verify | "✅ YÖK tanıyor" |
| Burs? | Always check | "❌ KP'de burs yok" |

**Penalty for skipping:** If you skip any of these 4, patron will reject the whole recommendation and say "medyo düzenbazın" (you're unreliable).

**Prompt reminder (NEW for July 2025 phase):** NEVER start "adalet” research with "observing existing workflows" and then presenting "three universities". Start with user-provided URLs first. The user's leads are your primary source.

See `references/university-program-search.md` for the full university program research pattern template and usage examples.

### Deep layering pattern (NOT cancel+recreate)
When Edel says "adımları derinleştir" or "derinlik arttırılabilir":
- **Keep existing phases** — do NOT cancel them
- **Add intermediate phases** between existing ones (e.g., Deep 1.5 between Deep 1 and Deep 2, Deep 2.75 between Deep 2.5 and Deep 3)
- Push the final synthesis phase further out to accommodate new layers
- This is different from the redirect pattern (cancel+recreate) — here we're adding depth, not changing direction

### Hermes Skills Inventory phase (for orchestration projects)
When the research involves Hermes agent orchestration, add a dedicated phase:
- `skills_list()` to catalog available skills
- `skill_view(name='hermes-agent-skill-authoring')` for authoring patterns
- Map which skills exist, which need to be created
- Output: skill gap analysis + new skill templates
- See `references/hermes-skills-inventory.md` for the prompt template

### Security/Circuit breaker phase (for autonomous operations)
When Vanitas will autonomously manage budget/systems:
- Dedicated phase for safety, monitoring, and rollback
- Tavily queries for circuit breaker patterns, anomaly detection, audit logging
- Output: guardrail architecture, kill switch design, approval flow
- See `references/security-phase.md` for the prompt template

---

## Phase 3: Monitor, Refine & Intervene

After creating cron jobs, list them with `cronjob(action='list')` and show Edel the timeline.

### When Edel redirects research (CANCEL+RECREATE pattern)
If Edel says "Faz X pek efektif değil" or gives a new direction:
1. **Cancel** the affected cron jobs: `cronjob(action='remove', job_id='...')`
2. **Recreate** with refined focus based on her specific feedback
3. **Don't append** — replace. Stale jobs running with old direction waste time and produce noise.

This happened twice in the Bardo session:
- First redirect: broad strategy → landing page + Instagram specifics (canceled Faz 2-4)
- Second redirect: strategy research → technical repos + MCP + Tavily deep search (canceled again)

### When user gives new tools (e.g., Tavily API key)
- Save credentials immediately: `write_file` → `chmod 600`
- Update running/upcoming cron jobs to use the new capability
- Add `code_execution` to `enabled_toolsets` if API calls via `execute_code` are needed

Check status periodically. If a phase fails:
1. Read the error from `cronjob(action='list')` → `last_status`
2. Fix the issue (missing dir, tool restriction, malformed prompt)
3. Re-run with `cronjob(action='run', job_id='...')`

---

## Post-Delivery

After the final report is delivered:
- Ask Edel which section to dive deeper into
- Offer to create follow-up cron jobs for implementation
- Save key findings to wiki for future reference
- **For live (non-cron) research sessions:** Save progress to `~/.hermes/arastirma-[topic].md`
  with sections: ✅ Best, 🟢 New, 🟡 Backup, ❌ Eliminated. Update after each session so Edel can
  review later. See `references/university-program-search.md` for an example structure.

---

## Alt Tür: Burs/Hibe Araştırması (Scholarship/Grant Research — 26 Haz 2026)

Bu alt tür, Edel'in "*şu burs veren sitelere bak*" dediğinde devreye girer. Normal üniversite araştırmasından farklıdır çünkü burs siteleri genelde:

- **Agregatör sitelerdir** (tek sitede onlarca burs ilanı)
- Çoğu ilanın **süresi dolmuştur** veya **yurt dışı içindir**
- Kriterler (GPA, YÖKDİL, vatandaşlık) net belirtilir

### Workflow

1. **Siteye gir ve tam listeyi çıkar** — Edel "baştan aşağı" dediğinde sitedeki TÜM ilanları tara, sadece ilk sayfadakilerle yetinme.
2. **Filtrele: Süresi geçmiş mi?** — Çoğu burs ilanı geçmiş yıllara ait olabilir. Süresi geçmiş ilanları ayıkla.
3. **Filtrele: Yurt dışı mı, yurt içi mi?** — Edel KKTC/Türkiye odaklı. ABD, İngiltere, Almanya gibi ülkeler için burslar ilgisini çekmez.
4. **Filtrele: Kriterler uyuyor mu?** — GPA 3.0+ gerekiyorsa ❌, YÖKDİL 70+ gerekiyorsa ❌
5. **Kalanları karşılaştırmalı sun** — deadline, miktar, kriterler, başvuru linki

### Known Scholarship Sites & Their Nature

| Site | Tip | İçerik |
|------|-----|--------|
| **ab-ilan.com** | Türkçe agregatör | AB fonları, hibe, burs, staj — güncel ama çoğu süresi dolmuş |
| **salto-youth.net** | Avrupa gençlik platformu | Erasmus+ eğitimleri, gençlik değişimleri — **üniversite bursu yok** |

### Known pitfalls

| Pitfall | Fix |
|---------|-----|
| İlan başlığı "açıldı" dese de süresi dolmuş olabilir | Her ilanın **yayın tarihi + son başvuru tarihi**ni kontrol et. ab-ilan.com'da "Bu ilanın süresi dolmuştur" uyarısını ara. |
| Burs miktarı cazip ama yurt dışı için | Ülke filtresi uygula — Edel KKTC/Türkiye dışındaki seçeneklerle ilgilenmez. |
| "TÜBİTAK yurt içi" KKTC'yi kapsar mı? | Genelde kapsamaz. Teyit edilemiyorsa "KKTC kapsam dışı olabilir" notu ekle. |
| Burs için GPA 3.0+ şartı çoğu ilanda var | Edel'in GPA 2.33 olduğu için otomatik ele. |
| Burs için YÖKDİL/YDS 50+ şartı çoğu ilanda var | Edel'in YÖKDİL 45 olduğu için otomatik ele. |

### Edel'in Profiline Uyan Burs Tipleri (Aktif/Gelecek)

Bu profilde nadiren aktif burs çıkar. En gerçekçi seçenekler:

1. **Üniversitenin kendi bursu** — GPA'ya göre değerlendirme (YDÜ'de olduğu gibi: diploma gönder, bakarlar)
2. **TÜBİTAK 2210 2. dönem** — Ekim'de açılır, KKTC kapsamı teyit edilmeli
3. **Ecolarship** (Heinrich Böll) — aktif, ayda 10.000 TL, ama ekoloji alanı şartı var

Not: Bu üçü dışında kalan çoğu burs ilanı ya süresi dolmuştur ya da yurt dışı içindir ya da GPA/YÖKDİL engeline takılır.

### Araştırma Öncesi Subagent Kullanımı (ZORUNLU)

Edel'in şu uyarısı kalıcıdır: **"Subagentları ve search skillerini kullanmayı unutmuyorsun değil mi?"**

Burs/üniversite/hibe gibi çok seçenekli araştırmalarda:
- `delegate_task` ile **hemen paralel subagent gönder** — bekleme, erteleme
- Her subagent farklı bir site/üniversite/burs türünü araştırsın
- Subagent'lar keşif yapsın, sen doğrulama yap
- Subagent göndermeyi unuttuğun her an Edel'in hatırlatması gerekir — **bu senin hatan**

## Live Session Research (Non-Cron Pattern)

When research happens in a LIVE conversation (not cron jobs), the workflow differs significantly:

### Workflow: Site Exploration → Multi-Angle Searches → Comparison → Stakeholder Delivery

1. **Explore user-provided URLs first** — if Edel gives specific sites (salto-youth.net, ab-ilan.com),
   extract their content thoroughly BEFORE jumping to web_search. The user's leads are the primary source.
2. **Then search broadly** — Erasmus Mundus, country-specific, university-specific
3. **Then narrow by deadline** — filter by what's OPEN NOW, not just what's best quality
4. **Address stakeholder questions** — when the user says "babam soracak" / parent will ask, pre-emptively
   collect: deadline date, total fee, YÖK denklik/recognition, burs availability
5. **Present as compact comparative tables** — one row per programme with the 4 stakeholder fields

### Deadline Proximity Priority (CRITICAL — 10 June 2026 Lesson)

Edel corrected: **"başvuru tarihi yakın olsun"** — prioritize programmes by deadline proximity,
not by programme quality or scholarship size.

- When presenting options, sort by deadline (soonest first)
- Flag AZ ÖNCE açılmış veya AÇILMAK ÜZERE olanları (🆕, 🔥)
- Clearly separate "gelecek yıl açılacak" (next intake) from "şu an açık" (now open)
- Erasmus Mundus full burs is exciting, but if deadline is 6 months away, don't lead with it —
  lead with what's open NOW. Mention the exciting-but-future option as backup.

### Stakeholder Questions Pattern (Parent/Sponsor)

When Edel says "babam soracak" / parent/financier has specific questions,
the programme details MUST include these 4 items for every option:

| Question | Example Answer |
|----------|---------------|
| **Ne zaman başvuru?** (Deadline) | "30 Haziran 2026 — 20 gün kaldı" |
| **Kaç para?** (Total fee) | "1,995,000 TL peşin (KDV dahil)" |
| **Diploma TR'de geçerli mi?** (YÖK Denklik) | "✅ YÖK tanıyor" or "⚠️ Bireysel başvuru gerekir" |
| **Burs var mı?** (Scholarship) | "❌ KP'de burs yok" or "✅ İlk 2'ye %100" |

**Pitfall:** Presenting only 2-3 of these and making the parent ask for the rest. Gather ALL 4
before presenting. If you can't find one (e.g. fee not on website), say "net değil" rather than omitting.
Present in a single clean table so the parent sees all options at a glance.

**Pitfall:** For turbo-pace requests ("hızlıca cevap ver"), shorten to bullet-level but
keep all 4 data points present.

---

### Subagent Reliability — DO NOT Trust Blindly

**Kritik ders (25 Haziran 2026):** `delegate_task` subagent'larının özetleri GÜVENİLİR DEĞİLDİR.
Edel'in ifadesiyle: **"bilgileri tam getirmiyorsun"**.

Subagent'lar şu hataları yapar:
- Eksik bilgi getirme (ücreti yazmama, GPA min atlama)
- Yanlış bilgi (program adını karıştırma, şartları yanlış aktarma)
- Kendi yorumlarını ekleme ("öneririm" gibi)
- Tarihleri karıştırma (2025-2026 ile 2026-2027'yi ayırt edememe)

**Kural:** Subagent çıktısını asla doğrudan Edel'e sunma. Subagent'ın bulduğu bilgiyi:
1. **Resmi kaynaktan doğrula** — üniversitenin kendi sayfasına gir, PDF'ini oku
2. **Eksik alanları tespit et** — GPA, ALES, ücret, YÖKDİL, başvuru tarihi — hepsi var mı?
3. **Eksikse "net değil" de** — uydurma veya subagent'ın yarım bilgisini sunma
4. **Sadece DOĞRULANMIŞ bilgiyi aktar**

### ⚠️ Subagent Fee Hallucination — ALWAYS Verify from Official Source

**Kanıtlanmış hata (25 Haziran 2026):** Subagent'lar sürekli yanlış ücret bildiriyor:
- Gedik Üniv: subagent "130 bin TL" dedi → gerçek **1.285.000 TL** (10x fark!)
- Altınbaş Üniv: subagent "550.000 TL" dedi → gerçek **1.100.000 TL**
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

**Ne zaman subagent kullanma:** Sadece ön tarama / keşif için. Keşif sonucunu asıl kaynaktan doğrula.

### Consolidated Source First — Multi-University Scanning

**Kritik ders (25 Haziran 2026):** Edel: *"internette bunları toplu arayabilecek site vs varsa kullanman daha iyi olabilir 3 4'lü istanbul ünileri taramak uzun sürüyor"*

Üniversite veya benzeri çok seçenekli araştırmalarda:
1. **Önce konsolide kaynağı bul** — tüm seçenekleri tek sayfada listeleyen site (örn. psikolojiarsiv.com, YÖK atlas)
2. **Konsolide kaynaktan ön eleme yap** — hangi üniversiteler senin kriterlerine uyuyor?
3. **Ancak ONDAN SONRA** tekil üniversite sayfalarına girerek doğrula
4. **Her üniversiteyi tek tek tarama** — önce büyük resim, sonra detay

**Sıra:** Konsolide kaynak → Web_search ile teyit → Resmi site ile doğrulama

### Session History Check — Before Any Research

**Kritik ders (25 Haziran 2026):** Edel: *"sen konuşma geçmişini çekemiyor musun? Aydın üniversitesine de baktık onu niye getiriyorsun?"*

Çok seçenekli araştırmaya başlamadan ÖNCE:
1. `session_search(query=...)` ile geçmiş konuşmaları kontrol et
2. `memory`'deki eliminated listeyi oku
3. Eğer session_search boş dönerse: **Edel'e sor** — "daha önce şu üniversitelere bakmış mıydık?"
4. Asla varsayım yapma. session_search boş diye "hiç konuşulmamış" anlamına gelmez.

### Eliminated Options Tracking

Her araştırma oturumunda:
- Eliminated seçenekleri memory'e kaydet (veya session boyunca kafanda tut)
- Bir seçenek elendikten sonra TEKRAR GETİRME
- Sadece HENÜZ KARAR VERİLMEMİŞ seçenekleri sun
- Elenenleri neden elendiğini tekrar açıklama — memory'de kayıtlı

### Parallel Subagent + Manual Gap-Fill Pattern (26 June 2026)

Bu oturumda keşfedilen pattern: subagent'larla geniş tarama yap, sonra boşlukları elle doldur.

**Workflow:**
1. **Subagent'ları toplu gönder** (delegate_task ile 4-6 paralel) — her biri farklı bir üniversiteyi araştırır
2. **Subagent sonuçlarını tara** — hangi alanlar eksik? (ücret, GPA, ALES, deadline, YÖKDİL)
3. **Doğrudan resmi kaynağa git** — subagent'ın bulamadığı/yanlış getirdiği verileri elle doğrula:
   - Ücret PDF'ini manuel aç (subagent 404 alabilir, sen direkt URL'den oku)
   - Başvuru takvimini resmi siteden kontrol et
   - Ders kataloğundan program varlığını teyit et
4. **Birleştir ve sun** — subagent bulguları + senin doğruladığın veriler

**Ne zaman kullanılır:** Çok sayıda üniversite/program paralel taranırken. Subagent'lar keşif içindir, doğrulama için değil.

**Pitfall:** Subagent'ın "bulamadım" dediği veriyi atlama. Çoğu zaman subagent sayfayı yanlış parse etmiştir veya PDF'i açamamıştır — sen direkt kaynağa gidince veri oradadır (ör: Haliç ₤850 ücretini subagent bulamadı ama PDF'te duruyordu).

Güncel üniversite verileri için `references/university-program-search.md` dosyasına bak.

### Pitfalls

| Pitfall | Fix |
|---------|-----|
| Skipping Phase 0 (no clarification) | ALWAYS ask 3-5 questions first |
| Not checking Tavily availability | Load `tavily-search` skill. Tavily PRIMARY, web_search fallback. Edel will ask "tavily kullandın mı?" if results feel shallow. Use `ctx_execute_file` — DO NOT use bash `$(cat file)` or `execute_code` (both silently fail due to secret redaction). |
| **Deadline proximity ignored** | For burs/fırsat araştırması, ALWAYS sort by deadline proximity (soonest first). Edel: "Global MINDS başvuru tarihi çok ileri" → flag future options as backup, lead with what's open NOW. |
| Research too broad → generic results | Narrow scope based on user answers |
| Probing deflected questions | Drop immediately — "O kim boşver" means move on |
| Cron jobs overlapping | Stagger 30-40 min apart |
| Final synthesis can't find files | Ensure `~/research_PROJE/` dir exists before Phase 1 |
| deliver=origin on research phases | Only final phase gets origin; research phases use local |
| User redirects research | Cancel+recreate affected jobs, don't append |
| User says "derinleştir" / "depth" | Add intermediate phases (1.5, 2.75), do NOT cancel existing. Push final phase out. |
| New API key/tool given mid-research | Save creds, update upcoming jobs, add code_execution toolset |
| ISO timestamps in schedule | Use relative durations: "30m", "65m", "120m" |
| delegate_task silently broken (model config ignored) | **Known Hermes bug #12440 (P1)** — subagents inherit parent model regardless of delegation config. Workaround: use `terminal` subprocess instead. Or accept same-model delegation if parent model suffices. When bug is fixed, resume normal delegate_task usage. |
| Subagent model selection — Edel's preference ignored | Edel explicitly corrected: **deepseek-v4-flash-free** kullanılmalı, north-mini-code-free veya mimo-v2.5-free kullanma. `delegate_task` alt ajanlarında model override dene. `opencode run -m opencode/deepseek-v4-flash-free` önce dene, 45sn timeout yerse delegate_task'e geç. Preference sırası: deepseek-v4-flash-free >> north-mini-code-free >= mimo-v2.5-free. |
| **University program research specificity** | This session discovered a need for DOMAIN-SPECIFIC university program research (deadline proximity, YÖK recognition, exact fee amounts, GPA minimums). Web search results had inconsistencies. Prioritize soonest-deadline programmes and present ALL 4 stakeholder questions (when/paid/denklik/burs) upfront. |

---

## Proven Pattern (Example)

From the Bardo marketing research project (2026-05-24):

```
~/research_bardo/
├── faz1_pazar_strateji.md       # Phase 1: Market research
├── faz2_googleads_ai.md         # Phase 2: Google Ads + AI repos
├── faz3_alternatif_kanallar.md  # Phase 3: Alternative channels + SEO
└── bardo_strateji_raporu.md     # Phase 4: Compiled strategy report
```

4 cron jobs, spaced 40-80 min apart, final delivery at 180m.
Each phase used `delegate_task` internally for parallel research within the phase.

See `references/bardo-prompts.md` for the exact prompts used.
See `references/tavily-integration.md` for Tavily API setup and code patterns.
See `references/university-program-search.md` for multi-country university program search with constraint filtering (deadline/GPA/budget/language).
See `references/burs-hibe-arastirmasi-ab-ilan-26-haz-2026.md` for scholarship/grant research findings from ab-ilan.com and salto-youth.net scans.
See `references/hermes-skills-inventory.md` for the skills inventory phase template.
See `references/security-phase.md` for the security/circuit breaker phase template.
See `references/cron-refinement-pattern.md` for iterative cron job refinement with real examples.
See `references/multi-page-course-scraping.md` for systematic multi-page course/documentation scraping technique.
See `references/upwork-job-research.md` for freelance platform (Upwork) job research with bot-detection workarounds and job-fit analysis templates.
See `references/ai-model-marketplace-research.md` for AI model marketplace research methodology (browser-based extraction from Zenmux/Pollinations/OpenRouter, model capability filtering, multi-criteria comparison).
