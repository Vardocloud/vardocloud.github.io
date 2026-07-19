# Session/State DB Protection — 19 Temmuz 2026

## Context

Edel reported that the conversation about "lokal PC'ye taşınma" (moving Vanitas/Hermes to a local PC) was no longer accessible via `session_search`. Investigation revealed:

- `state.db` (919MB) was **intact** with 1,621 sessions
- The specific session (`sohbethakkındahersey11T`, 11 Jul 2026, 46 messages) **did exist** in the database
- `session_search` FTS5 tool failed to find it with relevant keywords
- `temp_cleanup.py` SAFE list **did not include** `state.db` or any session files

## Files Protected (added 19 Jul 2026 to temp_cleanup.py SAFE_PREFIXES)

| Path | Description | Size |
|------|-------------|------|
| `~/.hermes/state.db` | Main session DB (all conversations) | 919 MB |
| `~/.hermes/sessions.db` | Secondary session index | 0 bytes (empty) |
| `~/.hermes/response_store.db` | Response cache | 20 KB |
| `~/.hermes/kanban.db` | Kanban board state | 156 KB |
| `~/.hermes/sessions/` | Session JSON dump directory | varies |
| `~/.hermes/data/` | Archive/queue JSON files | varies |

## Root Cause

The `SAFE_PREFIXES` list in `temp_cleanup.py` protected skills, plugins, config, scripts, and golden backups — but **not** the session database files. These files survived until now only because the cleanup script targets specific directories (`/tmp/`, `audio_cache/`, `image_cache/`, `cron/output/`) and never walks `~/.hermes/` root broadly. However, any future retention rule targeting the hermes root would have silently deleted 919MB of session history.

## session_search FTS5 Gap

Even with the data intact, `session_search` could not find the July 11 session using keywords like "lokal PC taşınma" or "karanlık ikiz qubes OS". The FTS5 index does contain these terms (verified via direct SQLite query on `messages_fts`), suggesting a tool-level query issue rather than data loss.

**When this happens again:** Use direct SQLite queries on `state.db` as a fallback:
```sql
SELECT s.title, s.id, datetime(s.started_at, 'unixepoch') as started, 
       substr(m.content, 1, 200) 
FROM messages m JOIN sessions s ON m.session_id = s.id 
WHERE m.content LIKE '%search_term%' AND m.role='user'
ORDER BY s.started_at DESC LIMIT 10;
```

## Prevention

- All `*.db` files under `~/.hermes/` are now in SAFE_PREFIXES
- The `sessions/` and `data/` directories are also protected
- Any new retention rule must check SAFE_PREFIXES first
