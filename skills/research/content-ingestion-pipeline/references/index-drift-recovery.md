# Index Drift Recovery for Ingestion Pipelines

> Cross-reference: content-ingestion-pipeline skill, step 6 ("Update navigation").
> Also: llm-wiki skill pitfalls ("Always update index.md and log.md").
> Last updated: 2026-07-10

## Problem

Automated ingestion pipelines (APA cron, Skool scanner, news-bundle) create
wiki files but skip updating `index.md` and `log.md`. Over time, the index
diverges from the filesystem: files exist but are invisible to navigation.

**Root cause:** Each pipeline focuses on its own output — create files, report
to user. None owns the cross-cutting `index.md`/`log.md` maintenance. The agent
is the only entity that sees the whole picture, so drift recovery falls to any
agent session that discovers it.

## Symptoms

- `index.md`'s "Last updated" date is older than the newest wiki files' `created` dates
- `log.md` ends days/weeks before files exist on disk
- You find files in `apa-articles/`, `skool/`, `news/` not listed in `index.md`

## Detection Scan

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"

# Find files newer than the index (quick scan)
find "$WIKI" -name "*.md" -newer "$WIKI/index.md" \
  -not -path "*/raw/*" \
  -not -path "*/_archive/*" \
  -not -path "*/vanitas-memory/*" 2>/dev/null | sort

# Frontmatter-based (precise scan)
python3 -c "
import os, re
wiki = os.environ.get('WIKI_PATH', os.path.expanduser('~/wiki'))
with open(f'{wiki}/index.md') as f:
    idx = f.read()
# Parse index.md last-updated date
m = re.search(r'Last updated:\s*(\d{4}-\d{2}-\d{2})', idx)
if not m:
    print('Could not find last-updated in index.md')
    exit(1)
index_date = m.group(1)
print(f'Index last updated: {index_date}')

# Find all md files with created > index_date
count = 0
for root, dirs, files in os.walk(wiki):
    dirs[:] = [d for d in dirs if d not in ('raw', '_archive', 'vanitas-memory')]
    for fn in files:
        if not fn.endswith('.md') or fn in ('index.md','log.md','SCHEMA.md'):
            continue
        fp = os.path.join(root, fn)
        with open(fp) as f:
            head = f.read(500)
        cm = re.search(r'^created:\s*(\d{4}-\d{2}-\d{2})', head, re.M)
        if cm and cm.group(1) > index_date:
            print(f'  UNINDEXED {cm.group(1)} | {fp}')
            count += 1
print(f'Found {count} unindexed files')
" 2>/dev/null
```

## Recovery

### Step 1 — Categorize by directory

Group discovered files by their parent directory:

```bash
# Piped summary
find "$WIKI" -name "*.md" -newer "$WIKI/index.md" \
  -not -path "*/raw/*" -not -path "*/_archive/*" \
  -not -path "*/vanitas-memory/*" 2>/dev/null \
  | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn
```

Typical drift hotspots: `apa-articles/`, `skool/`, `news/`, `concepts/`.

### Step 2 — Update index.md

Add batch entries per directory. One line per directory, not per file:

```markdown
- **apa-articles**: 4 entries from July 10 (Editor's Choice, President's Column, Sensory Processing, Sleep Podcast)
- **skool/ai-automation-society**: 6 entries from July 10 (24 Claude Tips, Fable 5, GPT-5.6 Sol Pipeline, AI SEO Agent, Skill Extraction, Fable vs Sol)
```

⚠️ Use `read_file` → modify → `write_file` for index.md updates. The growing
file causes `patch` "ambiguous match" errors (documented pitfall).

### Step 3 — Update log.md

Single batch entry:

```markdown
## [YYYY-MM-DD] backfill | Index drift recovery — N unindexed files found and cataloged
- Discovered and indexed: apa-articles/ (4), skool/ai-automation-society/ (6), news/science/ (2)
```

### Step 4 — Update page count

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
find "$WIKI" -name "*.md" \
  -not -path "*/raw/*" -not -path "*/_archive/*" \
  -not -path "*/vanitas-memory/*" \
  -not -name "index.md" -not -name "log.md" -not -name "SCHEMA.md" \
  2>/dev/null | wc -l
```

## When to Skip

- Time-sensitive cron → note drift, fix next time
- Unindexed files are all in `vanitas-memory/` or `_archive/` → excluded by design
- Drift < 1 day old → pipeline will fix itself

## Prevention (Pipeline Owners)

Each ingestion pipeline should, at a minimum, update `log.md` with a creation
entry for every batch of files it produces. `index.md` batch updates are
optional for pipelines but strongly recommended.
