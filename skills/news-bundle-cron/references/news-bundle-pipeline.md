# News Bundle Pipeline — Operational Reference

Detailed companion to the news-bundle-cron SKILL.md. Read this when first
running the cron, debugging a failed run, or performing ledger maintenance.

## File Templates

### Per-item news file (`news/<category>/<YYYY-MM-DD-slug>.md`)

```markdown
---
title: "News Item Title"
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: summary
tags: [category-tag, topic-tags]
sources: [SourceName/Institution]
confidence: high | medium | low
---

# News Item Title

## Ne?
[1-2 sentences: what happened]

## Kim?
[Who did it — researcher, institution, company]

## Nerede? / Nasıl?
[Where and how — method, location, mechanism]

## Neden Önemli?
[1-2 sentences: why this matters, implications]

📎 [Source Name], [Date]
```

### Day summary (`news/YYYY-MM-DD-haber-ozeti.md`)

```markdown
# DD Month YYYY — Haber Özeti

## Bilim (N)
1. [Title] — [one-line summary]
2. ...

## Teknoloji (N)
3. [Title] — [one-line summary]

## Ekonomi (N)
4. [Title] — [one-line summary]
```

### Ledger entry (appended to `processed_titles.md`)

```
## YYYY-MM-DD (NEW — Bundle)
- [Title] — [key detail, source, date]
- [Title] — [key detail, source, date]
...
```

## Cron Workflow Checklist

1. **Read ledger + ROTATION GATE** — `read_file ~/wiki/news/processed_titles.md`.
   Check `total_lines`; if >500, also read tail with `offset=<total_lines-80>`.
   **Do NOT use `terminal cat`** — terminal stdout caps at ~50 KB and silently
   truncates, dropping middle entries you need for dedup (confirmed July 12 2026:
   `cat` on the 54 KB ledger lost ~4.4 KB of mid-file entries).
   **Before appending: check ledger size.** If >500 lines OR >50 KB, rotate FIRST
   (see Rotation Procedure below). Do NOT append to an overdue ledger.

2. **List existing files** — `search_files pattern="*.md" target="files"
   path="~/wiki/news"` to see what's already filed. Cross-reference with
   ledger to catch partial runs (files without ledger entries = crashed run).

3. **Parallel discovery** — Use `web_extract` (NOT subagents) against source
   homepages. Tested URLs that return rich content without paywall:
   - `web_extract` batch 1: `sciencedaily.com/news/top/`,
     `sciencedaily.com/breaking/`, `sciencedaily.com/news/top/science/`
   - `web_extract` batch 2: `scitechdaily.com/`,
     `theguardian.com/technology/artificialintelligenceai`
   - `web_search` (2-3 calls, date-restricted to current month) for
     TechCrunch/Reuters headlines (these sites block web_extract)
   Max 5 URLs per `web_extract` call. Do NOT spawn subagents — they are
   slow, unreliable, and fabricate URLs (confirmed July 11 2026).

4. **Deduplicate** — fuzzy-match each candidate against ledger entries.
   Semantic equivalence beats exact string match. If unsure, skip — better
   to miss a story than duplicate one.

5. **Filter for balance** — 8-10 items total, ≥60% science+tech, 1-2 economy,
   no magazin/sport. Optional life/health item, not every run.

6. **Detail extraction** — `web_extract` (max 5 URLs per call) for the 3-5
   best candidates. If `web_extract` truncates, note `[?]` rather than
   inferring from headline alone.

7. **Write per-item files** — one `write_file` per item under
   `news/<category>/`. Use the template above.

8. **Write day summary** — `news/YYYY-MM-DD-haber-ozeti.md` aggregating
   the batch.

9. **Append to ledger** — new `## YYYY-MM-DD (NEW — Bundle)` heading
   with one-line-per-item entries.

10. **Deliver** — 5N1K-styled news thread with category emojis (🧠/🔬/📱/📊/🌿)
    and 📎 source citations. Group by category.

## Rotation Procedure

When `processed_titles.md` exceeds ~500 lines OR ~50 KB:

### Method A: Terminal (if available)
1. `mv ~/wiki/news/processed_titles.md ~/wiki/news/processed_titles-YYYY.md`
2. Create new `processed_titles.md` with header:
   ```
   # Processed News Titles — Dedup Ledger

   > Active ledger. Archive: processed_titles-YYYY.md
   > Append-only. Each batch gets a ## date heading.
   ```
3. Verify the archive file is readable.
4. Log the rotation in the day summary or a maintenance note.

### Method B: write_file (cron-safe, no terminal needed)
1. Read the full ledger in two parts: `read_file` (first 500 lines) +
   `read_file` with `offset=<total_lines-80>` (tail).
2. `write_file` to `~/wiki/news/processed_titles-YYYY.md` with the FULL
   concatenated content (everything you just read).
3. `write_file` to `~/wiki/news/processed_titles.md` with a fresh header
   + only the last ~80 lines (recent entries needed for ongoing dedup).
4. Log the rotation in the day summary or a maintenance note.

**Use Method B when running in cron mode** — it requires only `read_file`
and `write_file`, both of which work in cron mode without approval.

## Source Priority

| Source | Category | URL | web_extract works? |
|--------|----------|-----|---------------------|
| SciTechDaily | Science, Tech | https://scitechdaily.com/ | ✅ Yes |
| ScienceDaily Top | Science, Health | https://www.sciencedaily.com/news/top/ | ✅ Yes |
| ScienceDaily Breaking | All categories | https://www.sciencedaily.com/breaking/ | ✅ Yes |
| ScienceDaily Top Science | Science | https://www.sciencedaily.com/news/top/science/ | ✅ Yes |
| ScienceDaily homepage | All categories | https://www.sciencedaily.com/ | ✅ Yes |
| Universe Today | Space, Astronomy | https://www.universetoday.com/ | ✅ Yes |
| Guardian AI | Tech, AI, Policy | https://www.theguardian.com/technology/artificialintelligenceai | ✅ Yes |
| BBC Technology | Tech, AI, Health | https://www.bbc.com/technology | ✅ Yes (tested July 14) |
| BBC Science & Environment | Science, Space | https://www.bbc.com/news/science_and_environment | ✅ Yes (tested July 14) |
| TechCrunch | Tech, Startups | https://techcrunch.com/ | ✅ Yes (tested July 14) |
| Reuters Tech | Tech, AI, Economy | https://www.reuters.com/technology/ | ⚠️ Anti-bot blocks extract; use web_search |

## Common Pitfalls

- **read_file truncation** — Always check `total_lines`. If >500, read the
  tail separately. The most recent entries (the ones you need for dedup)
  are at the end.

- **terminal cat truncation** — `terminal` stdout is capped at ~50 KB and
  silently truncates large files, dropping middle content. Do NOT use
  `cat` to read `processed_titles.md` — use `read_file` with `offset`/`limit`
  for controlled reads. If you need just the tail: `read_file` with
  `offset=<total_lines-80>`. (Confirmed July 12 2026: `cat` on 54 KB ledger
  lost ~4.4 KB of mid-file entries.)

- **Ledger rotation not performed** — The rotation check is MANDATORY in
  step 1 of the workflow, not optional maintenance.
  **✅ Resolved July 18, 2026:** The overdue rotation (skipped July 12-15) was
  finally performed — 680 lines → 102, archive at `processed_titles-2026.md`.
  Do NOT rotate again unless `total_lines > 500` or size > 50 KB.
  **ROOT CAUSE (kept as lesson):** The agent reads the ledger content, sees
  familiar entries, and proceeds to news gathering without checking
  `total_lines` against the threshold. Additionally, the rotation procedure
  only documented `mv` (terminal), but cron-mode agents tend to avoid terminal
  — so rotation feels impossible and gets silently skipped.
  **PROVEN ROTATION METHODS:**
  - **Method A — terminal `cp + tail` (tested July 18 2026, works cleanly):**
    `cp processed_titles.md processed_titles-2026.md` then prepend a fresh
    header + `tail -85 processed_titles-2026.md > processed_titles.md`.
    Safer than `mv` — original preserved as backup during the operation.
  - **Method B — `write_file` (no terminal needed):**
    1. Read the full ledger (first 500 lines + `offset=<total_lines-80>` tail)
    2. `write_file` to `~/wiki/news/processed_titles-2026.md` with the FULL content
    3. `write_file` to `~/wiki/news/processed_titles.md` with just the header +
       last 80 lines (recent entries for ongoing dedup)
  This is the cron-safe rotation path.

- **web_extract URL limit** — Max 5 per call. Split into multiple calls.

- **execute_code blocked in cron** — Use `terminal`, `search_files`,
  `web_extract`, `web_search` directly. No `execute_code` in cron mode.

- **DO NOT use delegate_task subagents** — Subagents browsing news sites
  (BBC, TechCrunch, SciTechDaily, Reuters) are slow (180-260+ sec), token-hungry
  (~400K-1M tokens for 3-6 agents), and unreliable. They fabricate URLs, get blocked
  by Cloudflare, and return stale content. On July 13 2026, 3 subagents returned
  partially hallucinated story details and wrong URLs — a full second verification
  pass with web_search/web_extract was needed, doubling the work. Use `web_extract`
  against source homepages and `web_search` for date-restricted discovery instead.
  This was tested and confirmed on July 11 AND July 13 2026.

- **Best source URLs for web_extract** (tested July 2026, all return rich
  content without paywall/login):
  - `https://www.sciencedaily.com/news/top/` — top science headlines + summaries
  - `https://www.sciencedaily.com/breaking/` — breaking news with full summaries
  - `https://www.sciencedaily.com/news/top/science/` — science-specific top
  - `https://scitechdaily.com/` — physics, quantum, biology, space, AI
  - `https://www.theguardian.com/technology/artificialintelligenceai` — AI news
  - `https://techcrunch.com/` — startup/funding/product news (via browser or extract)
  - `https://www.reuters.com/technology/` — Reuters tech (anti-bot may block extract;
    use `web_search` as fallback)

- **News aggregator date lag** — ScienceDaily and SciTechDaily feature peer-
  reviewed studies on their front pages months to years after original publication.
  On July 13 2026: prune bone-density study (DOI: Feb 2024) and dark matter DAMA
  refutation (PRL: Sep 2025) appeared as "latest." Check DOI/journal dates when
  extracting. Acceptable to include (the aggregator coverage IS the news), but
  do NOT describe an old study as "new research" if publication date >6 months old.

- **Headline-only inference** — Don't write 5N1K details from just the
  headline. Use `web_extract` to get the article body. If details are
  missing, mark `[?]`.

- **Category directory missing** — `mkdir -p ~/wiki/news/science
  ~/wiki/news/tech ~/wiki/news/economy` before writing files if the
  directories don't exist yet. (Note: `write_file` auto-creates parent
  directories, so this is usually unnecessary.)

- **Output length limit** — 10 items × 5N1K format (3-4 sentences each) +
  citations ≈ 2500-3000 chars. The system may truncate the last few lines and
  require a continuation message. On July 15 2026, 10 items at full 5N1K length
  exceeded the response limit — the last item was cut mid-sentence and required
  a second message to complete.
  **Mitigation:** Keep each item to 2-3 sentences max. If the system still
  truncates, reduce to 8 items. The wiki files are the full record — the chat
  delivery is a summary, not the archive. Do NOT sacrifice the day-summary file
  (step 8) to fit more items in the chat output.
