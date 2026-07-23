# Turkish FTS5: Trigram vs Unicode61 Benchmark

**Date:** 23 Tem 2026
**Context:** session_search was missing Turkish conversations because unicode61 tokenizer
doesn't handle Turkish morphology (doesn't find roots, swells with suffixes).

## Setup

Two FTS5 tables in state.db, same data (872 wiki markdown files):

| Table | Tokenizer | Rows |
|-------|-----------|------|
| `wiki_fts` | `unicode61` (default) | 872 |
| `wiki_fts_trigram` | `trigram` | 872 |

## Test Results: Turkish Root Finding

| Turkish Word | unicode61 | trigram | Improvement |
|--------------|:---------:|:-------:|:-----------:|
| araştırma | 51 | **89** | **+75%** |
| değerlendirme | 23 | **42** | **+83%** |
| başvuru | 6 | **14** | **+133%** |
| konuştuk | **0** | **1** | unicode61 missed completely |
| klinik | 40 | **42** | +5% |
| çalışıyor | 26 | **28** | +8% |
| psikoloji | 53 | **55** | +4% |

## Limitations

- Trigram requires minimum 3 characters. 2-letter queries ("pc", "ai") don't work directly
- Trigram index is ~3x larger than unicode61 index (acceptable for 872 docs)
- session_search tool itself uses `messages_fts` (unicode61) — can't change that
- wiki_fts_trigram is a separate parallel index, searched manually via raw SQL

## Implementation

The `wiki_fts_trigram` table was created with:
```sql
CREATE VIRTUAL TABLE wiki_fts_trigram USING fts5(
    path, title, content, tags, file_hash, last_indexed,
    tokenize='trigram'
);
```

Populated by scanning all 872 `.md` files under `~/wiki/`, extracting title from `# ` headers,
tags from `#tag` patterns, and storing file_hash as mtime.

**Script:** `~/.hermes/scripts/wiki_trigram_reindex.py`
**Cron:** Daily at 02:30 (rebuilds from scratch each night to stay in sync with wiki changes)

## When to Use

For Turkish wiki searches where unicode61 returns 0 or few results, try raw trigram query:
```bash
sqlite3 ~/.hermes/state.db "SELECT COUNT(*) FROM wiki_fts_trigram WHERE wiki_fts_trigram MATCH 'araştırma';"
```

For session_search, as a fallback when the tool returns empty, query directly:
```bash
sqlite3 ~/.hermes/state.db "SELECT content FROM messages WHERE content LIKE '%anahtar%' LIMIT 5;"
```
