# Systematic Cron Maintenance Workflow

Generic procedure for a full cron health check. Use this when the user asks for "cron bakımı" or "tüm cron'ların bakım onarımı".

## Phase 1: Discovery

```python
# 1. List all cron jobs
cronjob(action='list')
```

Scan the output for:
- `last_status: "error"` — failed jobs
- `state: "paused"` — disabled jobs  
- `last_run_at` older than expected — stopped jobs
- `next_run_at` in distant future — schedule corruption

## Phase 2: Triage by Failure Type

### LLM-based jobs (has a `prompt_preview`)
Errors are in the job's output file at `~/.hermes/cron/output/<job_id>/<timestamp>.md`. Read it:
```python
read_file(path=f"~/.hermes/cron/output/<job_id>/<latest_file>")
```
Common LLM failure modes: model unavailable, tool limit hit, delivery misroute, content filter, quota exhausted.

### no_agent script jobs (has a `script` field, `no_agent=true`)
Script errors are in the same output directory. The file has a structured format showing:
```
# Cron Job: <name>
**Mode:** no_agent (script)
**Status:** script failed
Script exited with code N
stderr:
<actual error message>
```

Read the file:
```python
read_file(path=f"~/.hermes/cron/output/<job_id>/<latest_file>")
```

Common script failure modes:
- `No such file or directory` — script references a path that doesn't exist
- `line N: <path>: No such file or directory` — missing binary or directory
- `ModuleNotFoundError` — Python import fails (check which python binary vs which has packages installed)
- Exit code 127 — command not found
- Exit code 1 — script logic failure

## Phase 3: Root Cause Diagnosis

For each error, trace backward:

| Symptom | Investigate |
|---------|-------------|
| Python import error | `which python3` → `ls -la $(which python3)` (symlink target) → `python3 --version` → `pip3 show <pkg>` |
| Missing directory/file | `ls -la <parent_dir>` → script writes to dir that doesn't exist → `mkdir -p` |
| Missing env var | Script says "variable not set" → check `.env` file |
| Script sayısal çıkış | Check script content for the specific line referenced in stderr |

### Python Version Mismatch (Common Pattern)

Sometimes `/usr/bin/python3` is a symlink to a newer Python (3.13) but pip packages were installed under an older system Python (3.11):

```bash
# /usr/bin/python3 -> python3.13  ← symlink to newer version
# pip packages in /usr/local/lib/python3.11/site-packages/  ← older version
```

Fix: Change the script to use the correct Python binary explicitly:
```bash
# BEFORE
exec /usr/bin/python3 -c "..."

# AFTER  
exec /usr/local/bin/python3.11 -c "..."
```

Alternatively, install the missing package for the correct Python:
```bash
/usr/local/bin/python3.11 -m pip install <package>
```

## Phase 4: Fix Checklist

For each broken job, document:

- [ ] Root cause identified
- [ ] Fix applied (patch, mkdir, env var add, script edit)
- [ ] Fix verified (test run, import check, manual cron run)
- [ ] Job re-enabled (if was paused) or next_run confirmed

## Phase 5: Summary

Report to user:
```
**✅ Biten Bakım:**

| Ne Yapıldı | Durum |
|---|---|
| <cron name> fix | Test ✅ |
| <cron name> paused | Şifre yok, bekliyor |
| Sağlıklı cron'lar | N adet |
```

## Job Lifecycle Decisions

| Condition | Action |
|-----------|--------|
| Job paused >30 days, no clear fix | Remove (user to confirm) |
| Job missing critical credential | Pause, explain to user |
| Job has minor path/dir fix | Fix, keep running |
| Job model/provider outdated | Update model/provider |
