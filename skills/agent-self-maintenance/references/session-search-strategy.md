# Session Search Strategy for Turkish FTS5

> Born from the 22 Tem 2026 session where Edel reported "konuşulan konular hatırlanmıyor ve bulunamıyor." Root cause was NOT missing data — the session_search query used 7 AND-keywords without wildcards, returning 0-2 results despite 90+ matching messages existing in state.db.

## Architecture

state.db contains 45,517 messages across 1,697 sessions (425 Telegram, 1272 cron). Two FTS5 virtual tables:

| Table | Tokenizer | Turkish handling | Content size |
|---|---|---|---|
| `messages_fts` | default (`unicode61`) | Word-splits unicode, NO stemming | 45,517 docs |
| `messages_fts_trigram` | `trigram` | 3-char substrings, NO stemming | 45,517 docs |

**Neither tokenizer handles Turkish agglutinative morphology.** "taşıma" (noun: the transporting) and "taşıyalım" (verb: let's transport) share the root "taşı" but are completely different tokens in both tokenizers. FTS5 prefix wildcard (`*`) is the only reliable way to match Turkish inflections.

## Root cause of "not found" errors

The 19 Tem 2026 HP EliteBook 2730p session: Edel asked "seni lokal PC taşıyalım diye konuştuk plan yaptık hatırlamıyor musun?" Search used:

```
"lokal PC taşıma sunucu hermes local machine"  ← 7 terms, AND logic
```

Individual term matches (standard FTS5):
| Term | Matches |
|---|---|
| `lokal` | 219 |
| `pc` | 1068 |
| `taşıma` | 87 |
| `sunucu` | 597 |
| `hermes` | 11624 |
| `local` | 3880 |
| `machine` | 440 |

Combined AND: **2 results** (too narrow to be useful). The correct query:

```
"lokal* taşı* pc*"  → 32 results
"local* taşı* pc*"  → 90 results
```

## The 4-step recall workflow

### 1. session-index.md (primary)

Path: `~/wiki/references/session-index.md` (117 lines, 5.9 KB as of 22 Tem 2026)

This file has curated session summaries with topic tags. If the topic Edel is asking about appears here, use `session_search(session_id=ID)` to read the full session directly — no FTS5 needed.

**Advantage:** Zero Turkish-language issues, zero false negatives, single tool call.

### 2. Wildcard query (fallback)

When the topic is not in session-index.md or the session_id is unknown:

**Query construction rules:**
- Pick 2-4 distinct content words from the user's question
- Convert each to its Turkish root + append `*`
- Use AND between them (default FTS5 behavior)
- If results are 0-2: remove the least specific term and retry

**Examples from real sessions:**

```
# Edel asks about local PC plan
→ "lokal* taşı* pc*"              # 32 results

# Edel asks about investment advice
→ "yatırım* fon* borsa*"          # ~200 results

# Edel asks about a past seminar
→ "seminer* kayıt* ders*"         # ~50 results

# Edel asks about specific meeting time
→ "yarın* toplantı* saat*"        # narrow by adding terms
```

### 3. Trigram fallback (when standard FTS fails)

If standard FTS returns 0 results for a short word (≤3 chars like "pc", "ai"), try the trigram tokenizer. The trigram table indexes every 3-character substring, so short words are harder to match via trigram but special characters work better.

In practice, standard FTS5 with wildcard gives adequate results for Turkish. Trigram is not significantly better for Turkish morphology (confirmed 22 Tem 2026 — `konuşuyordum` returns 1 result in both tokenizers).

### 4. session-index.md update

After finding the session: if the topic was significant and isn't in session-index.md yet, add it. This prevents future FTS5 searches for the same topic.

## Pitfalls

- ❌ **Don't** search with >4 AND terms. Each additional term multiplies the chance of zero results.
- ❌ **Don't** search with exact Turkish inflections. Always use the root + `*`.
- ❌ **Don't** say "bulamadım" after 1-2 queries. Try at least 3 different formulations with wildcards.
- ❌ **Don't** trust FTS5 results count as "data absence." 0 results usually means bad query, not missing data.
- ✅ **Do** check session-index.md first — it's faster and more reliable than FTS5.
- ✅ **Do** memorize the common Turkish roots table in the main skill.
- ✅ **Do** verify with `session_search(session_id=...)` once you find a candidate.

## Turkish roots quick reference

| Root | Common forms | Wildcard |
|---|---|---|
| taşı- | taşıma, taşıyalım, taşınma, taşıyor, taşıdı | `taşı*` |
| konuş- | konuştuk, konuşuyoruz, konuşma, konuşmuştuk | `konuş*` |
| hatırla- | hatırladın, hatırlıyor, hatırlatma | `hatırla*` |
| yap- | yaptık, yapıyorum, yapalım, yapmadı | `yap*` (pair with another term) |
| gel- | geldim, geliyor, gelmişti, gelmez | `gel*` (pair) |
| söyle- | söyledin, söylüyor, söylemiştim | `söyle*` or `söylü*` |
| git- | gittim, gidiyor, gitmişti | `git*` (pair) |
| bil- | biliyor, bildin, bilmiyor | `bil*` (pair) |
| ver- | verdin, veriyor, vermişti | `ver*` (pair) |
| çalış- | çalıştı, çalışıyor, çalışmış | `çalış*` |

## Verification checklist

Before reporting "bulamadım / not found" to the user:

- [ ] Checked session-index.md? (faster and more reliable)
- [ ] Tried wildcards on Turkish roots? (`taşı*` not `taşıma`)
- [ ] Tried with 2-3 broad terms instead of 5-7 specific ones?
- [ ] Tried OR for Turkish↔English synonyms? (`lokal* OR local* OR yerel*`)
- [ ] Tried trigram tokenizer? (via direct FTS query if tool supports it)
- [ ] Searched at least 3 different query formulations?
