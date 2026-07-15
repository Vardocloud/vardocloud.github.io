# Dedup Check Sequence — APA Pipeline

> Consolidated procedure: index.md + filesystem double-verification before ingesting.
> Consolidates pitfalls scattered across the main SKILL.md into one runnable sequence.
> Applies to: all channels (Monitor, Press Release, Gmail newsletters, Events).

## The Core Problem

The index.md can be stale (files referenced but deleted, or entries added but files never written). The filesystem can have files not in the index (from manual cleanup). **Neither alone is sufficient.** Always check both.

## Sequence (run in this order, every cron cycle)

### Step 0: Weekend early exit (if applicable)

```bash
# If APA pipeline: check day of week
date +%u   # 6=Sat, 7=Sun → exit immediately
```

APA publishes Mon–Fri only. Weekend runs skip all scraping.

### Step 1: Read index.md completely

```bash
# Read full index — do NOT use offset/limit, or do offset=1 limit=200
read_file "$WIKI/apa-articles/index.md"
```

Capture every entry's filename and status. Note:
- Monitor articles → `2026-07-<slug>.md` naming
- Press releases → same naming convention
- Events → `apa-etkinlikler/` directory
- Podcasts → `2026-07-15-<slug>.md` naming

### Step 2: Filesystem verification

For every entry in the index that claims a file exists:

```bash
search_files "$FILENAME" target="files" path="$WIKI/apa-articles"
```

**Three outcomes:**
| Index says | Disk has | Action |
|------------|----------|--------|
| ✅ işlendi | ✅ File exists | Skip. Content already captured. |
| ✅ işlendi | ❌ File missing | **Re-create.** Pre-register artifact. Index was updated but file was never written (or was deleted). Creates the file from web_extract + browser if needed. Do NOT report this to user — silent fix. |
| ❌ (not in index) | ✅ File exists | Add to index. Previous cleanup missed index update. Silent fix. |
| ❌ (not in index) | ❌ File missing | **Genuinely new.** Process normally. |

### Step 3: Web discovery → Cross-reference with Steps 1+2

When web_search or web_extract finds candidate content:

```bash
search_files "core topic keywords" path="$WIKI/apa-articles" file_glob="*.md"
```

**Important:** Topic-based matching is more forgiving than URL/title matching. APA Monitor and Press Release titles differ for the same article. Search by core keywords, not exact title.

### Step 4: Create ONLY after double-negative

Only create a new file when:
- Index entry does NOT exist for this topic/title
- Filesystem search does NOT find a matching file
- Previous cron output does NOT reference this content (check via session_search)

### Step 5: Write + Index update in one pass

```bash
# 1. Write file
write_file "$WIKI/apa-articles/YYYY-MM-DD-<slug>.md" "...content..."

# 2. Read full index
read_file "$WIKI/apa-articles/index.md"

# 3. Append entry (string manipulation)
NEW_INDEX=$(echo "$INDEX" | head -n$((${SECTION_LINE}-1)); echo "| N | [Title](YYYY-MM-DD-<slug>) | Summary — date |"; echo "$INDEX" | tail -n+${SECTION_LINE})

# 4. Write updated index (always write_file after read_file to avoid partial-write bugs)
write_file "$WIKI/apa-articles/index.md" "$NEW_INDEX"
```

### Step 6: Update totals

Bump the `~N makale` counter in index.md header by 1.

## Pitfalls

- **Partial index read = partial data:** Using offset/limit to read index.md means you miss entries outside the window. Always read the full file, or use offset=1 limit=200 (read everything).
- **URL ≠ Title matching:** Press release titles often differ from Monitor titles for the same article. `"Young adults more perfectionistic"` vs `"Study: Growing up less scary"` can be the same research. Use core keywords.
- **"Haz" status ≠ processed:** If index entry says "Haz" (June) but no status like "işlendi" or "bekliyor", check carefully — it may be pre-registered but not yet extracted.
- **Index.md in the cron context (execute_code is blocked):** Since execute_code is unavailable in cron, you must use `read_file` + manual string processing + `write_file`. The `patch` tool is fragile with large index.md files (ambiguous match errors). Prefer `read_file → modify string → write_file` pattern.
- **Topic-based fuzzy match:** `search_files "patients chatbots" path="$WIKI/apa-articles"` catches articles that mention these words even if the title is different. Always do this before creating a new file.
