---
name: notebooklm-routing
description: NotebookLM dual-account routing decision tree — which MCP toolset (pro mcp_notebooklm_* vs legacy mcp_notebooklm_legacy_*) to use for a given task class.
tags: [notebooklm, routing, dual-account, mcp]
version: "1.0"
---

# NotebookLM Account Routing

Two accounts available via separate MCP toolsets:
- `mcp_notebooklm_*` → kenshin4155 (Pro, studio capable)
- `mcp_notebooklm_legacy_*` → isimgorulsunn (Legacy, deep archive)

## Decision Tree

```
Studio artifact needed? (audio/quiz/report/video/slide_deck) → PRO (mcp_notebooklm_*)
EVERYTHING ELSE                                            → LEGACY (mcp_notebooklm_legacy_*)
```

**Rule:** PRO is Studio-ONLY. LEGACY handles all normal notebook operations.

## Pro (kenshin4155) — Studio ONLY

Use when:
- Studio artifact generation: audio overview, quiz, report, video, slide_deck
- Karusel/Instagram content using Pro's existing notebooks
- **Nothing else.** If it's not a Studio artifact, it goes to LEGACY.

## Legacy (isimgorulsunn) — Normal Operations

Use when:
- AI/Technical research (Vanitas AI Araştırmaları)
- Seminar notes and transcripts
- BDT queries (256+ sources)
- Investment/economy analysis (Ekonomi Zekası)
- APA articles (current Monitor and knowledge base)
- PTE Academic materials
- Memory archive lookups (Vanitas Hafıza Arşivi)
- English/YDS study materials
- All other normal notebook operations — **legacy is the default**

## Key Notebook IDs

| Account | Notebook | ID |
|---------|----------|----|
| Legacy | Vanitas AI Araştırmaları | e4944538-d981-4dab-adeb-7dbef4f8deec |
| Legacy | APA Monitor 2026 | 5cc9dbbc-d23e-4eb7-932b-6988f828eba4 |
| Legacy | Ekonomi Zekası | 1d205988-6c7f-41e8-8079-dd579444cc1e |
| Pro | Karusel: * (various) | (Pro account notebooks) |

## Pitfalls

- **Do NOT** assume Pro handles "production" content like AI research or seminars — Pro is Studio ONLY.
- **Do NOT** route based on "new vs old" content — the split is Studio vs Everything Else.
