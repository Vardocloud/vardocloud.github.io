# Bundle.app Pipeline (Session Reference)

## Source

- URL: https://www.bundle.app/
- Frequency: Daily (cron job)
- Tool: `web_extract` (returns categorized summary)

**⚠️ Output variability:** web_extract output is NOT guaranteed.
- Best case: ~3.8K chars (headlines + short descriptions per category)
- Worst case: ~1K chars (minimal content — site may have changed or extraction degraded)
- When output is <2K chars, immediately skip to the **Browser Fallback** section below.
  Do not attempt to extract meaning from minimal text.

## Output Limitation

- Cap at **10 most important items** for the report to prevent truncation in delivery context.
- Quality over quantity. If a source has 50+ items, pick the top 10 by: geopolitical impact > security > AI/tech > economics > culture.

## NotebookLM Archive

- Notebook: "🧠 Vanitas Hafıza Arşivi" (ID: 6c7f3daa-1640-4fad-9917-ec44bc432e58)
- Title convention: `Bundle — YYYY-MM-DD HH:MM` (Istanbul time, 24h format)
- **Tool**: `nlm` CLI exclusively — MCP NotebookLM tools are broken (Google CookieMismatch)
- **nlm CLI offers TWO equivalent syntaxes** — both confirmed working:

  **Syntax 1 — `nlm source add` (file-based):**
  ```bash
  # Write content to a temp file first, then submit
  echo "content" > /tmp/bundle-archive-YYYY-MM-DD.md
  nlm source add <NOTEBOOK_UUID> --file /tmp/content.md --title "Bundle — YYYY-MM-DD HH:MM" --wait --wait-timeout 120
  ```
  - `--file` accepts a local markdown file path — avoids ALL shell quoting/special character issues
  - `--wait --wait-timeout 120` blocks until processing completes and returns the source ID
  - Output on success:
    ```
    Uploading <filename> and waiting for processing...
    ✓ Added source: Bundle — 2026-06-10 06:23
    Source ID: fff5d2f7-00bb-40b9-a4ff-67185ce872ca
    ```
  - On auth failure: CLI returns an error (no `✓ Added source` line). Check for the `✓` prefix.
  - **Workflow**: write content to `/tmp/bundle-archive-YYYY-MM-DD.md` → `nlm source add ... --file ...`

  **Syntax 2 — `nlm add text` (inline/pipe-based):**
  ```bash
  # Inline content with shell substitution (BEST for large content without temp file juggling)
  nlm add text <NOTEBOOK_UUID> "$(cat /tmp/bundle-archive-YYYY-MM-DD.txt)" --title "Bundle — YYYY-MM-DD HH:MM" --wait --wait-timeout 120
  ```
  - Text content is a POSITIONAL argument, NOT a `-t` flag
  - ✅ Correct: `nlm add text <UUID> "text content" --title "Bundle — YYYY-MM-DD HH:MM"`
  - ❌ Wrong: `nlm add text <UUID> -t "text" --title "Title"`  # -t does not exist
  - **`$(cat file)` works cleanly** even for content with special characters, newlines, quotes
  - Returns source ID directly in the same format as `nlm source add`:
    ```
    ✓ Added source: Bundle — 2026-06-10 09:59
    Source ID: 81660b57-2e18-403a-8405-f470a2cb2ad6
    ```
  - For pipe-based large content:
    ```bash
    cat /tmp/bundle-archive.txt | nlm add text <UUID> --title "Bundle — YYYY-MM-DD HH:MM"
    ```

  **Which to use?** Both achieve the same result. Prefer:
  - `nlm source add --file` for very large content (cleaner, no shell expansion concerns)
  - `nlm add text "$(cat file)"` for mid-size content and one-liner workflows (no extra file write step)
- **Deduplication**: `nlm` CLI does not have a `notebook_get` equivalent. Strategy:
  - Check the output of the `nlm add text` command for confirmation (look for source_id)
  - If title already exists, NotebookLM creates a duplicate — acceptable for journal
  - Alternatively, check the NotebookLM web UI manually between runs

### nlm Auth Failure — Known Error States

The nlm CLI can fail in different ways. **Note**: The `nlm source add` syntax is the CURRENT working command. If auth is working, it succeeds cleanly. Diagnostic approach:

| Error Message | Meaning | Action |
|---|---|---|
| `Profile 'default' not found. Run 'nlm login' first.` | Config missing/corrupt — nlm has no saved profile at all | Cannot fix in cron context. Report "Auth broken — nlm login needed". Skip archive. |
| `Authentication failed` or `401` | Auth token expired (typical ~7 day expiry) | Cannot fix in cron context. Skip archive. Report "Auth broken". |
| `Error: Network error` | nlm server unreachable | Retry once with 30s delay. If still fails, skip archive. |

**Cron handling (all cases):** Skip archive, continue with wiki processing, document error in report.
- Never block the pipeline — always fall through to wiki-only processing.
- All wiki work (page creation, index updates, log entries) proceeds normally.
- The missing archive entry is logged in `log.md` so manual backfill is possible.

### Wiki Processing — Known Patterns

### Batch Concept Checking (Efficient Verification)

Before creating or updating concepts, batch-check existing files in one parallel call:

```python
# Use multiple search_files calls in parallel to check all candidate concepts at once
search_files(target='files', path='~/wiki/concepts', pattern='israel-lebanon*')
search_files(target='files', path='~/wiki/concepts', pattern='ukraine*')
search_files(target='files', path='~/wiki/concepts', pattern='broadcom*')
# ... one per candidate concept
```

Each returns `total_count: 1` if file exists, `0` if new. Process results:
- **Total == 1** → Read file, check `updated` date, update if newer info available
- **Total == 0** → Create new concept page

This is faster than reading `index.md` and parsing it, especially when checking 8-10 specific filenames.

### Concept Creation Candidates (by domain):
- **Geopolitics**: border conflicts, sanctions, military strikes, peace deals
- **AI/Tech**: model releases, privacy updates, chip markets, security vulns
- **Economics**: market drops, mergers, tariffs, labor disputes
- **Culture**: philosophical figures, boycott movements, social psychology

### Existing pages to check for updates:
- `anthropic.md` — AI ethics context
- `nvidia-rtx-spark.md` — chip/AI hardware mentions
- `meta-ai-chatbot-instagram-vuln.md` — security/privacy context
- `broadcom-market-value-drop.md` — chip market volatility
- `scale-ai.md` — AI data labeling (added 2026-06-09)
- `whatsapp-ads-2026.md` — Meta ad strategy (added 2026-06-09)

### index.md Maintenance:
- After multiple runs, `index.md` accumulates duplicate "Recent Activity" entries
- During each run: scan for duplicates, consolidate same-date entries into one line
- **⚠️ Don't use `patch` for index.md edits** — as the file grows, fuzzy string matching causes "ambiguous match" errors. Use `read_file` → process with python → `write_file` instead.
- Keep page count accurate

### Browser Fallback (When web_extract Returns Minimal or Truncated Content)

Bundle.app is a JS-heavy SPA. web_extract may return only ~1KB of minimal content
(headlines without descriptions, or just the loading shell). The LLM summary
(~5K chars capped) may also miss critical headlines due to summarization bias.

**⚠️ web_extract truncation pitfall (June 2026):** web_extract commonly returns
~30K total chars but only the first ~5K are visible (LLM summarization timeout).
This gives the illusion of enough content, but TRUNCATION is likely. Even if output
is >2K chars, if it feels incomplete (only headlines visible from top 1-2 cards),
treat it as truncated and go browser-first.

**When to trigger browser fallback:**
- Output < 2K chars → minimal content, immediate switch
- Output > 2K but only first 1-3 headlines visible → truncation artifact
- User instruction says "get full headlines" or content feels thin

**Steps (browser_navigate, NOT Playwright — Browserbase tools work for Bundle):**

1. **Step 1** — Navigate separately to each category page:
   - `browser_navigate("https://www.bundle.app/en/breaking-news")` → Agenda
   - `browser_navigate("https://www.bundle.app/en/technology")` → Science & Tech
   - `browser_navigate("https://www.bundle.app/en/finance")` → Finance/Economy
2. **Step 2** — Each navigation returns a snapshot with all visible headlines.
   Read the `snapshot` field for StaticText lines containing article titles.
3. **Step 3** — Collect unique headlines across all 3 pages. Bundle's "Highlights"
   section shows ~15-20 headlines per page including brief summaries.
4. **Step 4** — Deduplicate against `processed_titles.md` using both exact match
   AND fuzzy match (Jaro-Winkler threshold ~0.85 for headline similarity).
5. **Step 5 (batch research)** — For 10-25 NEW headlines, delegate research to
   a subagent via `delegate_task`. This is MORE efficient than sequential web_search:
   ```python
   # Delegate batch research of all new stories to one subagent
   delegate_task(
       goal="Research these 25 news stories and return 2-3 sentence summaries...",
       toolsets=["web", "search"]
   )
   ```
   The subagent runs parallel web searches (~60 searches in 5 minutes) and returns
   structured data. This avoids context bloat from 25 sequential web_search calls.
6. **Step 6 (prioritize)** — From all verified headlines, select **5-7** by:
   tech/science > economy > AI > geopolitics > gündem (weighted per user preference)
7. **Step 7 (skip Playwright)** — Do NOT fall back to Playwright for Bundle. The
   browser_navigate tool (Browserbase) renders Bundle's SPA correctly. Only switch
   to Playwright if browser_navigate itself fails (timeout/403).

### Efficiency Principle (Updated)

### Efficiency Principle
Don't try to extract every article body. The headline + description is often enough to:
- Identify new entities/events that need wiki pages
- Recognize existing concepts that need updates
- Make the priority cut (top 10)

Only deep-search the stories that make the top 10 cut.

### Browser Session Rules for Cron Jobs
- Do NOT leave browser sessions open — always complete within the cron job's runtime
- No interactive elements needed — just scroll + snapshot
- Bundle.app has no login wall for browsing content

## Cron Delivery Rules

This pipeline runs as a scheduled cron job. Two delivery rules:

1. **Final response is auto-delivered** — do NOT call `send_message`. Your final output goes to the configured destination automatically.
2. **SILENT signal** — If there is genuinely nothing new to report (all stories seen before, no significant developments), respond with exactly `[SILENT]` (nothing else). This suppresses delivery.
3. **Hybrid instructions conflict** — If the cron job's step-by-step says "use send_message" but `send_message` is not in your available tools (it won't be in cron context), the system prompt rule wins. Just produce your report as the final response.
4. **Deliverables format** — Use the structured report format below. Keep it compact.

### Report Format (for final delivery)

Use this structured format with emoji indicators:

```
Bundle haber işleme tamamlandı. 📰

İşlenen haber: X başlık

Wiki'ye eklenen yeni kavram: Y adet
- kavram1 (kısa açıklama)
- kavram2 (kısa açıklama)

Güncellenen kavram: Z adet

NotebookLM arşiv: ✅ veya ⛔ (sebep belirt)

Dikkat çeken gelişmeler:
- En önemli 1-2 gelişme (tek cümleyle)
```

## Context Compaction During Long Runs

Processing 10+ news items generates many tool calls and can fill ~200K tokens,
triggering context compaction (the system replaces the conversation with a summary).

**If compaction occurs mid-run:**
- The compacted summary preserves key decisions and completed actions
- Complete any in-progress `kanban_*` or file writes IMMEDIATELY when you see compaction markers
- Do NOT re-read wiki pages you already processed — trust the compaction summary
- Focus on finishing the remaining steps (wiki updates, archive attempt, final report)
- The compaction summary is a handoff, not a blocker — continue working

## Decision Notes

- Skip routine sports, weather, traffic items — not domain-relevant
- Cultural items can bridge `psikoloji` and `maneviyat` domains — evaluate on depth
- Economic items with consumer behavior angle are high priority
- Security incidents are ALWAYS high priority
- When web_extract returns <2K chars, assume the page didn't render fully and go browser-first
