---
name: content-ingestion-pipeline
description: "Recurring external content ingestion into wiki and NotebookLM — news feeds, updates, scheduled pulls."
version: 1.6.0
author: Hermes Agent
metadata:
  hermes:
    tags: [wiki, notebooklm, ingestion, cron, news]
    category: research
    related_skills: [llm-wiki, notebooklm-pipeline]
---

## ⚠️ KRİTİK UYARI — Wiki ≠ NotebookLM (Edel'in isteği: 12 Tem 2026)

**Wiki'ye kaydetmek, içeriği NotebookLM'e otomatik olarak GÖNDERMEZ.** Bunlar Lighthouse'ın ayrı katmanlarıdır:
- **Layer 4 (LIBRARY / wiki):** `write_file` veya `patch` ile manuel yazılır
- **Layer 6 (VAULT / NotebookLM):** Ayrıca `nlm add text` veya `mcp source_add` ile ayrıca eklenmelidir

Her content ingestion run'ında, wiki yazıldıktan SONRA NotebookLM'e atılacak içerikler varsa ayrıca eklenmelidir. Cron auth sorunu çıkarsa, wiki ayağı yine de tamamlanır ama raporda "NotebookLM: ⛔ atlanmadı (sebep: auth)" notu düşülür. **Bu bir pipeline hatası değil, bilinçli bir gerçekliktir.** Otomatik bridge olmadığı sürece bu böyle kalacak.

## Workflow

## ⚠️ MANDATORY PRE-CHECK: Subscription/Auth-Required Sources

**CRITICAL RULE — Read this before any content extraction.**

If the source requires login/subscription/membership for full text:
1. **STOP** — Do NOT extract or save any content yet
2. **Search for credentials**: BWS (`.env`), `search_files` for credential files, `session_search` for past login attempts, Bitwarden (bw CLI / bw-serve API)
3. **Try to authenticate FIRST**: browser login with found credentials, API token refresh, cookie reuse
4. **Only if authentication fails after ≥2 genuine attempts**: fall back to public/summary content — AND report the failure to Edel with the exact error
5. **NEVER silently use summary/free content** when the user has subscription access to full text. A summary that loses 70%+ of the content value is not a substitute.

**Failure mode that triggered this rule (10 Tem 2026):** APA Monitor makaleleri `web_extract` ile özet olarak çekildi ve wiki'ye kaydedildi. Edel'in APA üyeliği vardı. Edel: *"bu çok yanlış senin üyeliğin var ona giriş yapmadan özet çekmemelisin. Özetler değil tam halleri bizi lazım."*

**Bu kural SADECE APA için değil — ücretli/üyelik gerektiren HER kaynak için geçerli.** JSTOR, ACM, Springer, PubMed makaleleri (full text sadece abonelikle), Elsevier, CE portalları, vb.

See `references/apa-full-text-extraction.md` for APA-specific login flow and `references/apa-email-tracking-links.md` for newsletter tracking link discovery.

## When to Use

- Cron jobs that fetch and process news sources
- Recurring content pulls that need deduplication
- Any scheduled ingestion where both wiki and NotebookLM are targets

## Workflow

0. **Dedup file health check (MANDATORY — do this BEFORE reading any content)**: Call `read_file` on `~/wiki/news/processed_titles.md`. Check the `"file_size"` field in the return output — NOT just the content. If `file_size > 15000`, **STOP here and rotate before doing anything else**:
   ```bash
   mv ~/wiki/news/processed_titles.md ~/wiki/news/processed_titles_archive-$(date +%Y-%m).md
   ```
   Then create a fresh file with just an archive-reference header. A bloated dedup file wastes context on every read and the threshold is a simple char-count check you can make in one glance at the metadata.
   - **Known failure pattern (June 27→28→29→30→July 2)**: The agent reads the file, focuses on the title content for dedup, and ignores the `file_size` metadata field entirely. This has happened **5 consecutive sessions** despite a "mandatory" label. The fix: check `file_size` BEFORE processing the content. If you see `> 15000`, rotate. Do not proceed to web_search or web_extract until rotation is done.
   - **Structural enforcement (July 2)**: After `read_file` returns, scan the JSON metadata FIRST — before reading any content lines. Look for `"file_size": NNNNN`. If NNNNN > 15000, your NEXT tool call MUST be `terminal` with the `mv` rotation command. No exceptions. Treat it like a compiler error — nothing else compiles until this is fixed. The 39KB file on July 2 wasted ~4K tokens of context just on dedup data from prior weeks.

1. **Fetch**: `web_extract` on the source URL
   - **Output alert:** If web_extract returns < 2K chars, the page likely didn't render fully (JS SPA issue). Immediately fall back to browser tools for content.
2. **Deduplicate (NotebookLM)**: `notebook_get` → check existing source titles for the source pattern
3. **Orient (wiki)**: Read `index.md` and `SCHEMA.md`
4. **Extract concepts**: For each item, decide if it gets a new wiki page or updates an existing one
5. **Write wiki**: Create/update pages with frontmatter, cross-references, English content
6. **Update navigation**: `index.md` + `log.md`
7. **Archive**: Add text source to NotebookLM using `nlm add text` CLI (preferred)
   or `source_add` MCP tool (fallback). Use the dated title convention defined in the
   pipeline's reference file for deduplication.

8. **Read & Extract Insights (CRITICAL)**: After filing, actively engage with the content.
   - Don't just passively collect and file — **read the material you just added**
   - Extract 2-3 key takeaways: "Bu yazıdan ne öğrendim, Edel'in bilgisine nasıl katkı sağlar?"
   - Share insights in your report: a short paragraph synthesizing what's interesting
   - If content has psychological/clinical relevance, explicitly note the connection
   - If it's a free event, note why it's worth attending and what topics it covers

## Category Weighting

When a user wants ALL categories but with WEIGHTED emphasis:

1. Define **primary categories** (e.g., tech, science, economy) and **secondary categories** (e.g., gündem, culture)
2. Select 8-10 total items — roughly 6-8 from primary, 1-2 from secondary
3. NEVER exclude secondary entirely unless the user explicitly says so
4. Group output by category with emoji indicators

User correction pattern: "Gündem de olsun, ağırlık şu 3 kategoride olsun" means include everything but weight the primary ones. Do NOT propose excluding categories unless the user says "sadece X".

## File-Based Deduplication (processed_titles.md)

For cron jobs that scrape sources without a database backend:

Use a **processed_titles.md** file stored under the source's wiki directory (e.g. `~/wiki/news/processed_titles.md` or `~/wiki/news/bundle/processed.md`).

**Workflow:**
1. At start of each run: read the file with `read_file`. If it doesn't exist, start fresh (empty list).
2. For each headline: compare against existing entries using both exact match AND fuzzy match (Levenshtein/Jaro-Winkler at threshold ~0.85).
3. Skip if already processed (exact or fuzzy match found).
4. After processing all items: append new titles to the file using `patch` (append mode via old_string/new_string targeting the last line).
5. Format: one title per line under dated section headers. Use descriptive qualifiers when a day has multiple batches: `## YYYY-MM-DD (NEW)` for the first run, then `## YYYY-MM-DD (NEW - evening batch)` or `## YYYY-MM-DD (NEW - second batch)` for subsequent runs on the same day. This prevents confusion when the same date has entries from multiple runs and helps the next run's dedup scan distinguish chronological order.

### Intra-Run Multi-Source Deduplication

When fetching MULTIPLE sections of the same publisher in one run (e.g., BBC News + BBC Business + BBC Technology via parallel `web_extract`), the same underlying story can appear across two or more pages with slightly different headlines.

**Detection pattern:**
1. Collect all headlines from all fetched sections into one working set
2. Cross-reference within the set: same proper nouns + same event type → same story
3. Before selecting final 5-7 items, deduplicate the in-memory set against itself
4. When two headlines describe the same event from different angles, keep the one with more specific detail (e.g., BBC Business's version usually has market/financial context — keep that one when filing under `economy/`)

**Why this matters:** Fetching BBC News + BBC Business + BBC Technology in one batch yields ~15-20 headlines, of which 4-6 may be the same stories reworded. Without intra-run dedup, you'd report "US-Iran deal" three times and miss genuinely different items.

**Cron-compatible approach (no execute_code):**
```
Step 1: web_extract BBC News → headlines A1-A8
Step 2: web_extract BBC Business → headlines B1-B7
Step 3: web_extract BBC Technology → headlines C1-C5
Step 4: Cross-reference A+B+C against processed_titles.md first
Step 5: Within the surviving fresh set, check for stories in 2+ sections
Step 6: Keep the most detailed variant; discard the redundant ones
```

### Follow-up / UPDATE Detection

A headline from a previous run may be a "pending" version (e.g., "braces for verdict", "awaits decision", "expected to sign"), while the current run has the resolution (e.g., "found guilty", "deal signed", "approved"). Simple fuzzy matching won't catch these as related — they are NOT duplicates but ARE the same story thread.

**Detection pattern:**
1. Scan old entries for signal words: "braces for", "awaits", "expected", "to be decided", "pending", "to vote on", "plan to"
2. If a new headline mentions the same entity/person/company/country (extract proper nouns), check if it resolves a pending story
3. Mark resolved items as **UPDATE** in the output, separate from fresh headlines

**UPDATE handling:**
- Report under the relevant category with an `🔄` or `(UPDATE)` prefix to distinguish from fresh news
- The existing wiki file should be complemented (not overwritten): create `topic-slug-YYYY-MM-DD-update.md` with the new resolution info
- In processed_titles.md, log the new resolution headline as a separate entry — the original "pending" entry stays as historical record

```python
from rapidfuzz import fuzz
threshold = 85
for new_title in new_headlines:
    if any(fuzz.token_sort_ratio(new_title, existing) >= threshold 
           for existing in processed_titles):
        skip()
```

**Why not just use the wiki index.md?** processed_titles is a flat, append-only list with no schema complexity — it's faster to read/write and doesn't pollute the wiki's content structure. Fuzzy match catches near-duplicates that exact match would miss (e.g., slight headline edits).

### ⚠️ Pitfall: Duplicate Entries from Patch Append

When using `patch` to append new titles to processed_titles.md, it's easy to accidentally include duplicate entries or corrupt the format — the `old_string`/`new_string` matching can miss overlaps or misidentify the insertion point. This happened on 2026-06-16: "Fox to buy Roku" appeared twice in the same batch.

**Prevention — verify after every patch:**
1. After the `patch` call, immediately do a quick dedup scan: read back the last section and check for exact-line duplicates.
2. If found, issue a second `patch` targeting the duplicate line for removal.
3. For large batches (10+ titles), consider splitting into two patches: one for tech/science, one for world/economy — smaller chunks reduce accidental overlap.

### 🔧 Recovery: Patch-Induced Format Corruption

If `patch` corrupts the file format — typically by prepending line numbers to existing entries (e.g., `390|390|- Earth may have been...` where `read_file` shows `LINE_NO|LINE_NO|- ...`) — recover with `sed`:

```bash
sed -i 's/^[0-9]*|//' ~/wiki/news/processed_titles.md
```

This removes the erroneous line-number prefix that `patch`'s fuzzy matching prepended. After recovery:
1. **Verify** with `read_file` that lines now start cleanly (no `N|N|` prefix, just `-` or `##`).
2. **Check for data loss** — count entries in the recent section against what you expect.
3. **Switch to `cat >>`** for all future appends — the corruption only happens with `patch`'s string-matching logic, which `cat >>` bypasses entirely.

**Corruption sign:** read_file output shows `395|395|- Super puff planets` instead of `395|- Super puff planets`. The doubled line-number prefix is the telltale symptom.

### ⚠️ Pitfall: rapidfuzz Unavailable in Cron Jobs

The fuzzy matching example below (`from rapidfuzz import fuzz`) uses `execute_code`, which is **BLOCKED in cron mode**. Since cron jobs cannot run Python code with external libraries, you cannot use rapidfuzz for fuzzy deduplication.

**Cron-compatible manual approach:**
- Manual comparison by the agent: scan processed entries for shared proper nouns, key phrases, or entity names
- Common near-duplicate patterns to watch for:
  - Same event with different descriptors (e.g., "braces for verdict" → "found guilty")
  - Same topic on different BBC sub-pages (headline may be worded differently on BBC News vs BBC Business)
  - Date-advanced stories ("to be signed Sunday" → "signed Tuesday")
- Trust your judgment: if two headlines clearly describe the same event with the same key actors, it's a duplicate

### ⚠️ processed_titles.md Grows Over Time — Rotation Required

The deduplication file `processed_titles.md` grows with every run. After ~20-30 daily runs at 15-20 titles each, it exceeds 15,000 chars (~450 titles) and becomes slow to read as well as a context burden.

**Monitoring (FIRST STEP — mandatory):** At the start of each run, note the char count from `read_file`. If it exceeds 15,000 chars, **rotate before proceeding** with any other work. Deferring rotation after content processing leads to repeated deferrals (observed pattern: June 27→28→29 all noted over-threshold but did not rotate). The rotation is a 2-line shell command — execute it immediately on detection, before any search or fetch.

**Pitfall — compaction blindness:** When resuming after context compaction, maintenance thresholds (rotation, index cleanup, index.md drift, log rotation) are silently skipped because the workflow appears "already complete." After every compaction resumption, re-read THIS section and check ALL maintenance thresholds explicitly before declaring work done. A 37K+ chars processed_titles.md wastes context on every subsequent run.

**Rotation procedure:**
1. Archive: `mv ~/wiki/news/processed_titles.md ~/wiki/news/processed_titles_archive-YYYY-MM.md`
2. Fresh start with archive reference header:
   ```markdown
   # Processed Titles
   > Active from: YYYY-MM-DD
   > Archive: processed_titles_archive-YYYY-MM.md (previous runs)
   ```
3. The archive file stays on disk for cross-date dedup if needed (search_files can still scan it)
4. The first run after rotation may find a few cross-date duplicates — this is acceptable

**Alternative (no rotation):** If the file stays under 15K chars, just keep appending. Only rotate when over threshold.

**Pitfall — over-rotation:** Don't rotate daily. At 15 titles/run, one rotation per 3-4 months is enough (< 1/year). The trigger is char count, not schedule.

## Wiki Storage for News Content

Store news-derived knowledge under `~/wiki/news/` organized by category directory:

- `~/wiki/news/tech/` — AI, hardware, software, crypto
- `~/wiki/news/science/` — research, health, space
- `~/wiki/news/economy/` — markets, companies, policy
- `~/wiki/news/gundem/` or `~/wiki/news/world/` — current affairs, geopolitics
  - Use `gundem/` for Turkish-named subdirs (consistent with other Turkish content)
  - Use `world/` for English-named subdirs (consistent with English wiki content)
  - Standardize on whichever naming convention the wiki uses — check existing dirs before creating

Each entry is a markdown file with frontmatter containing: source URL, date extracted, key data points.

### Wiki Entry Content Structure

Each news wiki entry should follow a consistent internal structure beyond the frontmatter:

```markdown
---
source_url: https://example.com/article
ingested: YYYY-MM-DD
sha256: <placeholder — compute on re-ingest if needed>
---

# Topic Title

## Temel Bilgi
Haberin özü — ne oldu, kim yaptı, nerede/nasıl? (2-3 cümle)

## Veri/İstatistik
Haberde geçen sayısal veriler, araştırma sonuçları, miktarlar.

## Anlamlı Çıkarım
Bu haber neden önemli? Ne öğreniyoruz? Edel'in bilgisine nasıl katkı sağlar? (1-2 cümle)
```

This three-section structure captures: what happened, what the data says, and why it matters. The `sha256` field is a placeholder on first write — compute over the body only on re-ingest to detect drift.

### File naming convention:
- Fresh items: `topic-slug-YYYY-MM-DD.md` (date at end for alphabetical grouping by topic)
- Follow-up/UPDATE items: `topic-slug-YYYY-MM-DD-update.md`
- This distinguishes resolution files from original reports without overwriting history

**Storage split:** News wiki files are transient — they capture current events. The main wiki (`~/wiki/concepts/`, `~/wiki/entities/`) should remain clean of daily news data. Only promote news to the main wiki when a news event produces durable knowledge (a new entity, a lasting concept, a permanent change).

This keeps the main wiki clean of transient news data while still preserving extracted knowledge.

## Output Limit (Cron Jobs)

Cron job outputs are delivered to the user as-is. To prevent truncation:

- **Default target: 8-10 items per run** when grouping by category — select the most critical/impactful items. Quality over quantity.
- **Tech/Science minimum: at least 6 of the 8-10 must be science + tech** (Edel's explicit preference). Economy = max 1-2. World/gündem = minimal or skip unless breaking. Magazin/spor = never. Life/yaşam = sparingly, not every run.
- If a source has 50+ items, pick top 4-5 from primary categories, 1-2 from secondary.
- If processing requires many tool calls, batch reads early to stay within context limits.
- **MAX 7 is OBSOLETE** — the user's v3 bundle instructions set the target to 8-10 with the 6-from-science+tech rule. If a different target is given inline, use the inline value.

### Content Depth & Length Proportionality

Content summarization length MUST match the article's depth and complexity. Do NOT apply a fixed sentence/paragraph cap to all content — this frustrates the user when a 3-page academic article gets reduced to 3 sentences.

| Content Type | Recommended Length |
|---|---|
| Short news/bulletin item (1 paragraph) | 3-5 sentences |
| Standard article (1-2 pages) | 5-10 sentences, 2 paragraphs |
| Long article/feature/review (3+ pages) | 10-15+ sentences, 3-4 paragraphs |
| Podcast episode summary | 3-5 sentences (who, what, why listen) |
| Event listing | 3-4 sentences (date, topic, speakers, registration) |

**Structure for each item (regardless of length):**
1. **What it is** — the core topic/question (1-2 sentences)
2. **What it says** — key findings, arguments, data (varies by article depth)
3. **What it means** — clinical/practical takeaway, "Yani..." (1-2 sentences)

**Cron-compatible guideline:** When in doubt between brevity and detail, err toward detail for substantive articles. The user explicitly prefers meaningful coverage over artificially short summaries. If an article has 3 major findings worth separate attention, give each one its own sentence — don't cram them into a single compressed line.

### Freshness Signals (Breaking News Prioritization)

BBC News timestamps items with relative time tags: "21 mins ago", "Just now", "1 hr ago". These indicate items that appeared AFTER the previous run's fetch time.

**Detection & prioritization:**
1. Cross-reference timestamps with the previous run's timestamp (stored in processed_titles.md section headers or output directory file mtimes)
2. Items with "X mins ago" or "Just now" that weren't in the previous run → tag as **BREAKING/FRESH**
3. Fresh items get selection priority even if they fall outside primary categories (e.g., a breaking culture/entertainment story like a celebrity death outweighs a routine economy update)
4. Group breaking items under a `⚡ Breaking` sub-header at the top of the output, before category-grouped content

**Thresholds:**
- "Just now" or < 30 mins → BREAKING priority
- 30-120 mins → FRESH (recommended for inclusion)
- 2+ hrs → STANDARD (category-weighting applies normally)

## Parallel News Gathering via Subagents

For efficient multi-source news collection in cron jobs, use **3 parallel delegate_task subagents** for science, tech, and world news:

```bash
delegate_task(tasks=[
  {"goal": "Find latest science news from June 26, 2026", "toolsets": ["web"]},
  {"goal": "Find latest technology news from June 26, 2026", "toolsets": ["web"]},
  {"goal": "Find world and Turkish news from June 26, 2026", "toolsets": ["web"]}
])
```

### Alternative: web_search Direct (Subagent-Free)

The parallel subagent approach has known risks (wrong dates, hallucinations, context contamination via summaries). For agents with direct web access, an alternative approach is **direct `web_search` queries** + targeted `web_extract`:

```
Step 1: web_search 3 parallel queries for different news angles
  e.g., "science news today June 27 2026", "tech news latest", "AI news today"
Step 2: web_extract on publisher front pages for actual story lists
  ScienceDaily front page, BBC News, Reuters Technology
Step 3: For each promising headline, web_extract the article URL for detail
Step 4: Alternative news angle search: targeted web_search for specific topics
  (e.g., "SpaceX Nasdaq 100", "OpenAI delayed rollout")
Step 5: Verification search for each promising story before filing
  (e.g., web_search "Microsoft quantum Nature paper Henry Legg critique June 2026"
   to confirm date, source, and key details before creating a wiki entry)
```

**Trade-offs:**
| Approach | Pros | Cons |
|----------|------|------|
| Parallel subagents | Wider coverage, parallel execution | Date hallucination risk, verification overhead |
| web_search direct | No hallucinated dates, no double verification | More sequential steps, higher context usage |
| Hybrid | Best coverage + verification | Most tool calls |

**Choose subagents when:** you need breadth (scanning 10+ source categories) and have time to verify.
**Choose web_search direct when:** you want verified, today-dated headlines with minimal rework and can tolerate fewer total items found.

### ⚠️ CRITICAL: Subagent Date Reliability

Subagents (delegate_task) **frequently return wrong dates** for news items. A typical failure:
- Task: "Find news from June 26, 2026"
- Subagent returns stories from June 15, June 24, or even February — labeled as "today's news"
- The subagent's model confuses "articles matching the query" with "articles from this date"

**Verification procedure (MANDATORY after every parallel subagent gather):**
1. Treat all subagent-returned dates as **unreliable by default**
2. For each claimed headline: independently verify the date via:
   - `web_extract` on the specific article URL (check for a visible date stamp)
   - `web_search` with the exact headline + date filter
   - Wikipedia Current Events portal for the target date
3. Remove any item whose date cannot be independently confirmed as today's news
4. Only after independent verification should items enter the dedup pipeline

**Trusted sources for date verification (in priority order):**
- **Wikipedia Current Events**: `https://en.wikipedia.org/wiki/Portal:Current_events/YYYY_MMMM_DD` — provides a reliable, human-curated list of what actually happened on a given date. Use `web_extract` on this URL as a ground-truth reference before finalizing any bundle.
- **BBC News homepage**: timestamps shown as "X mins ago" — cross-reference with the previous run's timestamp
- **ScienceDaily release pages**: each article has a clearly printed "Date: June 26, 2026" line
- **Specific publication pages**: Nature, Physical Review Letters, Current Biology — all show submission/accepted/published dates

**Why subagents fail on dates:** Subagents use search APIs that rank by relevance, not date. A highly relevant article from last week ranks higher than a barely-relevant article from today. The subagent's summary text then claims "today's top news" based on relevance, not recency. This is a structural limitation — no subagent prompt can fully fix it. Always verify.

### Parallel Source Gathering Workflow

```
Step 1: Launch 3 parallel subagents (science, tech, world/turkish)
Step 2: While waiting, read processed_titles.md (dedup baseline)
Step 3: Subagent results return → verify ALL dates independently
Step 4: Also check Wikipedia Current Events for the target date
Step 5: Cross-reference verified items against processed_titles.md
Step 6: Select top 8-10 (min 6 from science+tech) → write wiki → deliver
```

### ScienceDaily Date-URL Pattern

ScienceDaily's front page links to individual releases. The URL structure is:
- Works: `https://www.sciencedaily.com/releases/2026/06/260623014002.htm` (release ID)
- **404**: `https://www.sciencedaily.com/news/date/20260626` (date-based archive — does NOT work)

**For gathering ScienceDaily content:**
1. Use `web_extract` on `https://www.sciencedaily.com/` (front page)
2. The front page shows top headlines from today with dates clearly labeled
3. Click through to individual release URLs for full article text
4. Each release page has a clear "Date: June 26, 2026" line — reliable for verification

### SciTechDaily Date-URL Pattern (Distinct from ScienceDaily)

SciTechDaily (scitechdaily.com) is a **separate publication** from ScienceDaily — newer, modern layout, broader science coverage including space, health, physics, and AI.

URL structure:
- Front page: `https://scitechdaily.com/` — lists recent articles with snippets and dates
- Individual articles: `https://scitechdaily.com/slug-based-article-name/` (slug format, not release IDs)
- Category archives: `https://scitechdaily.com/news/space/` — WordPress taxonomy slugs, extract reliably

**Strengths:**
- Broader coverage than ScienceDaily (includes AI/tech articles alongside pure science)
- Clean markdown extraction via `web_extract` — no JS blocking, no paywalls
- Each article shows a clear "By: Author Name / Date: June 27, 2026" line
- Article URLs are stable slug-based format (no release ID expiry)

**Weaknesses:**
- No categorized sub-pages for fine-grained filtering (everything on front page or broad category archives)
- Individual articles may 404 if the slug changed (rare)

**Pitfall — duplicate stories across SciTechDaily and ScienceDaily:** Both sites cover the same press releases (university press releases, Nature papers, etc.) on the same day with different headlines. When extracting both: check proper nouns (journal name, researcher surname, institution) — if they match, it's the same story. Keep the version with more detailed coverage (SciTechDaily for AI/tech, ScienceDaily for biology/space).

### CQT and University Research Pages

For quantum computing and physics news, check university/centre highlights pages:
- `https://www.cqt.sg/` — Centre for Quantum Technologies (Singapore) — fresh research highlights
- Each highlight has a clearly printed date
- Use `web_extract` on the highlights page for recent discoveries

## Cron Tool Restrictions

In cron job mode, there is NO user to approve tool operations. This means:
- **❌ execute_code blocked** — runs arbitrary Python, blocked in cron mode (no user to approve). Do NOT use it for batch file creation, data processing, or script execution.
- **✅ write_file** — safe for batch-creating wiki entries. Call up to 6+ in parallel with no restrictions.
- **✅ terminal** — standard shell commands run normally in cron mode.
- **✅ browser tools** — browser_navigate, browser_snapshot, browser_scroll all work in cron context.
- **✅ delegate_task** — subagent delegation routes to a separate model and is NOT blocked by cron restrictions.
- **❌ clarify/call user** — cannot ask questions. Make decisions autonomously.

Workflow: write_file for content → terminal for post-processing → delegate_task for parallel research sub-tasks. Never attempt execute_code in a cron job — it will silently fail.

### BBC Article URL 404 / Delayed Resolution Pattern

BBC News homepage lists articles with relative timestamps ("25 mins ago", "1 hr ago"), but the **individual article URLs may return 404 or "Page not found" for several hours** after first appearing. This is a server-side BBC indexing delay, not a fetch failure.

**Symptoms:**
- `web_extract` on the article URL returns a 404/blocked page
- Same story's headline and excerpt ARE available from the BBC News homepage extract
- The homepage timestamp says "X hrs ago" — it's a real story, just the URL hasn't propagated

**Handling:**
1. ✅ Use the homepage-extracted summary for deduplication, wiki filing, and the output report
2. ❌ Do NOT retry the URL immediately on the same run — wastes calls, same 404
3. ❌ Do NOT fall back to browser tools for the 404 — this is a propagation delay, not an extraction issue
4. ✅ If full details are needed: set `confidence: medium` in the wiki page and check again on the next cron run
5. ✅ The homepage summary usually contains sufficient key facts (headline, who, what, impact) for filing

**Example (2026-06-16):** Japan rate hike story appeared on BBC News homepage at "1 hr ago" with full summary (BOJ raised to highest since 1995). The article URL returned 404 when fetched. The homepage data was sufficient for deduplication, wiki filing under `economy/`, and the bundle report.

### Dual-Batch Same-Day Deduplication

When a cron job runs multiple times per day, `processed_titles.md` may already contain entries from an earlier run on the **same calendar date**. Fresh BBC/ScienceDaily pages will include a mix of already-processed items and genuinely new ones.

**Procedure:**
1. Read ALL sections of `processed_titles.md` — not just today's — because stories can reappear in related-content panels days later
2. For each fresh headline: cross-reference against EVERY entry in the file, not just today's section
3. Exact-match check first (identical headline text), then entity-level check (same proper nouns + similar topic)
4. Items with timestamps < 30 mins ago on BBC are almost certainly new; "13 hrs ago" items are likely already processed
5. Append new items using `cat >>` heredoc (preferred over `patch` — avoids accidental duplicate line insertion)

**Why cross-date matching matters:** A story that trended on June 10 may appear in "Also in news" or related-article panels on June 16. Without full-file cross-referencing, it gets re-processed as a new item.

**Example (2026-06-16):** Earlier batch had 16 items. Second run found 20 fresh BBC headlines — 5 exact duplicates from the earlier batch, 3 entity-level matches from June 14-15, and 7 genuinely new items. Cross-date matching prevented 8 redundant filings.

## Deduplication Patterns

- **NotebookLM**: Use the dated title convention (`SourceType — YYYY-MM-DD HH:MM`).
  Duplicate titles are acceptable in the archive journal — the date/time stamp makes
  each entry uniquely identifiable. No explicit dedup check needed at archive time.
- **Wiki**: check `index.md` filenames before creating new pages
- **Existing concepts**: update `updated` date in frontmatter when mentioned again

### Wiki → NotebookLM Backfill Script

For batch-archiving existing wiki pages into NotebookLM Vault (Layer 6), use the bridge script at `~/.hermes/scripts/wiki_to_notebooklm.py`:

```bash
python3 ~/.hermes/scripts/wiki_to_notebooklm.py --list      # Show pending pages
python3 ~/.hermes/scripts/wiki_to_notebooklm.py --add <path> # Add one page
python3 ~/.hermes/scripts/wiki_to_notebooklm.py --all        # Batch backfill all pending
```

**Tracker:** `~/.hermes/data/wiki_notebooklm_index.json` — records which pages have been processed.
**Limit:** NotebookLM supports ~50 sources per notebook — batch only high-value content, not raw transient news.
**Workflow:** Orient → select high-value pages → `--add` or `--all` → verify in NotebookLM.

## NotebookLM Auth Failure & CLI Alternative (Cron Jobs)

NotebookLM auth fails in automated contexts for multiple reasons:
- MCP tools: Google CookieMismatch errors (unreliable in headless/automated)
- nlm CLI "Profile not found": config missing or corrupt (different from auth expiry)
- nlm CLI auth expiry: token expires ~7 days after last `nlm login`

**Two-tier approach:**
1. **Preferred (CLI)**: Use `nlm source add --file` CLI command for archiving wiki pages as sources.
   - **CONFIRMED WORKING (12 Tem 2026):** `nlm source add <NOTEBOOK_ID> --file <wiki_md_path> --title "Başlık" --wait --wait-timeout 120`
   - ✅ `--file` with markdown file = most reliable (no shell quoting issues)
   - ❌ `nlm add text` with inline content = failed with markdown special chars
   - On "Profile not found": diagnose with `nlm login --check` first
   - On success: look for `✓ Added source:` prefix in output
   - On auth error: skip immediately, do not retry
2. **Fallback (skip)**: If both CLI and MCP fail, skip NotebookLM archiving entirely
   and continue with wiki updates.

When archiving via nlm CLI (two equivalent syntaxes — both confirmed working):

**Syntax 1 — `nlm source add` (file-based, preferred for very large content):**
```bash
nlm source add <NOTEBOOK_UUID> --file /tmp/content.md --title "SourceType — YYYY-MM-DD HH:MM" --wait --wait-timeout 120
```
- **`--file`** flag accepts a local markdown file — avoids shell quoting issues entirely
- **`--wait --wait-timeout 120`** blocks until NotebookLM finishes processing

**Syntax 2 — `nlm add text` (inline/pipe, preferred for one-liner workflows):**
```bash
# Inline with $(cat file) — handles special chars and newlines cleanly
nlm add text <NOTEBOOK_UUID> "$(cat /tmp/content.md)" --title "SourceType — YYYY-MM-DD HH:MM"

# Or pipe-based:
cat /tmp/content.md | nlm add text <UUID> --title "SourceType — YYYY-MM-DD HH:MM"
```
- Text content is a POSITIONAL argument, not a `-t` flag
- **`$(cat file)` works cleanly with special characters, quotes, newlines**

See `references/bundle-app-pipeline.md` for full syntax details, known error states,
and the temp-file workaround for large content.

- Do NOT block the pipeline — skip NotebookLM archiving and continue with wiki updates
- Document in the report which auth failure occurred and that archiving was skipped
- All wiki work (page creation, index updates, log entries) proceeds normally
- The missing archive entry is logged in `log.md` so manual backfill is possible

### Diagnostic Pattern for nlm Failures

When `nlm add text` fails:
1. Note the exact error message (different errors = different root causes)
2. Classify: "Profile not found" (config) vs "Authentication failed" (expired) vs network error
3. Add to report under "NotebookLM arşiv: ⛔ (sebep: ...)"
4. Continue with wiki processing — never block the pipeline

### Categorization by Theme (Not Source)

For content pipelines with multiple source types (academic articles, newsletters, podcasts, events), organize output by **thematic category** rather than by source. This makes the report more useful and scannable.

**Example categories for psychology/clinical content:**
- 🧠 Klinik Pratik — treatment protocols, therapy methods, case studies
- 🤖 AI × Psikoloji — AI assessment tools, digital therapy, AI ethics
- 📈 Kariyer & Gelişim — CE opportunities, certifications, career resources
- 🔬 Araştırma — new studies, meta-analyses, current findings
- 📅 Etkinlik — webinars, seminars, conferences (mark free/paid clearly)

Each category gets its own section header with emoji. Within each section, items are ordered by importance/relevance. This replaces the flat source-based listing pattern.

## Daily NotebookLM Podcast Pipeline

For cron jobs that produce daily content summaries (academic newsletters, news feeds, research briefs), create a daily Audio Overview podcast via NotebookLM. This gives the user an audio summary they can listen to instead of (or alongside) reading the text report.

### Workflow

**Morning/Afternoon runs (content collection):**
1. Scan all sources for new content
2. Check existing NotebookLM notebook sources for duplicates
3. Add each NEW item as a source to the designated NotebookLM notebook
   - Use `source_add` with `source_type="text"` or `source_type="url"`
   - Title convention: `[Category Emoji] Article Title — YYYY-MM-DD`
   - Categorize with emoji prefix so sources are visually grouped
4. If NotebookLM is down: skip source addition, continue with wiki filing and text report only

**Evening run (podcast generation):**
1. After scanning and filing new content, check if ANY new sources were added today
2. If new sources exist → create Audio Overview:
   ```
   mcp_notebooklm_mcp_studio_create(notebook_id="...", artifact_type="audio", source_ids=[...])
   ```
3. Poll with `studio_status` until generation completes
4. Download the audio: `download_artifact(notebook_id, "audio", "/tmp/podcast-YYYY-MM-DD.mp3")`
5. Deliver to user as MEDIA:/tmp/podcast-YYYY-MM-DD.mp3 in the report
6. Write 1-2 sentences about the podcast content as a listening recommendation

**If no new content was found all day → [SILENT]** — don't create an empty podcast.

### Deduplication (NotebookLM Sources)

Before adding a source to NotebookLM:
1. Call `notebook_get(notebook_id)` to list existing sources
2. Compare new item titles against existing source titles (fuzzy match at 0.85 threshold)
3. Skip if any existing source title contains a similar enough match
4. This prevents the same article generating multiple podcast episodes

### Fallback

- If NotebookLM auth fails → skip podcast, deliver text-only report
- If Audio Overview fails to generate → note in report, don't retry
- If download fails → include the NotebookLM link in the report so user can listen there

## Index Drift Recovery

Automated pipelines may create wiki files without updating `index.md` or `log.md`.
When you discover such files during any task (not just lint), refer to
`references/index-drift-recovery.md` for detection scans and batch recovery steps.

## Pitfalls

- **Never modify files in `raw/`** — sources are immutable. Corrections go in wiki pages.
- **Always orient first** — read SCHEMA + index + recent log.
- **Audio generation takes 2-5 minutes** — the cron job must be patient. Set appropriate timeouts.
- **Daily podcast ≠ hourly podcast** — one podcast per day is the sweet spot. If the cron runs 3x daily, only the evening run creates a podcast.

## index.md Maintenance (After Multiple Runs)

After repeated ingestion runs, the wiki's `index.md` accumulates:
- Duplicate "Recent Activity" log entries at the bottom
- Stale formatting from different session styles

**Cleanup during each run:**
1. Check the "Recent Activity" section for duplicate entries
2. Consolidate entries by date — one line per run
3. Remove redundant repeats (same date listed 3+ times with same content)
4. **⚠️ Do NOT use `patch` for index.md edits** — the growing file causes "ambiguous match" errors. Use `read_file` to get full content → process with python/`execute_code` → `write_file` to overwrite.

### APA Full-Text Extraction (Member Login Required)

> **⚠️ CROSS-REFERENCE:** Detaylı APA makalesi tam metin workflow'u (browser extraction, CAPTCHA handling, subagent failure patterns, wiki dosya formatı) için `apa-referenced-content` skill'ine bak.
>
> Aşağıdaki notlar sadece APA login ve PsycNET erişimine odaklanır.

### Problem
APA Monitor makaleleri web_extract ile özet olarak wiki'ye kaydediliyor. Oysa Edel'in APA üyeliği var ve tam metinlere erişebiliyor. Özetler yetersiz kalıyor.

**Not — Public Monitor sayfaları için:** `web_extract` APA sayfalarında özet döndürür. Tam metin için browser kullanılır:
`browser_navigate(url)` → `browser_console(expression)` ile `<main>` içeriğini çek. Detaylı workflow: `apa-referenced-content` skill'inde "0. KAYNAĞI WEB'DEN ÇEK" bölümü.

### Problem
APA Monitor makaleleri web_extract ile özet olarak wiki'ye kaydediliyor. Oysa Edel'in APA üyeliği var ve tam metinlere erişebiliyor. Özetler yetersiz kalıyor — Edel: *"Özetler değil tam halleri bize lazım. APA'ya giriş yapabilmelisin."*

### Kural — Üyelik Gerektiren Kaynaklar İçin
APA Monitor gibi üyelik gerektiren kaynaklardan içerik işlerken:
1. **ÖNCE üyelik bilgisini kontrol et** — BWS, Bitwarden Password Manager, .env, memory ile tara
2. **Varsa browser ile login dene** — APA SSO (sso.apa.org) üzerinden email+şifre (Google OAuth ÇALIŞMIYOR — "verify email" dialog'unda takılır)
3. **APA kredansiyelleri Bitwarden Password Manager'da (bw)** — BWS'de DEĞİL. Önce BWS'den `BW_MASTER_PASSWORD` al, bw unlock et, APA item'ını bul
4. **Monitor PDF tercih edilir yöntem** — Tüm sayıyı PDF olarak indir (92 sayfa, 6.6MB)
5. **PsycNET full text çalışmaz** — APA temel üyeliği tüm dergilere tam metin erişimi vermez
6. **NotebookLM** — Monitor URL'leri doğrudan URL source olarak eklenebilir

### APA Login Detayları (CONFIRMED 10 Tem 2026)
- **Direkt APA SSO:** sso.apa.org/apasso/idm/apalogin — email+şifre ile ✅ çalışıyor
- **Google OAuth:** "Log in with Google" — ❌ "Please verify your email" dialog'unda takılır
- **Browser cookie:** Session cookie, disk'e yazılmaz
- **Member display name:** "Vatinas Reister"
- **APA üyeliği tüm PsycNET dergilerine erişim vermez**

Detaylı workflow: `references/apa-login-troubleshooting.md` ve `references/apa-full-text-extraction.md`

## What to Capture

- New entities/companies/products relevant to the user's domains
- Security incidents, market events, tech launches
- Cultural/philosophical events with psychological relevance
- **Sadece ücretsiz/erişime açık etkinlikler** — ücretli ($) olanları ve ücreti bilinmeyen/belirsiz olanları atla
- Skip: routine scores, weather unless domain-relevant
- Skip: paid events and events with unknown pricing — unless the user explicitly requested them

## 5N1K Anlatım Formatı (Türkçe Haber Paketleme)

When delivering news in Turkish for this user, use the **5N1K format** (Ne? Kim? Nerede? Ne Zaman? Nasıl? Neden?). This is the definitive output format for TR news bundles — developed and refined across multiple iterations (currently v3).

### Format Rules

```
**🧠 Bilim / 📱 Teknoloji / 📊 Ekonomi / 🌿 Yaşam — [Haber Başlığı]**

[5N1K yapısında 3-4 cümlelik kısa anlatım. Ne oldu? Kim yaptı? Nerede/Nasıl? Neden önemli?]

📎 [Kaynak Adı]
```

**Sample:**
```
**🧠 Bilim — Beynin odak filtresi keşfedildi**

Norveçli araştırmacılar fare beyninde dikkat dağıtıcıları filtreleyen nöron grubu buldu. Devre dışı bırakılınca odaklanma kayboldu. DEHB gibi dikkat bozukluklarına yeni tedavi yöntemleri geliştirilebilir.

📎 BBC News
```

### Category Emojis
- 🔬 / 🧠 Bilim (science)
- 📱 Teknoloji (tech)
- 📊 Ekonomi (economy)
- 🌿 Yaşam (lifestyle/health)
- 🌍 Dünya (world news)
- ⚡ Breaking (urgent/fresh items)

### Quantity Rules
- **Total**: 8-10 haber (Edel'in Bundle v3 tercihi)
- **Tech/Science minimum**: En az 6'sı bilim ve teknoloji olsun (Edel'in spesifik tercihi)
- **Economy**: Maksimum 1-2 haber
- **Gündem/World**: Çok az veya mümkünse atla (breaking durumu hariç)
- **Magazin/Spor**: Atlanır
- **Yaşam**: Seyrek, her seferde değil

### Deduplication (Intra-Bundle)
All 8-10 items must be UNIQUE stories. Before finalizing:
1. Scan all selected items for shared proper nouns + same event type
2. If two items describe the same underlying story (e.g., "OpenAI chip" appearing in both tech and economy), keep ONLY the more detailed version
3. Remove the redundant entry — even if it fits a different category
4. Verify final count still meets tech/science minimum after dedup

### Output Structure
Haberleri kategorilerine göre grupla, aynı kategori altında birden fazla haber varsa hepsini o kategorinin altında sırala. Her haber ayrı bir blok olsun (--- ayracı ile ayrılmış). En sondaki özet kısmında ("Öne çıkan tema") dikkat çeken bir gözlem paylaş.

### Language Tone
- Sohbet dili — resmi olma
- Kısa ve öz — uzun paragraflara girme
- 5N1K yapısını kullan ama kontrol listesi gibi sıralama
- Her haberin kaynağını 📎 ile belirt

## News Sources Catalog

A durable reference of all known news sources, their URL patterns, content profiles, and deduplication patterns is available at `references/news-sources-catalog.md`. Consult this before starting a gathering run to know which sources to prioritize and how they overlap. **Last updated 2026-07-02** — added Nature.com News and Reuters AI Hub as new primary/secondary sources.

## Pitfalls

- **Never modify files in `raw/`** — sources are immutable. Corrections go in wiki pages.
- **Always orient first** — read SCHEMA + index + recent log.
- Always update `index.md` page count and `log.md` after changes
- Use dated title convention for archival sources so future deduplication works
- **Context compaction during long runs**: Processing 10+ news items can fill 200K tokens and trigger context compaction. When you see compaction markers in the session, complete current writes ASAP and avoid re-reading pages unnecessarily.
- **index.md drift**: After 3+ runs, the "Recent Activity" section accumulates duplicates. Check and clean it during each run by consolidating same-date entries into one line.
- **index.md patch fragility**: As index.md grows, `patch` with exact-string matching can hit "ambiguous match" errors because the same string fragment appears in multiple places (especially with date-based entries). **Fix**: `read_file` to get the full content → python (or `execute_code`) to insert/edit lines → `write_file` to overwrite. `write_file` is deterministic — no fuzzy matching, no silent failure. Prefer this over `patch` for any index.md operation involving date lines or repeated-entry patterns.
- **NotebookLM auth expiry**: In cron contexts this cannot be fixed without interactive login. Never block the pipeline — always fall through to wiki-only processing.
- **BBC pages show ERR_BLOCKED_BY_CLIENT but still return content**: BBC's pages embed an `edigitalsurvey.com` survey script that triggers ERR_BLOCKED_BY_CLIENT in automated extraction. **This is NOT a failure** — the main article/headline content still comes through via `web_extract`. Do NOT fall back to browser tools when this error appears alongside >2K chars of content. Only switch to browser fallback when extracted content is genuinely below the 2K threshold (genuine empty/SFA response). Added 2026-06-15.
- **BBC sub-page blocking varies by path**: ERR_BLOCKED_BY_CLIENT severity differs per sub-page. `/news/technology` and `/news/business` often block MORE aggressively than `/news` (main page), returning < 1K chars or near-empty content. **Strategy**: BBC Business and Technology sub-page failures are NOT worth retrying or falling back to browser for — the main BBC News page already contains the same stories (tech/econ stories appear in both main and sub-page feeds). Skip failed sub-pages silently; use main page content for all categories. Only retry a sub-page if its story type is entirely absent from the main page (very rare). Added 2026-06-21.
- **TechCrunch Cloudflare Turnstile in web_extract output**: TechCrunch pages embed Cloudflare Turnstile + reCAPTCHA verification widgets that appear as text like "Checking your Browser…", "Verification failed", "Verification expired", "protected by reCAPTCHA" in `web_extract` output. **This is NOT a failure** — the actual article headlines, authors, dates, and content still come through alongside the verification text. Do NOT abandon TechCrunch or fall back to browser tools when you see this pattern. Only treat as failed if the extracted content is genuinely < 2K chars of real article text (excluding the verification boilerplate). Added 2026-06-30.
- **processed_titles.md update via write_file (cron-safe)**: In cron mode, `patch` has known corruption issues (doubled line-number prefixes) and `cat >>` requires terminal. The safest approach is `write_file`: read the full file → append new section → `write_file` the entire content back. **Context cost warning**: For a large file (>15K chars) this doubles the file content in context. This is another reason to **rotate first** — after rotation, the file is small and `write_file` is cheap. Added 2026-06-30.
- **ScienceDaily pages truncate article previews**: ScienceDaily's top page shows only article introductions (2-3 sentences) with links to full articles. Do NOT mistake this for thin content — the headline, date, and link are sufficient for deduplication and filing. For full article text, extract the individual article URL. Added 2026-06-15.
- **ScienceDaily run frequency**: ScienceDaily content is typically 1-3 days delayed vs BBC headlines. Checking it on every cron run (3x/day) rarely finds new content. Optimize: only fetch ScienceDaily on the first run of the day (06:15). Skip on 10:15 and 16:15 runs unless the user explicitly asks for science news. This saves 1 web_extract call per skipped run.
- **BBC Technology page content profile**: BBC Technology (`/news/technology`) is primarily evergreen features (smart glasses, digital health, World Cup tech, startup profiles), NOT breaking news. Breaking tech stories usually appear on BBC News main or BBC Business first. On routine runs, skip BBC Technology unless explicitly asked or when the user wants feature content. Fetching it on every run wastes a web_extract call on headlines that are either already processed or not newsworthy enough.
