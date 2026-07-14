# APA Practice Update "Quick Study" Pattern

> **When:** A Practice Update email has a "Quick Study" (formerly "Quick Hits") section at the bottom with 3-4 mini research summaries.
> **Source:** Practice Update (pracupdate@info.apa.org), usually Friday.
> **Origin:** 2026-06-26 pipeline execution.

## The Pattern

Practice Update emails have TWO content types:

| Section | Content | Wiki Treatment |
|---------|---------|---------------|
| **Feature article** (top) | Main article, 1-2 AI-generated images, editorial voice | Full wiki page: title-based slug, structured summary |
| **Quick Study** (bottom) | 3-4 independent mini-studies, each with citation + 2-3 paragraph summary | EACH mini-study → SEPARATE wiki page (independent papers) |

## Why Separate Wiki Pages for Quick Study?

Each Quick Study item is an INDEPENDENT research paper with its own:
- Authors + journal + year (must preserve for citation)
- Distinct methodology
- Unique clinical implications

Combining them into one "Quick Study roundup" file buries the individual papers and makes cross-referencing impossible later. Each paper is as valuable as a stand-alone article.

### Exception — News Items
If a Quick Study item is NOT a research paper but a news item / survey result (e.g., "New survey finds 45% of therapists report burnout"), it can be grouped into a single "practice-update-quick-study-YYYY-MM-DD.md" file.

## Naming Convention

### Stand-alone research papers
```
~/wiki/apa-articles/YYYY-MM-DD-<topic-slug>.md
```
Example: `2026-06-26-therapy-session-frequency-outcomes.md`

### News items only (no individual research papers)
```
~/wiki/apa-articles/2026-MM-DD-practice-update-quick-study.md
```
Example: `2026-06-26-practice-update-quick-study.md`

## File Structure (Research Paper)

```yaml
---
title: "Session Frequency and Therapy Outcomes — A Meta-Analysis"
created: 2026-06-26
updated: 2026-06-26
type: summary
tags: [apa, practice-update, quick-study, therapy]
sources: [Practice Update]
confidence: medium
---

# Session Frequency and Therapy Outcomes

## Source
Practice Update Quick Study, June 26, 2026

## Summary
Brief description (2-3 sentences).

## Key Findings
- Finding 1
- Finding 2
- Finding 3

## Clinical Relevance
How this applies in practice.

## Citation
Author A, Author B (2026). Title. *Journal Name*, Volume(Issue), pages.
```

## Index Entry Format

```
- **2026-06-26-session-frequency-outcomes**: Session frequency meta-analysis — weekly better than biweekly for depression (Practice Update Quick Study, 26 Haz 2026)
```

## Pitfalls

- **Don't merge all Quick Study items into one file.** Each research paper is independent — treating them as a batch buries individual value.
- **Preserve citations.** The full author/journal/year citation is essential for any future reference.
- **One email can = 4 wiki files.** A Practice Update with feature + 3 Quick Study papers = 4 separate files + index updates. This is normal.
- **Date disambiguation:** All Quick Study items from the same email share the same date. Use the topic slug for uniqueness, not date alone.
- **Index updates compound:** Adding 4 files at once means 4 index entries + 1 log entry. Batch them all before the final write_file to avoid multiple write passes.
