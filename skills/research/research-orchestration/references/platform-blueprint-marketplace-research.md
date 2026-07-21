# Platform Blueprint/Çözüm Marketplace Araştırması — NVIDIA Blueprints & Benzeri

**Session origin:** 2026-07-21 — NVIDIA build.nvidia.com/blueprints
**Umbrella skill:** `research-orchestration`

## Overview

When Edel asks to evaluate a technology platform's solution/blueprint marketplace (NVIDIA Blueprints, AWS Solutions, GCP Blueprints, Huggingface Spaces, etc.), use this methodology to systematically extract listing data, evaluate each solution, and produce tiered recommendations.

This is **distinct** from AI model marketplace research (`references/ai-model-marketplace-research.md`) — the target here is **full AI solutions/blueprints** with deployment options, hardware requirements, and use-case alignment, not just model pricing/capabilities.

## Workflow

### Phase 0: Platform Reconnaissance

Before diving into extraction:

1. **Count total items** — e.g., "42 blueprints" on NVIDIA
2. **Check pagination type**:
   - URL-based (`?page=2`) — easier, direct navigation works
   - JS tab-based (`<button>1</button><button>2</button>`) — needs browser_click
   - Infinite scroll — needs multiple scroll + extraction rounds
3. **Identify filter taxonomy**:
   - Industry/vertical (General, Healthcare, Financial Services, Retail, etc.)
   - Blueprint type (Launchable, Developer Example, Enterprise, NemoClaw)
   - Use case (Drug Discovery, AI Agent, Text-to-Speech, etc.)
4. **Check sort options** — Most Recent, Name ASC/DESC
5. **Note labeling system** — "12d" (12 days ago), "5mo" (5 months ago), "Deprecated" badges

### Phase 1: Initial Listing Scan (Browser + JS)

**Step 1 — Navigate and get headings:**
```javascript
// Get all blueprint card headings
Array.from(document.querySelectorAll('h3')).map(el => el.innerText?.substring(0, 150)).filter(Boolean)
```

**Step 2 — Get card descriptions with metadata:**
```javascript
// Extract full card content as text blocks
Array.from(document.querySelectorAll('[class*="grid"] > *, main > section > *, main > div > div > *'))
  .map(el => el.innerText?.substring(0, 300)).filter(Boolean)
```

**Step 3 — Get page text in bulk:**
```javascript
document.documentElement.innerText.substring(
  document.documentElement.innerText.indexOf("42 blueprints"),
  document.documentElement.innerText.indexOf("Items per page")
)
```

### Phase 2: Handle Paginated SPAs

NVIDIA's blueprint list uses a **tab-based SPA pagination** (Radix UI Tabs), not URL-based:

**Detection:**
- Page buttons are `<button>` elements with class `nv-tabs-trigger`
- Content of multiple pages exists simultaneously in DOM (virtualized rendering)
- The `data-state` attribute shows which tab is selected (`"active"` vs `"inactive"`)

**Strategies:**

**Strategy A — Tab Click (Preferred for SPA):**
```javascript
// 1. Find pagination buttons
const tabs = document.querySelectorAll('.nv-tabs-trigger');
// tab[0] = "1", tab[1] = "2"

// 2. Click the target page
tabs[1].click(); // Go to page 2
```

**Strategy B — Browser Vision + Annotations:**
Use `browser_vision(annotate=true)` to get visual annotations with ref IDs, then click directly:
```
"2" butonu → ref=e137, e160
browser_click(ref="e137")
```

**Strategy C — Navigate to Detail Pages Directly (Fastest):**
Once you know the URL pattern, skip the listing page entirely:
```
https://build.nvidia.com/{author}/{kebab-case-name}
e.g., https://build.nvidia.com/nvidia/pdf-to-podcast
```

**Pitfall:** `browser_navigate(url="...?page=2")` DOES NOT WORK for JS-tab SPAs — the URL parameter is ignored on reload.

### Phase 3: Extract Detail Page Content

**Method A — `web_extract` (faster, cleaner):**
Once you know the URL slug, use `web_extract` to get structured markdown:
```python
web_extract(urls=["https://build.nvidia.com/nvidia/nemotron-voice-agent"])
```

**Method B — `browser_navigate` + snapshot (for complex pages):**
Navigate to the detail page and use `browser_snapshot(full=true)` for interactive elements.

**Key data points to extract from each blueprint:**
| Field | Source | Example |
|-------|--------|---------|
| **Author** | URL segment | `/nvidia/` |
| **Title** | h1 | "Nemotron Voice Agent" |
| **Tags** | Card badges | "Launchable", "Developer Example", "Enterprise" |
| **Summary** | Card description | "Build Real-Time, Multimodal Voice Agents..." |
| **Category tags** | Link chips | "voice agent", "asr", "tts", "nvidia ai" |
| **GitHub URL** | "View GitHub" link | https://github.com/NVIDIA-AI-Blueprints/... |
| **Deploy option** | "Try Now" / "Deploy on Cloud" | Brev.dev launchable |
| **Architecture** | Detail page | ASR → LLM → TTS pipeline |
| **Hardware requirements** | Detail page | "1x L40 for ASR/TTS, 2x H100 for reasoning" |
| **Status** | Badge color | Active, Deprecated, Enterprise |

### Phase 4: Categorization & Prioritization

Organize findings in **tiers**:

| Tier | Criteria | Example |
|------|----------|---------|
| **Tier 1 — Directly Useful** | Matches existing stack, solves current problem, deployable now | NemoClaw for Hermes Agent (we use Hermes) |
| **Tier 2 — Future Value** | Needs adaptation or additional setup, solves future problem | Ambient Healthcare Agents (needs clinical adaptation) |
| **Tier 3 — Niche/Indirect** | Interesting patterns but low immediate relevance | Multi-Agent Intelligent Warehouse |

**Filter out:** Deprecated blueprints, hardware-inaccessible solutions, unrelated industries.

### Phase 5: Action Plan Generation

For Tier 1 items, produce an action plan with:

| Timeframe | Action | Blueprint |
|-----------|--------|-----------|
| **Hemen** | Install/integrate immediately | NemoClaw for Hermes Agent |
| **Kısa Vade (1-2 ay)** | Adapt to our stack | Nemotron Voice Agent → Voice Bridge |
| **Orta Vade (2-4 ay)** | Full integration | Ambient Healthcare Agents → Psikolog Asistanı |

Each action includes:
- **What to install** (GitHub repo, Docker image, NIM microservice)
- **Dependencies** (GPU, Docker, API keys)
- **Integration points** (existing Hermes skills, pipelines)

### Phase 6: Report Delivery

Structure the final report as:

1. **Genel Bakış** — Marketplace size, categories, total count
2. **Detaylı Analiz** — Per-blueprint breakdown with tech stack + requirements
3. **Tier 1: En Kritik** — Directly useful, with action plan
4. **Tier 2: Gelecek Değerlendirme** — Adaptation needed
5. **Tier 3: Niş** — Interesting but low priority
6. **Uyarılar & Engeller** — Deprecated items, hardware blockers, license issues
7. **Eylem Planı** — Prioritized timeline

## NVIDIA Blueprint URL Patterns

### Listing pages
- `https://build.nvidia.com/blueprints` — Main listing (42 items)
- Pagination: Tab-based (not URL), 24 items per page, 2 pages total

### Detail pages (working URLs from session)
| Blueprint | URL Slug |
|-----------|----------|
| NemoClaw for Hermes Agent | `/nvidia/nemoclaw-for-hermes-agent` (via card click) |
| Nemotron Voice Agent | `/nvidia/nemotron-voice-agent` ✅ |
| PDF to Podcast | `/nvidia/pdf-to-podcast` ✅ |
| Ambient Healthcare Agents | `/nvidia/ambient-healthcare-agents` ✅ |
| LLM Router | `/nvidia/llm-router` ✅ (deprecated) |

Note: Some page 2 blueprints (NVIDIA AI-Q, Voice Agent Framework, Traceability) have URLs that don't match simple kebab-case patterns — use browser_click on the card to navigate.

### Card click behavior on listing page
- Single click on card heading re-loads full listing page (SPA bug?)
- Double-click or JS-click on tab buttons may also not navigate
- **Workaround:** Construct URL manually by guessing kebab-case of title

## Known Platform Quirks

### NVIDIA build.nvidia.com
- **Tab-based pagination** — `?page=2` URL parameter is ignored on page load
- **Virtualized rendering** — Page 1 and Page 2 content may coexist in DOM but be visibility-toggled
- **innerText includes hidden content** — `document.documentElement.innerText` may include invisible page 2 content even when page 1 is selected
- **Card link click doesn't navigate** — clicking on a card heading link may reload the listing instead of opening the detail page. Use manual URL construction or browser_vision annotations
- **Deprecated badges** — Some blueprints marked "Deprecated" still appear in listings (LLM Router, Flood Intelligence, Cyborg Enterprise RAG)

### General SPA Marketplace Tips
- Always check if pagination is URL-based or JS-based before designing extraction strategy
- JS tab buttons often use `aria-label` for accessibility — search `[aria-label*="page"]` or `[aria-label*="Go to"]`
- Some SPAs use `<button>` not `<a>` for page navigation — look for `nv-tabs-trigger`, `[role="tab"]`, `[role="tablist"]`
- `browser_vision(annotate=true)` is indispensable for SPA navigation — it shows interactive element ref IDs that aren't exposed in truncated snapshots

## Evaluation Criteria for Blueprint-Style Solutions

| Criterion | Question | Weight |
|-----------|----------|--------|
| **Stack compatibility** | Does it integrate with our existing Hermes/Python/Docker stack? | High |
| **Deployability** | Can we run it without dedicated H100 GPUs? (NVIDIA hosted endpoints count) | High |
| **License** | Apache 2.0? NVIDIA SLA? Per-model licenses? | Medium |
| **Community/Support** | GitHub stars, recent commits, NVIDIA backing? | Medium |
| **Edge deployment** | Does it run on consumer GPUs (RTX 4090, DGX Spark)? | Low-Medium |
| **Status** | Active or Deprecated? | High (skip deprecated) |

## Related References

- `references/ai-model-marketplace-research.md` — AI model pricing/capability comparison (Zenmux/Pollinations/OpenRouter)
- `references/multi-page-course-scraping.md` — Systematic multi-page documentation scraping
- `references/upwork-job-research.md` — Freelance platform job research with bot-detection workarounds

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| SPA pagination doesn't respond to URL params | Use `browser_click` on tab buttons, not `browser_navigate` |
| Card click doesn't navigate to detail page | Manually construct URL: `https://build.nvidia.com/{author}/{kebab-title}` |
| Browser snapshot truncated at page 1 | Use `browser_console` with JS to extract page 2 content after clicking tab |
| Deprecated items still in listing | Check for "Deprecated" badge before evaluating |
| Missing hardware requirements on card | Navigate to detail page — HW reqs are in the Architecture tab |
| innerText returns invisible content | Use `browser_vision` or JS query on visible elements for accurate current-page content |
| Wrong URL slug for page 2 items | Try multiple kebab-case variations, or navigate via browser_click on the card heading link |
