# state.db Backup & Restore Architecture

**Created:** 23 Tem 2026
**Context:** Edel required FULL conversation history backup so that total restore is possible if everything is wiped.

## Backup Strategy

| Component | Frequency | Time | Method | Size |
|-----------|-----------|------|--------|------|
| **Full dump** | Weekly (Sunday) | 02:00 | `sqlite3 .dump messages + sessions` → gzip | ~73MB |
| **Incremental** | Daily | 02:00 | New messages since last backup, gzip | ~1-3MB |
| **Retention** | 14 days | N/A | Older full dumps auto-rotated | N/A |

Both go to `backups/state/` in the Hermes git repo → GitHub (`vardocloud.github.io.git`).

## How It Works

### Incremental
- `.last_msg_id` file tracks the last backed-up message ID
- Each night: dump all messages WHERE id > last_id
- Compressed with gzip (~30% of original size)
- Filename: `incr/msgs_YYYY-MM-DD.sql.gz`

### Full (Sundays only)
- Complete dump of messages table (46K rows)
- Complete dump of sessions table (1741 rows)
- 600s timeout (full dump takes 3-5 minutes)
- Filename: `full/msgs_YYYY-MM-DD.sql.gz` + `sessions_YYYY-MM-DD.sql.gz`

## Full Restore Procedure

After total data loss, with git repo cloned:

```bash
# 1. Restore config, skills, wiki (already in git)
cd ~/.hermes
git checkout .

# 2. Find latest full backup
ls -t backups/state/full/msgs_*.sql.gz | head -1

# 3. Decompress
gunzip -k backups/state/full/msgs_LATEST.sql.gz
gunzip -k backups/state/full/sessions_LATEST.sql.gz

# 4. Load into state.db
sqlite3 state.db < msgs_LATEST.sql
sqlite3 state.db < sessions_LATEST.sql

# 5. Apply all incremental dumps after the full dump date
for f in $(ls backups/state/incr/msgs_*.sql.gz | sort); do
  gunzip -k "$f"
  sqlite3 state.db < "${f%.gz}"
done

# 6. Rebuild FTS indexes (not included in dumps)
sqlite3 state.db "INSERT INTO messages_fts(messages_fts) VALUES('rebuild');"
sqlite3 state.db "INSERT INTO wiki_fts(wiki_fts) VALUES('rebuild');"
sqlite3 state.db "INSERT INTO wiki_fts_trigram(wiki_fts_trigram) VALUES('rebuild');"
```

## Key Principle (Edel)

Conversations are NEVER deleted. The 1741 sessions in state.db are a data treasure.
Retention = archive + optimize (trigram index, proper backup), NOT delete.
New messages add ~700-1000 rows/day → ~1-3MB in git.
