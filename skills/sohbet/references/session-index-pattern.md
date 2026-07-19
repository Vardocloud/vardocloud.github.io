# Session Index — FTS5 Fallback

## Problem

`session_search` uses FTS5 with a built-in tokenizer. For Turkish text, long compound queries, or sessions identified by non-standard titles, FTS5 may return zero results even when the session EXISTS in `state.db`. This happens because:

1. FTS5 tokenizer doesn't handle Turkish morphology well (agglutination, suffixes)
2. Queries with special characters, code snippets, or model names may not tokenize as expected
3. Very old sessions may be indexed but not surfaced by BM25 ranking

## Solution: Manual Session Index

Maintain a manually-curated index file at `~/wiki/references/session-index.md` that maps search tags → session IDs.

### Format
```markdown
## N. Topic Name
- **tag1, tag2, tag3** → `session_id` (date, message count)
  - *Detail:* what was discussed
  - *Session title:* original title from state.db
```

### When to Index
- After any conversation that:
  - Establishes core identity/rules (SOUL.md, COMPASS)
  - Makes strategic decisions (lokal PC plan, architecture changes)
  - Contains hard-to-find technical procedures
  - Edel explicitly calls "önemli"
- **Don't index** routine conversations, daily research, transient tasks

### Retrieval
1. Try `session_search` with multiple queries first
2. If all queries return empty → read `~/wiki/references/session-index.md`
3. Find session ID by tag matching
4. Use `session_search(session_id="<id>")` to read directly

### Why This Works
- Direct session ID lookup bypasses FTS5 entirely
- Tags are chosen by the agent who knows what terms will be searched later
- Index is a small plain text file — always readable, never fails

## Example Entry
```markdown
## 1. Kimlik Derinleştirme & Lokal PC Planı
- **Vanitas kimliği, SOUL.md, varlık sebebi, yoldaş, lokal PC, karanlık ikiz** 
  → `20260711_123750_3bff2c24` (11 Temmuz 2026, 46 mesaj)
  - *Detay:* SOUL.md yeniden yazımı, 4 katmanlı prompt injection savunması
```
