# University Fee Table Interpretation

## Problem

University fee pages often use multi-column tables. Misreading them leads to wrong financial advice.

## Case Study: York Europe Campus (2026-27)

### The Table (Raw)

| Programme | Full-Time (Home/EU) | Part-Time (Home/EU) | Full-Time (International) |
|---|---|---|---|
| Clinical Psychology – MSc (Dissertation) | €7,900 | €3,950 (per year) | €7,900 |
| Clinical Psychology – MSc (Internship) | €8,500 (1.5 yrs) | €8,500 (2.5 yrs) | €9,300 (1.5 yrs) |

### Wrong Interpretation ❌

- "€3,950 (per year)" → "Bu altı aylık taksit, 2 taksitte ödeniyor"
- "Part-time daha ucuz, yarı fiyatına"

### Correct Interpretation ✅

- Column 1: Full-time total cost (Home/EU student)
- Column 2: Part-time ANNUAL cost × 2 years = same total as column 1
- Column 3: Full-time total cost (International student)

**The "per year" tag on Part-Time column means "each year of part-time study costs this much" — NOT a semester installment.**

### The Pattern

1. **Tavily deep search** → finds the official fee page, returns raw table content
2. **Serper cross-check** → confirms the same URL is authoritative
3. **web_extract on the confirmed URL** → gets the page with visible COLUMN HEADERS
4. **Read column headers BEFORE interpreting numbers:**
   - Full-Time vs Part-Time vs International are different scenarios
   - "per year" = annual rate, "full course" = total for the program
   - "(N yrs)" = total program duration in that scenario
5. **Cross-check totals:** Part-time annual × years should ≈ Full-time total

## General Rules

- Never read numbers from a fee table without column headers
- If Tavily raw_content has the table but headers are ambiguous → web_extract the page
- "per year" modifiers on Part-Time columns are annual rates, not installment amounts
- When in doubt: look for a Registration Fee line (separate from tuition) — it confirms installment schedules are elsewhere
