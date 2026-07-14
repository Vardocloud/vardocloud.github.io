# APA Monitor Full-Text Extraction

## Workflow (Updated 10 Tem 2026)

### 1. APA Login
- URL: `https://sso.apa.org/apasso/idm/apalogin`
- Email+password (NOT Google OAuth)
- Browser tool must be used — cookies persist for session duration
- APA member display name: "Vatinas Reister"

### 2. Monitor PDF Download (PREFERRED — single file, all articles)

The entire Monitor issue (92 pages) is available as a single PDF:

1. Navigate to issue page: `https://www.apa.org/monitor/2026/07-08/`
2. Click "Download issue (PDF, 6.6MB)" link (ref=e151 in snapshot)
3. PDF opens in browser's built-in viewer (Chrome PDFium)
4. All 92 pages, full text, searchable
5. To extract: use browser_console `document.body.textContent` or snapshot

**Note:** The PDF URL `https://www.apa.org/monitor/2026/2026-07-08-monitor.pdf` returns 200 but Content-Type is text/html without login (redirects to login page). Must be accessed via browser with active APA session.

### 3. Per-Article Extraction (Alternative)

Monitor article pages are public (no paywall), so `web_extract` works after login:

1. `https://www.apa.org/monitor/2026/07-08/` (issue page — public)
2. Click article link → `web_extract` or browser tool

### 4. PsycNET Full Text — NOT Available with Basic Membership ⚠️

PsycNET (`psycnet.apa.org`) record pages are public (abstract only).
Full text (`/fulltext/...`) returns **403 Forbidden** even after APA member login.
APA basic membership does NOT include full-text journal access for all journals.

**PsycNET is a React SPA** — `document.body.textContent` returns empty.
Use browser_snapshot(full=true) for metadata/abstract extraction.
PDF links exist in the DOM but may not be clickable via ref= due to React rendering.

### 5. NotebookLM Upload

APA Monitor URL'leri NotebookLM'de indexleniyor:
```bash
nlm source add <NOTEBOOK_UUID> --url "https://www.apa.org/monitor/2026/07-08/brain-stimulation-mental-illness-treatment" --title "APA Monitor — TMS CE Corner — 2026-07-08" --wait
```

### 6. Known URL Patterns (Jul/Aug 2026)

- AI Reshaping Skills: `/monitor/2026/07-08/ai-job-skills-thinking`
- TMS Brain Stimulation: `/monitor/2026/07-08/brain-stimulation-mental-illness-treatment`
- Gambling Boom: `/monitor/2026/07-08/prediction-driven-gambling-mobile-betting-apps`
- Conversion Therapy Bans: `/monitor/2026/07-08/speech-conduct-conversion-therapy-bans`
- Healing from Infidelity: `/monitor/2026/07-08/psychologists-help-heal-infidelity`
- Animals in Therapy: `/monitor/2026/07-08/animals-therapy`
- Center for Behavioral Science & AI: `/monitor/2026/07-08/center-behavioral-science-ai`
- Volunteering: `/monitor/2026/07-08/volunteering-kind-acts`
- Student Loan Rules: `/monitor/2026/07-08/student-loan-debt`
- Model Licensing Act: `/monitor/2026/07-08/model-licensing-act-future-psychology`
- Sensory Processing: `/monitor/2026/07-08/sensory-processing-systems`
