# Bulk Email Newsletter Batch Processing

> Added 2026-07-17. Pattern for handling APA newsletters (Editor's Choice, Science Spotlight, etc.) that contain 5-10+ research summaries in a single email.

## When to Batch

A single email contains 3+ individual research article summaries → batch process.
1-2 articles → handle individually (standard pipeline).

## Workflow

### 1. Extract Full Email Body

Use Gmail API to get the full email body, NOT web_extract (tracking links, HTML noise):

```bash
GAPI="python $HOME/.hermes/skills/productivity/google-workspace/scripts/google_api.py"
$GAPI gmail search "from:apa.org newer_than:5d" --max 20
$GAPI gmail get MESSAGE_ID
```

The email body contains all article summaries in clean text.

### 2. Create One Consolidated Wiki File

Single YAML-frontmatter .md file with all articles under headings:

```yaml
---
title: "Editor's Choice — July 16, 2026 (10 Articles)"
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: summary
tags: [editor-choice, research, batch]
sources: [email/apa-editors-choice-YYYY-MM-DD]
confidence: high
---
# Editor's Choice — YYYY-MM-DD
## 1. Title
**Authors** — *Journal*
**Key Finding:** 1-2 sentences.
**Clinical Relevance:** 1 sentence ("Yani...").
## 2. Title
...
```

### 3. Add One NotebookLM Source

NOT 10 separate sources — rate-limit risk. One text source with all summaries:

```python
mcp_notebooklm_source_add(
    notebook_id="c44469fe-...",
    source_type="text",
    title="[🔬 Editor's Choice] 16 Tem 2026 — 10 Yeni Araştırma Makalesi",
    text="[2-3 sentence summary per article + journal/author info]",
    wait=True,
    wait_timeout=60
)
```

### 4. Update Index with One Row

Single table row for the entire batch, not 10 rows:

```
| 9 | Editor's Choice (16 Temmuz) — 10 makale: [summary list] 🔬 | 2026-07-17-editors-choice.md | Editor's Choice | 17 Tem |
```

### 5. Report Under One Category

In the final report, list all articles numbered (❶❷❸...) under a single category heading such as "Editor's Choice — 10 Yeni Araştırma".

## Benefits

- Fewer tool calls (1 wiki write + 1 NBLM source instead of 10 each)
- Lower rate-limit risk on NotebookLM
- Cleaner index (one row per batch instead of 10)
- Easier to skim in reports

## Pitfalls

- Don't skip individual standout articles: if one article in the batch is exceptionally important (AI × psychology, major meta-analysis, practice-changing), flag it separately in the report with a ⭐ marker
- Batch size: 10+ articles per batch is fine for a summary. If a single batch exceeds 15 articles, split into sub-batches by topic
- Email link tracking: Gmail API body contains APA click-tracking URLs, not direct article URLs. That's fine for summaries; the email text is the source of value here
