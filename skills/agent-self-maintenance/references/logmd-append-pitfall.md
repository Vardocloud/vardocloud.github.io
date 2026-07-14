# log.md Append Pitfall (25 Jun 2026)

## The Problem

The Hermes `write_file` tool **overwrites** the entire target file. Using it on
`wiki/log.md` destroys every prior entry because log.md is an append-only
chronological record.

## How It Happened

- Agent called `write_file(path="wiki/log.md", content="...")` intending to
  append a new entry
- Result: all prior log entries were destroyed
- Recovery required manual backfill using `session_search` to reconstruct 9
  missing days of entries

## Recovery Procedure

1. Stop writing to the file immediately
2. Use `session_search(query="...", sort="newest")` to find recent sessions
3. For each lost day, reconstruct what happened from session transcripts
4. Use `patch` tool to append entries one at a time:
   ```
   old_string: "## [YYYY-MM-DD] <last entry header>"
   new_string: "## [YYYY-MM-DD] <last entry header>\n## [YYYY-MM-DD] action | recovered description"
   ```
5. Verify with `read_file(path, offset=<last-20>)`

## Prevention

- Never use `write_file` on any append-only file
- Use `patch` with the last entry line as `old_string` target
- Use terminal `echo "new entry" >> log.md` when terminal tools are available
- For backfill: `patch` is reversible; `write_file` is not

## Related

- `llm-wiki` skill governs wiki operations (blocked by security scan)
- `session_search` is the recovery source for lost log entries
