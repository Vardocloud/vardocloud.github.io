---
name: news-bundle-cron
description: "Recurring multi-source news cron — dedup ledger, 5N1K wiki storage, batch workflow for the Bundle Gündem İşleme v3 cron job"
version: 1.2.0
metadata:
  hermes:
    tags: [news, cron, wiki, ingestion, dedup, 5n1k]
    category: media
    related_skills: [llm-wiki, content-ingestion-pipeline]
---

# News Bundle Cron — Recurring News Ingest + Wiki Storage

This skill governs the recurring (daily or weekly) news-bundle cron job that
fetches headlines across science, technology, economy, and life categories,
deduplicates them against a persistent ledger, writes per-item markdown files
into `~/wiki/news/`, and delivers a 5N1K-formatted batch summary.

The cron prompt itself ("Bundle Gündem İşleme v3" and successors) defines the
exact batch balance and tone; this skill captures the **file layout**, the
**deduplication ledger mechanics**, and the **silent failure modes** that
re-running the cron will hit if not encoded.

## When This Skill Activates

- A scheduled cron job processes a multi-category news bundle (BBC, ScienceDaily,
  SciTechDaily, TechCrunch, Reuters, etc.) for delivery to a chat thread.
- The agent needs to file those news items into `~/wiki/news/` and deduplicate
  against prior batches.
- The agent is asked to lint, rotate, or debug the news ledger.

## Core Concepts

1. **Three file tiers** under `~/wiki/news/`:
   - `news/<category>/<YYYY-MM-DD-slug>.md` — one per news item, in a category subdir
   - `news/YYYY-MM-DD-haber-ozeti.md` — per-day bundle summary aggregating the batch
   - `news/processed_titles.md` — single append-only dedup ledger (the silent-rotor: see Pitfalls)

2. **5N1K headings are real headings here**, not the conversational weave that the
   sohbet skill forbids listing. A news report file is a structured document. Use
   `## Ne?`, `## Kim?`, `## Nerede?`, `## Ne Zaman?`, `## Nasıl?`, `## Neden Önemli?`
   plus optional `## Veri` (for stats) and `## Çıkarım` (one-liner).

3. **Category emojis** in the delivered chat thread: 🧠 bilim, 🔬 science, 📱 teknoloji,
   📊 ekonomi, 🌿 yaşam. Add 📎 source citation line under each item.

## Silent Failure Modes (read before each run)

- **`read_file` truncation at ~500 lines** — `processed_titles.md` already crossed
  this in July 2026. The first read silently drops the most recent entries — exactly
  the ones the next cron needs for dedup. **Always check `total_lines` in the
  response; if >500, also `read_file` with `offset=<total_lines-50>` to read the tail.**

- **Ledger rotation** — when `processed_titles.md` exceeds ~500 lines OR ~50 KB,
  rotate by year: rename to `processed_titles-YYYY.md`, start a fresh ledger with a
  one-line pointer to the archive. The same threshold logic as llm-wiki's `log.md`.
  **The rotation check is a MANDATORY step in the workflow (step 1), not an optional
  maintenance task.**
  **✅ ROTATION COMPLETED — July 18, 2026:** The overdue rotation was finally
  performed. Ledger went from 680 lines / 62 KB → 102 lines (fresh, with last
  ~85 entries retained for dedup). Full archive saved to
  `processed_titles-2026.md`. The four consecutive skips (July 12-15) are
  resolved. **Do NOT rotate again unless `total_lines > 500` or size > 50 KB.**
  **ROOT CAUSE of the original repeated skips (kept as a lesson):** The rotation
  gate was buried in the Pitfalls section and easy to miss when the agent jumps
  straight to news gathering. The workflow step 1 says "ROTATION GATE" but the
  agent reads the ledger, sees the content, and proceeds to search without
  checking the size threshold. Additionally, the rotation procedure only
  documented `mv` (terminal command), but agents in cron mode tend to avoid
  terminal and only use `read_file`/`write_file`/`patch` — so rotation feels
  impossible and gets silently skipped.
  FIX: After `read_file` returns, **check `total_lines` IMMEDIATELY**. If >500,
  STOP — rotate before doing anything else. No exceptions.
  **PROVEN ROTATION METHODS (all cron-safe):**
  - **Method A — terminal `cp + tail` (tested July 18, works cleanly):**
    `cp processed_titles.md processed_titles-2026.md` (archive, original
    preserved as backup during op) then `tail -85 processed_titles-2026.md >
    processed_titles.md` with a fresh header prepended. Safer than `mv` because
    the original is never deleted mid-operation.
  - **Method B — `write_file` (no terminal needed):**
    1. Read the full ledger (first 500 lines + `offset` tail to get all content)
    2. `write_file` to `~/wiki/news/processed_titles-2026.md` with the FULL content
    3. `write_file` to `~/wiki/news/processed_titles.md` with just the header +
       last 80 lines (recent entries for ongoing dedup)

- **`execute_code` blocked under cron mode** — when `approvals.cron_mode` is set
  without a user present to approve, `execute_code` is rejected. Use direct tools
  (`web_search`, `web_extract`, `read_file`, `patch`, `write_file`) instead.

- **`web_extract` max 5 URLs per call** — batch accordingly when verifying 10
  candidates; two calls of 5 each is fine.

- **Don't synthesize without a source** — if `web_extract` truncated details for an
  item, mark `[?]` rather than inferring from the headline alone.

- **DO NOT use `delegate_task` subagents for news gathering** — tested July 11 AND
  July 13 2026: subagents (3-6 parallel) consumed 180-260+ seconds and ~400K-1M tokens,
  returned fabricated URLs, stale articles, and were blocked by Cloudflare/anti-bot
  protection. On July 13, subagent results included hallucinated story details and
  wrong URLs that required a full second verification pass with `web_search`/
  `web_extract` — doubling the work. `web_extract` against the same sources returned
  richer, accurate content in seconds. **Use `web_extract` + `web_search` directly.
  Subagents are counterproductive for this task. This rule was violated on July 13
  and the exact predicted failure occurred. Do NOT repeat.**

- **News aggregator date lag** — ScienceDaily and SciTechDaily often feature peer-
  reviewed studies on their front page months or even 1-2 years after original
  publication. On July 13 2026, the prune bone-density study (DOI: Feb 2024) and
  the dark matter DAMA refutation (PRL: Sep 2025) appeared as "latest" despite
  being old. This is acceptable for a news bundle (the aggregator coverage IS the
  news), but: (a) check the DOI/journal date when extracting details, (b) do NOT
  describe an old study as "new research" if the publication date is >6 months old,
  (c) if a story seems too old to include, skip it in favor of genuinely recent work.

- **Day-summary file skipped (recurring)** — On July 14 AND July 15 2026, the cron
  wrote per-item/category batch files under `news/<category>/` but did NOT write the
  day-summary file (`news/YYYY-MM-DD-haber-ozeti.md`). On July 15, the agent wrote
  `science/2026-07-15-batch.md` and `tech/2026-07-15-batch.md` (category batches)
  thinking these were sufficient — they are NOT. The day-summary is the primary
  deliverable (step 8), per-item files are optional (step 7, "frequently skipped
  to save time"). **Category batch files are NOT a replacement for the day-summary.**
  The day-summary (`YYYY-MM-DD-haber-ozeti.md`) aggregates ALL categories in one
  document and is what makes the news wiki searchable by date.
  **Always write the day-summary file.** If time is tight, skip per-item files.

## Workflow (deterministic order)

1. **Read ledger + ROTATION GATE.** Read `processed_titles.md` via
   `read_file` (check `total_lines`; if >500, also `read_file` with
   `offset=<total_lines-80>` to read the tail for recent dedup entries).
   **Before doing anything else, check ledger size:**
   - If `total_lines > 500` OR file size > 50 KB → **rotate NOW**
     (see Rotation Procedure in `references/news-bundle-pipeline.md`).
     Rename to `processed_titles-YYYY.md`, start fresh ledger, then
     read the fresh file.
   - **Do NOT append to an overdue ledger.** Appending without rotating
     makes truncation worse and dedup less reliable every run.
   Also `search_files pattern="*.md" target="files" path="~/wiki/news"` to
   list existing per-item files — cross-reference with ledger to catch
   partial runs (files without ledger entries = a crashed prior run).
   **Do NOT use `terminal cat` to read the ledger** — terminal stdout
   caps at ~50 KB and silently truncates, dropping middle entries you
   need for dedup. Use `read_file` with offset/limit instead.
2. Parallel discovery via `web_extract` + `web_search` (NOT subagents):
   - `web_extract` batch 1 (3 URLs): ScienceDaily `/news/top/`, `/breaking/`,
     `/news/top/science/`
   - `web_extract` batch 2 (2 URLs): SciTechDaily `/`, Guardian AI section
   - `web_search` (2-3 calls, current month): TechCrunch/Reuters headlines
     (these sites block `web_extract`; use search results for discovery)
   - **Recommended: 5 parallel `web_search` calls** for category coverage:
     science, technology, space/astronomy, health/biotech, economy — all
     with `"July YYYY"` date restriction. Tested July 14 2026: 5 simultaneous
     calls returned rich results in one round, no need for iterative searching.
   - **Also effective: `web_extract` on 3 news homepages simultaneously**
     (ScienceDaily + UniverseToday + SciTechDaily in one call, BBC + BBC Science +
     TechCrunch in another). Tested July 14 2026.
   See Pitfalls for why `delegate_task` subagents must NOT be used.
3. Deduplicate: fuzzy-match each candidate against ledger entries. Semantic
   equivalence beats exact string match (e.g. "Hubble captures stellar sparkler"
   ≈ "NASA's Hubble spots a stellar sparkler").
4. Filter for batch balance: 8-10 items, ≥60% science+tech, 1-2 economy,
   no magazin/sport. Optional life/health item, not every run.
5. Detail extraction: `web_extract` (max 5 URLs per call) for the 3-5 best
   candidates to fill 5N1K headings.
6. Write per-item files under `news/<category>/`.
   **In cron runs, this step is frequently skipped to save time** — the day-summary
   file (step 7) captures all items in one document and is what the delivered output
   mirrors. Per-item files add value for long-term wiki searchability but are not
   required for the cron's primary deliverable. If time is tight, skip to step 7.
7. Write day summary at `news/YYYY-MM-DD-haber-ozeti.md` (or `news/YYYY-MM-DD-bundle.md`).
8. Append to ledger with a new `## YYYY-MM-DD (NEW — Bundle)` heading.
9. Final response: 5N1K-styled news thread with category emojis and 📎 citations.

## Lint / Maintenance

When asked to audit or rotate the news ledger:

- Check `processed_titles.md` line count and byte size.
- If either threshold crossed, rotate by year (see above).
- Verify every per-item file since the last rotation has a corresponding line in
  the ledger (otherwise dedup missed it).
- Verify the day-summary file exists for each cron-run date in the ledger.
- Check for orphan per-item files (no matching ledger entry) — they signal a
  partial run that crashed between step 6 and step 8.

## Related

- `references/news-bundle-pipeline.md` — operational details, file templates,
  rotation procedure, and cron workflow checklist. Read this for the full
  step-by-step when first running or debugging the cron.
- `llm-wiki` — general wiki conventions and orientation; the `news/` directory
  is an extension of the wiki governed by this skill.
- `content-ingestion-pipeline` — sibling skill for general content ingestion
  into wiki + NotebookLM (this skill is news-cron-specific).