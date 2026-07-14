# University Program Cost Analysis Template

## When to Use
Researching and comparing university programs (master's/PhD) across countries with multiple criteria: language, GPA requirements, tuition fees, living costs, accreditation, visa/work rights.

## Excel Template Structure (7 Sheets)

### Sheet 1: Genel Özet (General Overview)
- All candidate programs listed: University, Program Name, Country, Duration, Language, Total Cost
- Color-coded by viability (green = viable, yellow = needs verification, red = eliminated)
- Eliminated programs get ❌ marker with one-line reason — never mixed into active comparison

### Sheet 2: Kriter Karşılaştırması (Criteria Comparison)
- Columns: Program, Language, GPA Minimum, IELTS/TOEFL, Duration, Accreditation (YÖK/other)
- **Filter by Edel's criteria FIRST, then list.** Non-matching programs get brief reason, not full row.
- Use official .edu pages as source of truth for admission requirements

### Sheet 3: Maliyet Analizi (Cost Analysis)
- Columns: Tuition (annual), Tuition (total), Living (monthly), Living (annual), One-time Fees, Total Cost
- Living costs: Numbeo baseline + student forum cross-reference (Reddit, Erasmusu)
- One-time fees: registration, visa application, health insurance, residence permit
- Add 15-20% buffer for hidden/unexpected costs

### Sheet 4: Ödeme Planları (Payment Plans)
- Installment options per university: number of installments, deadlines, early payment discounts
- Part-time alternatives with per-year cost breakdown
- Currency and exchange rate notes (€ preferred, £ and $ converted)

### Sheet 5: Vize ve Çalışma (Visa & Work)
- Student visa requirements per country (financial proof, documents, processing time)
- Work permit rules during study (hours/week, restrictions)
- Post-graduation stay rights and job search periods
- Country-specific legislation references (e.g., Greece Law 5275/2026)

### Sheet 6: Risk Analizi (Risk Analysis)
- Accreditation stability (HAHE approval pending, program under review)
- YÖK recognition status (official database check)
- Currency fluctuation risk (TRY vs program currency)
- Political/economic stability indicators for each country

### Sheet 7: Referanslar (References)
- All source URLs with access dates
- Official university pages, government sites, student forums
- Organized by program/country for easy verification

## Research Methodology

### Phase 1: Initial Discovery
```
unified-search queries:
  "[field] [degree] [country] English international students tuition 2026"
  "[country] university [field] master's low GPA acceptance"
  "YÖK tanınan üniversiteler [country]"
```

### Phase 2: Official Verification
- `web_extract` on official .edu program pages for exact fees, admission requirements
- Cross-reference tuition with university's official fee schedule (PDF)
- Verify YÖK recognition via YÖK's official database, not third-party claims
- Check application deadlines and intake periods (Fall/Spring)

### Phase 3: Living Cost Research
- Numbeo for baseline cost of living (rent, food, transport, utilities)
- Reddit/Erasmus forums for student-reported actual costs
- Cross-reference with official government student visa financial requirements
- Note: official minimum ≠ actual comfortable living cost

### Phase 4: Structured Output
- Build Excel with `openpyxl`:
  ```python
  # Write script to /tmp, execute via terminal
  # execute_code may be blocked in certain contexts
  from openpyxl import Workbook
  from openpyxl.styles import Font, PatternFill, Alignment
  from openpyxl.utils import get_column_letter
  ```
- Format: frozen headers, auto-filter, currency formatting (€), conditional coloring
- Column widths: auto-fit or manual for readability
- Deliver via Telegram native file attachment (`MEDIA:/path/to/file.xlsx`)

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| Listing eliminated programs in active comparison | Separate "Elenenler ve Nedenleri" section, don't mix |
| Skipping Edel's core criteria (GPA, language, budget) | Filter first, list second. Non-matching → brief ❌ note |
| Using outdated tuition data | Always check official .edu pages, note academic year (2026/27) |
| Trusting one source for fees | Cross-reference: official page + PDF fee schedule + third-party |
| Missing one-time fees | Track: registration, visa, health insurance, residence permit |
| Forgetting payment structure differences | Document installments, part-time options, early payment discounts |
| execute_code blocked (cron/restricted context) | `write_file` to /tmp then `terminal python3 /tmp/script.py` |
| Living cost from one source only | Cross-reference Numbeo + student forums + visa requirements |
| Ignoring post-graduation rights | Check work permits, job search visas, residency paths |
| YÖK status from unofficial sources | Use only YÖK's official database, note "pending verification" |
