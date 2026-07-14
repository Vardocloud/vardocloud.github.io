# Wiki → NotebookLM Bridge

Bridge wiki pages (Layer 4) to NotebookLM (Layer 6, Vault) for permanent deep archive.

## Working Method (CONFIRMED 12 Jul 2026)

```bash
# ✅ WORKS — file-based, markdown-safe
nlm source add <NOTEBOOK_ID> --file <wiki_md_path> --title "Title" --wait --wait-timeout 120

# ❌ DOES NOT WORK — inline markdown special chars break it
# nlm add text <NOTEBOOK_ID> "$(cat file.md)" --title "..."   # FAILS with special chars
```

## Profile Rules (Edel, 12 Jul 2026)

- **legacy** = DEFAULT for archive/memory operations (nlm source add, notebook query)
- **pro** = Studio only (audio, video, slide_deck, infographic, quiz)

Switch default: `nlm login switch legacy`

## Notebooks

| Notebook | ID | Purpose |
|----------|-----|---------|
| Vanitas AI Araştırmaları | `e4944538-d981-4dab-adeb-7dbef4f8deec` | Skool/tech/AI content (primary) |
| APA Monitor 2026 | `5cc9dbbc-d23e-4eb7-932b-6988f828eba4` | APA articles |

## Steps

1. Save to wiki (`write_file` under `~/wiki/skool/...`)
2. Auth check: `nlm login --check --profile legacy`
3. Add source:
   ```bash
   nlm source add "$NB_ID" --file "$WIKI_PATH" --title "$TITLE" --wait --wait-timeout 120
   ```
4. Verify: look for `✓ Added source: ... (ready)` in output
5. On auth failure: skip, report in summary, retry next cron tick

## Source Limit

NotebookLM allows ~50 sources per notebook. Beyond that, rotate to a new notebook or prune old sources. Do NOT attempt backfill of all 716 wiki pages — that would require 15+ notebooks.

## Auth Health

- `nb_keepalive.py` runs on cron `nb_keepalive_2h` (every 20 min)
- Both profiles confirmed `✓ Authentication valid!` (12 Jul 2026)
- Chrome CDP port 18800: `curl -sf http://127.0.0.1:18800/json/version`

## Batch Backfill

```bash
python3 ~/.hermes/scripts/wiki_to_notebooklm.py --list     # List pending
python3 ~/.hermes/scripts/wiki_to_notebooklm.py --add <p>   # Single page
python3 ~/.hermes/scripts/wiki_to_notebooklm.py --all        # All (~30min, 716 pages)
```
