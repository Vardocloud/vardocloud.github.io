> ⚠️ **OBSOLETE (11 Tem 2026)** — Bu dosya eski `nlm` CLI (v0.8.1 jacob-bd) içindir.
> Sistemde yüklü olan `notebooklm-mcp` v2.0.11 **bu komutları desteklemez.**
> Güncel CLI referansı: `references/v2.0.11-cli.md`

# nlm CLI Usage Patterns (OBSOLETE)

## Studio Status (generation progress)

```bash
nlm studio status <notebook_id>
```

Returns JSON array:
```json
[
  {
    "id": "artifact-uuid",
    "type": "audio",
    "status": "completed",
    "custom_instructions": null,
    "visual_style_prompt": null
  }
]
```

Status values:
- `queued` — waiting in generation queue
- `processing` — actively being generated
- `completed` — ready to download
- `failed` — generation error

## Download Artifacts

⚠️ **`nlm download`** is a command group. `nlm download 48085236...` fails.
Use `nlm download audio <notebook_id> --id <artifact_id>`.

## Studio Create (trigger generation)

```bash
nlm studio create <notebook_id> --type audio
nlm studio create <notebook_id> --type video
nlm studio create <notebook_id> --type infographic
nlm studio create <notebook_id> --type slide-deck
nlm studio create <notebook_id> --type report
nlm studio create <notebook_id> --type mind-map
nlm studio create <notebook_id> --type data-table
nlm studio create <notebook_id> --type quiz
nlm studio create <notebook_id> --type flashcards
```

***

**Bu komutların tamamı v2.0.11'de çalışmaz.**
Kullanılacak MCP tool'ları: `studio_create`, `studio_status`, `download_artifact`.
