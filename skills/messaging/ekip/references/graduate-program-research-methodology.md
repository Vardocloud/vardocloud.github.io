# Graduate Program Research Methodology (Europe)

Learned during clinical psychology master's research for Edel (5 June 2026).

## Research Pattern (Proven)

When researching graduate programs for Edel:

1. **Parallel `web_search`** — 3-5 searches simultaneously targeting different countries/regions
2. **Extract promising pages** with `web_extract` — target: admission pages, program descriptions, fee pages
3. **Compile comparison table** — always include these columns:
   - University + Program name
   - Language of instruction
   - Annual fees (non-EU rate)
   - Total program cost
   - GPA minimum
   - Interview/entrance exam?
   - Additional language requirement?
   - Application deadline
   - Key constraint notes

4. **Present as table + conversational summary** — not report format

## Why This Pattern Won

- `delegate_task` for web research **timed out** at 600s (3 parallel subagents all failed, consistent across two batches — 6 total failures on 5 June 2026)
- Direct `web_search` + `web_extract` was faster and more reliable
- Edel wants **comprehensive coverage**: all countries, all universities, not just top 3

## Critical Rules

### DONT re-list eliminated options
When Edel says "X and Y are eliminated, focus on Z", remove X and Y from all subsequent tables and summaries. Re-listing them wastes time and signals "not listening." Only reintroduce if new information changes the elimination criteria — and ask first.

### ALWAYS have the source link ready
When making specific claims about programs ("internship requires Greek"), Edel will ask "are you sure? bring the link." Have the program page URL ready. Web_extract results contain the URL — always include it in your notes. Corollary: distinguish between explicit requirements on the page vs. inferences you made. Say "the page states X" not "this program requires X" when quoting. Say "I interpret this as Y" when inferring.

## Edel's Constraints (Always Check)

- Budget: TL değeri düşük → prioritize affordable programs
- No second language: English-only programs
- Clinical psychology label required (not just "psychology")
- Prefers no interview/entrance exam ("meşakkatli")
- Turkish psychology graduate targeting European programs

## Country-Specific Notes

### Italy — Best Value for English Clinical Psychology
6 programs found (June 2026):
- Sapienza Rome: Applied Dynamic & Clinical Psychology (~€2,924/yr, entrance test)
- Tor Vergata Rome: Clinical Psychosexology (~€1,000/yr)
- Padua: Clinical, Social & Intercultural (€2,739/yr, interview, 20 non-EU spots)
- Padua: Cognitive Neuroscience & Clinical Neuropsychology (€2,739/yr)
- Bergamo: Clinical Psych for Individuals (€0-2,100 total, Italian B1/B2 required ❌)
- Bologna: Psychology of Wellbeing (~€400+, interview min 21/30, EU-only 2nd intake)

### Ireland — No Interview, Higher Cost
- Range: €17,000-24,000/yr (1-year programs)
- 2:2 (55%) accepted at UCC, Galway, DCU, UL
- 60%+ required at UCD, TCD
- PSI accreditation critical

### Germany — Free but Clinical Almost Never in English
- Public universities: tuition-free (€150-350 semester fee)
- Clinical psychology programs: 95% German-taught
- English options: Neuro-Cognitive Psych, Cognitive Science, Neurosciences (not clinical)

### Spain — PGS Requires Spanish
- Máster en Psicología General Sanitaria = mandatory for practice
- All public PGS programs in Spanish/Catalan
- Non-EU fees: €1,100-15,000 depending on region
- GPA-flexible universities: Salamanca, Rovira i Virgili, Valencia, Jaén

### Portugal — Public Cheap but Programs in Portuguese
- Public: €495-697/yr
- International: €3,000-8,000
- English clinical psychology: not found

### Balkans / Eastern Europe
- Poland: SWPS Warsaw €9,200/yr (sınav+mülakat). AFMKU Krakow (€3,800/yr AB) — eliminated from final 6 due to interview requirement.
- Czech: Mostly Czech-taught, Masaryk psychology in Czech
- **Slovakia — UPJŠ Košice (Final 6 ✅):** Pavol Jozef Šafárik University, MSc Clinical Psychology, English, ~€5,500/yr, YÖK✅, AB üyesi. No GPA minimum published. Living costs ~€500-700/month. Strong research university (QS #1001-1200).
- Limited English clinical options found in region overall

### Greece — York Europe Campus (Major Discovery)
**CITY College, University of York Europe Campus (Thessaloniki):**
- MSc Clinical Psychology — English, 1yr dissertation / 1.5yr internship
- Degree awarded directly by **University of York** (UK Russell Group, THE #154)
- €7,900 dissertation track / €9,300 internship track (international rate)
- No minimum GPA published ("good performance" language)
- Psychology bachelor's likely not mandatory
- **Staj için Yunanca şart** (internship track only) — dissertation track has no Greek requirement
- Deadline: July 2026 for October 2026 start
- YÖK: University of York recognized, individual denklik assessment needed
- Student reviews ⭐4.5/5, but career support weak, campus relocated to outskirts
- Living costs: €600-800/month

### Kazakhstan — Turan University
**Turan University (Almaty):**
- MSc Clinical Psychology — English/Kazakh/Russian
- Two tracks: Research (2yr) / Specialized (1yr)
- ~€6,200 total, no GPA requirement (open admission)
- Psychology or medicine bachelor's required
- EEG lab + PBS-BOS psychophysiology complex — strong research infrastructure
- QS Asia #1001-1100
- YÖK: Recognized ✅
- Turkish-friendly environment, easy visa
- Living costs: €350-500/month

### Caucasus & Central Asia (June 2026 — Full Region Scan)

**Scope:** Azerbaijan, Georgia, Kazakhstan, Kyrgyzstan, Uzbekistan, Tajikistan, Turkmenistan, Armenia.

#### 🇦🇿 Azerbaijan — 2nd Viable Option Beyond WCU
**Khazar University (Baku):**
- **MS Clinical Psychology** — English, YÖK ✅ (Mevlana listesinde)
- Early bird: $3,750/yr / Regular: $5,000/yr
- TOEFL/IELTS optional, GPA esnek
- Early bird deadline: 1 June 2026, regular: 31 Aug 2026
- Known programs: MS Clinical Psych + MS Applied Psych (two separate tracks)

#### 🇰🇿 Kazakhstan — Most Dense Market
| University | Program | Fee/yr | YÖK | Note |
|------------|---------|--------|-----|------|
| Turan University | Clinical Psychology | ~$730-2,500 | ✅ | Research/Specialized tracks |
| Al-Farabi KazNU | Clinical Psychology YL | ~$4,200 | ✅ | Mevlana listesinde, köklü devlet üni |
| Astana Medical Univ | Clinical Psychology (24mo) | ~$2,889 | ⚠️ | Devlet hizmeti sadece burslulara |
| Abay KazNPU | Psychology (bilişsel) | ~$2,084 | ⚠️ | Klinik değil, araştırma odaklı |

**Key finding:** KazNU Turan'dan daha prestijli ama $4,200 vs $730-2,500 farkı var.

#### 🇬🇪 Georgia — Eliminated
No English clinical psychology master's found. Caucasus University has the program but in Georgian. Ilia State, Tbilisi State: bachelor's level or Georgian-only.

#### 🇰🇬 Kyrgyzstan — Eliminated
AUCA (American University of Central Asia): MA Applied Psychology, $9,997/yr, IELTS 5.0. NOT clinical psychology. YÖK status unclear.

#### 🇦🇲🇺🇿🇹🇯🇹🇲 Others — Eliminated
Armenia: 14 universities offer psychology master's, none in English clinical psychology.
Uzbekistan, Tajikistan, Turkmenistan: No English clinical psychology master's found.

## Final Output Files (Do NOT Regenerate — Use These)

| File | Content | Status |
|------|---------|--------|
| `wiki/azerbaycan-kazakistan-klinik-psikoloji-analiz.xlsx` | 7-sheet Excel: Azerbaijan + Kazakhstan detailed comparison (Haz 2026) | **Current** |
| `wiki/avrupa-klinik-psikoloji-analiz.xlsx` | Europe-wide comparison (Italy, Greece, Ireland, etc.) | Previous round |

**Current Final 6 (Haz 2026):**
1. WCU Bakü 🇦🇿 — €3,700/yr, YÖK✅
2. Khazar Bakü 🇦🇿 — $3,750-5,000/yr, YÖK✅
3. KazNU Almatı 🇰🇿 — ~$4,200/yr, YÖK✅
4. Turan Almatı 🇰🇿 — ~$730-2,500/yr, YÖK✅
5. UPJŠ Košice 🇸🇰 — ~€5,500/yr, YÖK✅, AB
6. York Selanik 🇬🇷 — €7,900/yr, York diploması, YÖK✅

**Eliminated from earlier rounds:** AFMKU Krakow (mülakat), MIC Madrid (sahte üni ❌), Georgia/Kyrgyzstan/Armenia (İngilizce klinik psikoloji yok)

### Spain — MIC College ⚠️ RED FLAG
**Madrid International College (MIC):**
- MSc Clinical Psychology listed but **NOT a legitimate university**
- Accreditation from alternative medicine associations (Panhellenic Assoc. of Complementary Alternative Medicine), not Spanish Ministry of Education
- Also offers Iridology, Aromatherapy, Naturopathy — holistic/alternative focus
- Ranking claims ("3rd Nature Index Young University") appear fabricated
- YÖK recognition: virtually impossible
- **Verdict: DO NOT RECOMMEND** for clinical psychology licensure
