# University Research Pattern — Master's Program Deep-Dive

## When to Use
Recurring task: researching international master's programs (especially clinical psychology) for Edel. Each university gets the same treatment: find, verify, summarize.

## Search Layer (use unified-search skill)

### Phase 1 — Surface Scan (Tavily)
```bash
TAVILY_KEY=$(head -1 ~/.hermes/tavily_key.txt)
# Query template:
query = "UniversityName City ProgramName master's program tuition fee 2025 2026 international students"
```
Tavily's AI answer often includes the tuition fee directly. Cross-check with official sources.

### Phase 2 — Brave Cross-Validation
```bash
BRAVE_KEY=$(head -1 ~/.hermes/brave_key.txt)
# Same query, look for:
# - Different tuition figures → flag discrepancy
# - Rankings/mentions → verify university legitimacy
# - Student forums → insider info
```

## Browser Deep-Dive (when web_extract fails)

### Pages to Find on the University Site
1. **Program page** — `/en/obrprogramms/clinical-psychology` or similar
   - Look for: language of instruction, duration, admission requirements
2. **Tuition fee page** — `/en/price` or `/en/tuition-fees`
   - Look for: PDF download links for official fee tables
3. **Foreign/international students page** — `/en/foreign-students` or `/en/international`
   - Look for: specific admission procedure, deadline, document list
4. **Department/Faculty page** — to find the right contact person
5. **Master's program overview page** — `/en/magistratura/` or `/en/graduate-programs`

### PDF Extraction Technique
- Many universities host fee tables and admission rules as PDFs on Google Drive
- Find the direct Google Drive link from the webpage
- Download: `https://drive.google.com/uc?export=download&id=FILE_ID`
- Extract text: Use `pdftotext` or python's `PyMuPDF` (fitz)
- Search for key terms: language, master, foreign, deadline, price in KZT/USD/EUR
- Note: Google Drive may require a confirm token on first request — handle with retry

### Must-Find Data Points
| Data Point | Where to Look | Verification |
|------------|--------------|--------------|
| Program exists & code | Program page + ENIC accreditation | Cross-check both |
| Language of instruction | Program page vs. master's overview page | If contradictory → flag |
| Tuition fee | Price page PDF | Cross-check with 3rd party |
| Application deadline | Foreign students page + Admission rules PDF | Get exact date |
| Admission requirements | Admission rules PDF + program page | Interview? Exam? GPA? |
| YÖK denklik | Search for university ranking + bilateral agreements | Flag if uncertain |
| Contact person | Department/faculty page | Prefer named person over generic |

### Common Pitfalls
- **Fee table columns misread**: Always check column headers. "Per year" vs "per semester" vs "per credit hour"
- **Language contradictions**: Master's overview page may say "Kazakh, Russian" while the specific program page says "English" — ask the contact
- **Exchange rates**: Check current rate (exchangerate-api.com) — don't rely on old conversions
- **PDFs in Russian/Kazakh**: Use browser translation or OCR if needed — don't skip them
