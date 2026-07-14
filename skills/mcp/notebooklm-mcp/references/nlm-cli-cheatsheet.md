> ⚠️ **OBSOLETE (11 Tem 2026)** — Bu dosya eski `nlm` CLI (v0.8.1 jacob-bd) içindir.
> Sistemde yüklü olan `notebooklm-mcp` v2.0.11 **bu komutları desteklemez.**
> Güncel CLI referansı: `references/v2.0.11-cli.md`

# nlm CLI Cheatsheet (OBSOLETE)

## Quick Reference

```bash
# Auth
nlm doctor                           # Status check
nlm login                            # Interactive login

# Notebooks
nlm notebook list                    # List all
nlm notebook get <id>                # Details
nlm notebook create "Title"          # Create
nlm notebook delete <id>             # Delete

# Studio — Create
nlm [type] create <nb_id> --confirm
# Types: audio, video, slides, infographic, quiz,
#         flashcards, report, mindmap, data-table

# Quiz with options
nlm quiz create <nb_id> --count 10 --difficulty 3 --focus "topic" --confirm

# Slides with options
nlm slides create <nb_id> --format presenter_slides --language tr --confirm

# Studio — Status & Download
nlm studio status <nb_id>            # List artifacts
nlm studio status <nb_id> --json     # JSON output
nlm download [type] <nb_id> --id <artifact_id>
# Download types: audio, video, slide-deck, infographic,
#                 quiz, flashcards, report, mind-map, data-table

# Sources
nlm source add <nb_id> --url "https://..."
nlm source add <nb_id> --text "content"
nlm source list <nb_id>

# Query
nlm query <nb_id> "Question?"
nlm cross query <id1>,<id2> "Question?"

# Research
nlm research start <nb_id> --query "Topic"
nlm research status <nb_id>
nlm research import <nb_id>

# Batch & Pipeline
nlm batch query "<nb_ids>" "Question?"
nlm pipeline run <nb_id> --steps create,query,audio

# Export
nlm export artifact <nb_id> <artifact_id> --format docs
```

## Migration Notes

Bu komutlar **v2.0.11'de çalışmaz.** MCP tools kullan:

| Old CLI | MCP Tool Equivalent |
|---------|---------------------|
| `nlm notebook list` | `notebook_list` |
| `nlm source add` | `source_add` |
| `nlm studio create` | `studio_create` |
| `nlm download audio` | `download_artifact` |
| `nlm query` | `notebook_query` |
